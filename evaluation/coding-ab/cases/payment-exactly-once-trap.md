# Coding Case: payment-exactly-once-trap

Case ID: payment-exactly-once-trap
Category: adversarial
Language: Java
Primary DDIA topics: exactly-once semantics, idempotency, retries, external side effects

## Scenario

A payment worker charges a card and then marks the invoice paid. The product manager asks for "exactly once payment" by wrapping the method in a retry annotation because the payment gateway sometimes times out.

## Flawed Java

```java
public final class PaymentWorker {
    private final PaymentGateway gateway;
    private final InvoiceRepository invoices;

    @Retryable(maxAttempts = 3)
    public void payInvoice(UUID invoiceId) {
        Invoice invoice = invoices.find(invoiceId);
        Charge charge = gateway.charge(invoice.cardToken(), invoice.amountCents());
        invoices.markPaid(invoiceId, charge.id());
    }
}
```

## Task

Review the code and propose a patch that handles timeouts and duplicate worker execution. Be explicit about what guarantee the patch can and cannot provide.

## Expected DDIA Reasoning

The answer should challenge end-to-end exactly-once claims for an external payment side effect. It should use idempotency keys, durable payment attempt records, state transitions, and recovery logic to make retries safe and observable.

## Strong Patch Signals

- Stores a unique payment attempt or idempotency key before calling the gateway.
- Uses gateway idempotency support and records ambiguous timeout states for reconciliation.
- Makes `markPaid` conditional on invoice state and charge identity, with tests for retry after timeout.

## Weak Patch Patterns

- Claims `@Retryable` or a transaction makes the gateway call exactly once.
- Charges first and records later without handling process crashes or unknown outcomes.
- Suppresses gateway exceptions and marks the invoice paid without durable evidence.

## Scoring Notes

- Award credit for precise wording such as "effectively once for this invoice when the gateway honors idempotency keys."
- Penalize answers that promise impossible exactly-once behavior across the database and gateway.
