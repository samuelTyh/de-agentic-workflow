# Troubleshooting

Common Airflow and Astronomer errors with solutions.

## Airflow Errors

### `airflow.exceptions.AirflowNotFoundException: Connection '<conn_id>' is not defined`

**Cause:** DAG references a connection that doesn't exist.
**Fix:** Create the connection in Airflow UI (Admin → Connections) or via CLI. See [Connection Management](connection-management.md).

### `airflow.exceptions.AirflowSensorTimeout`

**Cause:** Sensor timed out waiting for a condition.
**Fix:**
1. Check what the sensor is waiting for (upstream DAG, file, external system)
2. If upstream is late → wait or escalate
3. If sensor config is too tight → increase `timeout` and `poke_interval`
4. Consider using `mode='reschedule'` instead of `mode='poke'` to free up worker slots

### `airflow.exceptions.AirflowTaskTimeout`

**Cause:** Task exceeded its `execution_timeout`.
**Fix:**
1. Check if the underlying operation (query, API call) is genuinely slow
2. Optimize the operation — see [Performance Tuning](performance-tuning.md)
3. If the operation is legitimately slow, increase `execution_timeout`

### `Task received SIGTERM / Worker killed`

**Cause:** Worker ran out of memory or was terminated.
**Fix:**
1. Check Astronomer worker resource usage
2. Increase worker memory in Astronomer UI → Deployment → Settings
3. Optimize the task to use less memory (streaming, chunked processing)
4. Move heavy tasks to a dedicated worker queue with more resources

### `DAG Import Error`

**Cause:** Python syntax error, missing dependency, or import failure.
**Fix:**
1. Check: `astro run airflow dags list-import-errors`
2. Fix the syntax or dependency issue
3. If missing package → add to `requirements.txt` and redeploy

### `Duplicate DAG ID`

**Cause:** Two DAG files define the same `dag_id`.
**Fix:** Search for the duplicate: `grep -r "dag_id='<id>'" dags/` and rename one.

## Snowflake-Related Errors in DAGs

### `snowflake.connector.errors.ProgrammingError: 000606: No active warehouse`

**Cause:** Snowflake warehouse is suspended and auto-resume is off, or role doesn't have access.
**Fix:**
1. Check warehouse status in Snowflake
2. Resume warehouse or verify the role has USAGE on the warehouse
3. Ensure connection in Airflow has the correct warehouse set

### `snowflake.connector.errors.DatabaseError: 250001: Could not connect to Snowflake`

**Cause:** Authentication failure, network issue, or wrong account identifier.
**Fix:**
1. Verify credentials in the Airflow connection
2. Check account identifier format (may need `<account>.<region>`)
3. Check network — does the Astronomer environment have access to Snowflake?

### `snowflake.connector.errors.ProgrammingError: 002003: SQL compilation error`

**Cause:** SQL syntax error, missing object, or permission issue.
**Fix:**
1. Copy the SQL from the task logs
2. Run it manually in Snowflake to get the detailed error
3. Fix the SQL and redeploy

## Astronomer-Specific Issues

### `Deploy fails: image build error`

**Cause:** Dependency conflict or missing system package.
**Fix:**
1. Check build logs for the specific error
2. Test locally: `astro dev start` — does it build?
3. Pin conflicting dependencies in `requirements.txt`
4. If system package needed → add to `Dockerfile`

### `Deployment unhealthy`

**Cause:** Scheduler or webserver failing to start.
**Fix:**
1. Check deployment logs in Astronomer UI
2. Common causes: DAG parsing error, missing connection, resource limits
3. If resource limits → scale up in deployment settings
4. If DAG error → fix and redeploy, or remove the broken DAG file
