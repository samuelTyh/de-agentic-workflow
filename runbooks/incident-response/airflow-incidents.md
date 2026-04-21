# Airflow Incidents

## Common Failure Scenarios

### DAG Failure — Task Error

**Symptoms:** Task instance marked as `failed`, error in task logs.

**Steps:**
1. Open Airflow UI → DAG → Failed task instance → Logs
2. Identify the error:
   - **Connection error** → Check Airflow connections, verify target system is up
   - **Timeout** → Check if data volume increased, consider increasing timeout or optimizing query
   - **Code error** → Check recent commits to the DAG, identify the breaking change
   - **Permission error** → Verify service account permissions on target system
3. If the error is transient (network blip, temporary lock): clear the task and let it retry
4. If the error is persistent: fix the root cause, then clear and retry

### DAG Failure — Upstream Dependency

**Symptoms:** Task waiting on a sensor that never triggers, or ExternalTaskSensor timeout.

**Steps:**
1. Identify which upstream DAG/task the sensor is waiting for
2. Check the upstream DAG's status — is it running, failed, or not scheduled?
3. If upstream is failed → fix upstream first, then this DAG will proceed
4. If upstream is delayed → monitor, adjust sensor timeout if needed
5. If upstream is from another team → escalate per [Escalation](escalation.md)

### Scheduler Issues

**Symptoms:** DAGs not being scheduled, tasks stuck in `queued`, scheduler heartbeat stale.

**Steps:**
1. Check scheduler health: `airflow jobs check` or Airflow UI health page
2. Check scheduler logs for errors
3. If scheduler is down → restart scheduler service
4. If tasks are stuck in queued → check executor capacity (worker slots, parallelism)
5. If persists → escalate to data platform team

### DAG Not Appearing

**Symptoms:** New or modified DAG not showing in Airflow UI.

**Steps:**
1. Check DAG file is in the correct DAGs folder
2. Check for Python import errors: `airflow dags list-import-errors`
3. Fix syntax/import issues and wait for scheduler to pick up the change
4. Check `.airflowignore` if the file is being excluded

## Recovery Checklist

After resolving any Airflow incident:
- [ ] Root cause identified and fixed
- [ ] Failed tasks cleared and re-run successfully
- [ ] Downstream data verified (row counts, freshness)
- [ ] Teams thread updated with resolution
- [ ] Postmortem created if P1 or P2
