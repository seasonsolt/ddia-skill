Your message in idiomatic English: “Can you review this Java payment worker and suggest the smallest patch that safely handles gateway timeouts and duplicate execution, while being clear about what correctness guarantees are possible?”

## 1) Assumptions and workload shape
- A single invoice can be charged once and should only create one successful upstream charge.
- Workers may run more than once for the same invoice due to retries (`@Retryable`) and concurrent workers.
- Gateway calls can timeout after side effects have already happened.

## 2) What is wrong in the current code
- `gateway.charge(...)` and `invoices.markPaid(...)` are two separate systems with no atomic boundary.
- A timeout after a successful charge can cause duplicate charging on retry.
- `@Retryable` retries the whole method, but without idempotency, duplicates are expected.
- No state machine/claiming guard around concurrent executions, so duplicate workers can race.

This is a distributed data consistency issue because the DB state (“paid”) and payment system side effects (“charge created”) can diverge and be replayed.

## 3) Smallest practical patch
Make the invoice row a payment state machine and use an idempotency key for the gateway.

### Patch idea (minimal)
- Add one payment attempt key + status columns (or reuse existing columns):  
  `paymentRequestId`, `paymentState` (`OPEN`, `CHARGING`, `PAID`), and `gatewayChargeId`.
- Claim payment in DB before calling the gateway (single state transition).
- Call gateway with a stable idempotency key.
- Mark paid only if claim state matches expected values.
- Only retry on transient gateway/network errors.

```java
public final class PaymentWorker {
    private final PaymentGateway gateway;
    private final InvoiceRepository invoices;

    @Transactional
    @Retryable(
        maxAttempts = 3,
        retryFor = { PaymentTimeoutException.class, TransientIoException.class },
        noRetryFor = { IllegalArgumentException.class }
    )
    public void payInvoice(UUID invoiceId) {
        Invoice invoice = invoices.findForUpdate(invoiceId)
            .orElseThrow(() -> new IllegalArgumentException("Invoice not found"));

        if (invoice.isPaid()) return;

        // Deterministic idempotency key (at least per invoice; can be per attempt token if needed)
        String idempotencyKey = invoice.getPaymentRequestId() != null
            ? invoice.getPaymentRequestId()
            : invoiceId.toString();

        if (invoice.getPaymentRequestId() == null) {
            boolean claimed = invoices.tryStartPayment(invoiceId, idempotencyKey); // atomic transition OPEN -> CHARGING
            if (!claimed) {
                Invoice latest = invoices.get(invoiceId);
                if (latest.isPaid()) return;
                throw new RetryableInProgressException(invoiceId);
            }
        } else if (invoice.isCharging() && invoice.getGatewayChargeId() != null) {
            return; // previous successful charge got recorded with same key
        }

        Charge charge = gateway.charge(
            invoice.cardToken(),
            invoice.amountCents(),
            idempotencyKey
        );

        boolean marked = invoices.markPaidIfCharging(invoiceId, idempotencyKey, charge.id()); // only from CHARGING+matching key
        if (!marked) {
            throw new IllegalStateException("Invoice state changed while charging");
        }
    }
}
```

Repository method intent:
- `findForUpdate`: select invoice `FOR UPDATE`.
- `tryStartPayment`: `UPDATE ... SET state='CHARGING', paymentRequestId=? WHERE id=? AND state='OPEN'`.
- `markPaidIfCharging`: `UPDATE ... SET state='PAID', gatewayChargeId=? WHERE id=? AND state='CHARGING' AND paymentRequestId=?`.

## 4) Consistency, source of truth, and transaction boundaries
- Source of truth for invoice outcome: your invoice DB row (`state`, `gatewayChargeId`).
- Gateway is authoritative for actual money movement and must be queried/reconciled when state is ambiguous.
- DB transaction can protect claim + read-modify-write of invoice state, but cannot include gateway call; that is the fundamental split-brain point.

## 5) Guarantees this patch provides / does not provide
- What it can provide:
  - At-most-once charge attempts on the gateway if the gateway respects idempotency keys.
  - At-most-once DB-marked payment per invoice under normal retries and concurrent duplicates.
  - Deterministic handling of duplicate/replayed `payInvoice` calls.
- What it cannot provide:
  - Absolute “exactly-once” in a distributed boundary (network + crash + timeout windows).
  - If gateway does not enforce idempotency, duplicate charges remain possible without extra external reconciliation.

## 6) Failure modes and operational visibility
- Failure mode: timeout right after charge success, before DB update  
  → retry reuses same idempotency key; gateway returns existing charge or deduplicates.
- Failure mode: crash after claim, before charge  
  → invoice remains `CHARGING`; needs recovery path.
- Failure mode: stale `CHARGING` lock for long time  
  → detect and alert on aged `CHARGING` rows.

Operational signals:
- `payment_claim_conflict_total`
- `gateway_charge_retries_total` by cause
- `gateway_charge_idempotent_reused_total`
- `invoice_stuck_charging_count` (age > threshold)
- `markPaid_if_charging_miss_total` (state divergence indicator)

## 7) Tests to validate
- Unit/integration: duplicate retry after timeout does not create second successful charge (`gateway` called once, or twice-but-deduped by key).
- Concurrent worker test: two threads call `payInvoice` for same invoice; only one transitions to `PAID`.
- Timeout-before-mark test: simulate timeout after successful gateway call; retry should not create extra charge and eventually marks paid.
- Recovery test: simulate crash after claim but before charge; reconciliation/monitoring surfaces stale `CHARGING` and recovers deterministically.

If you want, I can provide a compact “drop-in” version tailored exactly to your current `Invoice` fields and repository API signatures.