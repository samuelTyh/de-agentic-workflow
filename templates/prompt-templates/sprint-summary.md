# Sprint Summary

**Agent:** PMO Agent

## Inputs
- Sprint name or "current" for active sprint

## Steps
1. Query Jira for all tickets in the sprint
2. Group by status: Done, In Progress, To Do, Blocked
3. Identify blockers and who is blocked
4. Calculate completion percentage (done story points / total story points)
5. Pull any relevant Notion meeting notes from this sprint period

## Output Format

### Sprint: [Name] — [X]% Complete

**Done** ([N] tickets, [X] pts)
| Ticket | Summary | Assignee | Points |
|--------|---------|----------|--------|

**In Progress** ([N] tickets, [X] pts)
| Ticket | Summary | Assignee | Points | Days in Progress |
|--------|---------|----------|--------|-----------------|

**Blocked** ([N] tickets)
| Ticket | Summary | Assignee | Blocker |
|--------|---------|----------|---------|

**To Do** ([N] tickets, [X] pts)
| Ticket | Summary | Priority |
|--------|---------|----------|

### Key Risks
- [Tickets at risk of not completing this sprint]
- [Dependencies on external teams]
