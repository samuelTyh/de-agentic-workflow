# DAG Deployment

Procedures for deploying new or updated DAGs to Astronomer.

## Deployment Methods

### Via Astronomer CI/CD (recommended)

Triggered by merging to main via Azure DevOps pipeline. Uses the `ci-build-test.yaml` template for validation, then `astro deploy` for deployment.

**Flow:**
1. Create feature branch
2. Develop and test locally: `astro dev start`
3. Push branch, create PR
4. CI pipeline runs lint + tests
5. Merge to main → CD pipeline runs `astro deploy`

### Via CLI (manual, for hotfixes)

```bash
# Deploy to a specific Astronomer deployment
astro deploy <deployment-id>

# Deploy with a specific image tag
astro deploy <deployment-id> --image-tag <tag>
```

Use manual deploy only for P1/P2 hotfixes. Always follow up with a proper PR.

## Local Development

```bash
# Start local Airflow environment
astro dev start

# Restart after changing dependencies
astro dev restart

# Run a specific task locally
astro run airflow tasks test <dag_id> <task_id> <execution_date>

# Check for import errors
astro run airflow dags list-import-errors
```

## Pre-Deployment Checklist

- [ ] DAG tested locally with `astro dev start`
- [ ] No import errors: `astro run airflow dags list-import-errors`
- [ ] Task dependencies are correct (check Graph view)
- [ ] `catchup=False` set if not a backfill DAG
- [ ] Retry policy configured (`retries`, `retry_delay`)
- [ ] `on_failure_callback` set for alerting
- [ ] Connections and variables used (no hardcoded credentials)
- [ ] PR approved via Code Review Agent

## Rollback

If a deployment causes issues:

1. **Quick rollback:** Redeploy the previous image tag
   ```bash
   astro deploy <deployment-id> --image-tag <previous-tag>
   ```
2. **Git rollback:** Revert the PR on main, which triggers a new deploy
3. **Pause the DAG:** If rollback isn't immediate, pause the broken DAG in the UI to prevent further failed runs
