# Phase 0: DDL & RBAC Baseline + Storage Integrations

Apply the SnowDDL PROD baseline to Account B and recreate Azure storage integrations with updated IAM trust. Tickets: [TVF-136](https://enpal.atlassian.net/browse/TVF-136), [TVF-135](https://enpal.atlassian.net/browse/TVF-135).

## Part A: SnowDDL PROD Baseline (TVF-136)

First real `make apply-prod` of `dcm_mvp/snowddl_mvp` against Account B.

### Prerequisites

- `dcm_mvp/snowddl_mvp` CI/CD pipelines configured ([TVF-10](https://enpal.atlassian.net/browse/TVF-10) done)
- Database layout finalized ([TVF-13](https://enpal.atlassian.net/browse/TVF-13))
- Azure Key Vault available for service user keys
- Account B bootstrap user available (ACCOUNTADMIN role for initial apply)

### Step 1: Bootstrap Service Users

Per `snowddl_mvp/README.md`, register:

- `SNOWDDL` — the bot that runs `snowddl apply`
- `BOOTSTRAP_USER` — used only for initial bootstrap, then deprivileged
- `FALLBACK_ADMIN_USER` — break-glass admin for recovery scenarios

### Step 2: Generate and Store KPA Keys

Generate RSA key pairs for the bootstrap users. Store private keys in Azure Key Vault:

- `snowddl-user-key` — for `SNOWDDL` service user
- `snowddl-bootstrap-key` — for `BOOTSTRAP_USER`

Register public keys on the Snowflake users:

```sql
ALTER USER SNOWDDL SET RSA_PUBLIC_KEY='<public-key-pem-contents>';
ALTER USER BOOTSTRAP_USER SET RSA_PUBLIC_KEY='<public-key-pem-contents>';
```

### Step 3: Plan

```bash
cd dcm_mvp/snowddl_mvp
make plan-prod
```

Review the plan output carefully — this is the first apply, so expect a lot of object creation. Confirm:
- Warehouses match the approved DB layout
- Business roles + technical roles align with the Miro board design
- Service users have correct grants
- SCIM external grants are included

### Step 4: Apply

```bash
make apply-prod
```

This creates:
- Warehouses
- Business roles (e.g., `DE_DEVELOPER`, `DE_READER`, `DS_DEVELOPER`)
- Technical roles
- Service users with fresh KPA keys
- SCIM external grants

### Step 5: Apply External Grants

```bash
make apply-grants
```

### Step 6: Verify Idempotency

```bash
make plan-prod
```

Expected: zero diff. Any diff indicates non-deterministic config or hand-edits in B — investigate before proceeding.

### Step 7: Dev Environment

```bash
make plan-dev
make apply-dev
```

Verifies `DEV__` env-prefixed objects deploy cleanly.

### Part A Exit Criteria

- [ ] `make plan-prod` against B shows zero diff after first apply
- [ ] `make plan-dev` deploys `DEV__` objects cleanly
- [ ] External grants applied via `make apply-grants`
- [ ] SnowDDL Plan + Apply pipelines run green end-to-end on a real PR

---

## Part B: Azure Storage Integrations & IAM Trust (TVF-135)

Recreate storage integrations from A in B, with updated Azure trust policies.

### Prerequisites

- Part A complete (SnowDDL baseline applied — service users and roles exist)
- Cloud / IAM team engaged (file ticket on Day 1 of Phase 0 — long lead time)

### Step 1: Enumerate Source Storage Integrations

From account A:

```sql
SHOW STORAGE INTEGRATIONS;
```

Cross-reference with source repos:
- `vpp-data-warehouse/ingestion/storage_integrations/*`
- `vpp-data-warehouse/export/storage_integrations/*`

### Step 2: Create Integrations on Account B

Via SnowDDL (preferred, long-term):

Define integrations in `dcm_mvp/snowddl_mvp/prod_config/` and apply.

Via transitional DDL (acceptable during migration):

```sql
CREATE OR REPLACE STORAGE INTEGRATION <integration_name>
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'AZURE'
    ENABLED = TRUE
    AZURE_TENANT_ID = '<tenant-id>'
    STORAGE_ALLOWED_LOCATIONS = ('<azure://...>');
```

### Step 3: Get Account B's External ID

```sql
DESC STORAGE INTEGRATION <integration_name>;
```

Record `AZURE_MULTI_TENANT_APP_NAME` and `AZURE_CONSENT_URL` — these differ from A.

### Step 4: Coordinate with Cloud/IAM Team

Provide the Cloud team:
- New external ID / App Registration name for B
- List of storage containers that must trust the new ID

Cloud team actions (out of DE team's scope):
- Update Azure App Registration / Managed Identity
- Grant the new identity access to each storage container
- Confirm trust policy update per container

### Step 5: Create External Stages in B

```sql
CREATE OR REPLACE STAGE <database>.<schema>.<stage_name>
    STORAGE_INTEGRATION = <integration_name>
    URL = '<azure://...>'
    FILE_FORMAT = <file_format>;
```

### Step 6: Validate Read Path (Ingestion)

```sql
LIST @<database>.<schema>.<stage_name>;
```

Expected: returns file listing. If empty or errors → verify IAM trust and storage permissions with Cloud team.

### Step 7: Validate Write Path (Export)

Test export (e.g., Flexa `forecasts_sync`):

```sql
COPY INTO @<database>.<schema>.<stage_name>/test/
FROM (SELECT 1 AS test_col)
FILE_FORMAT = (TYPE = PARQUET)
OVERWRITE = TRUE;
```

Verify the file appears in the target storage container.

### Part B Exit Criteria

- [ ] Every storage integration in A has a working twin in B
- [ ] `LIST @stage` succeeds for every read path
- [ ] At least one write path (e.g., Flexa `forecasts_sync`) tested end-to-end from B
- [ ] List of integrations and B-side status added to migration tracker
