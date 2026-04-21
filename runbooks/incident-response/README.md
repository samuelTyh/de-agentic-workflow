# Incident Response

On-call and incident response procedures for the data engineering team.

## Severity Levels

| Level | Definition | Response Time | Examples |
|-------|-----------|---------------|----------|
| **P1 Critical** | Production data pipeline down, data loss, downstream consumers blocked | Immediate (< 15 min) | Main ETL pipeline failure, Snowflake account outage, data corruption |
| **P2 High** | Pipeline degraded, data delayed, workaround available | Within 1 hour | DAG partial failure with retry possible, warehouse performance degraded |
| **P3 Medium** | Non-critical pipeline failure, no immediate downstream impact | Within 4 hours | Dev/staging pipeline broken, non-critical DAG failure |
| **P4 Low** | Cosmetic issue, minor data discrepancy, non-urgent | Next business day | Minor data type mismatch, logging gaps, non-blocking warnings |

## Quick Reference

1. **Incident detected** → Start in [Triage](triage.md)
2. **Identify the system** → Jump to the relevant runbook:
   - [Airflow Incidents](airflow-incidents.md)
   - [Snowflake Incidents](snowflake-incidents.md)
   - [Azure DevOps Incidents](azure-devops-incidents.md)
   - [Data Quality Incidents](data-quality-incidents.md)
3. **Need to escalate?** → See [Escalation](escalation.md)
4. **After resolution** → Fill out [Postmortem Template](postmortem-template.md)

## Communication

- **Primary channel:** Microsoft Teams — dedicated incident thread in team channel
- **When to notify:** All P1 and P2 incidents must be posted to Teams immediately
- **Thread format:** `[P1] [System] Brief description` (e.g., `[P1] [Airflow] Main ETL pipeline down since 06:00 UTC`)

## Contacts

| Role | Who | When to Contact |
|------|-----|-----------------|
| DE Team | @data-engineering | All incidents |
| Data Platform Team | @data-platform | Infrastructure, Snowflake account-level, networking |
| Upstream Data Providers | [See escalation guide](escalation.md) | Source data issues, API changes, SLA breaches |
