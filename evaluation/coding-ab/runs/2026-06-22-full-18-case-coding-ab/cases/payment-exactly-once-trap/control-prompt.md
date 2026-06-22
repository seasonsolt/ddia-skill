You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A payment worker charges a card and then marks the invoice paid. The product manager asks for "exactly once payment" by wrapping the method in a retry annotation because the payment gateway sometimes times out.

## Java Code

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
