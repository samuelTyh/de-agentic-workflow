# Bug Template

**Type:** Bug

## Fields

- **Summary:** [BUG: Brief description of the defect]
- **Priority:** [Critical / High / Medium / Low]
- **Assignee:** [Team member]
- **Sprint:** [Current sprint if urgent, backlog otherwise]
- **Labels:** [bug, and domain label: data-pipeline | snowflake | airflow | platform | ml-integration]
- **Affects Version:** [Release or deployment date when bug was found]

## Description

### Environment
- **Where:** [Production / Staging / Dev]
- **Service:** [Airflow DAG name / Snowflake object / Pipeline name / etc.]
- **When discovered:** [Date and time]
- **Discovered by:** [Person or monitoring alert]

### Current Behavior
[What is happening — include error messages, logs, screenshots]

### Expected Behavior
[What should happen instead]

### Steps to Reproduce
1. [Step]
2. [Step]
3. [Step]

### Impact
- **Data affected:** [Tables, rows, pipelines impacted]
- **Users affected:** [Downstream consumers, dashboards, reports]
- **Workaround available:** [Yes — describe / No]

### Root Cause (if known)
[Initial analysis or hypothesis]

### Definition of Done
- [ ] Root cause identified
- [ ] Fix implemented and tested
- [ ] Regression test added
- [ ] Code review approved
- [ ] Deployed and verified in affected environment
- [ ] Monitoring confirms resolution
