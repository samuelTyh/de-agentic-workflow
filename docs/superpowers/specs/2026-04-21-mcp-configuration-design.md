# MCP Configuration — Design Spec

## Overview

Update MCP server configuration to use real, verified packages and align with the team's authentication strategy.

**Decision:** Built-in Claude Code connectors for Jira and Notion (OAuth, zero config). Self-hosted MCP servers for Snowflake and Azure DevOps (env var credentials).

## Changes

### 1. config/mcp-servers.json

Remove Jira and Notion entries (handled by built-in connectors). Replace placeholder Snowflake and Azure DevOps entries with real packages:

- **Snowflake:** `Snowflake-Labs/mcp` — Python-based, requires Python 3.12+. Supports dual-account connection (A and B) for migration.
- **Azure DevOps:** `@azure-devops/mcp` — npm package. Each user provides PAT.

### 2. agents/security/credentials.template.yaml

- **Jira/Notion:** Keep entries but note they use built-in Claude Code OAuth — no env vars needed.
- **Snowflake:** Keep env var entries as-is. Add note about dual-account config for migration.
- **Azure DevOps:** Keep env var entries as-is.

### 3. docs/setup-guide.md (new)

Onboarding guide for new team members covering:
1. Clone repo
2. Authenticate Jira via Claude Code built-in connector (OAuth)
3. Authenticate Notion via Claude Code built-in connector (OAuth)
4. Install and configure Snowflake MCP server (Python, env vars)
5. Install and configure Azure DevOps MCP server (npm, env vars)

## What does NOT change

- Agent CLAUDE.md files — they reference services at capability level, not connection level
- Approval tiers and data boundaries — unchanged
- Audit policy — unchanged
