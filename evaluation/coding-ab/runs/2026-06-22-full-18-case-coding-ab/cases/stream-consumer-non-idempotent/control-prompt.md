You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A loyalty service grants points when payment events arrive from a stream. After a consumer restart and replay, some users received more points than expected for the same payment.

## Java Code

```java
public final class LoyaltyConsumer {
    private final LoyaltyRepository loyalty;

    public void onPaymentCaptured(PaymentCaptured event) {
        int points = event.amountCents() / 100;
        loyalty.addPoints(event.userId(), points);
    }
}
```

## Task

Review the handler and propose a patch that makes payment replay and duplicate delivery safe.
