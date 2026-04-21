# Postmortem Template

Complete this for all P1 and P2 incidents. Optional for P3.

---

## Incident: [Title]

**Date:** YYYY-MM-DD
**Duration:** [Start time] — [End time] (total: X hours/minutes)
**Severity:** P1 / P2 / P3
**Incident Owner:** [Name]
**Status:** Draft / Reviewed / Complete

## Summary

[2-3 sentences: what happened, what was the impact, how was it resolved]

## Timeline

| Time (UTC) | Event |
|------------|-------|
| HH:MM | Incident detected by [source] |
| HH:MM | [Action taken] |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Verified resolved |

## Impact

- **Data affected:** [Tables, rows, date ranges]
- **Consumers affected:** [Dashboards, reports, ML pipelines, teams]
- **Data loss:** [Yes — describe / No]
- **Duration of impact:** [How long consumers saw bad/missing data]

## Root Cause

[What specifically caused the incident — be precise, not "human error"]

## Resolution

[What was done to fix it — specific steps taken]

## What Went Well

- [Things that worked during the response]

## What Could Be Improved

- [Things that slowed down detection or resolution]

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Preventive measure] | [Name] | YYYY-MM-DD | Open |
| [Detection improvement] | [Name] | YYYY-MM-DD | Open |
| [Process improvement] | [Name] | YYYY-MM-DD | Open |

## Lessons Learned

[Key takeaways the team should remember]
