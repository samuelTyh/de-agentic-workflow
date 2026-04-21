# ML Context Digest

**Agent:** DS/ML Liaison Agent

## Inputs
- Time range (default: last 7 days)
- (Optional) Specific repo or team member to focus on

## Steps
1. Scan ML/DS git repos for recent commits and PRs
2. Identify changes that affect data engineering:
   - New or modified feature tables
   - Schema changes to existing tables
   - New model deployments or retraining pipelines
   - Changes to data ingestion requirements
3. Pull related Jira tickets and Notion docs
4. Query Snowflake for new/modified feature tables in the period
5. Translate findings into DE implications

## Output Format

### ML/DS Digest — [Date Range]

### Changes Requiring DE Action
| Change | Repo/Source | DE Impact | Suggested Action |
|--------|------------|-----------|-----------------|

### Informational (No Action Needed)
| Change | Repo/Source | Summary |
|--------|------------|---------|

### New/Modified Feature Tables
| Table | Database.Schema | Changed By | What Changed |
|-------|----------------|------------|-------------|

### Upcoming
[Known upcoming ML work that will need DE support]
