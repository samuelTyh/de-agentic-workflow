# DAG Monitoring

Daily procedures for monitoring pipeline health and responding to failures.

## Daily Checklist

1. **Check Airflow UI** → Browse → DAGs → sort by "Last Run" status
   - Green = success, Red = failed, Yellow = running, Light blue = queued
2. **Review failed runs** → click the red DAG → check task instances
3. **Check SLA misses** → Browse → SLA Misses (if configured)
4. **Review email alerts** → check team inbox for `on_failure_callback` notifications

## Responding to Failed Tasks

### Step 1: Read the Logs

1. Airflow UI → DAG → Graph view → click the failed task → Logs
2. Identify the error type:
   - **Connection error** → see [Connection Management](connection-management.md)
   - **Timeout** → see [Performance Tuning](performance-tuning.md)
   - **Code error** → check recent commits to the DAG
   - **Resource error** → check Astronomer worker resources

### Step 2: Decide on Action

| Scenario | Action |
|----------|--------|
| Transient error (network blip, temp lock) | Clear the task and let it retry |
| Known flaky task | Clear and retry, but create a ticket to fix root cause |
| Code bug | Fix the code, deploy, then clear and retry |
| Upstream dependency late | Wait, or clear the sensor timeout and re-trigger |
| Resource exhaustion | Scale worker via Astronomer UI, then retry |

### Step 3: Clear and Retry

**Clear a single task:**
1. Airflow UI → DAG → Graph → click failed task → Clear
2. Options: clear downstream tasks if they depend on this one
3. Monitor the re-run

**Clear multiple tasks:**
1. Airflow UI → DAG → Grid view → select date range
2. Click "Clear" to re-run all failed tasks in the range

**Via CLI:**
```bash
astro run airflow tasks clear <dag_id> -t <task_id> -s <start_date> -e <end_date>
```

## Monitoring Stuck Tasks

**Symptoms:** Tasks in `running` state for longer than expected.

**Steps:**
1. Check task duration against historical average
2. If running much longer than usual → check underlying query/process
3. If task appears hung → check worker logs in Astronomer UI
4. If worker is unhealthy → terminate the task instance and retry

## DAG Parsing Errors

**Check for import errors:**
```bash
astro run airflow dags list-import-errors
```

If a DAG has parsing errors, it won't appear in the UI and won't run.
