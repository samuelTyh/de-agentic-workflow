# Changelog

All notable changes to this framework are recorded here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the repo
uses [CalVer](https://calver.org/) versioning (`YYYY.MM.DD`) — a version
represents "the state of policies, agents, and runbooks as of that date."

## How to Update

Every PR that introduces a user-facing change adds one or more bullets under
`[Unreleased]` before merge. The PR template has a checklist item as a
reminder, and CI fails PRs that don't touch `CHANGELOG.md`. Non-user-facing
PRs (typo fixes, pure internal refactors, CI-only tweaks) can opt out by
including `[skip-changelog]` in any commit message on the PR.

A maintainer cuts a dated release by renaming `[Unreleased]` to
`[YYYY.MM.DD]` when enough changes have accumulated (target: roughly weekly,
or immediately after a policy-affecting change).

**Sub-section conventions** (only include what applies to the release):

- **Added** — new agents, runbooks, templates, integrations, docs
- **Changed** — modified agent scope, capability changes, doc reorganizations
- **Deprecated** — announced but not yet removed
- **Removed** — deletions
- **Fixed** — corrections to existing definitions or docs
- **Security** — changes to approval tiers, data boundaries, audit policy,
  credential handling

## Pattern Reuse

This CHANGELOG pattern is reusable across team repos that use CalVer. The
extracted artifacts:

- `templates/changelog-template.md` — starter `CHANGELOG.md` for a new repo
- `templates/pipeline-templates/changelog-check.yaml` — drop-in Azure DevOps
  job that enforces CHANGELOG updates on PRs
- `docs/adopting-changelog-pattern.md` — copy-paste adoption guide

For the optional scheduled release-cut automation, also copy
`scripts/cut_release.py` and `azure-pipelines-release.yml`.

---

## [Unreleased]

### Added

- `CHANGELOG.md` with backfilled release history (2026-04-20 through 2026-04-23)
- PR template checklist item requiring a CHANGELOG update for user-facing changes
- README link to CHANGELOG under Docs & References
- CHANGELOG enforcement CI check — fails PRs that don't touch `CHANGELOG.md`.
  Opt-out via `[skip-changelog]` in any commit message on the PR.
- Scheduled release-cut pipeline (`azure-pipelines-release.yml`) — runs at
  18:00 UTC Monday through Thursday, opens a PR that moves `[Unreleased]`
  content into a new dated section; human approves the PR per normal branch
  policy. Friday through Sunday are skipped — anything landing in that
  window is swept up in Monday's cut.
- `scripts/cut_release.py` — helper that implements the CHANGELOG rewrite;
  usable locally via `--dry-run` and `--date` flags
- Setup-guide step documenting the one-time pipeline registration
- Reusable CHANGELOG pattern for other CalVer-versioned team repos:
  `templates/changelog-template.md`, `templates/pipeline-templates/changelog-check.yaml`,
  and `docs/adopting-changelog-pattern.md`
- Post-merge tagging pipeline (`azure-pipelines-tag-release.yml`) — on every
  push to `main`, if the latest commit message contains `cut release YYYY.MM.DD`,
  creates an annotated tag `vYYYYMMDD` at `main` HEAD with the matching
  CHANGELOG section as the tag message. Tags serve as rollback markers and
  compact references.
- `scripts/extract_release_notes.py` — extracts a release section from
  `CHANGELOG.md` for the tag message; usable locally via
  `--version YYYY.MM.DD`.
- Adoption guide updated with the post-merge tagger steps.

### Changed

- Snowflake migration inventory runbook (`runbooks/snowflake-migration/object-inventory.md`)
  now describes the actual `DS_Snowflake_Migration.xlsx` workbook as the canonical
  tracker — six sheets (Airflow PROD DAGs, Snowflake tables/views, procedures, stages,
  functions, plus an Overview index), per-row disposition vocabulary
  (`DELETE`/`ARCHIVE`, `MIGRATE TO NEW ACCOUNT`, `KEEP IN OLD ACCOUNT`, `DATA SHARE`),
  and a "categories not yet in the workbook" gap list pointing at storage integrations,
  named shares, Streamlit apps, service users, monitors, and downstream dashboards.
  Refresh-inventory SQL queries retained as a maintenance section. Fixes BI contact
  to Michael Gabriel for consistency with `runbooks/snowflake-migration/README.md`.

---

## [2026.04.23]

### Added

- Azure DevOps CI pipeline (`azure-pipelines.yml`) that runs on every PR to
  `main` and validates YAML syntax, JSON syntax, and markdown style
- `.markdownlint.yaml` with structural rules enabled and noisy style rules
  disabled with rationale per rule
- `node_modules/` entry in `.gitignore`

### Changed

- All pipeline templates in `templates/pipeline-templates/` pinned from
  `ubuntu-latest` to `ubuntu-24.04` so future pipelines start from a known
  Ubuntu version

---

## [2026.04.22]

### Added

- Git Workflow Agent (`agents/git-workflow/`) with per-repo branching strategy
  support (GitHub Flow and Git Flow), branch-naming enforcement, and PR
  lifecycle management
- Per-repo branching configuration (`config/git-workflow.yaml`) for the four
  active team repos: `vpp-data-warehouse` (GitHub Flow), `vpp-snowpark-apps`,
  `vpp-airflow`, `enpal-energy-ds-snowflake-infra` (all Git Flow with `dev`
  as the integration branch)
- PR templates for GitHub (`.github/pull_request_template.md`) and Azure
  DevOps (`.azuredevops/pull_request_template.md`), aligned with the Jira
  ticket template structure
- Global `README.md` onboarding document covering architecture, agent roster,
  quick start, team workflow policies, and repo layout

### Changed

- Code Review Agent gains a hybrid PR review flow — auto-triggered by the Git
  Workflow Agent on new PRs, posts findings as a comment, does not
  auto-approve; humans make the final merge decision
- Root `CLAUDE.md` and Orchestrator gain a **Git Workflow Policy** section
  declaring that direct commits to protected branches are forbidden and PRs
  are mandatory on both GitHub and Azure DevOps
- Setup guide adds a Step 6 covering branch-protection configuration on both
  platforms
- Git Flow integration branch renamed from `develop` to `dev` to match team
  convention; `merge_style` extended from scalar to a map keyed by target
  branch (squash into `main`, merge no-ff into `dev`)

### Security

- New `git_workflow` approval tier — `git:push_to_protected_branch`,
  `git:force_push_shared`, `git:merge_without_review`, and `git:bypass_hooks`
  are **forbidden**; all write operations require approval
- New `git_workflow` entry in `data-boundaries.yaml` restricting writes on
  protected branches and force-pushes on shared branches

---

## [2026.04.21]

### Added

- MCP server configuration (`config/mcp-servers.json`) with real packages:
  Jira and Notion via Claude Code's built-in OAuth connectors, Snowflake via
  self-hosted `Snowflake-Labs/mcp` (dual-account for migration), Azure DevOps
  via self-hosted `@azure-devops/mcp`
- Setup guide (`docs/setup-guide.md`) covering Claude Code built-in
  connectors, Snowflake and Azure DevOps MCP server installation, and
  verification steps
- Jira ticket templates (`templates/jira-ticket-templates/`): story, bug,
  epic, task
- Prompt templates (`templates/prompt-templates/`): sprint-summary,
  dag-review, sql-review, migration-status, ml-context-digest, pr-review,
  pipeline-troubleshoot
- Azure DevOps pipeline templates (`templates/pipeline-templates/`):
  ci-build-test, cd-deploy, python-package-build, snowflake-artifact-upload,
  git-change-detection-deploy
- Architecture Agent (`agents/architecture/`) with binding-with-approval
  authority and ADR workflow; `docs/adr/` directory for Architecture
  Decision Records
- Incident response runbook (`runbooks/incident-response/`) — severity
  levels (P1–P4), triage, per-system guides (Airflow, Snowflake, Azure
  DevOps, data quality), escalation, and postmortem template
- Pipeline ops runbook (`runbooks/pipeline-ops/`) — DAG monitoring,
  deployment, connection management, performance tuning, backfill
  operations, troubleshooting; scoped to Astronomer (managed Airflow)
- Snowflake migration runbook (`runbooks/snowflake-migration/`) — 6-phase
  playbook aligned with Jira epic TVF-7, covering inventory (TVF-133), DDL
  baseline and storage integrations (TVF-135/TVF-136), schema-scoped
  replication and shares (TVF-8/TVF-9/TVF-137/TVF-138), services migration
  (TVF-11/TVF-15/TVF-139/TVF-140/TVF-142/TVF-143), parity validation
  (TVF-141), cutover (TVF-134), and SnowDDL adoption + cleanup + governance
  (TVF-144/TVF-145/TVF-146)

### Changed

- Credentials template documents Jira and Notion as OAuth (no env vars
  needed) and Snowflake and Azure DevOps as env-var based
- General Data Engineering Agent strengthened to cover implementation work
  (scaffolding DAGs, writing transformation logic, building data quality
  frameworks) in addition to review — aligns with how Snowflake SQL and
  Snowpark agents already combine both roles

### Removed

- Planned automation scripts (`scripts/dispatch.py`,
  `scripts/validate-migration.py`, `scripts/sync-context.py`) — agents
  handle these tasks directly via MCP servers; `scripts/` retained as a
  placeholder for future non-agent automation
- Migration Agent reference to `scripts/validate-migration.py` (now points
  to the Snowflake MCP server directly)

---

## [2026.04.20]

### Added

- Design spec (`docs/superpowers/specs/2026-04-20-agent-workflow-framework-design.md`)
  for the Config-First orchestrator framework
- Implementation plan (`docs/superpowers/plans/2026-04-20-agent-workflow-framework.md`)
- Security / Guardrail Layer (`agents/security/`) — policy layer inherited
  by all agents, covering credential management, action guardrails
  (autonomous / requires-approval / forbidden), data boundaries, and audit
  trail
  - `approval-tiers.yaml` — per-agent action tiers
  - `data-boundaries.yaml` — per-agent data scope
  - `credentials.template.yaml` — required credential fields (no values)
  - `audit-policy.yaml` — logging requirements
- Orchestrator agent (`agents/orchestrator/`) — routing, multi-agent
  coordination, cross-agent summarization, approval enforcement
- Root `CLAUDE.md` with project overview, agent roster, security summary,
  and new-agent onboarding steps
- Specialized agents:
  - PMO — Jira/Notion project coordination
  - Migration — Snowflake account A→B
  - DS/ML Liaison — ML/DS context translation for DE team
  - Snowflake SQL — SQL authoring, review, optimization
  - Snowpark Dev — Snowpark Python procedures, UDFs, DataFrames
  - General Data Engineering — Airflow, pipelines, data modeling, data quality
  - QA / Testing — unit, integration, e2e testing
  - Code Review — PR review, code quality, security checks
  - Platform Engineering — Azure DevOps CI/CD (strictly scoped)
- Agent template (`agents/_template/`) — blank scaffold for new agents
- MCP server configuration skeleton (`config/mcp-servers.json`) with
  placeholder package names (real packages added 2026-04-21)
- Directory scaffolds: `runbooks/` (snowflake-migration, pipeline-ops,
  incident-response), `templates/` (jira-ticket-templates, prompt-templates,
  pipeline-templates), `logs/audit/` (git-ignored)
