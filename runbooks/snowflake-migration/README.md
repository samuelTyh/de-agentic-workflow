# Snowflake Migration: Account A → B

Step-by-step procedures for migrating from Snowflake account A to account B.

## Approach

- **DDL and RBAC:** Managed via snowDDL — roles, users, grants, warehouses, and schema objects are defined declaratively on account B (clean slate, not migrated from A)
- **Data migration:** Hybrid approach:
  - **Large historical tables:** Export from A → stage → import to B
  - **Everything else:** Re-ingest from original data sources into B's pipelines
- **Validation:** Object-by-object comparison between accounts

## Migration Phases

| Phase | Guide | Status |
|-------|-------|--------|
| 1. Inventory | [Object Inventory](object-inventory.md) | |
| 2. DDL Setup | [DDL and RBAC Setup](ddl-rbac-setup.md) | |
| 3. Data Migration | [Data Migration](data-migration.md) | |
| 4. Stored Procedures, UDFs, Tasks, Streams | [Code Objects Migration](code-objects-migration.md) | |
| 5. Validation | [Validation](validation.md) | |
| 6. Cutover | [Cutover](cutover.md) | |

## Prerequisites

- Access to both Snowflake accounts (A and B) — see `agents/security/credentials.template.yaml`
- snowDDL configured for account B
- Astronomer environment ready for re-ingestion pipelines
- Jira epic created for tracking (use the epic template in `templates/jira-ticket-templates/epic.md`)

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| RBAC | Fresh definition via snowDDL | Clean slate, no legacy role baggage |
| DDL | snowDDL declarative | Reproducible, version-controlled |
| Data (large tables) | Export/import via stages | Faster than re-ingestion for historical bulk data |
| Data (other tables) | Re-ingest from source | Clean data lineage, validates source pipelines |
| Warehouses | Fresh definition | Sized for account B workload, not legacy config |
