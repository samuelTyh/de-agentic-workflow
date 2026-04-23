# Setup Guide

Onboarding guide for new team members to use the agent-workflow framework.

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- Python 3.12+
- Node.js (for npx)
- Access to: Jira, Notion, Snowflake, Azure DevOps

## Step 1: Clone the Repo

```bash
git clone <repo-url>
cd agent-workflow-dev
```

## Step 2: Connect Jira (built-in)

Jira uses Claude Code's built-in Atlassian Rovo connector — no API tokens needed.

1. Open Claude Code
2. Go to Settings > Connectors (or use `/connectors`)
3. Find **Atlassian Rovo** and click **Connect**
4. Complete the OAuth flow in your browser
5. Done — Claude Code now has access to your Jira project

## Step 3: Connect Notion (built-in)

Notion uses Claude Code's built-in Notion connector — no API tokens needed.

1. Open Claude Code
2. Go to Settings > Connectors (or use `/connectors`)
3. Find **Notion** and click **Connect**
4. Complete the OAuth flow and select the workspace to grant access
5. Done — Claude Code now has access to your Notion workspace

## Step 4: Configure Snowflake MCP Server

Snowflake uses a self-hosted MCP server (`Snowflake-Labs/mcp`).

### Install

```bash
pip install snowflake-mcp-server
# or
uv add snowflake-mcp-server
```

### Set Environment Variables

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
# Snowflake — primary account (account A)
export SNOWFLAKE_ACCOUNT="your-account-identifier"
export SNOWFLAKE_USER="your-username"
export SNOWFLAKE_PASSWORD="your-password"
export SNOWFLAKE_ROLE="your-default-role"
export SNOWFLAKE_WAREHOUSE="your-default-warehouse"

# Snowflake — migration target (account B)
# Only needed if you're working on account migration
export SNOWFLAKE_ACCOUNT_B="target-account-identifier"
export SNOWFLAKE_USER_B="your-username-on-b"
export SNOWFLAKE_PASSWORD_B="your-password-on-b"
export SNOWFLAKE_ROLE_B="your-role-on-b"
export SNOWFLAKE_WAREHOUSE_B="your-warehouse-on-b"
```

### Register in Claude Code

```bash
claude mcp add snowflake -- python -m snowflake_mcp_server
```

For dual-account migration work:
```bash
claude mcp add snowflake_account_b -- python -m snowflake_mcp_server \
  --account "$SNOWFLAKE_ACCOUNT_B" \
  --user "$SNOWFLAKE_USER_B" \
  --password "$SNOWFLAKE_PASSWORD_B" \
  --role "$SNOWFLAKE_ROLE_B" \
  --warehouse "$SNOWFLAKE_WAREHOUSE_B"
```

## Step 5: Configure Azure DevOps MCP Server

Azure DevOps uses a self-hosted MCP server (`@azure-devops/mcp`).

### Create a Personal Access Token

1. Go to Azure DevOps > User Settings > Personal Access Tokens
2. Create a new token with the scopes your work requires (work items, pipelines, code)
3. Copy the token

### Set Environment Variables

```bash
export AZDO_PAT="your-personal-access-token"
export AZDO_ORG_URL="https://dev.azure.com/yourorg"
```

### Register in Claude Code

```bash
claude mcp add azure_devops -- npx -y @azure-devops/mcp
```

## Step 6: Enable Branch Protection Rules (one-time, per repo)

The framework's Git Workflow Policy forbids direct commits to protected branches. This must also be enforced at the platform level on each hosting provider.

### On GitHub

For each repo, an admin enables branch protection on every branch listed in the repo's `protected_branches` (minimum `main`; Git Flow repos also protect the integration branch — the team uses `dev`):

1. Go to **Settings → Branches → Branch protection rules → Add rule**
2. Branch name pattern: `main` (repeat for `dev` on Git Flow repos)
3. Enable:
   - **Require a pull request before merging**
   - **Require approvals** (at least 1)
   - **Dismiss stale pull request approvals when new commits are pushed**
   - **Do not allow bypassing the above settings** (includes admins)
4. Save

### On Azure DevOps

For each repo, an admin enables branch policies on every branch listed in the repo's `protected_branches` (minimum `main`; Git Flow repos also protect the integration branch — the team uses `dev`):

1. Go to **Repos → Branches → find the branch → `...` → Branch policies**
2. Enable:
   - **Require a minimum number of reviewers** (at least 1)
   - **Reset code reviewer votes when there are new changes**
   - **Check for linked work items** (recommended)
   - **Limit merge types** — squash recommended by default
3. Save

### Declare Strategy in Config

After enabling platform-level protection, declare the repo's branching strategy in this repo's `config/git-workflow.yaml` so the Git Workflow Agent knows how to operate:

```yaml
repos:
  my-project/my-repo:
    strategy: github_flow  # or git_flow
    protected_branches: [main]  # add dev for git_flow
    merge_style:
      main: squash
      # dev: merge_no_ff   # add for git_flow
```

## Step 7: Register the Scheduled Release Pipeline (one-time, admin)

The repo ships with two Azure DevOps pipelines:

- `azure-pipelines.yml` — PR validation (registered automatically on first PR)
- `azure-pipelines-release.yml` — scheduled release cut at 18:00 UTC, Monday through Thursday

The **release pipeline** must be registered manually once by a repo admin so the daily cron trigger fires:

1. In Azure DevOps: **Pipelines → New Pipeline**
2. Source: Azure Repos Git → `enpal-energy-ds-agentic-workflow`
3. Configure: **Existing Azure Pipelines YAML file**
4. Path: `/azure-pipelines-release.yml`
5. Save (do not Run — the schedule will trigger it)
6. Rename the pipeline to something like `agent-workflow-dev — scheduled release` for clarity

The pipeline uses `System.AccessToken` to push a feature branch and open a PR. The project build service identity needs **Contribute** permission on the repo (default — no change needed) and **Create branch** permission (also default). Branch protection still governs merges.

**What it does:** at 18:00 UTC on Monday–Thursday, if `CHANGELOG.md` has content under `[Unreleased]`, the pipeline opens a PR that moves that content into a new dated section. A maintainer reviews and merges the PR per normal branch policy. Friday through Sunday are intentionally skipped — anything that lands in that window is swept up in Monday's cut.

**What it does NOT do:** merge the release PR automatically. Human approval is always required.

## Verify Setup

After completing all steps, start a Claude Code session in this repo and verify:

```
> Summarize my current Jira sprint
> Show me recent Notion meeting notes
> List databases in Snowflake account A
> Show Azure DevOps pipeline status
```

If any of these fail, check that:
1. Built-in connectors show as "Connected" in Claude Code settings
2. Environment variables are set (`echo $SNOWFLAKE_ACCOUNT`, etc.)
3. MCP servers are registered (`claude mcp list`)
