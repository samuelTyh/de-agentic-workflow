# Phase 3: Data Migration

Hybrid approach: export/import for large historical tables, re-ingest from source for everything else.

## Method 1: Export/Import (Large Historical Tables)

For tables classified as "export-import" in the inventory.

### Step 1: Create Stage on Account B

```sql
-- Create an internal stage on account B for receiving data
CREATE OR REPLACE STAGE <database>.<schema>.migration_stage
    FILE_FORMAT = (TYPE = PARQUET);
```

Or use an external stage (S3/Azure Blob/GCS) accessible from both accounts.

### Step 2: Unload from Account A

```sql
-- On account A: unload table to stage
COPY INTO @<database>.<schema>.migration_stage/<table_name>/
FROM <database>.<schema>.<table_name>
FILE_FORMAT = (TYPE = PARQUET)
HEADER = TRUE
OVERWRITE = TRUE
MAX_FILE_SIZE = 268435456;  -- 256 MB per file
```

For very large tables, partition the unload by date or key range:

```sql
COPY INTO @migration_stage/<table_name>/year=2024/
FROM (
    SELECT * FROM <table_name>
    WHERE created_date BETWEEN '2024-01-01' AND '2024-12-31'
)
FILE_FORMAT = (TYPE = PARQUET);
```

### Step 3: Transfer Stage Data

If using external stage — data is already accessible from both accounts.

If using internal stages — download from A, upload to B:

```bash
# Download from account A
snowsql -a $SNOWFLAKE_ACCOUNT -u $SNOWFLAKE_USER \
    -q "GET @<stage>/<table_name>/ file:///tmp/migration/<table_name>/"

# Upload to account B
snowsql -a $SNOWFLAKE_ACCOUNT_B -u $SNOWFLAKE_USER_B \
    -q "PUT file:///tmp/migration/<table_name>/* @<stage_b>/<table_name>/"
```

### Step 4: Load into Account B

```sql
-- On account B: load from stage into target table
COPY INTO <database>.<schema>.<table_name>
FROM @<database>.<schema>.migration_stage/<table_name>/
FILE_FORMAT = (TYPE = PARQUET)
MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
```

## Method 2: Re-Ingest from Source

For tables classified as "re-ingest" in the inventory.

### Step 1: Update Airflow Connections

Add account B connection in Astronomer:

```bash
astro run airflow connections add 'snowflake_account_b' \
    --conn-type 'snowflake' \
    --conn-host "$SNOWFLAKE_ACCOUNT_B" \
    --conn-login "$SNOWFLAKE_USER_B" \
    --conn-password "$SNOWFLAKE_PASSWORD_B" \
    --conn-schema 'PUBLIC' \
    --conn-extra '{"role": "'$SNOWFLAKE_ROLE_B'", "warehouse": "'$SNOWFLAKE_WAREHOUSE_B'"}'
```

### Step 2: Update or Duplicate DAGs

Two approaches:

**A) Duplicate DAGs (safer):** Copy existing DAGs, point to account B, run in parallel until validated.

**B) Update connection in existing DAGs:** Change the Snowflake connection ID. Simpler but no rollback path.

Recommendation: **A (duplicate)** during migration, then remove old DAGs after cutover.

### Step 3: Run Pipelines

1. Trigger the duplicated DAGs targeting account B
2. For historical data: run backfills (see `runbooks/pipeline-ops/backfill-operations.md`)
3. Monitor pipeline runs in Astronomer UI

## Tracking

Update the inventory tracking table as each table is migrated:

| Table | Method | Started | Completed | Validated |
|-------|--------|---------|-----------|-----------|
| | export-import / re-ingest | YYYY-MM-DD | YYYY-MM-DD | Yes/No |

## Checklist

- [ ] All "export-import" tables unloaded, transferred, and loaded
- [ ] All "re-ingest" pipelines running against account B
- [ ] Historical backfills completed for re-ingested tables
- [ ] Tracking table fully updated
