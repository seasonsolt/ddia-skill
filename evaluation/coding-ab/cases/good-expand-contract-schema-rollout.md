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
