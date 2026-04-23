# agent-workflow

Knowledge base and configuration hub for an AI-assisted data engineering workflow. This repo is the reference point for orchestrator logic, subagent definitions, approval policies, and shared conventions used across all team projects.

## Who This Is For

- A 10-person data engineering team working on VPP (Virtual Power Plant, Forecasting & Trading)
- Daily stack: Airflow (Astronomer), Snowflake, Snowpark, Azure DevOps
- Collaborators who consume data from or contribute to DS/ML workflows

## The Problem It Solves

Without shared conventions, every team member interacts with AI coding tools differently — different prompts, different guardrails, different assumptions. That creates drift, audit gaps, and inconsistent code.

This repo provides:

- **One orchestrator** that routes requests to the right specialized agent
- **13 specialized agents** with clear scope, capabilities, and guardrails
- **Tiered approval model** so write actions always have human oversight
- **Policy inheritance** — every agent automatically follows security, data, and workflow rules
- **Declared team workflows** — branching, PR review, incident response, migration — all captured as runbooks and templates

Clone this repo, follow the setup guide, and every team member gets the same agent behavior.

## How It Works

This is **Config-First** — no runtime service to deploy. The framework is a set of files that Claude Code (and similar AI coding tools) reads as context:

```
User request
   ↓
Root CLAUDE.md (orchestrator)
   ↓
Intent classification → routes to the right agent
   ↓
agents/<name>/CLAUDE.md (identity, capabilities, scope)
   ↓
Inherits policies from:
   - agents/security/ (approval tiers, data boundaries, audit)
   - config/git-workflow.yaml (branching, PR rules)
   - docs/adr/ (architecture decisions)
   ↓
Executes with human approval for write actions
```

External integrations happen via:

- **MCP servers** for Jira, Notion (built-in Claude Code OAuth), Snowflake, Azure DevOps (self-hosted)
- **Git** for source code and PRs on GitHub or Azure DevOps

## Agent Roster

| # | Agent | Domain |
|---|-------|--------|
| 1 | [Security / Guardrail](agents/security/CLAUDE.md) | Policy layer — approval tiers, data boundaries, credentials, audit |
| 2 | [Orchestrator](agents/orchestrator/CLAUDE.md) | Routing, multi-agent coordination, cross-agent summarization |
| 3 | [Architecture](agents/architecture/CLAUDE.md) | System/pipeline architecture, design decisions, ADRs |
| 4 | [PMO](agents/pmo/CLAUDE.md) | Jira lifecycle, Notion integration, sprint planning |
| 5 | [Migration](agents/migration/CLAUDE.md) | Snowflake account A→B migration |
| 6 | [DS/ML Liaison](agents/ds-ml-liaison/CLAUDE.md) | ML/DS context translation for DE team |
| 7 | [Snowflake SQL](agents/snowflake-sql/CLAUDE.md) | SQL authoring, review, optimization |
| 8 | [Snowpark Dev](agents/snowpark-dev/CLAUDE.md) | Snowpark Python procedures, UDFs, DataFrames |
| 9 | [General DE](agents/data-engineering/CLAUDE.md) | Airflow, pipelines, data modeling, data quality |
| 10 | [QA / Testing](agents/testing/CLAUDE.md) | Unit, integration, e2e testing |
| 11 | [Code Review](agents/code-review/CLAUDE.md) | PR review (hybrid first-pass auto-review) |
| 12 | [Platform Eng](agents/platform-engineering/CLAUDE.md) | Azure DevOps CI/CD, pipeline optimization |
| 13 | [Git Workflow](agents/git-workflow/CLAUDE.md) | Branching, PR lifecycle, commit conventions |

New agents scaffold from [`agents/_template/`](agents/_template/CLAUDE.md).

## Quick Start

1. **Clone the repo**
   ```bash
   git clone <this-repo-url>
   cd agent-workflow-dev
   ```

2. **Follow the setup guide** — [`docs/setup-guide.md`](docs/setup-guide.md)
   - Authenticate Jira and Notion via Claude Code's built-in connectors
   - Install and configure the Snowflake MCP server
   - Install and configure the Azure DevOps MCP server
   - Enable branch protection on your repos

3. **Verify** — start a Claude Code session in this repo and try:
   ```
   > Summarize my current Jira sprint
   > Review this Airflow DAG: <path>
   > What's the current state of the Snowflake migration?
   ```

Estimated setup time: ~30 minutes per user.

## Using This in Your Projects

This repo is the single source of truth for agent conventions. To use it in another repo:

**Option A — Reference globally.** Point your Claude Code config to this repo's `CLAUDE.md` so every project inherits the agent roster and policies.

**Option B — Symlink in project root.** From your project repo:
```bash
ln -s /path/to/agent-workflow-dev/CLAUDE.md ./CLAUDE.md
```
Your project-specific instructions can live in a separate file (e.g., `PROJECT.md`) that your Claude Code session reads alongside.

**Option C — Copy relevant agent files.** For one-off needs, copy the specific agent's CLAUDE.md into your project's `.claude/` directory.

Whichever option you choose, the agent definitions in this repo are authoritative. Update them here, pull the changes, and every user's agents update consistently.

## Team Workflow Policies

### Git Workflow

- **Direct commits to protected branches are forbidden.** All changes go through a feature branch and pull request.
- Branching strategy is per-repo, declared in [`config/git-workflow.yaml`](config/git-workflow.yaml) — GitHub Flow or Git Flow.
- Branch naming: `<type>/<description>` (types: feat, fix, docs, style, refactor, test, chore, perf)
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- The Code Review Agent auto-generates a first-pass review comment on every new PR. Humans make the final merge decision.
- Works on both GitHub and Azure DevOps.

### Approval Model

Every agent action is classified into one of three tiers ([`agents/security/approval-tiers.yaml`](agents/security/approval-tiers.yaml)):

- **autonomous** — read operations, summaries, diffs (proceed without asking)
- **requires-approval** — write operations (user must confirm)
- **forbidden** — destructive operations (refused outright)

Trusted recurring actions can be promoted from `requires-approval` to `autonomous` over time.

### Audit Trail

Every write action is logged to `logs/audit/` (git-ignored) with user, agent, action, timestamp, approval status. See [`agents/security/audit-policy.yaml`](agents/security/audit-policy.yaml).

### Data Boundaries

Each agent declares its data scope. Agents do not surface raw credentials, connection strings, or PII. Sensitive Notion pages can be tagged for exclusion. See [`agents/security/data-boundaries.yaml`](agents/security/data-boundaries.yaml).

## Adding a New Agent

1. Copy the template: `cp -r agents/_template agents/<new-agent-name>`
2. Fill in [`agents/<new-agent-name>/CLAUDE.md`](agents/_template/CLAUDE.md) — identity, capabilities, scope, integrations
3. Add approval tiers to [`agents/security/approval-tiers.yaml`](agents/security/approval-tiers.yaml)
4. Add data boundaries to [`agents/security/data-boundaries.yaml`](agents/security/data-boundaries.yaml)
5. Add the agent to the roster above and to [`agents/orchestrator/CLAUDE.md`](agents/orchestrator/CLAUDE.md)
6. Open a PR — the Code Review Agent will run a first-pass review

## Repo Layout

```
agent-workflow-dev/
├── CLAUDE.md                    # Root orchestrator — loaded by Claude Code
├── README.md                    # You are here
├── agents/
│   ├── orchestrator/            # Routing, coordination
│   ├── security/                # Policy layer (approval tiers, boundaries, audit)
│   ├── <agent>/CLAUDE.md        # Each specialized agent
│   └── _template/               # Scaffold for new agents
├── config/
│   ├── mcp-servers.json         # MCP server connection configs
│   └── git-workflow.yaml        # Per-repo branching strategy
├── runbooks/
│   ├── snowflake-migration/     # 8-file migration runbook (TVF-7)
│   ├── pipeline-ops/            # Airflow/Astronomer operations
│   └── incident-response/       # Severity levels, triage, postmortem
├── templates/
│   ├── jira-ticket-templates/   # Story, bug, epic, task
│   ├── prompt-templates/        # Reusable agent prompts
│   └── pipeline-templates/      # Azure DevOps YAML templates
├── docs/
│   ├── setup-guide.md           # Onboarding guide
│   ├── adr/                     # Architecture Decision Records
│   └── superpowers/             # Design specs and implementation plans
├── scripts/                     # Placeholder for future non-agent automation
└── logs/audit/                  # Local audit logs (git-ignored)
```

## Docs & References

- [Setup guide](docs/setup-guide.md) — new user onboarding
- [CHANGELOG](CHANGELOG.md) — policy and framework change history (CalVer)
- [Snowflake migration runbook](runbooks/snowflake-migration/README.md) — TVF-7 playbook
- [Pipeline operations runbook](runbooks/pipeline-ops/README.md) — Astronomer Airflow ops
- [Incident response runbook](runbooks/incident-response/README.md) — severity levels, triage, postmortem
- [Architecture Decision Records](docs/adr/) — binding team standards
- [Design specs](docs/superpowers/specs/) — agent framework, templates, MCP config
- [Implementation plans](docs/superpowers/plans/) — how the framework was built

## Tech Stack

- Python 3.12+ managed with [uv](https://docs.astral.sh/uv/)
- Markdown for agent definitions and runbooks
- YAML for config and approval tiers
- MCP for Jira, Notion, Snowflake, Azure DevOps integrations
