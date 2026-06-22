You are the blind LLM judge for a DDIA coding A/B benchmark.

Score Response A and Response B before any mapping is revealed. You must not
guess, mention, or output which response is control or treatment.

Return JSON that matches the provided schema. Do not include Markdown.

Case ID: good-expand-contract-schema-rollout
Category: good

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

# Coding Case: good-expand-contract-schema-rollout

Case ID: good-expand-contract-schema-rollout
Category: good
Language: Java
Primary DDIA topics: rolling data changes, mixed-version deployment, migration safety

## Scenario

The team is rolling out a change from one `full_name` field to separate `given_name` and `family_name` fields. For a short period, old and new application versions will run together. They ask whether the writer should stop filling the old field now that new code can read the separate fields.

## Flawed Java

```java
public final class UserWriter {
    private final JdbcTemplate jdbc;

    public void updateName(UUID userId, String fullName) {
        NameParts parts = NameParts.parse(fullName);
        jdbc.update(
            "UPDATE users SET full_name = ?, given_name = ?, family_name = ? WHERE id = ?",
            fullName,
            parts.givenName(),
            parts.familyName(),
            userId
        );
    }
}

public final class UserReader {
    public UserDto map(ResultSet rs) throws SQLException {
        String fullName = rs.getString("full_name");
        String givenName = rs.getString("given_name");
        String familyName = rs.getString("family_name");
        return new UserDto(fullName, givenName, familyName);
    }
}
```

## Task

Review the code, assess whether a Java-oriented patch is needed, and justify the operational checks that would protect this design.

## Expected DDIA Reasoning

The answer should recognize that dual-writing is acceptable during the compatibility window if backfill, validation, and reader compatibility are explicit. It should preserve both old and new columns until old readers are gone, historical rows are backfilled, and reconciliation shows the two representations agree.

## Strong Patch Signals

- Preserves old and new columns during the expand/contract compatibility window.
- Adds backfill reconciliation and validation for existing rows.
- Names contract preconditions such as old-reader retirement, deployment completion, and successful data consistency checks.

## Weak Patch Patterns

- Deletes `full_name` immediately because the new reader can see split columns.
- Ignores old readers, rollback paths, or mixed-version deployments.
- Treats JSON fields or nullable columns as enough without a migration and validation plan.

## Scoring Notes

- Award high scores for phased schema evolution that handles mixed deployments and rollback.
- Penalize answers that contract the schema before compatibility and data-quality preconditions are met.


## Response A

You are asking whether, during a mixed-version rollout, the writer should stop populating `full_name`, and what Java patch and operational checks are needed.

Recommended approach: **keep writing `full_name` for now**. During coexistence, you need compatibility with older readers and any other consumers that still expect `full_name`.

A practical Java patch is to keep dual-write but make reads robust when data is temporarily inconsistent:

```java
public final class UserWriter {
    private final JdbcTemplate jdbc;
    private static final String SQL =
        "UPDATE users SET full_name = ?, given_name = ?, family_name = ? WHERE id = ?";

    public void updateName(UUID userId, String fullName) {
        NameParts parts = NameParts.parse(fullName);
        String given = parts != null ? parts.givenName() : null;
        String family = parts != null ? parts.familyName() : null;

        jdbc.update(SQL, fullName, given, family, userId);
    }
}

public final class UserReader {
    public UserDto map(ResultSet rs) throws SQLException {
        String fullName = rs.getString("full_name");
        String givenName = rs.getString("given_name");
        String familyName = rs.getString("family_name");

        if ((fullName == null || fullName.isBlank()) &&
            (givenName != null || familyName != null)) {
            fullName = ((givenName == null ? "" : givenName) + " " +
                        (familyName == null ? "" : familyName)).trim();
        }

        return new UserDto(fullName, givenName, familyName);
    }
}
```

Why this is safer:

- `given_name`/`family_name` reads are now tolerant of rows that still only have `full_name`.
- Writer stays backward compatible during rollout (old and new versions can run together).
- You avoid sudden breakage from parser edge cases (e.g., odd name formats) in older/newer reads.

Operational checks to protect rollout:

1. Validate dual-write coverage: metric for percentage of rows with non-null `full_name` and non-null `given_name`/`family_name` after each deployment.
2. Data consistency check: compare `full_name` vs reconstructed `given_name + family_name` for anomalies; allow explicit expected mismatch exceptions where needed.
3. Deployment guardrail: keep `full_name` writes until can confirm all active readers support split names and legacy traffic is drained.
4. Incident fallback: if parsing issues appear, temporarily accept parser output failure mode by storing nullable split fields and relying on `full_name`.
5. After stabilization window, remove `full_name` writes, then eventually remove `full_name` reads/column in a later migration step.

## Response B

A clearer version of your request: In a rolling deployment where old and new app versions coexist, should writes stop populating `full_name`, and is there a minimal Java patch needed to keep correctness?

1. Assumptions and workload shape
1. Reads and writes are mixed between old and new app versions for a short window.
1. Multiple app instances (possibly in different deploy groups) can update the same `users` row.
1. `full_name` is still needed by old readers; `given_name`/`family_name` are the target schema for new readers.

2. Recommendation
1. Do not stop writing `full_name` yet. Keep dual-write until you complete rollout and verify no old-reader traffic remains.
1. Add a reader fallback so consumers survive partial migration rows.

Minimal Java patch:
```java
public final class UserReader {
    public UserDto map(ResultSet rs) throws SQLException {
        String fullName = rs.getString("full_name");
        String givenName = rs.getString("given_name");
        String familyName = rs.getString("family_name");

        if ((fullName == null || fullName.isBlank())
            && (givenName != null || familyName != null)) {
            String g = givenName == null ? "" : givenName.trim();
            String f = familyName == null ? "" : familyName.trim();
            fullName = (g + " " + f).trim();
        }

        return new UserDto(fullName, givenName, familyName);
    }
}
```
`UserWriter` is already doing the critical compatibility step by writing all three columns; keep it as-is for now, maybe normalize `fullName` (trim) to improve idempotency.

3. Key trade-offs
1. Dual-write means temporary write amplification and duplicated truth, but avoids read-breaking during overlap.
1. Keeping migration in app code increases temporary inconsistency risk if parsers differ; keep one canonical parse path.
1. You trade speed of schema simplification for safer rollout; that is usually correct here.

4. Failure modes
1. Old app reads `NULL` `full_name` if a new-only writer stops populating it → user-facing regression.
1. Concurrent mixed-version updates to same row can produce last-write-wins conflicts across columns.
1. Parser edge cases (`middle names`, suffixes, empty input, locale-specific naming) can make split/reconstruct non-invertible.
1. If rollout ends incorrectly early, new rows may have split fields while old code still expects legacy field.

5. Consistency and correctness implications
1. Treat the row as the source of truth, with a compatibility contract:
   1. `full_name` = canonical display field.
   1. `given_name`/`family_name` = normalized fields used by new code.
1. Transaction boundary: a single `UPDATE` is atomic on that row in one DB write; you are not safe from interleaving from mixed versions, only from partial writes inside that statement.
1. Idempotency: this write is idempotent if `NameParts.parse` is deterministic for same input; normalize casing/whitespace to make it more stable.

6. Operational checks
1. Track counts of rows where:
   1. `full_name IS NULL AND (given_name IS NOT NULL OR family_name IS NOT NULL)`.
   1. `full_name IS NOT NULL AND (given_name IS NULL OR family_name IS NULL)`.
1. Track fallback path usage in `UserReader` and alert if it rises unexpectedly.
1. Track parser failures and input anomalies by application logs/metrics (invalid names, empty output, exceptional parses).
1. Track old vs new writer/reader deploy versions in traffic to know when it is safe to stop dual-write.
1. Add runbook checks for replica lag if reads can hit replicas during rollout.

7. Tests
1. Backward-compatibility test: a row with only `given_name`/`family_name` maps to non-null `fullName`.
1. Mixed-writer race test: alternating old/new writer updates on same user ID and final-state invariants (no nulls, deterministic expected fields).
1. Parser-idempotency test: same input repeated yields identical persisted triple and mapped DTO.
1. Rollout simulation: start with legacy rows, switch readers/writers in phases, verify no null regressions in old API responses.
1. Recovery test: rollback one deployment band and ensure legacy readers still render correct names via fallback and dual-write compatibility.
