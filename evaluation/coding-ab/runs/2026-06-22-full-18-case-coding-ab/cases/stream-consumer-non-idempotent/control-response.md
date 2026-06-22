A more idiomatic version of your request is:  
*Review this Java payment handler as a general backend task and propose a patch to make it safe when events are replayed or delivered more than once.*

Use an idempotent, transactional write path so each payment event is applied at most once.

```java
public final class LoyaltyConsumer {
    private final LoyaltyRepository loyalty;

    public LoyaltyConsumer(LoyaltyRepository loyalty) {
        this.loyalty = loyalty;
    }

    public void onPaymentCaptured(PaymentCaptured event) {
        int points = Math.max(event.amountCents(), 0) / 100;
        // true => first time this event is seen, false => duplicate replay
        loyalty.awardPointsForPaymentOnce(event.userId(), event.paymentId(), points);
    }
}
```

```java
public interface LoyaltyRepository {
    /**
     * Applies points exactly once per payment event.
     * @return true if points were added, false if this payment event was already processed.
     */
    boolean awardPointsForPaymentOnce(String userId, String paymentEventId, int points);
}
```

```java
// Example JDBC-style implementation
@Transactional
public boolean awardPointsForPaymentOnce(String userId, String paymentEventId, int points) {
    int inserted = jdbcTemplate.update("""
        INSERT INTO processed_payments (payment_event_id, user_id, processed_at)
        VALUES (?, ?, NOW())
        ON CONFLICT (payment_event_id) DO NOTHING
        """, paymentEventId, userId);

    if (inserted == 0) {
        return false; // duplicate or replayed event
    }

    jdbcTemplate.update("""
        INSERT INTO loyalty_balances (user_id, points)
        VALUES (?, ?)
        ON CONFLICT (user_id) DO UPDATE
        SET points = loyalty_balances.points + EXCLUDED.points
        """, userId, points);

    return true;
}
```

Required schema piece:

- Add a unique constraint/index on `processed_payments(payment_event_id)` so duplicates are rejected safely under concurrent replay.

Also critical: ensure `PaymentCaptured` carries a stable unique `paymentId` from the payment source; without that identifier, idempotency cannot be guaranteed correctly.