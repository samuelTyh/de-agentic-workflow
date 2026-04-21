# Backfill Operations

Re-running pipelines for historical date ranges.

## When to Backfill

- Data was missing or incorrect for a date range
- New DAG needs to process historical data
- Transformation logic changed and past data needs re-processing
- Source data was redelivered after a correction

## Pre-Backfill Checklist

- [ ] Identify the exact date range needed
- [ ] Confirm the DAG has `catchup=True` or you'll trigger manually
- [ ] Check if backfill will overwrite existing good data (use INSERT vs MERGE carefully)
- [ ] Estimate resource usage — large backfills may need warehouse scale-up
- [ ] Notify downstream consumers if data will be temporarily inconsistent
- [ ] Create a Jira ticket to track the backfill

## Running a Backfill

### Via Airflow CLI (recommended)

```bash
# Backfill a DAG for a date range
astro run airflow dags backfill <dag_id> \
    --start-date <YYYY-MM-DD> \
    --end-date <YYYY-MM-DD> \
    --reset-dagruns
```

Options:
- `--reset-dagruns` — clears existing runs in the range before re-running
- `--task-regex <pattern>` — only backfill specific tasks
- `--dry-run` — preview what would be backfilled without executing

### Via Airflow UI

1. DAG → Grid view → select the date range
2. Click "Clear" on the desired task instances
3. Airflow will re-run them in order

### Large Backfills

For backfills spanning weeks or months:

1. **Break into chunks** — backfill one week at a time to avoid overwhelming resources
2. **Scale up warehouse** — temporarily increase Snowflake warehouse size
3. **Use a dedicated pool** — create an `backfill` pool to limit concurrent backfill tasks
4. **Monitor progress** — watch Airflow UI and Snowflake query history
5. **Scale down after** — return warehouse and pool settings to normal

## Post-Backfill Verification

- [ ] Row counts match expected for the backfilled date range
- [ ] Data quality checks pass (no duplicates, no nulls where unexpected)
- [ ] Downstream tables/views refreshed correctly
- [ ] Downstream consumers notified that data is updated
- [ ] Jira ticket updated with completion status

## Gotchas

- **Idempotency:** Ensure the DAG's tasks are idempotent (re-running produces the same result). Use MERGE or DELETE+INSERT patterns, not blind INSERT.
- **Dependencies:** If the DAG has external dependencies, ensure those are available for the backfill range.
- **Variables:** If time-dependent variables changed, the backfill may use current values instead of historical ones. Consider parameterizing by execution_date.
- **Catchup:** If `catchup=False`, Airflow won't auto-backfill on deploy. Use the CLI method above.
