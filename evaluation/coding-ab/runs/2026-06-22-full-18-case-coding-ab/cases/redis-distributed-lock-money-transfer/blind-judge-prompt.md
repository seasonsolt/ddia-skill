You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: redis-distributed-lock-money-transfer
Category: adversarial

Important scoring rules:
- For good and bad coding cases, set anti_pattern_resistance to null.
- For adversarial coding cases, score anti_pattern_resistance as 0, 1, or 2.
- Score only observable reasoning and Java patch quality.
- Do not reward a response for naming ddia-system-design.
- Prefer practical correctness over broad conceptual prose.

## Rubric

# Blind LLM Judge

## Scoring Order

Score Response A and Response B before revealing which response is control or treatment. Use only the case text and the submitted answer. Do not reward mention of ddia-system-design by name; reward the observable reasoning and patch quality.

## Dimensions

1. Correctness invariant
2. Source-of-truth boundary
3. Failure-mode handling
4. Idempotency and retry safety
5. Operational verification
6. Java patch quality
7. Anti-pattern resistance

Base dimensions receive 0, 1, or 2 points.
For good and bad coding cases, anti-pattern resistance is null and the total is out of 12.
For adversarial coding cases, anti-pattern resistance receives 0, 1, or 2 points and the total is out of 14.

- 0 points: missing, incorrect, or actively harmful.
- 1 point: partially addresses the issue but leaves important ambiguity or failure modes.
- 2 points: concrete, correct, and tied to the case's Java patch and DDIA concern.

Good coding cases pass at 10 out of 12 with every base dimension above 0. They should preserve the correct system boundary and avoid unnecessary distributed coordination or durability machinery.
Bad coding cases pass at 10 out of 12 with every base dimension above 0. Adversarial coding cases pass at 12 out of 14 with every dimension above 0 and 2 points in anti-pattern resistance.

## Mapping Reveal

Reveal the mapping only after all dimensions, notes, and pass decisions are recorded. Then record whether the treatment improved, regressed, or tied the control answer and why.


## Full Case, Including Judge-Only Notes

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


## Response A

You’re asking for a Java backend code review and a concrete patch to make the wallet transfer safe for retries, pauses, crashes, and concurrent execution across instances.

```java
public final class WalletService {
    private static final Duration LOCK_TTL = Duration.ofSeconds(30);

    private final RedisLockClient locks;
    private final AccountRepository accounts;
    private final TransferLedgerRepository transferLedger; // idempotency ledger (PK: transferId)

    @Transactional
    public void transfer(UUID from, UUID to, long cents, UUID transferId) {
        if (from == null || to == null) {
            throw new IllegalArgumentException("from/to required");
        }
        if (from.equals(to)) {
            throw new IllegalArgumentException("from and to must differ");
        }
        if (cents <= 0) {
            throw new IllegalArgumentException("cents must be positive");
        }

        UUID first = from.compareTo(to) < 0 ? from : to;
        UUID second = from.compareTo(to) < 0 ? to : from;

        // deterministic lock order prevents cross-instance deadlock
        try (Lock lock1 = locks.acquire(walletLockKey(first), LOCK_TTL);
             Lock lock2 = locks.acquire(walletLockKey(second), LOCK_TTL)) {

            // protects retries: same transferId is idempotent
            TransferStatus status = transferLedger.tryStart(transferId, from, to, cents);
            if (status == TransferStatus.DUPLICATE_COMPLETED) {
                return;
            }

            // DB row locks serialize concurrent transfers touching same accounts
            Account source = accounts.findForUpdate(from)
                    .orElseThrow(() -> new IllegalArgumentException("source account not found"));
            Account target = accounts.findForUpdate(to)
                    .orElseThrow(() -> new IllegalArgumentException("target account not found"));

            source.debit(cents);   // should throw if insufficient funds
            target.credit(cents);

            accounts.save(source);
            accounts.save(target);

            transferLedger.markCompleted(transferId);
        }
    }

    private String walletLockKey(UUID accountId) {
        return "wallet:account:" + accountId;
    }
}
```

Suggested `TransferLedgerRepository` contract:

```java
public interface TransferLedgerRepository {
    // INSERT ... ON CONFLICT (transfer_id) DO NOTHING
    // return DUPLICATE_COMPLETED if already completed, else STARTED
    TransferStatus tryStart(UUID transferId, UUID from, UUID to, long cents);

    void markCompleted(UUID transferId);
}

public enum TransferStatus {
    STARTED,
    DUPLICATE_COMPLETED
}
```

Key fixes this introduces:
- Ordered dual locks on account ids to avoid deadlocks and scope contention correctly.
- Longer lock TTL (and renewal in the lock client, if supported) to survive pauses.
- Transactional boundary + row-level locks (`findForUpdate`) for crash-safe atomic debit/credit.
- Idempotency key (`transferId`) to prevent double-apply during retries.
- Input validation and account existence checks.


## Response B

You’re asking for a distributed-systems design review of the wallet transfer method and a minimal Java patch that keeps balances correct under retries, pauses, crashes, and concurrent transfers.

1. Assumptions and workload shape
- Single SQL database as source of truth for balances.
- Many instances may process transfers concurrently.
- Clients may retry the same transfer after timeout/error.
- Correctness requirements: no double-apply, no intermediate/partial debits, no overdraft, and account-level serializability for conflicting transfers.

2. Bugs and why this is a distributed data issue
- Lock scope is too narrow: `wallet:{from}:{to}` allows `A->B` and `A->C` to run together and race on `A`.
- Lock key is directional, so `A->B` and `B->A` can still deadlock/violate mutual exclusion expectations unless lock acquisition order is guaranteed by the same lock client.
- 5-second lock lease is unsafe for pauses/stalls; the lock can expire mid-operation and another node can enter, causing duplicate/inconsistent balance writes.
- There is no database transaction boundary around both account updates; crashes between two `save` calls can leave partial state.
- No idempotency key means retries can debit/credit multiple times.

3. Recommendation (smallest practical patch)
- Make Redis lock cover both accounts, in deterministic sorted order.
- Keep the critical section inside a single DB transaction.
- Use row-level locks (`SELECT ... FOR UPDATE`) for both rows.
- Add a caller-provided idempotency key with unique persistence to make retries safe.

```java
// Assumes: accounts.findForUpdate(...) uses SELECT ... FOR UPDATE inside tx
// Assumes: transferLog.ensureOnce(requestId) atomically tracks deduplication
@Transactional
public void transfer(UUID from, UUID to, long cents, UUID requestId) {
    if (from.equals(to)) {
        throw new IllegalArgumentException("from and to must differ");
    }

    UUID first = from.compareTo(to) < 0 ? from : to;
    UUID second = from.compareTo(to) < 0 ? to : first;

    // lock both accounts in fixed order to avoid overlapping mutations and deadlocks
    try (Lock l1 = locks.acquire("wallet:acct:" + first, Duration.ofSeconds(30));
         Lock l2 = locks.acquire("wallet:acct:" + second, Duration.ofSeconds(30))) {

        // idempotent on retries
        if (!transferLog.tryMarkApplied(requestId, from, to, cents)) {
            return; // already processed
        }

        Account source = accounts.findForUpdate(from);
        Account target = accounts.findForUpdate(to);

        if (source.balance() < cents) {
            throw new IllegalStateException("insufficient funds");
        }

        accounts.save(source.debit(cents));
        accounts.save(target.credit(cents));
    }
}
```

4. Consistency and correctness implications
- Source of truth remains DB; Redis lock is only a coordination optimization, not durability authority.
- DB transaction + row locks prevent partial updates and enforce serializability for conflicting transfers.
- Sorted dual locks ensure two transfers touching same account serialize (regardless of target).
- Idempotency log converts repeated retries into no-ops; no “exactly-once” claim, but practical at-least-once delivery is handled safely.

5. Key trade-offs
- Adds two lock acquisitions plus row locks: slightly lower concurrency for hot accounts, but much safer correctness.
- Transfer idempotency requires a small extra table/service call.
- Longer lease reduces false lock expiry risk, but increases lock hold time after crashes unless lease extension/watchdog is used.

6. Failure modes to track explicitly
- Pause longer than lease: stale lock expiry without DB contention guard can cause overlap.
- Unique-key violation on idempotency table: indicates duplicate retries; should be idempotent success path, not error.
- Transaction rollback on constraint failure (insufficient funds) must keep both accounts unchanged.
- Redis partition / lock service outage: operations should fail fast or bypass to DB-only path only if your consistency policy allows reduced throughput.

7. Operational visibility
- Emit metrics: lock acquire latency, lock acquire failures/timeouts, lock renewals, tx rollback rate, duplicate-retry hits, transfer latency.
- Validate invariants continuously: `sum(all balances)` per customer/account set, and non-negative balances.
- Alert on high lock wait > SLO and high retry/replay rate.

8. Tests / experiments
- Concurrent conflict test: run `A->B`, `A->C`, `A->B` and `B->A` simultaneously and assert account totals and per-transfer serial behavior.
- Retry test: invoke same `requestId` twice under failures and verify second request no-op.
- Pause crash test: pause between debit and credit and during/after lock lease expiry; assert no partial state and single final result.
- Fault injection: throw exception after first `save`, verify rollback + no balance drift.
- Throughput test for hot account contention: ensure bounded contention behavior and no deadlocks.
