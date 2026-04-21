# Performance Tuning

Optimizing slow or resource-heavy DAGs on Astronomer.

## Diagnosing Slow DAGs

### Step 1: Identify the Bottleneck

1. Airflow UI → DAG → Grid/Gantt view → find the slowest task(s)
2. Check task duration trends — is it getting slower over time?
3. Common bottlenecks:
   - **Single slow task** → optimize that task's query/logic
   - **Many tasks queued** → parallelism or pool limits
   - **Sensors waiting** → upstream dependency delay
   - **High scheduling lag** → scheduler overloaded

### Step 2: Task-Level Optimization

**Slow Snowflake queries:**
- Check query profile in Snowflake UI for full table scans
- Add clustering keys or filter on partition columns
- Use appropriate warehouse size — scale up for heavy transforms, back down after
- See the SQL Review prompt template for a full checklist

**Slow Python tasks:**
- Profile the code — are you loading too much data into memory?
- Use Snowpark DataFrames for pushdown instead of pulling data locally
- Consider breaking large tasks into parallel subtasks

**Slow file operations:**
- Use streaming instead of loading entire files into memory
- Compress data during transfer

### Step 3: DAG-Level Optimization

**Parallelism:**
- Set `max_active_tasks` on the DAG to control concurrent task execution
- Use Airflow pools to limit resource-heavy tasks across DAGs
- Check Astronomer worker capacity — scale if needed

**Task dependencies:**
- Review the Graph view — are tasks unnecessarily sequential?
- Identify tasks that can run in parallel and adjust dependencies
- Use task groups for logical grouping without sequential dependencies

**Scheduling:**
- Avoid scheduling many DAGs at the same time (e.g., all at midnight)
- Stagger schedules to distribute load: `0 */2 * * *` instead of `0 0 * * *`
- Use data-aware scheduling (datasets) where applicable

## Astronomer-Specific Tuning

### Worker Resources

Adjust in Astronomer UI → Deployment → Settings → Worker Resources:
- **CPU/Memory:** Scale up for compute-heavy tasks
- **Replicas:** Add workers for parallelism
- **Scaling:** Use worker queues for different resource profiles

### Scheduler

- **Scheduler replicas:** Add a second scheduler for high DAG count
- **DAG file processing interval:** Increase if you have many DAGs (reduces CPU load)
- **Min file process interval:** Default 30s, increase for large deployments

### Pool Management

```bash
# List pools
astro run airflow pools list

# Create a pool (limits concurrent tasks that use this pool)
astro run airflow pools set <pool_name> <slots> '<description>'
```

Use pools for:
- Limiting concurrent Snowflake queries (prevent warehouse overload)
- Limiting concurrent API calls (respect rate limits)
- Isolating resource-heavy tasks from lightweight ones
