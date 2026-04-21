# Triage

First-response decision tree. Goal: identify what's broken, assess severity, route to the right runbook.

## Step 1: How Was the Incident Detected?

| Source | Likely System | Go To |
|--------|--------------|-------|
| Airflow alert / DAG failure notification | Airflow | [Airflow Incidents](airflow-incidents.md) |
| Snowflake query error / timeout | Snowflake | [Snowflake Incidents](snowflake-incidents.md) |
| Azure DevOps pipeline failure | Azure DevOps | [Azure DevOps Incidents](azure-devops-incidents.md) |
| Downstream user reports bad/missing data | Data Quality | [Data Quality Incidents](data-quality-incidents.md) |
| Multiple systems affected | Start with the upstream-most system | Check in order: Source → Snowflake → Airflow → Downstream |

## Step 2: Assess Severity

Ask these questions:

1. **Is production data affected?** (consumers seeing wrong/missing data)
   - Yes → P1 or P2
2. **Are downstream consumers blocked?** (dashboards, reports, ML pipelines)
   - Yes, blocked → P1
   - Yes, degraded but functional → P2
3. **Is there a workaround?**
   - No workaround → escalate severity by one level
   - Workaround available → document it in the Teams thread

## Step 3: Communicate

1. Post to Microsoft Teams: `[Severity] [System] Brief description`
2. Tag yourself as incident owner
3. Update the thread as you investigate — others may have context

## Step 4: Investigate

Jump to the system-specific runbook. If you're unsure which system is the root cause, start with the upstream-most system and work downstream.

## Step 5: Can't Identify the System?

If after 15 minutes you can't identify the root cause:
- Post your findings so far to Teams
- Tag a second team member for a fresh perspective
- Check if multiple systems are affected (cascade failure)
- See [Escalation](escalation.md) if infrastructure is suspected
