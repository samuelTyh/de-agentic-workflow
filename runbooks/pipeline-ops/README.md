# Pipeline Operations

Day-to-day operational procedures for the data engineering team's Airflow pipelines running on Astronomer.

## Quick Reference

| Task | Guide |
|------|-------|
| Monitor and triage DAG runs | [DAG Monitoring](dag-monitoring.md) |
| Deploy new or updated DAGs | [DAG Deployment](dag-deployment.md) |
| Manage connections, variables, secrets | [Connection Management](connection-management.md) |
| Optimize slow or resource-heavy DAGs | [Performance Tuning](performance-tuning.md) |
| Re-run pipelines for historical data | [Backfill Operations](backfill-operations.md) |
| Common errors and fixes | [Troubleshooting](troubleshooting.md) |

## Environment

- **Platform:** Astronomer (managed Airflow)
- **CLI:** `astro dev` (local), `astro deployment` (remote)
- **Alerting:** Airflow built-in (`on_failure_callback`, email alerts). Future: Datadog integration.
- **Deployment:** Via Astronomer CI/CD or `astro deploy`

## Alerting Setup

Current alerting uses Airflow's built-in mechanisms:

```python
default_args = {
    'on_failure_callback': failure_callback,
    'email_on_failure': True,
    'email': ['team-de@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}
```

When migrating to Datadog, replace callbacks with Datadog's Airflow integration and StatsD metrics.
