You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

An account service consumes balance-related events from Kafka and stores the last applied sequence on each account. The team asks for a Java patch after seeing occasional skipped or out-of-order account updates during a topic migration.

## Java Code

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
