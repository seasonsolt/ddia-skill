You are participating in a coding A/B benchmark.

Do not edit files, do not run commands, and do not mention this benchmark setup.

Produce the answer only.

# Coding Control Instructions

Answer the Java coding case without using or referencing ddia-system-design.

Do not load, invoke, mention, or rely on the DDIA system design skill. Review the code as a general Java backend coding task and provide the patch you would normally recommend.

## Scenario

A wallet service transfers money between accounts. The team added Redis locks around the method and now wants approval to run transfers concurrently across many service instances.

## Java Code

```java
public final class WalletService {
    private final RedisLockClient locks;
    private final AccountRepository accounts;

    public void transfer(UUID from, UUID to, long cents) {
        String lockKey = "wallet:" + from + ":" + to;
        try (Lock ignored = locks.acquire(lockKey, Duration.ofSeconds(5))) {
            Account source = accounts.find(from);
            Account target = accounts.find(to);
            accounts.save(source.debit(cents));
            accounts.save(target.credit(cents));
        }
    }
}
```

## Task

Review the code and propose a patch that protects account balances under retries, pauses, crashes, and concurrent transfers.
