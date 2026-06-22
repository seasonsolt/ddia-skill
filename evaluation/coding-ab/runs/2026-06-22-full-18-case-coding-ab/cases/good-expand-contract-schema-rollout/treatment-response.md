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