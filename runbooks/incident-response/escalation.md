# Escalation Guide

When to escalate beyond the data engineering team.

## Decision: Handle vs Escalate

| Situation | Action |
|-----------|--------|
| Bug in our DAG/SQL/pipeline code | Handle internally |
| Snowflake query performance issue | Handle internally |
| Azure DevOps pipeline config issue | Handle internally |
| Snowflake account-level outage | Escalate to data platform team |
| Infrastructure / networking issue | Escalate to data platform team |
| Source data missing or late | Escalate to upstream data provider |
| Source schema changed without notice | Escalate to upstream data provider |
| API rate limit or access revoked | Escalate to upstream data provider |

## How to Escalate

### To Data Platform Team

**When:** Infrastructure issues, Snowflake account-level problems, networking, permissions you can't grant yourself.

**How:**
1. Post in the data platform team's Teams channel
2. Include: severity, affected system, what you've tried, timeline
3. Format: `[Escalation] [P-level] [System] Description`
4. Tag the on-call person if known

**What to include:**
- Error messages and logs
- Timeline (when it started, when detected)
- Impact (which pipelines, downstream consumers affected)
- What you've already tried

### To Upstream Data Providers

**When:** Source data issues — missing data, schema changes, SLA breaches, API problems.

**How:**
1. Check if there's a known contact or Teams channel for the data provider
2. Open a Jira ticket (use the bug template) documenting the issue
3. Send a Teams message with the Jira ticket link
4. Format: `[Data Issue] [Source: provider name] Description`

**What to include:**
- Which data source and table(s) affected
- Expected vs actual delivery time
- Sample of the issue (missing rows, schema diff, error response)
- Impact on our pipelines and consumers

## Escalation Timeline

| Severity | If no response in... | Next step |
|----------|---------------------|-----------|
| P1 | 15 minutes | Escalate to team lead, try alternate contact |
| P2 | 1 hour | Follow up in Teams, tag manager |
| P3 | 4 hours | Follow up next business day |
| P4 | Next business day | Follow up in next sync meeting |
