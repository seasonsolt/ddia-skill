# Coding Case: stream-consumer-non-idempotent

Case ID: stream-consumer-non-idempotent
Category: bad
Language: Java
Primary DDIA topics: message delivery, idempotency, transactions, recovery

## Scenario

A loyalty service grants points when payment events arrive from a stream. After a consumer restart and replay, some users received more points than expected for the same payment.

## Flawed Java

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

## Expected DDIA Reasoning

The answer should recognize that stream delivery, retries, and replay can duplicate side effects. A patch should record processed event IDs in durable storage or make the loyalty sink idempotent, and the deduplication record and points update should be committed atomically.

## Strong Patch Signals

- Uses a unique processed-message table keyed by payment or event id.
- Updates points and records processing in the same database transaction.
- Adds replay and duplicate-message tests that verify points are awarded once.

## Weak Patch Patterns

- Relies on Kafka exactly-once semantics alone while the database side effect remains non-idempotent.
- Uses an in-memory set for processed events, losing state on restart.
- Swallows duplicate exceptions after the points update already happened.

## Scoring Notes

- Award high scores for connecting at-least-once delivery to durable idempotency at the sink.
- Penalize answers that only move offset commits without addressing duplicate side effects.
