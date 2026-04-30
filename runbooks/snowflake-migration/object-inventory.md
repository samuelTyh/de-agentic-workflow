# Phase 0: Migration Dependency Inventory

Track every dependency that needs migration or coordination. Ticket: [TVF-133](https://enpal.atlassian.net/browse/TVF-133).

## Tracker

The canonical tracker is the SharePoint workbook **`snowflake-migration-tracker.xlsx`**. Every PROD_VPP_DB object, Airflow PROD DAG, external dependency, and service user is one row. Linked from [TVF-7](https://enpal.atlassian.net/browse/TVF-7) and [TVF-133](https://enpal.atlassian.net/browse/TVF-133). Reviewed weekly until Phase 4 closes.

The workbook lives in SharePoint to support real-time multi-user editing during weekly migration syncs. The TVF-133 ticket carries the canonical link.

`DS_Snowflake_Migration.xlsx` is the **historical input** — the original PROD_VPP_DB inventory survey owned by the DS team. Its asset rows have been imported into the canonical tracker; treat the DS file as a read-only audit reference. Do not record new dispositions there.

## Tracker Structure

Three sheets plus a README sheet.

| Sheet | What it lists |
|-------|---------------|
| `README` | One-page guide: conventions, weekly meeting checklist, sheet index |
| `Inventory` | Main line-item tracker — one row per object |
| `External deps` | Items gated on external stakeholders (Azure IAM, Flexa, BI, etc.) |
| `Service users & KPA` | Service-user / KPA key rotation status |

### `Inventory` columns

| Column | Description |
|--------|-------------|
| `ID` | `INV-NNN`, sequentially assigned |
| `Category` | One of: Airflow DAG, Table, View, Stored Procedure, UDF, Stage, Storage Integration, Outbound Share, Service User (extend as new categories appear) |
| `Name` | DAG id, or `SCHEMA.OBJECT` for Snowflake objects |
| `Source` | `Account A` for everything imported; otherwise the external account |
| `Repo + path` | Where the source-of-truth code or definition lives |
| `Disposition` | One of: `Move to B`, `Stay in A`, `Dual-target`, `Delete`, or blank if undecided |
| `Workstream` | `WS-1` through `WS-6`, or `Cross-cutting`. Assigned at review. |
| `Owner (DRI)` | Single named person (not a team). Empty until assigned. |
| `Related Jira` | TVF-XXX ticket key |
| `Status` | `Not started → In progress → Shadow → Verified → Done`, plus `Blocked` for external holds |
| `Blocker notes` | Free text — open dependencies, external waits |
| `ETA` | Target completion date |
| `Last updated` | ISO date, set on every edit |

### Disposition vocabulary

Each row has exactly one disposition:

| Value | Meaning |
|-------|---------|
| `Move to B` | Recreate on Account B (via SnowDDL or direct DDL) |
| `Stay in A` | Stays in Account A. Includes data shared into B via Snowflake share — that share decision is tracked separately, not as a distinct disposition. |
| `Dual-target` | Runs against both accounts during the parallel window |
| `Delete` | Drop — not migrated |
| (blank) | Not yet decided. Resolve before Phase 1 begins. |

## Imported Coverage

The initial import seeded the `Inventory` sheet with ~440 rows from `DS_Snowflake_Migration.xlsx`:

| Category | Rows imported |
|----------|---------------|
| Airflow DAG | 80 |
| Table | 159 |
| View | 82 |
| Stored Procedure | 86 |
| Stage | 25 |
| UDF | 7 |

Plus three pre-existing seed rows for categories DS doesn't track (storage integration, outbound share, service user) — see [Categories Beyond the DS Survey](#categories-beyond-the-ds-survey).

About a quarter of imported rows already carry a disposition from the DS team's prior work. The remaining rows need disposition decisions in Phase 0.

## Categories Beyond the DS Survey

[TVF-133](https://enpal.atlassian.net/browse/TVF-133) requires tracking categories the DS spreadsheet doesn't cover. These are added as new rows in the `Inventory` sheet (or, for cross-cutting items, in `External deps` / `Service users & KPA`).

| Category | Source of truth (today) | Notes |
|----------|------------------------|-------|
| Storage integrations (inbound + outbound) | `vpp-data-warehouse/ingestion/storage_integrations/*` and `export/storage_integrations/*` | Recreated on B via SnowDDL — see [TVF-135](https://enpal.atlassian.net/browse/TVF-135) |
| Inbound named shares | `ENPAL_COMPUTE_PROD_SHARE` (BI, contact: Michael Gabriel), legacy VPP IoT (`raw/*`, `processed.V2_*`, `master_data_*`, `DAM`), Meteomatics weather | See [TVF-9](https://enpal.atlassian.net/browse/TVF-9) |
| Outbound shares | Flexa (currently blob via `export/storage_integrations/flexa`), BI (forecasts/KPIs return) | See [TVF-138](https://enpal.atlassian.net/browse/TVF-138) |
| Streamlit apps | `vpp-snowpark-apps/apps/streamlit/*` | The `STREAMLIT` schema is captured among Stage rows, but the apps themselves are separate — see [TVF-140](https://enpal.atlassian.net/browse/TVF-140) |
| Service users + KPA keys | `airflow_service_user`, `forecast_api_service_user`, `snowddl` bot, etc. — Azure Key Vault | Tracked in the `Service users & KPA` sheet — see [TVF-143](https://enpal.atlassian.net/browse/TVF-143) |
| Resource monitors + alerts | Per-warehouse credit limits; Snowflake task-failure alerts; Datadog/Grafana/New Relic integrations | See [TVF-142](https://enpal.atlassian.net/browse/TVF-142) |
| Downstream dashboards & reports | Tableau and Streamlit consumers | Identify per-dashboard ownership and validate post-cutover |

When you fill a gap, add the row(s) and update this section.

## Refreshing the Inventory

The DS spreadsheet was originally populated with `SHOW`/`information_schema` queries against Account A. Re-run these to spot drift between the tracker and current Account A state.

```sql
-- Databases and schemas
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE PROD_VPP_DB;

-- Tables and views
SELECT
    table_schema,
    table_name,
    table_type,
    table_owner,
    row_count,
    bytes,
    ROUND(bytes / 1024 / 1024 / 1024, 2) AS size_gb
FROM PROD_VPP_DB.information_schema.tables
WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY bytes DESC;

-- Procedures
SELECT procedure_schema, procedure_name, procedure_owner
FROM PROD_VPP_DB.information_schema.procedures
WHERE procedure_schema NOT IN ('INFORMATION_SCHEMA');

-- Functions (UDFs)
SELECT function_schema, function_name, function_owner
FROM PROD_VPP_DB.information_schema.functions
WHERE function_schema NOT IN ('INFORMATION_SCHEMA')
  AND function_owner IS NOT NULL;

-- Stages
SHOW STAGES IN DATABASE PROD_VPP_DB;

-- Pipes and file formats (not currently in the tracker — add rows if relevant)
SHOW PIPES IN DATABASE PROD_VPP_DB;
SHOW FILE FORMATS IN DATABASE PROD_VPP_DB;
```

Compare each result set against the corresponding rows in the `Inventory` sheet. New rows in the query output without a tracker entry are undecided dispositions — file as new `INV-NNN` rows with disposition blank.

## DS-Owned Schemas to Replicate

Cross-references the disposition decisions. These schemas are the ones moving to Account B via schema-scoped replication ([TVF-137](https://enpal.atlassian.net/browse/TVF-137)).

**In scope (replicated to B):**

- `FEATURE_STORE`
- `FORECASTS`
- `FORECAST_API`
- `FORECAST_META`
- `ENERGY_TIMESERIES_CLEANING`
- `IOT_TIMESERIES_PROFILES`

**Out of scope (stays in A, possibly consumed via inbound share):**

- `RAW`, `RAW_ELEMENTARY`, `RAW_ODS`, `RAW_SNOWFLAKE_COST_MONITORING`
- `PROCESSED`
- `PUBLIC`
- Anything tagged `master_data_*` or `DAM`

If a row in the tracker is dispositioned `Move to B` but its schema is not in the in-scope list above, treat that as a discrepancy and resolve before migration.

## Phase 0 Exit Criteria

- [ ] Tracker linked from [TVF-7](https://enpal.atlassian.net/browse/TVF-7) and [TVF-133](https://enpal.atlassian.net/browse/TVF-133)
- [ ] Every `Inventory` row has a non-blank Disposition
- [ ] Every `Inventory` row has an Owner (DRI) assigned
- [ ] No discrepancies between the disposition and the [DS-Owned Schemas to Replicate](#ds-owned-schemas-to-replicate) list
- [ ] Each "Category Beyond the DS Survey" has at least one tracker row, or is intentionally deferred with a note in `Blocker notes`
- [ ] Weekly review cadence established and the README sheet's checklist runs each meeting
