# Phase 0: Migration Dependency Inventory

Build a single source-of-truth tracker listing every dependency that needs migration or coordination. Ticket: [TVF-133](https://enpal.atlassian.net/browse/TVF-133).

## Tracker Location

Notion or Confluence — agree with team, then link from [TVF-7](https://enpal.atlassian.net/browse/TVF-7). Reviewed weekly until Phase 4 closes.

## Tracker Schema

Each entry should capture:

| Column | Description |
|--------|-------------|
| Name | Object/dependency name |
| Category | See categories below |
| Owner | Person or team responsible |
| Source | Account A location (or external provider) |
| Target | Account B location, or "stays in A (shared)" |
| Status | Not started / In progress / Migrated / Validated |
| Blocker notes | Open dependencies, external waits |
| ETA | Target completion date |

## Categories to Capture

### Storage Integrations
Inbound + outbound, Azure + AWS. Source locations:
- `vpp-data-warehouse/ingestion/storage_integrations/*`
- `vpp-data-warehouse/export/storage_integrations/*`

### Inbound Data Shares
- **BI** — `ENPAL_COMPUTE_PROD_SHARE` from main BI Snowflake account (contact: Alex Sutcliffe)
- **Legacy VPP IoT** — `raw/*`, `processed.V2_*`, `master_data_*`, `DAM` (stays in A, shared into B)
- **Meteomatics** — weather data (external provider, needs coordination to re-share to B locator)

### Outbound Data Shares
- **Flexa** — forecast export (currently `export/storage_integrations/flexa` blob sync; confirm whether to switch to Snowflake share)
- **Main BI** — any forecasts/KPIs published back to BI (confirm direction with BI team)
- Others — enumerate as discovered

### Snowpark Stored Procedures
- `vpp-data-warehouse/pipelines/prod/procedures/*` — forecast procs (`tso_*`, `system_*`, `pool_*`, `household_*`), feature_store procs (`update_vpp_system_pools`), validation procs
- `vpp-snowpark-apps/apps/snowpark/*`

### Streamlit Apps
- `vpp-snowpark-apps/apps/streamlit/*`

### Airflow DAGs
- `vpp-airflow/dags/*` — every DAG that touches Snowflake

### Downstream Dashboards & Reports
- Tableau dashboards
- Streamlit apps (internal consumers)

### Service Users + KPA Keys
Azure Key Vault entries to migrate/rotate:
- `airflow_service_user`
- `forecast_api_service_user`
- `snowddl` bot
- Any others (e.g., dbt when activated)

### Resource Monitors + Monitoring Alerts
- Credit limits per warehouse family
- Snowflake task-failure alerts
- Datadog / Grafana / New Relic Snowflake integrations

## DS-Owned Schemas to Replicate

**In scope** (will move to B via replication):
- `feature_store`
- `forecasts`
- `forecast_api`
- `model_registry`
- `energy_timeseries_cleaning`
- `analytics` (if applicable)

**Out of scope** (stays in A, consumed via inbound share):
- `raw/*`
- `processed.V2_*`
- `master_data_*`
- `DAM`

## Phase 0 Exit Criteria

- [ ] Tracker exists and is linked from [TVF-7](https://enpal.atlassian.net/browse/TVF-7)
- [ ] First full inventory pass complete
- [ ] All categories captured with at least one entry where applicable
- [ ] Every entry has an owner assigned
- [ ] Weekly review cadence established
