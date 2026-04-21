# Phase 2: DDL and RBAC Setup

Set up account B's schema objects, roles, and grants using snowDDL.

## Prerequisites

- snowDDL installed and configured for account B
- Account B credentials set (`SNOWFLAKE_ACCOUNT_B` env vars)
- RBAC design approved (use Architecture Agent for design decisions)

## Step 1: Define RBAC in snowDDL

Define roles, users, and grants in your snowDDL config. This is a **fresh design**, not a copy of account A.

Typical role hierarchy for DE team:

```
ACCOUNTADMIN
└── SYSADMIN
    ├── DE_ADMIN          -- manages DE objects
    │   ├── DE_DEVELOPER  -- read/write on DE schemas
    │   └── DE_READER     -- read-only on DE schemas
    ├── DS_DEVELOPER      -- read/write on DS/ML schemas
    └── SERVICE_ROLE      -- used by Airflow/pipelines
```

Adjust based on your team's needs. Document the decision as an ADR (`docs/adr/`).

## Step 2: Define Warehouses in snowDDL

```yaml
# Example snowDDL warehouse config
warehouses:
  DE_ETL_WH:
    size: MEDIUM
    auto_suspend: 60
    auto_resume: true
    comment: "ETL pipeline workloads"
  DE_ANALYTICS_WH:
    size: SMALL
    auto_suspend: 120
    auto_resume: true
    comment: "Ad-hoc analytics and queries"
```

## Step 3: Define Database and Schema Structure

Define all databases and schemas in snowDDL config, matching the inventory from Phase 1 (minus any objects you're intentionally dropping).

## Step 4: Apply snowDDL

```bash
# Dry run — preview changes
snowddl -c <config_path> --apply-mode plan

# Apply — create objects on account B
snowddl -c <config_path> --apply-mode apply
```

## Step 5: Verify

```sql
-- On account B, verify objects were created
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE <database_name>;
SHOW ROLES;
SHOW WAREHOUSES;
```

Compare against the inventory tracking table.

## Checklist

- [ ] RBAC design approved and documented as ADR
- [ ] Roles, users, grants defined in snowDDL
- [ ] Warehouses defined in snowDDL
- [ ] All databases and schemas created
- [ ] snowDDL config committed to version control
- [ ] Verification queries confirm all objects exist on account B
