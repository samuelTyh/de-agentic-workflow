# DAG Review

**Agent:** General Data Engineering Agent

## Inputs
- DAG file path or DAG ID
- (Optional) Specific concern: performance, correctness, dependencies

## Steps
1. Read the DAG file
2. Check against criteria:
   - Task dependencies are correct (no circular, no missing upstream)
   - Schedule interval matches data source refresh rate
   - Retry policy is set (retries, retry_delay)
   - Timeout configured to prevent zombie tasks
   - No hardcoded credentials or connection strings
   - Uses Airflow variables/connections, not inline values
   - SLA/alerting configured for critical DAGs
   - Task naming follows convention: {domain}_{action}_{target}
3. Flag anti-patterns:
   - Top-level code outside DAG context
   - Heavy computation in the DAG file itself
   - Missing `catchup=False` for non-backfill DAGs
   - Using `BashOperator` where a typed operator exists

## Output Format

### Summary
[One-line verdict: pass / needs changes / critical issues]

### Issues Found
| Severity | Line | Issue | Suggested Fix |
|----------|------|-------|---------------|

### Recommendations
[Optional improvements, not blockers]
