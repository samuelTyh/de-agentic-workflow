# Agent Workflow Framework — Design Spec

## Overview

Config-First orchestrator framework for a 10-person data engineering team. This repo (`agent-workflow-dev`) serves as the central knowledge base, configuration hub, and lightweight automation layer for all agent-driven workflows.

**Approach:** Config-First — knowledge base files (CLAUDE.md, runbooks, templates) define agent behavior; MCP servers handle external integrations; lightweight Python scripts automate repeatable tasks. No custom runtime needed — leverages Claude Code's native agent capabilities.

**Team setup:** 10 human users, shared Jira project, shared Notion workspace. Each user runs Claude Code locally and inherits agent conventions from this repo.

## Repo Structure

```
agent-workflow-dev/
├── CLAUDE.md                        # Root orchestrator instructions
├── agents/
│   ├── orchestrator/
│   │   └── CLAUDE.md                # Routing, coordination, summarization
│   ├── security/
│   │   ├── CLAUDE.md                # Policy definitions
│   │   ├── approval-tiers.yaml      # Per-agent action tiers
│   │   ├── data-boundaries.yaml     # Data scope constraints
│   │   ├── credentials.template.yaml# Credential requirements (no values)
│   │   └── audit-policy.yaml        # Logging requirements
│   ├── pmo/
│   │   └── CLAUDE.md                # Jira/Notion project coordination
│   ├── migration/
│   │   └── CLAUDE.md                # Snowflake account A→B migration
│   ├── ds-ml-liaison/
│   │   └── CLAUDE.md                # ML/DS context translation
│   ├── platform-engineering/
│   │   └── CLAUDE.md                # Azure DevOps CI/CD, pipeline optimization
│   ├── snowflake-sql/
│   │   └── CLAUDE.md                # Snowflake SQL authoring, review, optimization
│   ├── snowpark-dev/
│   │   └── CLAUDE.md                # Snowpark Python procedures, UDFs, DataFrames
│   ├── data-engineering/
│   │   └── CLAUDE.md                # General DE: Airflow, pipelines, data modeling, data quality
│   ├── testing/
│   │   └── CLAUDE.md                # Unit, integration, e2e testing
│   ├── code-review/
│   │   └── CLAUDE.md                # PR review, code quality, security checks
│   └── _template/
│       └── CLAUDE.md                # Blank scaffold for new subagents
├── runbooks/
│   ├── snowflake-migration/         # Step-by-step migration procedures
│   ├── pipeline-ops/                # Airflow DAG triage, Snowpark errors
│   └── incident-response/           # On-call procedures
├── templates/
│   ├── jira-ticket-templates/       # Standard ticket formats
│   └── prompt-templates/            # Reusable prompt patterns
├── config/
│   └── mcp-servers.json             # MCP server connection configs
├── scripts/
│   ├── dispatch.py                  # Launch agent sessions with context
│   ├── validate-migration.py        # Snowflake A↔B object diffing
│   └── sync-context.py              # Pull ML context from repos/Notion/Snowflake
├── logs/
│   └── audit/                       # Agent action logs (git-ignored)
├── docs/
│   └── superpowers/specs/           # Design specs
└── pyproject.toml
```

## Component Designs

### 1. Security / Guardrail Layer

Policy layer inherited by all agents. Not user-facing — enforced automatically.

**Four pillars:**

#### 1a. Credential Management
- Each user authenticates with their own tokens (Jira, Notion, Snowflake)
- No shared service accounts
- Credentials stored in user-local config, never committed to repo
- `agents/security/credentials.template.yaml` documents required credentials without values
- MCP servers inherit credentials from the user's environment variables

#### 1b. Action Guardrails
- Defined in `agents/security/approval-tiers.yaml`, per agent
- Three tiers:
  - `autonomous` — read operations, summaries, diffs
  - `requires-approval` — write operations (create, update, assign, transition)
  - `forbidden` — destructive operations (drop, bulk modify, delete)
- Rate limits: write-heavy agents (PMO) capped at 5 write actions per session before re-approval
- Promotable patterns: trusted recurring actions can be moved from `requires-approval` to `autonomous` in config

#### 1c. Data Boundaries
- Each agent declares its data scope in its CLAUDE.md
- Agents must not surface raw credentials, connection strings, or PII in outputs
- Sensitive Notion pages can be tagged for exclusion from agent access
- Migration Agent accesses Snowflake metadata only — not row-level PII

#### 1d. Audit Trail
- Every write action logged to `logs/audit/` with: user, action, agent, timestamp, approval status
- Read actions logged at session-summary level
- Audit logs are git-ignored but persist locally
- Optional: push to shared location for team visibility

**Extensibility:** Security config files use a template structure with clear sections for adding new policies. Each pillar has a dedicated YAML file that can be extended without modifying agent CLAUDE.md files.

---

### 2. Orchestrator

Root-level agent defined in the repo's main CLAUDE.md and `agents/orchestrator/CLAUDE.md`.

**Responsibilities:**

1. **Intent classification** — determines which subagent handles a request:
   - Ticket/task management → PMO Agent
   - Snowflake migration → Migration Agent
   - ML/DS context questions → DS/ML Liaison Agent
   - Azure DevOps CI/CD → Platform Engineering Agent
   - Snowflake SQL writing/analysis/optimization → Snowflake SQL Agent
   - Snowpark Python procedures/UDFs/DataFrames → Snowpark Developer Agent
   - General DE (Airflow, pipelines, data modeling, data quality) → General Data Engineering Agent
   - Testing (unit, integration, e2e) → QA / Testing Agent
   - Code review (PRs, quality, security) → Code Review Agent

2. **Context loading** — reads the target agent's CLAUDE.md and relevant runbooks, passes them as context to the Claude Code session

3. **Approval enforcement** — checks `agents/security/approval-tiers.yaml` before allowing actions

4. **Multi-agent coordination** — manages handoffs between agents when a task spans multiple domains (e.g., PMO creates a migration ticket → Migration Agent executes → PMO updates ticket status)

5. **Cross-agent summarization** — aggregates status across all active agents into a unified view (migration progress, ticket blockers, ML/DS updates). Summaries are returned directly in the user's Claude Code session on request

---

### 3. PMO Agent

**File:** `agents/pmo/CLAUDE.md`

**Identity:** Project coordination specialist for a 10-person team sharing one Jira project and Notion workspace.

**Autonomous (read):**
- Query Jira: ticket status, sprint progress, blockers, stale tickets, workload distribution
- Pull Notion: meeting notes, decisions, action items
- Generate sprint summaries, burndown insights, blocker reports

**Requires approval (write):**
- Create tickets with acceptance criteria
- Decompose epics into stories/tasks (proposes breakdown, waits for approval before creating)
- Update ticket fields: status, assignee, priority
- Transition workflow states
- Draft sprint plans and propose assignments
- Clean up stale/duplicate tickets
- Write meeting summaries to Notion

**Forbidden:**
- Reassign another user's in-progress ticket without approval
- Bulk operations (>5 tickets) without re-confirmation
- Delete tickets (only close/archive)
- Modify Notion pages owned by others without approval

**Constraints:**
- Attributes all Jira changes to the requesting user, not the agent
- Surfaces conflicting priorities across team members to the orchestrator

**Integrations:** Jira MCP server, Notion MCP server

---

### 4. Migration Agent

**File:** `agents/migration/CLAUDE.md`

**Identity:** Snowflake migration specialist for account A → B transition.

**Autonomous (read):**
- Inventory objects on both accounts: databases, schemas, tables, views, UDFs, stages, pipes
- Diff configurations between accounts
- Compare role hierarchies and grants
- Validate row counts post-migration

**Requires approval (write):**
- Generate migration scripts
- Update Airflow DAG connection configs
- Modify Snowflake object definitions

**Forbidden:**
- Drop objects on source account
- Modify production grants without explicit approval

**Key assets:**
- `runbooks/snowflake-migration/` — step-by-step procedures (built incrementally as migration progresses)
- `scripts/validate-migration.py` — automated diffing between accounts

**Success criteria:** Both accounts have parity on migrated objects, all pipelines point to account B, zero data loss validated.

**Integrations:** Snowflake (Snowpark scripts or MCP server), Jira (via PMO for tracking migration tickets)

---

### 5. DS/ML Liaison Agent

**File:** `agents/ds-ml-liaison/CLAUDE.md`

**Identity:** Translator between data science/ML work and data engineering context. Helps DE team follow up on colleagues' ML work.

**Autonomous (read):**
- Scan ML/DS git repos for recent changes: new models, experiment configs, feature engineering
- Pull related Jira tickets and Notion docs
- Query Snowflake for feature tables and model registry metadata
- Generate rolling context digests

**Requires approval (write):**
- Create summary docs in Notion
- Create follow-up Jira tickets for DE work triggered by ML changes (e.g., "new feature table needs a pipeline")

**Forbidden:**
- Modify ML/DS code or experiment configs

**Key behaviors:**
- Summarizes in DE terms — translates ML concepts into pipeline/data platform implications
- Flags what needs DE attention: new feature tables needing ingestion pipelines, schema changes affecting downstream DAGs, model deployments requiring new Snowflake resources
- Maintains a rolling context digest so users don't start from zero each session

**Integrations:** Git repos (read), Jira MCP server, Notion MCP server, Snowflake (Snowpark/MCP)

---

### 6. Snowflake SQL Agent

**File:** `agents/snowflake-sql/CLAUDE.md`

**Identity:** Snowflake SQL specialist. Writes, reviews, and optimizes SQL for Snowflake — queries, stored procedures, tasks, streams, DDL, and performance tuning.

**Autonomous (read):**
- Analyze query performance (query history, execution plans, warehouse utilization)
- Review SQL for correctness, style, and Snowflake best practices
- Inspect table structures, clustering keys, materialized views
- Identify anti-patterns (e.g., unnecessary `SELECT *`, missing partition pruning, exploding joins)

**Requires approval (write):**
- Write new SQL (DDL, DML, stored procedures, tasks, streams)
- Refactor existing SQL for performance
- Modify table structures (add columns, change clustering keys, create views)
- Generate data quality check queries

**Forbidden:**
- Execute DML on production without explicit approval
- Drop or truncate tables
- Modify access control (grants, roles)

**Scope boundary:** Snowflake SQL only. Does not cover Snowpark Python, Airflow orchestration, or account-level administration (that's Migration Agent's domain).

**Integrations:** Snowflake (query/metadata), Jira (via PMO for SQL-related tickets)

---

### 7. Snowpark Developer Agent

**File:** `agents/snowpark-dev/CLAUDE.md`

**Identity:** Snowpark Python SDK specialist. Develops stored procedures, UDFs, UDTFs, and DataFrame transformations using Snowpark Python.

**Autonomous (read):**
- Review existing Snowpark code for correctness and best practices
- Analyze UDF/procedure performance and resource usage
- Inspect Snowpark DataFrame logic and transformation chains
- Identify anti-patterns (e.g., unnecessary `collect()`, missing pushdown opportunities, serialization issues)

**Requires approval (write):**
- Write new stored procedures and UDFs/UDTFs in Snowpark Python
- Refactor existing Snowpark code for performance
- Create DataFrame transformation pipelines
- Write unit tests for Snowpark code (local testing with `snowpark-python` fixtures)

**Forbidden:**
- Deploy procedures/UDFs to production without approval
- Modify warehouse or session-level configurations
- Alter access control or grants

**Scope boundary:** Snowpark Python SDK only. SQL authoring goes to Snowflake SQL Agent. Airflow orchestration is separate. Account administration is Migration Agent's domain.

**Integrations:** Snowflake (Snowpark session), Git repos (Snowpark code), Jira (via PMO)

---

### 8. General Data Engineering Agent

**File:** `agents/data-engineering/CLAUDE.md`

**Identity:** General data engineering specialist. Covers pipeline development, orchestration, data modeling, and data quality — independent from Snowflake.

**Autonomous (read):**
- Review Airflow DAGs for correctness, best practices, anti-patterns
- Analyze pipeline dependencies and scheduling logic
- Inspect data models and schema designs
- Review data quality checks and validation logic
- Audit ETL/ELT patterns (ingestion, incremental loads, SCD)

**Requires approval (write):**
- Write or modify Airflow DAGs
- Create data pipeline orchestration logic
- Design data models and schema definitions
- Build data quality validation frameworks
- Write transformation logic (non-Snowflake)

**Forbidden:**
- Modify production Airflow DAGs without approval
- Change Airflow connections or variables in production
- Delete or disable existing DAGs

**Scope boundary:** General DE only. Snowflake SQL → Snowflake SQL Agent. Snowpark Python → Snowpark Developer Agent. Snowflake account admin → Migration Agent. Azure DevOps CI/CD → Platform Engineering Agent.

**Integrations:** Airflow (DAG repos), Git repos, Jira (via PMO)

---

### 9. QA / Testing Agent

**File:** `agents/testing/CLAUDE.md`

**Identity:** Testing specialist. Writes, reviews, and maintains tests across all layers — unit, integration, end-to-end. Framework-agnostic but aligned with the team's tech stack.

**Autonomous (read):**
- Review existing test coverage and identify gaps
- Analyze test failures and flaky tests
- Audit test quality (assertions, fixtures, mocking patterns)
- Inspect CI test results from Azure DevOps pipelines

**Requires approval (write):**
- Write unit tests (pytest for Python, Snowpark local testing)
- Write integration tests (Airflow DAG validation, Snowflake connectivity)
- Write end-to-end tests (pipeline execution, data flow validation)
- Refactor test infrastructure (fixtures, conftest, test utilities)
- Create test data generators and factories

**Forbidden:**
- Execute tests against production data/environments without approval
- Modify production configurations to make tests pass
- Skip or disable existing tests without approval

**Scope boundary:** Testing only. Does not write implementation code — works with domain agents (Snowflake SQL, Snowpark, DE, Platform) to understand what needs testing, then owns the test code.

**Integrations:** Git repos (test code), Azure DevOps (CI test results), Snowflake (integration test targets), Jira (via PMO for test-related tickets)

---

### 10. Code Review Agent

**File:** `agents/code-review/CLAUDE.md`

**Identity:** Code review specialist. Reviews PRs and code changes for correctness, style, security, and maintainability across the team's tech stack.

**Autonomous (read):**
- Review PRs for logic errors, anti-patterns, and style violations
- Check for security issues (credential leaks, injection risks, excessive permissions)
- Verify adherence to team conventions and coding standards
- Assess change impact (blast radius, downstream dependencies)
- Cross-reference related Jira tickets for requirement alignment

**Requires approval (write):**
- Post review comments on PRs
- Request changes or approve PRs
- Suggest refactoring with code examples

**Forbidden:**
- Merge or close PRs
- Push commits to others' branches
- Approve PRs that touch production deployment configs without human co-review

**Key behaviors:**
- Reviews in context of domain — defers to domain agents for deep technical judgment (e.g., asks Snowflake SQL Agent whether a query optimization is valid)
- Flags security concerns to the Security / Guardrail Layer
- Prioritizes actionable feedback over style nitpicks

**Scope boundary:** Review only. Does not write implementation code — that's the domain agents' job. Does not write tests — that's the QA / Testing Agent.

**Integrations:** Git repos (PRs, diffs), Azure DevOps (PR workflow), Jira (via PMO for ticket context)

---

### 11. Platform Engineering Agent

**File:** `agents/platform-engineering/CLAUDE.md`

**Identity:** CI/CD and platform engineering specialist. Strictly scoped to Azure DevOps — pipelines, build/release optimization, pipeline templates, infrastructure automation within Azure DevOps.

**Autonomous (read):**
- Review Azure DevOps pipeline definitions (YAML)
- Analyze build/release performance: slow stages, flaky steps, failure patterns
- Audit pipeline configurations against team conventions
- Inspect pipeline templates for reuse opportunities

**Requires approval (write):**
- Create or modify pipeline YAML definitions
- Update environment variables and service connections
- Optimize pipeline stages (caching, parallelization, dependency pruning)
- Create reusable pipeline templates in `templates/pipeline-templates/`

**Forbidden:**
- Modify production deployment gates without approval
- Delete or disable existing pipelines
- Change service principal permissions or secrets

**Key behaviors:**
- Enforces pipeline conventions (naming, stage ordering, approval gates)
- Suggests optimizations based on build telemetry (e.g., "stage X takes 8 min — add caching")
- Maintains reusable pipeline templates

**Scope boundary:** Azure DevOps only. Does not cover Airflow deployment, Snowflake CI, or other pipeline systems.

**Integrations:** Azure DevOps (pipeline YAML in git repos), Jira (via PMO for platform work tickets)

---

### 12. New Agent Template

**File:** `agents/_template/CLAUDE.md`

Blank scaffold for creating new subagents. Contains:
- Identity section (role, domain, tone)
- Capability tiers (autonomous / requires-approval / forbidden)
- Integration declarations
- Data scope declarations
- Runbook references (if any)

To add a new agent: copy `agents/_template/` to `agents/<new-agent-name>/`, fill in the CLAUDE.md, and add the agent's approval tiers to `agents/security/approval-tiers.yaml`.

---

## Integration Layer

### MCP Servers

| Service   | MCP Server          | Used By                        |
|-----------|---------------------|--------------------------------|
| Jira      | Jira MCP server     | PMO, Orchestrator              |
| Notion    | Notion MCP server   | PMO, DS/ML Liaison             |
| Snowflake | Snowflake MCP / Snowpark | Migration, DS/ML Liaison, Snowflake SQL, Snowpark Dev |
| Azure DevOps | Azure DevOps REST API | Platform Engineering      |

Connection configs defined in `config/mcp-servers.json`. Each user provides their own credentials via environment variables.

### Approval Tiers Config

```yaml
# agents/security/approval-tiers.yaml (example structure)
pmo:
  autonomous:
    - jira:read
    - notion:read
    - summarize
  requires_approval:
    - jira:create
    - jira:update
    - jira:transition
    - notion:write
  forbidden:
    - jira:delete
    - jira:bulk_reassign
  rate_limits:
    write_actions_per_session: 5

migration:
  autonomous:
    - snowflake:read
    - snowflake:diff
  requires_approval:
    - snowflake:generate_script
    - airflow:update_config
  forbidden:
    - snowflake:drop
    - snowflake:modify_grants_prod

code_review:
  autonomous:
    - git:read_prs
    - git:review_diffs
    - git:check_security
    - jira:read_ticket_context
  requires_approval:
    - git:post_review_comments
    - git:request_changes
    - git:approve_pr
  forbidden:
    - git:merge_pr
    - git:close_pr
    - git:push_to_others_branches
    - git:approve_prod_deploy_pr

testing:
  autonomous:
    - test:review_coverage
    - test:analyze_failures
    - test:audit_quality
    - azdo:read_test_results
  requires_approval:
    - test:write_unit
    - test:write_integration
    - test:write_e2e
    - test:refactor_infrastructure
  forbidden:
    - test:execute_against_prod
    - test:modify_prod_config
    - test:skip_existing

data_engineering:
  autonomous:
    - airflow:review_dags
    - airflow:analyze_dependencies
    - data_model:review
    - data_quality:review
  requires_approval:
    - airflow:write_dags
    - airflow:modify_dags
    - data_model:create
    - data_quality:create_framework
  forbidden:
    - airflow:modify_prod_dags
    - airflow:change_prod_connections
    - airflow:delete_dags

snowpark_dev:
  autonomous:
    - snowpark:review_code
    - snowpark:analyze_performance
    - snowpark:inspect_dataframes
  requires_approval:
    - snowpark:write_procedures
    - snowpark:write_udfs
    - snowpark:refactor
    - snowpark:write_tests
  forbidden:
    - snowpark:deploy_prod
    - snowpark:modify_warehouse_config
    - snowpark:modify_grants

snowflake_sql:
  autonomous:
    - snowflake:read_query_history
    - snowflake:analyze_performance
    - snowflake:review_sql
  requires_approval:
    - snowflake:write_sql
    - snowflake:modify_tables
    - snowflake:create_procedures
  forbidden:
    - snowflake:execute_prod_dml
    - snowflake:drop_tables
    - snowflake:modify_grants

platform_engineering:
  autonomous:
    - azdo:read_pipelines
    - azdo:analyze_performance
  requires_approval:
    - azdo:create_pipeline
    - azdo:modify_pipeline
    - azdo:update_variables
  forbidden:
    - azdo:delete_pipeline
    - azdo:modify_prod_gates
    - azdo:change_service_principals
```

## Automation Layer

### scripts/dispatch.py
Launches Claude Code sessions with the correct agent context loaded. Reads the target agent's CLAUDE.md, attaches relevant runbooks, and applies security policies.

### scripts/validate-migration.py
Connects to both Snowflake accounts, diffs object inventories (databases, schemas, tables, roles, grants), and reports discrepancies. Used by Migration Agent and runbooks.

### scripts/sync-context.py
Pulls recent ML/DS context from git repos, Notion, and Snowflake feature tables. Produces a digest for the DS/ML Liaison Agent to reference.

## Team Adoption

**Onboarding a new user:**
1. Clone this repo
2. Copy `agents/security/credentials.template.yaml` to local config
3. Set environment variables for Jira, Notion, Snowflake tokens
4. Configure MCP servers using `config/mcp-servers.json`
5. Start using Claude Code — orchestrator conventions are inherited automatically

**Customization:** Users can override agent behavior locally if their role differs, but the repo's conventions are the team default.
