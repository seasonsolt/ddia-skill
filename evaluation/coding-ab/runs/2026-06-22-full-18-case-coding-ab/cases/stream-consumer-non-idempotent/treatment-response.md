A more natural version of your request: *“Please review this handler and propose the smallest Java patch that makes payment replay and duplicate delivery safe, while focusing on distributed-data concerns like source of truth, consistency, transactions, idempotency, failure modes, visibility, and tests.”*

**1) Assumptions and workload shape**
- Payment events are consumed from a stream with at least once delivery.
- Restarts and replay can re-deliver the same `PaymentCaptured` event.
- Each payment must contribute points exactly once per user.
- `loyalty` storage is the system-of-record for balances.

**2) Recommendation**
The current handler is not idempotent: it always calls `addPoints`, so duplicates grant points multiple times.  
Treat `paymentId` (or another unique event identifier) as an idempotency key and make the dedupe + balance update atomic in one DB transaction.

Minimal patch pattern:

```java
public final class LoyaltyConsumer {
    private final LoyaltyRepository loyalty;

    public void onPaymentCaptured(PaymentCaptured event) {
        int points = event.amountCents() / 100;
        boolean applied = loyalty.applyPaymentOnce(event.paymentId(), event.userId(), points);
        if (!applied) {
            // duplicate replay; ignore
        }
    }
}
```

```java
@Transactional
public boolean applyPaymentOnce(UUID paymentId, String userId, int points) {
    int inserted = jdbc.update(
        """
        INSERT INTO processed_payments(payment_id, user_id, points)
        VALUES (?, ?, ?)
        ON CONFLICT (payment_id) DO NOTHING
        """, paymentId, userId, points);

    if (inserted == 0) {
        return false;
    }

    jdbc.update("UPDATE loyalty_account SET points = points + ? WHERE user_id = ?", points, userId);
    return true;
}
```

Also add/ensure schema:
- `processed_payments.payment_id` is `PRIMARY KEY` (or unique).
- Optional: unique index per `(user_id, payment_id)` if needed for traceability.

**3) Key trade-offs**
- Adds one write + one read/insert check per event (small, usually acceptable).
- Requires a durable idempotency store; this is a small schema change but gives a real correctness fix.
- This improves against replay duplicates, not against missing/invalid payment IDs (if `paymentId` is absent you need synthetic keys or producer-side idempotency).

**4) Failure modes**
- Duplicate delivery: now swallowed after first successful insert.
- Concurrent consumers processing same payment: only one insert succeeds due to unique constraint.
- Crash between insert and commit: both insert and points update roll back together (transactional safety).
- Crash after commit: event is safely marked processed, replay becomes no-op.
- Null/unstable `paymentId`: system still vulnerable; must validate contract.

**5) Consistency and correctness implications**
- Source of truth remains the points table (balance), with `processed_payments` as write-ahead dedupe evidence.
- Transaction boundary now defines correctness: “mark processed” and “apply points” are all-or-nothing.
- You do not need global distributed consensus here; DB-level uniqueness plus single-writer atomic tx is enough for this duplicate class.

**6) Operational visibility**
- Count and expose metric: `loyalty.replay_deduped_events_total`.
- Track failure metric: `loyalty.apply_payment_tx_failures_total`.
- Alert on high duplicate ratio (may indicate producer retry storms).
- Log with `paymentId`, `userId`, and result (`applied`/`skipped`) for incident tracing.

**7) Tests to validate**
- Duplicate event replay: same `paymentId` twice, balance changes once.
- Concurrent duplicate replay (2+ threads): balance changes once and no deadlock/constraint exceptions.
- Crash simulation before/after transaction: verify no partial update by forcing rollback.
- Missing/invalid eventId test: assert event is rejected and measured as bad input.
- Idempotency on full consumer restart/replay sequence: persisted balance remains correct.