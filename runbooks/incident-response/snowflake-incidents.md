# Snowflake Incidents

## Common Failure Scenarios

### Query Failure — Timeout

**Symptoms:** Query killed after exceeding statement timeout, `STATEMENT_TIMEOUT_IN_SECONDS` error.

**Steps:**
1. Check query ID in Snowflake query history
2. Review execution plan — look for full table scans, exploding joins, missing pruning
3. If data volume spike → check source data for unexpected growth
4. If query was fine before → check if clustering keys changed, tables were restructured
5. Optimize query or increase warehouse size temporarily

### Query Failure — Permission

**Symptoms:** `Insufficient privileges` error.

**Steps:**
1. Identify which role the query ran under
2. Check `SHOW GRANTS ON <object>` for the required object
3. If role is correct but grants are missing → request grants (requires approval)
4. If wrong role → fix the connection/session configuration

### Warehouse Suspended / Not Available

**Symptoms:** Queries queuing, `Warehouse is suspended` error.

**Steps:**
1. Check warehouse status: `SHOW WAREHOUSES LIKE '<name>'`
2. If suspended → resume: `ALTER WAREHOUSE <name> RESUME` (if you have permission)
3. If credit quota exceeded → check with Snowflake admin
4. If auto-suspend is too aggressive → review auto-suspend settings

### Data Freshness Issues

**Symptoms:** Tables not updated on schedule, stale data in downstream reports.

**Steps:**
1. Check the pipeline that loads the table (Airflow DAG or Snowpipe)
2. If Airflow → see [Airflow Incidents](airflow-incidents.md)
3. If Snowpipe → check `SYSTEM$PIPE_STATUS('<pipe_name>')` for errors
4. If source data is late → escalate to upstream data provider per [Escalation](escalation.md)
5. Check `INFORMATION_SCHEMA.LOAD_HISTORY` for recent load attempts

### Account-Level Issues

**Symptoms:** Multiple queries failing, login issues, widespread errors.

**Steps:**
1. Check Snowflake status page for outages
2. If account-specific → escalate to data platform team
3. During migration: verify which account (A or B) is affected and whether traffic should be rerouted

## Recovery Checklist

After resolving any Snowflake incident:
- [ ] Root cause identified and fixed
- [ ] Affected queries/pipelines re-run
- [ ] Data integrity verified (row counts, checksums)
- [ ] Teams thread updated with resolution
- [ ] Postmortem created if P1 or P2
