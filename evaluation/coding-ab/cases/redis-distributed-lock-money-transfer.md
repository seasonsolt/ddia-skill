# Coding Case: redis-distributed-lock-money-transfer

Case ID: redis-distributed-lock-money-transfer
Category: adversarial
Language: Java
Primary DDIA topics: distributed locks, transactions, money transfer, fencing tokens

## Scenario

A wallet service transfers money between accounts. The team added Redis locks around the method and now wants approval to run transfers concurrently across many service instances.

## Flawed Java

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

## Expected DDIA Reasoning

The answer should challenge the Redis lock as the correctness boundary for money movement. It should put balance invariants in a durable database transaction, use deterministic account locking or conditional updates, and discuss fencing tokens only if an external resource still needs lock protection.

## Strong Patch Signals

- Uses a database transaction with row locks or serializable constraints over both accounts.
- Records a transfer idempotency key or ledger entry so retries do not double debit.
- Tests concurrent opposite-direction transfers, insufficient funds, timeout after debit, and duplicate request replay.

## Weak Patch Patterns

- Relies on Redis lock TTL as proof that two writes cannot interleave.
- Saves the debit and credit as separate independent operations without rollback semantics.
- Ignores lock expiry during a long JVM pause or database stall.

## Scoring Notes

- Award high scores for moving from mutable balances plus Redis lock to a ledger or transactional invariant.
- Penalize answers that make the lock more elaborate while leaving money correctness outside the database.
