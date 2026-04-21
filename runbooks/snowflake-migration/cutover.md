# Phase 6: Cutover

Switch production workloads from account A to account B.

## Pre-Cutover Checklist

- [ ] All Phase 1-5 checklists complete
- [ ] Validation signed off by team lead
- [ ] Downstream consumers notified of cutover window
- [ ] Rollback plan reviewed and ready
- [ ] Jira ticket created for cutover tracking

## Cutover Steps

### Step 1: Announce Maintenance Window

Post to Microsoft Teams:
```
[Migration] Snowflake cutover: Account A → B
Window: YYYY-MM-DD HH:MM — HH:MM UTC
Impact: Brief pipeline pause. Data may be delayed up to [X] hours.
```

### Step 2: Pause Pipelines on Account A

```bash
# Pause all DAGs that write to account A
astro run airflow dags pause <dag_id>
```

### Step 3: Final Data Sync

For export/import tables, run a final incremental export to capture data written since the last migration batch:

```sql
-- On account A: export only new/changed rows
COPY INTO @migration_stage/<table_name>/final/
FROM (
    SELECT * FROM <table_name>
    WHERE last_modified > '<last_migration_timestamp>'
)
FILE_FORMAT = (TYPE = PARQUET);
```

Load into account B.

### Step 4: Switch Airflow Connections

**Option A (connection swap):**
```bash
astro run airflow connections delete 'snowflake_default'
astro run airflow connections add 'snowflake_default' \
    --conn-type 'snowflake' \
    --conn-host "$SNOWFLAKE_ACCOUNT_B" \
    --conn-login "$SNOWFLAKE_USER_B" \
    --conn-password "$SNOWFLAKE_PASSWORD_B" \
    --conn-schema 'PUBLIC' \
    --conn-extra '{"role": "'$SNOWFLAKE_ROLE_B'", "warehouse": "'$SNOWFLAKE_WAREHOUSE_B'"}'
```

**Option B (DAG-level switch):** If DAGs were duplicated, unpause the account B DAGs and retire the account A versions.

### Step 5: Resume Tasks on Account B

```sql
-- Resume in dependency order: root tasks first
ALTER TASK <database>.<schema>.<root_task> RESUME;
ALTER TASK <database>.<schema>.<child_task> RESUME;
```

### Step 6: Resume Pipelines

```bash
astro run airflow dags unpause <dag_id>
```

### Step 7: Verify

1. Monitor first DAG runs against account B
2. Check Snowflake query history on account B for expected activity
3. Verify downstream dashboards and reports show fresh data
4. Check for errors in Airflow logs

## Post-Cutover

### Day 1
- [ ] All pipelines running successfully against account B
- [ ] Downstream consumers confirmed data is correct
- [ ] No errors in Airflow logs related to Snowflake connections

### Week 1
- [ ] All scheduled DAGs have completed at least one full cycle
- [ ] Data quality checks passing
- [ ] Performance baseline established on account B
- [ ] Any issues documented and resolved

### Decommission Account A (after stabilization)
- [ ] Confirm no pipelines still reference account A
- [ ] Remove account A Airflow connections
- [ ] Rename `snowflake_account_b` connection to `snowflake_default` if not already done
- [ ] Archive account A credentials
- [ ] Update `config/mcp-servers.json` to remove account A config
- [ ] Update this runbook with final status

## Rollback Plan

If critical issues are found after cutover:

1. **Pause account B pipelines**
2. **Revert Airflow connection** to point back to account A
3. **Resume account A pipelines**
4. **Notify team and downstream consumers**
5. **Investigate and fix** the issue on account B
6. **Re-attempt cutover** once resolved

The rollback window is until account A data goes stale (typically 24-48 hours after cutover). After that, account A data is no longer current and rollback becomes more complex.
