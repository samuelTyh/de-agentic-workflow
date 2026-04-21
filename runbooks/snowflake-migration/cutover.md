# Phase 3: Cutover & Rollback

Execute the production cutover from Account A to Account B. Ticket: [TVF-134](https://enpal.atlassian.net/browse/TVF-134).

**Prerequisites:** Rehearsal #2 signed off (see `validation.md`). DS tech lead + Platform/Cloud owner approval.

## Stakeholders

Runbook reviewed and approved by:
- DS tech lead
- Platform / Cloud owner
- BI team (inbound share impact)

Notified of cutover window:
- DS team
- BI team (Alex Sutcliffe)
- Flexa (outbound share impact)
- Any Streamlit app users
- Forecast API consumers

## Pre-Cutover Checklist (Day Before)

- [ ] Rehearsal #2 sign-off recorded in [TVF-7](https://enpal.atlassian.net/browse/TVF-7)
- [ ] Cutover window announced to all stakeholders
- [ ] Rollback plan reviewed by on-call engineer
- [ ] Incident channel created in Microsoft Teams
- [ ] All services ready on B (sprocs deployed, Streamlit redeployed, Airflow connection present)
- [ ] Parity check is green for the last 24 hours
- [ ] Final version of cutover runbook shared (this doc + any team-specific additions)

## Cutover Window Timeline

Estimate based on Rehearsal #2 timings. Typical target: 2-4 hours.

| Step | Owner | Estimated Duration |
|------|-------|-------------------|
| 1. Announce start | Incident commander | 5 min |
| 2. Freeze A writes | DE team | 15 min |
| 3. Drain DAGs | DE team | 30-60 min |
| 4. Final replica refresh | DE team | 15-30 min (depends on lag) |
| 5. Promote B replica | DE team | 5 min |
| 6. Flip connection strings | DE + Platform teams | 15 min |
| 7. Unpause DAGs + resume tasks | DE team | 10 min |
| 8. Smoke tests | DE + DS teams | 30-45 min |
| 9. Announce complete | Incident commander | 5 min |

## Cutover Steps

### Step 1: Announce Start

Post to Microsoft Teams:
```
[Cutover] Snowflake New Energy Migration: Account A → B
Start: YYYY-MM-DD HH:MM UTC
Expected duration: ~3 hours
Impact: VPP pipelines paused. DS workloads temporarily unavailable.
Thread: [this thread]
```

### Step 2: Freeze A Writes

1. **Pause all DS-owned Airflow DAGs** that write to A's DS-owned schemas:
   ```bash
   astro run airflow dags pause <dag_id>
   ```
2. **Pause any Snowflake tasks** writing to DS-owned schemas on A:
   ```sql
   -- On Account A
   ALTER TASK <task_name> SUSPEND;
   ```
3. Verify no write activity on A via query history

### Step 3: Drain DAGs

Wait for any in-flight DAG runs to complete. Do not force-kill unless necessary — let tasks finish gracefully.

- Monitor Airflow UI: all tasks in success/failed/skipped state (no running/queued)
- If a task is stuck: investigate before killing (it may be mid-write to A)

### Step 4: Final Replica Refresh

Trigger a final refresh so B has the latest A data before promotion:

```sql
-- On Account B
ALTER DATABASE <db_name> REFRESH;

-- Wait for completion
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DATABASE_REFRESH_HISTORY('<db_name>'))
ORDER BY START_TIME DESC
LIMIT 1;
```

Verify `STATUS = 'SUCCEEDED'` before proceeding.

### Step 5: Promote B Replica

```sql
-- On Account B
ALTER DATABASE <db_name> PRIMARY;
```

After promotion, B owns the database — it becomes read/write.

Run quick sanity check:
```sql
-- On Account B
-- Test write to a dummy table
CREATE OR REPLACE TABLE <db>.PUBLIC.cutover_test (ts TIMESTAMP_NTZ);
INSERT INTO <db>.PUBLIC.cutover_test VALUES (CURRENT_TIMESTAMP());
DROP TABLE <db>.PUBLIC.cutover_test;
```

### Step 6: Flip Connection Strings

Update every consumer to target Account B:

**Airflow connections:**
```bash
# Update the default Snowflake connection to point to B
astro run airflow connections delete 'snowflake_default'
astro run airflow connections add 'snowflake_default' \
    --conn-type 'snowflake' \
    --conn-host "$SNOWFLAKE_ACCOUNT_B" \
    --conn-login 'airflow_service_user' \
    --conn-schema 'PUBLIC' \
    --conn-extra '{"role": "'$AIRFLOW_ROLE_B'", "warehouse": "'$AIRFLOW_WH_B'", "authenticator": "SNOWFLAKE_JWT", "private_key_content": "<kpa-key>"}'
```

**Forecast API config:** Update to point at B (redeploy if config is baked in).

**Streamlit apps:** Flip user-facing URLs/links to B-deployed versions.

**`vpp-data-warehouse` + `vpp-snowpark-apps` CI/CD:** Already targets B (done in Phase 2). Verify no lingering A references.

### Step 7: Unpause DAGs + Resume Tasks

```bash
# Unpause Airflow DAGs
astro run airflow dags unpause <dag_id>
```

```sql
-- On Account B: resume tasks in dependency order (root tasks first)
ALTER TASK <root_task> RESUME;
ALTER TASK <child_task> RESUME;
```

### Step 8: Smoke Tests

Run full smoke test suite:

**Airflow:**
- [ ] First post-cutover DAG run succeeds
- [ ] No Snowflake connection errors in task logs
- [ ] Output tables on B populated correctly

**Snowpark procedures:**
- [ ] Sample proc per forecast family (TSO, system, pool, household) runs successfully on B
- [ ] Feature store procs execute and update tables

**Forecast API:**
- [ ] Production traffic routed to B
- [ ] Response latencies within SLA
- [ ] Sample responses match pre-cutover baseline

**Streamlit apps:**
- [ ] All apps accessible at new URLs
- [ ] Data displayed matches expectations

**Shares:**
- [ ] Inbound shares (BI, VPP legacy, Meteomatics) queryable from B
- [ ] Outbound shares (Flexa, BI) consumable by their consumers

### Step 9: Announce Complete

Post to Microsoft Teams:
```
[Cutover] Complete at HH:MM UTC.
All services running against Account B. Smoke tests passed.
Monitoring closely for the next 48 hours.
```

Move on to post-cutover monitoring (see below).

---

## Rollback Criteria

Abort cutover and rollback if any of these occur:

**Critical — rollback immediately:**
- Data mismatch exceeding documented tolerance on critical tables
- Smoke test failures that cannot be resolved within 30 minutes
- Production-critical DAG fails repeatedly against B
- Forecast API returns errors or wildly incorrect responses

**Discretionary — assess and decide:**
- Minor parity drift within tolerance
- Non-critical DAG failures (documented workaround available)
- Streamlit app issues (users can use A copy during rollback)

Decision authority: DS tech lead + on-call engineer during cutover window.

## Rollback Procedure

### Step 1: Announce Rollback

Post to Teams immediately:
```
[Cutover] Issues detected — initiating rollback to Account A.
```

### Step 2: Re-Freeze B Writes

Pause all Airflow DAGs targeting B, suspend B tasks.

### Step 3: Revert Connection Strings

Point everything back at A:
```bash
astro run airflow connections delete 'snowflake_default'
# Re-add original A-facing connection
astro run airflow connections add 'snowflake_default' \
    --conn-type 'snowflake' \
    --conn-host "$SNOWFLAKE_ACCOUNT" \
    ...
```

Revert Forecast API config. Revert Streamlit URLs.

### Step 4: Resume A Pipelines

Unpause A-facing DAGs and tasks. A data should be current since we froze writes ~2-3 hours ago.

### Step 5: Verify A is Serving Traffic

Smoke test the same scenarios, now against A.

### Step 6: Investigate

- Preserve logs and metrics from the failed cutover
- File a Jira ticket documenting the failure
- Postmortem to understand root cause
- Re-attempt cutover only after fixes validated in another rehearsal

## Rollback Window

The rollback window is open until A data goes stale (typically 24-48 hours after cutover).

After that window, A is no longer current and rollback becomes complex — would require freezing B writes and running a reverse replication or export/import from B back to A. Avoid this situation by monitoring aggressively in the first 48 hours and rolling back decisively if issues appear.

---

## Post-Cutover Monitoring

### First 48 Hours

- [ ] Incident channel stays open; engineer on-call
- [ ] Parity check runs every 4 hours (not daily) — spot divergence quickly
- [ ] Every scheduled DAG run monitored
- [ ] Forecast API latency + error rate dashboards checked hourly
- [ ] Streamlit app feedback collected from users
- [ ] Flexa + BI consumer confirmation of outbound shares

### First 7 Days

- [ ] All scheduled DAGs have completed at least one full cycle on B
- [ ] Data quality checks passing
- [ ] Performance baseline established on B
- [ ] Cost baseline established (credit usage per warehouse)
- [ ] Any issues documented and resolved
- [ ] Incident channel closed if stable

### Decommission Account A (Phase 4)

After stabilization (typically 2-4 weeks):
- [ ] Confirm no pipelines still reference Account A for writes to DS-owned schemas
- [ ] Revoke A-side KPA keys for rotated service users ([TVF-143](https://enpal.atlassian.net/browse/TVF-143))
- [ ] Remove Account A Airflow connection
- [ ] Update `config/mcp-servers.json` — rename `snowflake_account_b` to `snowflake_default`, archive A config
- [ ] Preserve A as a read source via inbound share (IoT raw data stays in A permanently per TVF-146 governance doc)
- [ ] Update this runbook with final status

## Acceptance Criteria for TVF-134

- [ ] Runbook reviewed and approved by DS tech lead + Platform/Cloud owner
- [ ] Runbook dry-run alongside Rehearsal #2
- [ ] Runbook used for actual cutover
- [ ] Rollback criteria explicitly defined
- [ ] Rollback procedure documented and validated
