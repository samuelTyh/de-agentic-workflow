# Snowflake Migration: Account A → B (New Energy Account)

Step-by-step procedures for migrating VPP (Virtual Power Plant, Forecasting & Trading) workloads from Account A to the New Energy Snowflake Account (Account B).

**Epic:** [TVF-7](https://enpal.atlassian.net/browse/TVF-7) — New Energy Snowflake Account

## Approach

**Hybrid A-then-B strategy:**

1. **During migration:** Schema-scoped **Snowflake replication** copies DS-owned schemas from A to B as a read-only replica. Everything else in A is consumed from B via **inbound data shares**.
2. **Cutover:** Freeze A writes → final replica refresh → promote B replica → flip connection strings → smoke test.
3. **Post-cutover (Phase 4):** Reverse-engineer B's replicated objects into declarative SnowDDL YAML for long-term management.

### What moves to Account B

**DS-owned schemas (replicated):**
- `feature_store`
- `forecasts`
- `forecast_api`
- `model_registry`
- `energy_timeseries_cleaning`
- `analytics`

**Services redeployed against B:**
- `vpp-airflow` DAGs (connection re-pointed)
- `vpp-data-warehouse` Snowpark stored procedures (forecast, feature_store, validation procs)
- `vpp-snowpark-apps` CI/CD pipelines (Snowpark apps + Streamlit)
- Forecast API

### What stays in Account A (consumed via inbound share)

- `raw/*` — IoT time-series data
- `processed.V2_*` — legacy processed data
- `master_data_*` — reference data
- `DAM` — day-ahead market data
- Ingestion pipelines DS does not own

## Key Repositories

| Repo | Purpose |
|------|---------|
| `dcm_mvp/snowddl_mvp` | Declarative DDL and RBAC config for Account B (Plan + Apply CI/CD pipelines) |
| `vpp-data-warehouse` | Snowpark stored procedures (`pipelines/prod/procedures/*`) + legacy DDL (being retired) |
| `vpp-snowpark-apps` | Snowpark apps (`apps/snowpark/*`) + Streamlit apps (`apps/streamlit/*`) |
| `vpp-airflow` | DAGs that touch Snowflake |

## Phases & Tickets

| Phase | Guide | Tickets |
|-------|-------|---------|
| **Phase 0: Inventory & Baseline** | [Phase 0: Inventory](object-inventory.md) | [TVF-133](https://enpal.atlassian.net/browse/TVF-133) |
| **Phase 0: DDL & Storage Setup** | [Phase 0: DDL & RBAC Setup](ddl-rbac-setup.md) | [TVF-135](https://enpal.atlassian.net/browse/TVF-135), [TVF-136](https://enpal.atlassian.net/browse/TVF-136) |
| **Phase 2: Data Migration** | [Phase 2: Data Migration](data-migration.md) | [TVF-8](https://enpal.atlassian.net/browse/TVF-8), [TVF-9](https://enpal.atlassian.net/browse/TVF-9), [TVF-137](https://enpal.atlassian.net/browse/TVF-137), [TVF-138](https://enpal.atlassian.net/browse/TVF-138) |
| **Phase 2: Services Migration** | [Phase 2: Services Migration](code-objects-migration.md) | [TVF-11](https://enpal.atlassian.net/browse/TVF-11), [TVF-15](https://enpal.atlassian.net/browse/TVF-15), [TVF-139](https://enpal.atlassian.net/browse/TVF-139), [TVF-140](https://enpal.atlassian.net/browse/TVF-140), [TVF-142](https://enpal.atlassian.net/browse/TVF-142), [TVF-143](https://enpal.atlassian.net/browse/TVF-143) |
| **Phase 2: Parity & Rehearsals** | [Phase 2: Validation](validation.md) | [TVF-141](https://enpal.atlassian.net/browse/TVF-141) |
| **Phase 3: Cutover** | [Phase 3: Cutover](cutover.md) | [TVF-134](https://enpal.atlassian.net/browse/TVF-134) |
| **Phase 4: SnowDDL Adoption & Cleanup** | [Phase 4: Adoption & Cleanup](adoption-cleanup.md) | [TVF-144](https://enpal.atlassian.net/browse/TVF-144), [TVF-145](https://enpal.atlassian.net/browse/TVF-145), [TVF-146](https://enpal.atlassian.net/browse/TVF-146) |

## Stakeholders

| Team / Party | Role | Contact |
|--------------|------|---------|
| DS team | Primary migration owner | Internal Teams |
| BI team | Inbound `ENPAL_COMPUTE_PROD_SHARE` from main BI Snowflake | Alex Sutcliffe |
| Cloud / IAM team | Azure trust policy updates, storage integrations (long lead time) | File ticket on Day 1 of Phase 0 |
| Flexa | Outbound forecast share (currently blob export, may switch) | External |
| Meteomatics | Weather data inbound share | External |
| Platform / Cloud lead | Cutover sign-off | Internal |
| DS tech lead | Cutover sign-off | Internal |

## Prerequisites

- Access to both Snowflake accounts — see `agents/security/credentials.template.yaml`
- SnowDDL repo `dcm_mvp/snowddl_mvp` cloned and CI/CD pipelines configured ([TVF-10](https://enpal.atlassian.net/browse/TVF-10) done)
- Azure Key Vault access for storing KPA keys
- Database layout finalized ([TVF-13](https://enpal.atlassian.net/browse/TVF-13))
- SSO via Microsoft EntraID configured ([TVF-17](https://enpal.atlassian.net/browse/TVF-17) done)

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| DCM tool | SnowDDL | Evaluated in [TVF-12](https://enpal.atlassian.net/browse/TVF-12) / [TVF-14](https://enpal.atlassian.net/browse/TVF-14) |
| Data migration mechanism | Schema-scoped replication | Fast, Snowflake-native, low operational risk |
| Legacy IoT data location | Stays in A, consumed via inbound share | Avoids moving petabytes of time-series data |
| Long-term DDL source of truth | SnowDDL (post Phase 4 adoption) | Declarative, reproducible, version-controlled |
| Authentication | KPA key pairs via Azure Key Vault | Aligns with team security standard |

## Migration Dependency Tracker

The single source of truth for tracking all dependencies is a Notion or Confluence page per [TVF-133](https://enpal.atlassian.net/browse/TVF-133). Link from TVF-7 once created. Reviewed weekly until Phase 4 closes.
