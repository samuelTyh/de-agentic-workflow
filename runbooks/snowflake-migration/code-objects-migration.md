# Phase 2: Services Migration

Migrate DS services (Airflow, Snowpark procedures, Streamlit apps, Forecast API), recreate monitoring, and rotate credentials. Tickets: [TVF-11](https://enpal.atlassian.net/browse/TVF-11), [TVF-15](https://enpal.atlassian.net/browse/TVF-15), [TVF-139](https://enpal.atlassian.net/browse/TVF-139), [TVF-140](https://enpal.atlassian.net/browse/TVF-140), [TVF-142](https://enpal.atlassian.net/browse/TVF-142), [TVF-143](https://enpal.atlassian.net/browse/TVF-143).

## Part A: Rotate Service User KPA Keys (TVF-143)

Runs in parallel with service deployment — service users must exist on B with fresh keys before their consumers can target B.

### Service Users to Rotate

- `airflow_service_user` — used by `vpp-airflow`
- `forecast_api_service_user` — used by Forecast API
- `snowddl` bot — used by SnowDDL CI/CD
- Any others (e.g., dbt when activated)

### Steps Per Service User

1. Generate fresh RSA key pair on a secure machine
2. Register public key on Account B user (via SnowDDL `user.yaml` `rsa_public_key` entry or transitional SQL)
3. Store private key base64-encoded in Azure Key Vault:
   - Use new secret names (e.g., `snowddl-airflow-key-accountb`) OR
   - Rotate existing names with consumer coordination
4. Update all CI/CD variable groups / pipeline references to the new secret
5. Validate `snow connection test` succeeds for the service user

### Parallel Window

- Keep A-side keys valid during the parallel window
- Revoke A-side keys after successful cutover

### Part A Exit Criteria

- [ ] Every service user in B authenticates successfully from its production consumer
- [ ] All private keys stored in Azure Key Vault
- [ ] CI/CD pipelines reference the new secret names
- [ ] Rotation plan documented: which keys revoke when

---

## Part B: Airflow — Re-point to Account B (TVF-11)

### Steps

1. **Add Account B Snowflake connection to Airflow:**
   ```bash
   astro run airflow connections add 'snowflake_account_b' \
       --conn-type 'snowflake' \
       --conn-host "$SNOWFLAKE_ACCOUNT_B" \
       --conn-login 'airflow_service_user' \
       --conn-password "$KPA_PRIVATE_KEY" \
       --conn-schema 'PUBLIC' \
       --conn-extra '{"role": "'$AIRFLOW_ROLE_B'", "warehouse": "'$AIRFLOW_WH_B'", "authenticator": "SNOWFLAKE_JWT", "private_key_content": "<key>"}'
   ```

2. **Test in staging:** Flip one or two DAGs from `vpp-airflow` to a scratch DB in B, run a full day, diff results against A (see Rehearsal #1 in `validation.md`)

3. **Re-test every DAG end-to-end in a staging environment before production cutover**

### DAG Migration Approach

Two patterns — use what fits each DAG:

- **Connection ID swap:** Change `snowflake_default` to `snowflake_account_b` in the DAG. Simpler, no code duplication.
- **Duplicate DAGs:** Copy the DAG with a different `dag_id`, point the copy at B, run both in parallel. Better rollback, more overhead.

Recommend duplicating for critical DAGs during rehearsals, swap for the rest at cutover.

### Part B Exit Criteria

- [ ] Account B Snowflake connection configured in Airflow
- [ ] Every DAG re-tested end-to-end in staging against B
- [ ] KPA key rotated and validated for `airflow_service_user`

---

## Part C: Snowpark Stored Procedures — `vpp-data-warehouse` (TVF-139)

Deploy all sprocs under `vpp-data-warehouse/pipelines/prod/procedures/*` to Account B.

### Scope

Covers:
- **Forecast procs:** `tso_*`, `system_*`, `pool_*`, `household_*`
- **feature_store procs:** `update_vpp_system_pools`
- **Validation procs**

### Steps

1. **Update deployment scripts** to target B:
   - New account locator (`SNOWFLAKE_ACCOUNT_B`)
   - Service user (`airflow_service_user` or dedicated sproc service user)
   - Role and warehouse from B's SnowDDL config

2. **Build and upload Snowpark packages:**
   - Use the `snowflake-artifact-upload.yaml` Azure DevOps template (in `templates/pipeline-templates/`)
   - Upload `.whl` files to Account B stages

3. **Create procedures on B:**
   ```sql
   CREATE OR REPLACE PROCEDURE <db>.<schema>.<proc_name>(...)
   RETURNS ...
   LANGUAGE PYTHON
   RUNTIME_VERSION = '3.12'
   PACKAGES = ('snowflake-snowpark-python')
   IMPORTS = ('@<stage>/<package>.whl')
   HANDLER = '<module>.<function>';
   ```

4. **Smoke-test each proc:**
   - Against the replicated DS-owned schemas in B (read-only replica), OR
   - Against a scratch DB with a representative data sample
   - At least one sample proc per forecast family (TSO, system, pool, household)

5. **Update CI/CD pipeline** for `vpp-data-warehouse` to deploy to B on merge

### Part C Exit Criteria

- [ ] All sprocs exist and are callable in Account B
- [ ] CI/CD pipeline for `vpp-data-warehouse` deploys to B on merge
- [ ] Smoke-test output from B matches A within tolerance for at least one sample per forecast family

---

## Part D: Snowpark Apps + Streamlit — `vpp-snowpark-apps` (TVF-15 + TVF-140)

Migrate `vpp-snowpark-apps` CI/CD pipelines and redeploy Streamlit apps.

### CI/CD Pipeline Migration (TVF-15)

1. Update all CI/CD pipelines in `vpp-snowpark-apps` to target Account B
2. Update pipeline variable groups / Azure Key Vault references:
   - Account B service users
   - Account B warehouses
   - Account B KPA keys (from Part A)
3. Covers deployment of:
   - Snowpark sprocs (`apps/snowpark/*`)
   - Streamlit apps (`apps/streamlit/*`)
4. Verify deploys from `main` / `dev` branches land in B automatically
5. Label old A-facing pipelines as legacy or decommission

### Streamlit Apps Migration (TVF-140)

1. Redeploy Streamlit apps under `vpp-snowpark-apps/apps/streamlit/*` to Account B
2. Update connection strings, service users, role references
3. **Shadow mode:** Apps live in B pointing at replica data; users can access both A and B copies during parallel window
4. Collect feedback from stakeholders accessing B-side apps during shadow period
5. Draft cutover checklist item: flip user-facing URLs/links on cutover weekend

### Part D Exit Criteria

- [ ] Every CI/CD pipeline in `vpp-snowpark-apps` green against Account B
- [ ] Deploys from `main` / `dev` branches land in B automatically
- [ ] All Streamlit apps live and functional in B against replicated/shared data
- [ ] Shadow-period stakeholder sign-off recorded
- [ ] URL flip checklist item added to cutover runbook

---

## Part E: Forecast API (TVF-11)

### Steps

1. **Set up `forecast_api_service_user` in B** with fresh KPA key (Part A)
2. **Update Forecast API config** to target B:
   - Account locator: `$SNOWFLAKE_ACCOUNT_B`
   - Role: `FORECAST_API_ROLE` (or as defined in SnowDDL)
   - Warehouse: dedicated warehouse per SnowDDL config
3. **Shadow mode validation:**
   - Run production traffic against B in shadow
   - Compare responses against A
4. **Flip to B** at cutover time

### Part E Exit Criteria

- [ ] Forecast API config updated to target B
- [ ] `forecast_api_service_user` authenticated with KPA key
- [ ] Shadow validation complete — responses match A within tolerance
- [ ] Flip step added to cutover runbook

---

## Part F: Monitoring & Alerting (TVF-142)

### Resource Monitors

Recreate resource monitors from A in B via SnowDDL or admin scripts. Define credit limits per warehouse family:
- DE_ETL warehouses
- DE_ANALYTICS warehouses
- REPLICATION_REFRESH warehouse (new for B, credit-alert it separately)
- Snowpark procedure warehouses
- Forecast API warehouse

### Alerts

Recreate in B:
- Snowflake task-failure alerts
- Streams-to-lambda-style monitoring used in A
- Credit alerts per warehouse family
- Credit alert for replication refresh warehouse (new cost line item specific to B)

### External Monitoring

Re-target any external integrations at Account B:
- Datadog Snowflake integration (future: aligns with team's Datadog migration plan)
- Grafana dashboards
- New Relic (if used)

### Ownership & Escalation

Document in the runbook:
- Alert name → owner mapping
- Response procedures per alert type
- Escalation path per severity

### Part F Exit Criteria

- [ ] All monitoring in A has an equivalent configured in B
- [ ] Test alerts fire successfully in B
- [ ] Alert ownership and response procedures documented
- [ ] Credit alerts cover the replication refresh warehouse

---

## Phase 2 Services Migration Overall Exit Criteria

- [ ] All Parts A-F exit criteria met
- [ ] Migration tracker shows all services as "Migrated" or "Validated"
- [ ] Every service runs end-to-end against Account B in staging
- [ ] All KPA keys rotated and stored in Azure Key Vault
- [ ] Ready for Rehearsal #2 (see `validation.md`)
