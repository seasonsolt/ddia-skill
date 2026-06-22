# Coding Case: kafka-total-ordering-trap

Case ID: kafka-total-ordering-trap
Category: adversarial
Language: Java
Primary DDIA topics: stream processing, ordering, idempotency, partitioning

## Scenario

An account service consumes balance-related events from Kafka and stores the last applied sequence on each account. The team asks for a Java patch after seeing occasional skipped or out-of-order account updates during a topic migration.

## Flawed Java

```java
public final class AccountEventConsumer {
    private final AccountRepository accounts;

    public void onEvent(AccountEvent event) {
        Account account = accounts.find(event.accountId());
        if (event.sequence() <= account.lastSequence()) {
            return;
        }
        accounts.save(account.apply(event));
    }
}
```

## Task

Review the consumer and propose a Java-oriented patch. Keep the answer focused on the ordering guarantee the code relies on, how that guarantee should be enforced, and tests for replay, duplicates, and deployment changes.

## Expected DDIA Reasoning

The answer should state that Kafka only orders records within a partition, not globally across a topic. A strong patch must ensure all events for one account use the account ID as the partition key, or move the invariant into a durable conditional sequence check that rejects stale updates and handles gaps without corrupting account state.

## Strong Patch Signals

- Partitions events by account ID or another stable key that maps all account events to the same partition.
- Uses a durable conditional update on account ID and sequence instead of a check-then-save race.
- Handles duplicate delivery, replay from earlier offsets, and sequence gaps explicitly.
- Mentions repartitioning, producer changes, or topic migration as deployment risks that need validation.

## Weak Patch Patterns

- Assumes Kafka provides global ordering across partitions.
- Uses timestamps as the ordering authority for account mutations.
- Ignores repartitioning or producer-key changes during deployment.
- Keeps a non-transactional `find` then `save` sequence check as the only correctness guard.

## Scoring Notes

- This adversarial case tests ordering guarantees and idempotent stream processing.
- Award high scores for patches that combine partition-key discipline with durable idempotency checks.
- Penalize answers that rely on consumer-thread ordering without proving per-account partitioning or storage-level guards.
