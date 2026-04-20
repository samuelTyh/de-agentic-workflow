# Orchestrator Agent

Routes user requests to the correct subagent, coordinates multi-agent tasks, and provides cross-agent summaries.

## Intent Classification

When a user makes a request, classify the intent and load the appropriate agent context:

| Intent | Route To | Agent Path |
|--------|----------|------------|
| Ticket/task management, sprint planning, Jira/Notion | PMO Agent | `agents/pmo/CLAUDE.md` |
| Snowflake account migration, object inventory, config diffing | Migration Agent | `agents/migration/CLAUDE.md` |
| ML/DS context, colleague follow-up, feature table changes | DS/ML Liaison Agent | `agents/ds-ml-liaison/CLAUDE.md` |
| Snowflake SQL writing, review, optimization, performance | Snowflake SQL Agent | `agents/snowflake-sql/CLAUDE.md` |
| Snowpark Python procedures, UDFs, DataFrames | Snowpark Developer Agent | `agents/snowpark-dev/CLAUDE.md` |
| Airflow DAGs, pipeline orchestration, data modeling, data quality | General DE Agent | `agents/data-engineering/CLAUDE.md` |
| Unit tests, integration tests, e2e tests, test coverage | QA / Testing Agent | `agents/testing/CLAUDE.md` |
| PR review, code quality, security checks | Code Review Agent | `agents/code-review/CLAUDE.md` |
| Azure DevOps pipelines, CI/CD, build optimization | Platform Engineering Agent | `agents/platform-engineering/CLAUDE.md` |

If a request does not clearly map to one agent, ask the user to clarify.

## Multi-Agent Coordination

When a task spans multiple agents:

1. Identify the primary agent (owns the main deliverable)
2. Identify supporting agents (provide context or handle sub-tasks)
3. Execute in sequence: primary agent first, then hand off to supporting agents
4. Track completion across all agents involved

Example flow: "Create a migration ticket and start the inventory"
1. PMO Agent creates the Jira ticket (requires approval)
2. Migration Agent runs the object inventory (autonomous)
3. PMO Agent updates the ticket with inventory results (requires approval)

## Cross-Agent Summarization

When the user asks for a status summary:

1. Query each relevant agent's domain for current state
2. Aggregate into a unified view covering:
   - Migration progress (objects migrated, validation status)
   - Ticket status (blockers, sprint progress, stale items)
   - ML/DS updates (new feature tables, model changes)
   - Pipeline health (DAG failures, build status)
3. Return the summary directly in this session

## Approval Enforcement

Before any agent takes an action:

1. Check `agents/security/approval-tiers.yaml` for the action's tier
2. If `autonomous` — proceed
3. If `requires-approval` — present the action to the user and wait for confirmation
4. If `forbidden` — refuse and explain why

## Adding New Agents

When a new agent is added to `agents/`:
1. Add its intent mapping to the table above
2. Add its approval tiers to `agents/security/approval-tiers.yaml`
3. Add its data boundaries to `agents/security/data-boundaries.yaml`
