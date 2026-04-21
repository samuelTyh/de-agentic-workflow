# SQL Review

**Agent:** Snowflake SQL Agent

## Inputs
- SQL file path or inline SQL
- (Optional) Context: what the query does, expected data volume

## Steps
1. Read the SQL
2. Check for correctness:
   - Joins have correct predicates (no accidental cross joins)
   - WHERE clauses are selective (partition pruning where possible)
   - GROUP BY matches SELECT columns
   - Data types are compatible in comparisons
3. Check for performance:
   - Avoid `SELECT *` — select only needed columns
   - Use clustering key columns in WHERE/JOIN when available
   - Avoid functions on indexed/clustered columns in predicates
   - Check for exploding joins (many-to-many without filters)
   - CTEs vs subqueries — prefer CTEs for readability, but check for repeated scans
4. Check for Snowflake best practices:
   - Use `QUALIFY` instead of subquery for window function filtering
   - Use `TRY_CAST` / `TRY_TO_*` for defensive type conversion
   - Use `MERGE` for upsert patterns instead of DELETE+INSERT
   - Transient tables for staging/temp data

## Output Format

### Summary
[One-line verdict: pass / needs changes / critical issues]

### Issues Found
| Severity | Location | Issue | Suggested Fix |
|----------|----------|-------|---------------|

### Performance Notes
[Estimated impact and optimization suggestions]
