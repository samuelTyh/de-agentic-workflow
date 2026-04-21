# Migration Status

**Agent:** Migration Agent

## Inputs
- None (queries both Snowflake accounts)

## Steps
1. Connect to account A and account B
2. Inventory objects on both accounts: databases, schemas, tables, views, UDFs, stages, pipes
3. Diff the inventories — what exists in A but not B, what exists in both
4. For objects that exist in both: compare row counts, schema definitions, grants
5. Check Airflow DAG configs — which still point to account A
6. Pull related Jira tickets for migration progress

## Output Format

### Migration Status: Account A → B

**Overall:** [X]% objects migrated

### Objects
| Type | In A | In B | Migrated | Remaining |
|------|------|------|----------|-----------|

### Discrepancies
| Object | Issue | Action Needed |
|--------|-------|---------------|

### Pipeline Status
| DAG | Points To | Needs Update |
|-----|-----------|-------------|

### Open Tickets
| Ticket | Summary | Status |
|--------|---------|--------|
