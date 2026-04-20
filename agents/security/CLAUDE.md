# Security / Guardrail Layer

This is the policy layer inherited by all agents. It is not a user-facing agent — it defines constraints that all other agents must follow.

## Credential Management

- Each user authenticates with their own tokens (Jira, Notion, Snowflake, Azure DevOps)
- No shared service accounts
- Credentials are stored in user-local config, never committed to this repo
- See `credentials.template.yaml` for required credential fields
- MCP servers inherit credentials from the user's environment variables

## Action Guardrails

All agent actions are classified into three tiers defined in `approval-tiers.yaml`:

- **autonomous** — read operations, summaries, diffs. No approval needed.
- **requires-approval** — write operations (create, update, assign, transition). User must confirm.
- **forbidden** — destructive operations (drop, bulk modify, delete). Never allowed without explicit override.

Rate limits: write-heavy agents (e.g., PMO) are capped at 5 write actions per session before re-approval.

Promotable patterns: trusted recurring actions can be moved from `requires-approval` to `autonomous` by updating `approval-tiers.yaml`.

## Data Boundaries

Defined in `data-boundaries.yaml`. Each agent declares its data scope in its own CLAUDE.md.

Core rules:
- Agents must not surface raw credentials, connection strings, or PII in outputs
- Sensitive Notion pages tagged for exclusion are off-limits to all agents
- Snowflake agents accessing metadata only — not row-level PII — unless explicitly scoped otherwise

## Audit Trail

Defined in `audit-policy.yaml`.

- Every write action logged to `logs/audit/` with: user, action, agent, timestamp, approval status
- Read actions logged at session-summary level
- Audit logs are git-ignored but persist locally
- Optional: push to shared location for team visibility

## Extensibility

Each pillar has a dedicated YAML file. To add new security policies:
1. Add the policy to the relevant YAML file
2. No need to modify individual agent CLAUDE.md files — they inherit from this layer
