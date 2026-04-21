# Data Quality Incidents

## Common Failure Scenarios

### Missing Data

**Symptoms:** Downstream report shows gaps, NULL counts higher than expected, row counts dropped.

**Steps:**
1. Identify the affected table(s) and time range
2. Trace upstream:
   - Check the Airflow DAG that loads this table — did it run? Did it succeed?
   - Check Snowflake load history: `SELECT * FROM INFORMATION_SCHEMA.LOAD_HISTORY WHERE TABLE_NAME = '<table>'`
   - Check source data — did the upstream provider deliver the data?
3. If pipeline ran but data is missing → check for filter/WHERE clause changes in the transformation
4. If source data is missing → escalate to upstream data provider per [Escalation](escalation.md)

### Incorrect Data

**Symptoms:** Values don't match expectations, aggregations are wrong, duplicates present.

**Steps:**
1. Identify specific rows/columns affected
2. Compare current data against a known-good state (backup, previous snapshot)
3. Check recent changes:
   - Git log for the transformation code
   - Schema changes on source or target tables
   - New data arriving with unexpected format/values
4. If transformation bug → fix the code, re-run the pipeline for affected date range
5. If source data quality issue → document and escalate

### Schema Drift

**Symptoms:** Pipeline fails because column was added, removed, renamed, or type changed.

**Steps:**
1. Compare current schema against expected schema
2. Identify the source of change:
   - Upstream provider changed their schema → escalate and adapt
   - Internal schema migration → check if migration was incomplete
3. Update transformation code to handle the new schema
4. If column was removed → check if downstream consumers depend on it

### Stale Data

**Symptoms:** Data hasn't been refreshed, last update timestamp is old.

**Steps:**
1. Check the pipeline schedule — is it running on time?
2. If pipeline is running but data isn't fresh → check for WHERE clauses filtering out recent data
3. If pipeline isn't running → see [Airflow Incidents](airflow-incidents.md)
4. If source data is stale → escalate to upstream data provider

## Recovery Checklist

After resolving any data quality incident:
- [ ] Root cause identified and fixed
- [ ] Affected data corrected or backfilled
- [ ] Downstream consumers notified of the issue and resolution
- [ ] Data quality check added to prevent recurrence
- [ ] Teams thread updated with resolution
- [ ] Postmortem created if P1 or P2
