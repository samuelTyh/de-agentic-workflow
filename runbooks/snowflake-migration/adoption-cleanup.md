# Phase 4: SnowDDL Adoption, Legacy Cleanup, Governance

Post-cutover work to absorb B into declarative SnowDDL, retire legacy directories, and publish the A/B governance document. Tickets: [TVF-144](https://enpal.atlassian.net/browse/TVF-144), [TVF-145](https://enpal.atlassian.net/browse/TVF-145), [TVF-146](https://enpal.atlassian.net/browse/TVF-146).

## Context

After cutover, Account B owns all DS-owned schemas (they were promoted from replicas to primaries). These objects exist in B but are not yet declared in `dcm_mvp/snowddl_mvp`. This phase closes that gap and retires legacy DDL management approaches.

## Part A: SnowDDL Adoption Sprint (TVF-144)

Reverse-engineer all DS-owned schema objects in Account B into SnowDDL YAML.

### Scope

Cover all object types in DS-owned schemas:
- Tables
- Views (standard + materialized)
- Streams
- Stages
- Dynamic tables
- Stored procedures
- File formats
- Sequences

### Target Layout

```
dcm_mvp/snowddl_mvp/prod_config/vpp_db/
├── feature_store/
│   ├── tables/
│   ├── views/
│   ├── streams/
│   └── stored_procs/
├── forecasts/
├── forecast_api/
├── model_registry/
├── energy_timeseries_cleaning/
└── analytics/
```

### Steps

1. **Use `snowddl-convert`** or a hand-written script to reverse-engineer existing B objects into YAML

2. **Iterate `snowddl plan`** until diff is zero:
   ```bash
   cd dcm_mvp/snowddl_mvp
   make plan-prod
   ```
   Expected: zero diff against live B.

3. **Delete corresponding `.sql` files** from `vpp-data-warehouse/ddl/vpp/*` in the same PRs to prevent drift

4. **Update team workflow docs:** All new VPP_DB changes go via SnowDDL PR, not via the legacy `ddl/` directory

### Part A Exit Criteria

- [ ] `snowddl plan` against Account B shows zero diff for all DS-owned schemas
- [ ] No object exists in B that is not declared in SnowDDL YAML
- [ ] Corresponding `.sql` files deleted from `vpp-data-warehouse/ddl/vpp/*`
- [ ] Engineering workflow documented: PRs to `dcm_mvp/snowddl_mvp`, not legacy `ddl/`

---

## Part B: Retire Legacy DDL Directories (TVF-145)

After adoption sprint completes, archive or remove legacy DDL locations in `vpp-data-warehouse`.

### Directories to Archive/Remove

- `vpp-data-warehouse/ddl/` — superseded by SnowDDL
- `vpp-data-warehouse/access_control/` — superseded by SnowDDL roles/grants
- `vpp-data-warehouse/warehouses/` — superseded by SnowDDL warehouses
- `vpp-data-warehouse/ingestion/` — once SnowDDL owns storage integrations
- `vpp-data-warehouse/export/` — once SnowDDL owns storage integrations

### Directories to Keep (for now)

- `vpp-data-warehouse/pipelines/prod/procedures/*` — Snowpark sprocs remain the repo's responsibility (or consider moving to `vpp-snowpark-apps` as a separate decision)

### Steps

1. **Confirm SnowDDL has absorbed** every legacy directory's responsibility
2. **Remove or archive** the legacy directories (preserve via git history or archive branch)
3. **Add README redirect** in `vpp-data-warehouse/` pointing future readers to `dcm_mvp/snowddl_mvp` as the new source of truth
4. **Remove old CI/CD pipelines** that applied the legacy SQL files (Azure DevOps pipelines for `ddl/`, `access_control/`)
5. **Add changelog entry** documenting the archive/removal

### Part B Exit Criteria

- [ ] Legacy directories archived with a clear changelog entry
- [ ] README points future readers to SnowDDL
- [ ] No CI/CD pipeline still runs against the legacy DDL files
- [ ] `vpp-data-warehouse/pipelines/prod/procedures/*` still functional (Snowpark sprocs retained)

---

## Part C: Governance Document — A/B Split (TVF-146)

Write the canonical document describing the steady-state split between Account A and Account B.

### Document Contents

**What permanently stays in Account A:**
- IoT raw data (`raw/*`)
- `processed.V2_*`
- `master_data_*`
- `DAM`
- Ingestion pipelines DS does not own

**What lives in Account B:**
- DS-owned schemas (feature_store, forecasts, forecast_api, model_registry, energy_timeseries_cleaning, analytics)
- Forecast API
- Streamlit apps
- Snowpark stored procedures (forecast, feature store, validation)

**How data flows between them:**
- A → B: inbound share from legacy VPP DB
- A → B (via BI): `ENPAL_COMPUTE_PROD_SHARE` from main BI account
- External → B: Meteomatics weather data share
- B → external: Flexa outbound (share or blob export, decision final)
- B → BI: any forecasts/KPIs returned to BI team

**Ownership:**
- Account A: [team that owns A going forward — record here]
- Account B: DS team

**Rules for adding new schemas/databases:**
> "Default to B via SnowDDL unless the object is IoT raw data or master data."

**Cost split:**
- Credit attribution: each account billed separately
- How credits roll up for finance reporting

### Steps

1. Draft the document under Confluence / Notion
2. Review with:
   - DS leads
   - BI leads
   - Platform leads
3. Get approval sign-offs
4. Link from [TVF-7](https://enpal.atlassian.net/browse/TVF-7) as the canonical reference post-migration

### Part C Exit Criteria

- [ ] Governance doc published under Confluence / Notion
- [ ] Reviewed and approved by DS + BI + platform leads
- [ ] Linked from [TVF-7](https://enpal.atlassian.net/browse/TVF-7)
- [ ] Team workflow updated: new objects default to B via SnowDDL

---

## Phase 4 Overall Exit Criteria

- [ ] All B-side DS-owned objects declared in SnowDDL YAML (zero-diff plan)
- [ ] Legacy DDL directories archived and CI/CD pipelines removed
- [ ] Governance document published and linked from TVF-7
- [ ] Migration tracker all entries in "Validated" or "Decommissioned" state
- [ ] TVF-7 epic closed
