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