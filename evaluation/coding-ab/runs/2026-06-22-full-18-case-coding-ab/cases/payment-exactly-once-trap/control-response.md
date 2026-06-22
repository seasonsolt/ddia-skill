Your request in natural English: *Please review this Java payment worker code and propose a patch that safely handles timeouts and duplicate executions, and clearly state what guarantees are and are not provided.*

### Review findings
- `@Retryable` on the whole method can retry after `gateway.charge(...)` returns/throws, so a timeout can cause double charging and/or duplicate `markPaid`.
- There is no coordination between workers, so two workers can charge the same invoice concurrently.
- `markPaid(...)` is not idempotent with respect to retries or duplicate calls.

### Recommended patch (core idea)
Use a two-step worker lease + stable idempotency key:

1. Atomically claim the invoice in DB before calling the gateway (PROCESSING lease).
2. Use that same stored `attemptId` as gateway idempotency key.
3. Make payment completion idempotent and only allow completion when lease matches current attempt.
4. Never retry before an explicit lease/attempt is visible in DB.

```java
public final class PaymentWorker {
    private static final Duration PAYMENT_LEASE_TTL = Duration.ofMinutes(5);

    private final PaymentGateway gateway;
    private final InvoiceRepository invoices;
    private final Clock clock;

    @Retryable(
        maxAttempts = 3,
        retryFor = {GatewayTimeoutException.class, GatewayTransientIOException.class},
        noRetryFor = {InvoiceAlreadyPaidException.class}
    )
    public void payInvoice(UUID invoiceId) {
        PaymentReservation reservation = invoices.reserveForPayment(invoiceId, PAYMENT_LEASE_TTL, clock.instant());

        if (reservation.status() == PaymentReservation.Status.PAID) {
            return;
        }
        if (reservation.status() == PaymentReservation.Status.HELD_BY_OTHER_WORKER) {
            return;
        }

        UUID attemptId = reservation.attemptId();
        Invoice invoice = reservation.invoice();

        Charge charge;
        try {
            charge = gateway.charge(new ChargeRequest(
                invoice.cardToken(),
                invoice.amountCents(),
                attemptId // stable idempotency key persisted by reservation
            ));
        } catch (GatewayTimeoutException | GatewayTransientIOException e) {
            invoices.markTransientFailure(invoiceId, attemptId, e.getMessage());
            throw e;
        }

        // Idempotent completion: safe if retried
        invoices.markPaidIfCurrentAttempt(invoiceId, attemptId, charge.id());
    }
}
```

```java
public interface InvoiceRepository {
    PaymentReservation reserveForPayment(UUID invoiceId, Duration leaseTtl, Instant now);

    // Atomically:
    // - if PAID -> return Paid
    // - if PROCESSING and lease not expired -> return HeldByOtherWorker
    // - else set status=PROCESSING, attemptId=existingOrNew, leaseUntil=now+leaseTtl
    // then return reservation(invoice, attemptId, state)

    boolean markPaidIfCurrentAttempt(UUID invoiceId, UUID attemptId, String chargeId);
    // SQL idea:
    // UPDATE invoices
    // SET status='PAID', charge_id=:chargeId, paid_at=now(), error=null
    // WHERE id=:invoiceId AND status='PROCESSING' AND payment_attempt_id=:attemptId

    void markTransientFailure(UUID invoiceId, UUID attemptId, String reason);
}
```

### What this patch can guarantee
- Prevents duplicate in-flight workers for the same invoice via DB lease/lock.
- Prevents duplicate charges if `PaymentGateway` honors the idempotency key.
- Makes `markPaid` idempotent for the same attempt.
- On timeout retries, the same attempt key is reused, so repeated retries do not usually duplicate charging.

### What this patch cannot guarantee
- **Cannot guarantee exactly once** if the gateway does not support idempotent requests.
- Cannot fully guarantee completion if the process crashes after external charge succeeds but before DB updates; you still need periodic reconciliation for that edge.
- A very long network partition plus short lease TTL could allow lease takeover; final correctness then depends on gateway idempotency and repository checks.