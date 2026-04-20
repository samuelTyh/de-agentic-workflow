# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Knowledge base and configuration hub for agent-workflow. This repo is the reference point for orchestrator logic, subagent definitions, and shared conventions across all future development work.

**Domain:** Data engineering — Airflow, Snowpark, Snowflake, Azure DevOps, pipeline orchestration, platform engineering.

**Tech:** Python 3.12+, managed with [uv](https://docs.astral.sh/uv/).

**Team:** 10 users sharing one Jira project and one Notion workspace.

## Commands

- **Run**: `uv run main.py`
- **Add dependency**: `uv add <package>`
- **Sync environment**: `uv sync`

## Orchestrator

This repo functions as a Config-First orchestrator. When a user makes a request, classify the intent and load the appropriate agent context from `agents/`. See `agents/orchestrator/CLAUDE.md` for the full routing table and coordination logic.

### Agent Roster

| Agent | Path | Domain |
|-------|------|--------|
| Security | `agents/security/` | Policy layer — approval tiers, data boundaries, credentials, audit |
| PMO | `agents/pmo/` | Jira full lifecycle, Notion integration, sprint planning |
| Migration | `agents/migration/` | Snowflake account A→B migration |
| DS/ML Liaison | `agents/ds-ml-liaison/` | ML/DS context translation for DE team |
| Snowflake SQL | `agents/snowflake-sql/` | SQL authoring, review, optimization |
| Snowpark Dev | `agents/snowpark-dev/` | Snowpark Python procedures, UDFs, DataFrames |
| General DE | `agents/data-engineering/` | Airflow, pipelines, data modeling, data quality |
| QA / Testing | `agents/testing/` | Unit, integration, e2e testing |
| Code Review | `agents/code-review/` | PR review, code quality, security checks |
| Platform Eng | `agents/platform-engineering/` | Azure DevOps CI/CD, pipeline optimization |

### Security

All agents inherit constraints from `agents/security/`. Actions are tiered: autonomous (read), requires-approval (write), forbidden (destructive). See `agents/security/approval-tiers.yaml`.

### Adding a New Agent

1. Copy `agents/_template/` to `agents/<new-agent-name>/`
2. Fill in the CLAUDE.md with identity, capabilities, scope, integrations
3. Add approval tiers to `agents/security/approval-tiers.yaml`
4. Add data boundaries to `agents/security/data-boundaries.yaml`
5. Add the agent to the roster table above and to `agents/orchestrator/CLAUDE.md`
