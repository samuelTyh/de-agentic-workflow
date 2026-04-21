# Phase 2: Data Migration

Schema-scoped replication for DS-owned data + inbound/outbound data shares. Tickets: [TVF-8](https://enpal.atlassian.net/browse/TVF-8), [TVF-9](https://enpal.atlassian.net/browse/TVF-9), [TVF-137](https://enpal.atlassian.net/browse/TVF-137), [TVF-138](https://enpal.atlassian.net/browse/TVF-138).

## Part A: Schema-Scoped Replication (TVF-137 / TVF-8)

Replicate DS-owned schemas from Account A to Account B as a read-only, auto-refreshing replica.

### In Scope Schemas

- `feature_store`
- `forecasts`
- `forecast_api`
- `model_registry`
- `energy_timeseries_cleaning`
- `analytics` (if applicable)

### Mechanism Options

Evaluate and choose one before starting:

| Option | Best For | Notes |
|--------|----------|-------|
| Full-DB replication with schema-scoped exclude list | Simpler setup, one replication relationship | Includes everything by default, maintained exclude list |
| Per-schema replication | Fine-grained control over refresh schedules per schema | More replication relationships to manage |
| Share-based bulk copy via CTAS | Smaller one-shot datasets | No auto-refresh — one-time copy only |

**Recommended:** Per-schema replication for core DS schemas; CTAS for small reference-like schemas if any.

### Step 1: Enable Replication on Source (Account A)

```sql
-- On Account A (ORGADMIN)
ALTER DATABASE <db_name> ENABLE REPLICATION TO ACCOUNTS <org_name>.<account_b_name>;
```

### Step 2: Create Replica on Account B

```sql
-- On Account B (ACCOUNTADMIN)
CREATE DATABASE <db_name>
    AS REPLICA OF <org_name>.<account_a_name>.<db_name>;
```

### Step 3: Configure Refresh Schedule

Create a task that refreshes the replica on a cadence acceptable for parity:

```sql
-- On Account B
CREATE OR REPLACE TASK REFRESH_<db_name>_TASK
    WAREHOUSE = REPLICATION_REFRESH_WH
    SCHEDULE = 'USING CRON 0 */4 * * * UTC'  -- every 4 hours, adjust per SLA
AS
    ALTER DATABASE <db_name> REFRESH;

ALTER TASK REFRESH_<db_name>_TASK RESUME;
```

### Step 4: Size the Refresh Warehouse

- Create a dedicated warehouse (e.g., `REPLICATION_REFRESH_WH`) via SnowDDL
- Start small (XS/S), increase if replication lag exceeds threshold
- Add a credit alert specific to this warehouse (new cost line item for B)

### Step 5: Monitor Replication Lag

```sql
-- Check replication status
SELECT *
FROM TABLE(INFORMATION_SCHEMA.DATABASE_REFRESH_HISTORY('<db_name>'))
ORDER BY START_TIME DESC
LIMIT 10;

-- Check lag
SHOW REPLICATION DATABASES;
```

Target: lag < agreed SLA (typically < 1 hour for DS workloads).

### Step 6: Document Promote/Failover Command

For cutover, the promote command:

```sql
-- On Account B (at cutover)
ALTER DATABASE <db_name> PRIMARY;
```

Dry-run this during Rehearsal #2 (see `validation.md`).

### Part A Exit Criteria

- [ ] B has read-only, auto-refreshing copies of all in-scope schemas
- [ ] Row-count parity passes for every table (tolerance documented in tracker)
- [ ] Refresh warehouse sized and monitored with credit alert
- [ ] Promote command documented and dry-run'd during rehearsal

---

## Part B: Inbound Data Shares (TVF-9)

Set up inbound shares into Account B for everything that stays in A or comes from external providers.

### Inbound Share #1: Main BI Snowflake — `ENPAL_COMPUTE_PROD_SHARE`

**Contact:** Alex Sutcliffe (BI Senior Analytics Engineer)

**Steps:**
1. Coordinate with BI to activate a new inbound share targeting Account B's locator
2. Create database from the share on Account B:
   ```sql
   CREATE DATABASE ENPAL_COMPUTE_PROD FROM SHARE <bi_account>.ENPAL_COMPUTE_PROD_SHARE;
   ```
3. Grant usage to appropriate business roles
4. Validate reads from B using the target business role

### Inbound Share #2: Legacy VPP DB (time-series IoT)

**Stays in Account A permanently.** Shared into B so DS pipelines can read without migration.

**Objects shared:**
- `raw/*`
- `processed.V2_*`
- `master_data_*`
- `DAM`

**Steps:**
1. On Account A: create a SHARE containing these objects
   ```sql
   CREATE SHARE VPP_LEGACY_SHARE;
   GRANT USAGE ON DATABASE <legacy_db> TO SHARE VPP_LEGACY_SHARE;
   GRANT USAGE ON SCHEMA <legacy_db>.raw TO SHARE VPP_LEGACY_SHARE;
   GRANT SELECT ON ALL TABLES IN SCHEMA <legacy_db>.raw TO SHARE VPP_LEGACY_SHARE;
   -- repeat for processed, master_data, DAM
   ALTER SHARE VPP_LEGACY_SHARE ADD ACCOUNTS = <account_b>;
   ```
2. On Account B: create database from share
   ```sql
   CREATE DATABASE VPP_LEGACY FROM SHARE <account_a>.VPP_LEGACY_SHARE;
   ```
3. Grant usage to business roles that need read access

### Inbound Share #3: Meteomatics (weather data)

**External provider.**

**Steps:**
1. Reach out to Meteomatics with Account B's locator
2. Request they re-share their weather data to B
3. Accept the share on B and create database from it
4. Validate queries return expected weather data

### Part B Exit Criteria

- [ ] Every listed inbound share is visible and queryable from B using the target business role
- [ ] Validation queries return expected row counts for each share
- [ ] Share access documented in the migration tracker

---

## Part C: Outbound Data Shares (TVF-138)

Recreate outbound shares from Account B to external consumers.

### Consumers to Coordinate With

- **Flexa** — currently consumes via `export/storage_integrations/flexa` blob sync. Decision: keep blob export from B, or switch to a Snowflake share? Confirm with Flexa stakeholder.
- **Main BI Snowflake** — if DS publishes forecasts/KPIs back to BI, coordinate with BI team on direction.
- **Others** — enumerate from the migration tracker.

### Steps Per Consumer

1. Provide consumer with Account B's account locator
2. On Account B: create the outbound share
   ```sql
   CREATE SHARE <consumer>_SHARE;
   GRANT USAGE ON DATABASE <db> TO SHARE <consumer>_SHARE;
   GRANT USAGE ON SCHEMA <db>.<schema> TO SHARE <consumer>_SHARE;
   GRANT SELECT ON <specific_tables_or_views> TO SHARE <consumer>_SHARE;
   ALTER SHARE <consumer>_SHARE ADD ACCOUNTS = <consumer_account>;
   ```
3. Have the consumer validate SELECT from the share
4. Run a parallel-read window: consumer accepts B share while still consuming A share, compares results

### Flexa Specific Validation

Flexa currently receives data via blob export (`export/storage_integrations/flexa/forecasts_sync`). Validate the blob export still runs end-to-end from B after storage integrations are recreated ([TVF-135](https://enpal.atlassian.net/browse/TVF-135)).

### Part C Exit Criteria

- [ ] Every downstream consumer has accepted the B-side share (or confirmed blob export from B works)
- [ ] Parallel-read window complete — consumer validates B reads match A reads
- [ ] Flexa export validated end-to-end from B
- [ ] Outbound share relationships documented in the migration tracker

---

## Phase 2 Data Migration Overall Exit Criteria

- [ ] All Phase 2 Part A, B, C exit criteria met
- [ ] Migration tracker shows all data dependencies as "Migrated" or "Validated"
- [ ] Replication lag within SLA
- [ ] Daily parity check passing (see `validation.md`)
