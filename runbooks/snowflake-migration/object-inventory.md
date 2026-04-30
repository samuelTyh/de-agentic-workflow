# Phase 0: Migration Dependency Inventory

Track every dependency that needs migration or coordination. Ticket: [TVF-133](https://enpal.atlassian.net/browse/TVF-133).

## Tracker

The canonical tracker is the SharePoint workbook **DS_Snowflake_Migration.xlsx** ([open](https://enpal-my.sharepoint.com/:x:/r/personal/teresa_rueskamp_enpal_de/_layouts/15/Doc.aspx?sourcedoc=%7B6E89299C-B987-4403-BB6D-2EE8E401578D%7D&file=DS_Snowflake_Migration.xlsx&action=default&mobileredirect=true&DefaultItemOpen=1)). Linked from [TVF-7](https://enpal.atlassian.net/browse/TVF-7). Reviewed weekly until Phase 4 closes.

The workbook covers `PROD_VPP_DB` Snowflake objects and Airflow PROD DAGs. Other migration-affected categories (storage integrations, named shares, service users, monitors, downstream dashboards) are not yet on a sheet and need separate tracking — see [Categories Not Yet in the Workbook](#categories-not-yet-in-the-workbook).

## Workbook Structure

Six sheets, each with a per-row disposition decision.

| Sheet | Rows | What it lists |
|-------|------|---------------|
| `Overview Snowflake` | ~13 | Index of the other Snowflake sheets, open questions, action items |
| `Airflow PROD DAGs` | ~80 | Every PROD DAG in `vpp-airflow` |
| `PROD_VPP_DB.tables&views` | ~240 | Tables and views across all schemas |
| `PROD_VPP_DB.procedures` | ~85 | Stored procedures |
| `PROD_VPP_DB.stages` | ~25 | Internal and external stages |
| `PROD_VPP_DB.functions` | ~8 | UDFs |

### Sheet column conventions

**`Airflow PROD DAGs`**

| Column | Description |
|--------|-------------|
| `Name` | DAG id |
| `Deployment` | e.g. `PROD_DEPLOYMENT( Airflow v3.1.6 )` |
| `Schedule` | Human-readable schedule from Airflow UI |
| `Owner` | DAG owner email |
| `Tags` | Astronomer/Airflow tags (comma-separated, sometimes truncated) |
| `Migrate to new instance` | Disposition checkbox (see vocabulary below) |
| `Keep in old instance` | Disposition checkbox |

**`PROD_VPP_DB.*` (tables&views, procedures, stages, functions)**

| Column | Description |
|--------|-------------|
| `<TYPE>_SCHEMA` | Schema name (e.g. `FORECASTS`, `FEATURE_STORE`) |
| `<TYPE>_NAME` | Object name |
| `<TYPE>_TYPE` | For tables&views and stages only — `BASE TABLE`, `VIEW`, `Internal Named`, etc. |
| `<TYPE>_OWNER` | Snowflake role that owns the object (e.g. `VPP_ADMIN`, `DATA_SCIENTIST`) |
| `DELETE` (or `DELETE / ARCHIVE`) | Disposition checkbox |
| `MIGRATE TO NEW ACCOUNT` | Disposition checkbox |
| `KEEP IN OLD ACCOUNT` | Disposition checkbox |
| `DATA SHARE` (tables&views only: `DATA SHARE to the new instance`) | Disposition checkbox |

### Disposition vocabulary

Every row gets exactly one disposition. The four mutually-exclusive choices are:

| Value | Meaning |
|-------|---------|
| `DELETE` / `ARCHIVE` | Drop the object — not migrated, not shared |
| `MIGRATE TO NEW ACCOUNT` | Recreate on Account B (via SnowDDL or direct DDL) |
| `KEEP IN OLD ACCOUNT` | Stays in Account A; not directly accessible from B |
| `DATA SHARE` | Stays in Account A but exposed to Account B via Snowflake share |

### Schemas observed in the workbook

`tables&views`: ENERGY_TIMESERIES_CLEANING, FEATURE_STORE, FORECASTS, FORECAST_API, FORECAST_META, IOT_TIMESERIES_PROFILES, PROCESSED, PUBLIC, RAW, RAW_ELEMENTARY, RAW_ODS, RAW_SNOWFLAKE_COST_MONITORING

`procedures`: ENERGY_TIMESERIES_CLEANING, FEATURE_STORE, FORECASTS, IOT_TIMESERIES_PROFILES

`stages`: ENERGY_TIMESERIES_CLEANING, FEATURE_STORE, FORECASTS, RAW, SNOWPARK, STREAMLIT

`functions`: FEATURE_STORE, FORECASTS

## DS-Owned Schemas to Replicate

Cross-references the disposition decisions. These schemas are the ones moving to Account B via schema-scoped replication ([TVF-137](https://enpal.atlassian.net/browse/TVF-137)).

**In scope (replicated to B):**

- `FEATURE_STORE`
- `FORECASTS`
- `FORECAST_API`
- `FORECAST_META`
- `ENERGY_TIMESERIES_CLEANING`
- `IOT_TIMESERIES_PROFILES`

**Out of scope (stays in A, consumed via inbound share):**

- `RAW`, `RAW_ELEMENTARY`, `RAW_ODS`, `RAW_SNOWFLAKE_COST_MONITORING`
- `PROCESSED`
- `PUBLIC`
- Anything tagged `master_data_*` or `DAM`

If a row in the workbook is dispositioned `MIGRATE TO NEW ACCOUNT` but its schema is not in the in-scope list above, treat that as a discrepancy and resolve before migration.

## Categories Not Yet in the Workbook

[TVF-133](https://enpal.atlassian.net/browse/TVF-133) requires tracking these categories too. They are not currently on a workbook sheet and need separate tracking — either added as new sheets, or kept in a per-category note linked from TVF-7.

| Category | Source of truth (today) | Notes |
|----------|------------------------|-------|
| Storage integrations (inbound + outbound) | `vpp-data-warehouse/ingestion/storage_integrations/*` and `export/storage_integrations/*` | Recreated on B via SnowDDL — see [TVF-135](https://enpal.atlassian.net/browse/TVF-135) |
| Inbound named shares | `ENPAL_COMPUTE_PROD_SHARE` (BI, contact: Michael Gabriel), legacy VPP IoT (`raw/*`, `processed.V2_*`, `master_data_*`, `DAM`), Meteomatics weather | See [TVF-9](https://enpal.atlassian.net/browse/TVF-9) |
| Outbound shares | Flexa (currently blob via `export/storage_integrations/flexa`), BI (forecasts/KPIs return) | See [TVF-138](https://enpal.atlassian.net/browse/TVF-138) |
| Streamlit apps | `vpp-snowpark-apps/apps/streamlit/*` | The `STREAMLIT` schema is captured in `stages` but the apps themselves aren't on a sheet — see [TVF-140](https://enpal.atlassian.net/browse/TVF-140) |
| Service users + KPA keys | `airflow_service_user`, `forecast_api_service_user`, `snowddl` bot, etc. — Azure Key Vault | See [TVF-143](https://enpal.atlassian.net/browse/TVF-143) |
| Resource monitors + alerts | Per-warehouse credit limits; Snowflake task-failure alerts; Datadog/Grafana/New Relic integrations | See [TVF-142](https://enpal.atlassian.net/browse/TVF-142) |
| Downstream dashboards & reports | Tableau and Streamlit consumers | Identify per-dashboard ownership and validate post-cutover |

If you fill these gaps, update this section to match.

## Refreshing the Inventory

The workbook was originally populated with `SHOW`/`information_schema` queries against Account A. Re-run these to spot drift between the workbook and current state.

```sql
-- Databases and schemas
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE PROD_VPP_DB;

-- Tables and views (matches `PROD_VPP_DB.tables&views`)
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

-- Procedures (matches `PROD_VPP_DB.procedures`)
SELECT procedure_schema, procedure_name, procedure_owner
FROM PROD_VPP_DB.information_schema.procedures
WHERE procedure_schema NOT IN ('INFORMATION_SCHEMA');

-- Functions (matches `PROD_VPP_DB.functions`)
SELECT function_schema, function_name, function_owner
FROM PROD_VPP_DB.information_schema.functions
WHERE function_schema NOT IN ('INFORMATION_SCHEMA')
  AND function_owner IS NOT NULL;

-- Stages (matches `PROD_VPP_DB.stages`)
SHOW STAGES IN DATABASE PROD_VPP_DB;

-- Pipes and file formats (not currently on a sheet — TODO if relevant)
SHOW PIPES IN DATABASE PROD_VPP_DB;
SHOW FILE FORMATS IN DATABASE PROD_VPP_DB;
```

Compare each result set to the corresponding sheet. New rows in the query output without a workbook entry mean undecided dispositions — file as open questions in the `Overview Snowflake` sheet.

## Phase 0 Exit Criteria

- [ ] Workbook linked from [TVF-7](https://enpal.atlassian.net/browse/TVF-7)
- [ ] Every row in every sheet has a disposition selected
- [ ] No discrepancies between the disposition and the [DS-Owned Schemas to Replicate](#ds-owned-schemas-to-replicate) list
- [ ] Each "category not yet in the workbook" has either been added as a sheet or has its own tracking note linked from TVF-7
- [ ] Weekly review cadence established
