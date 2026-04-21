# Phase 1: Object Inventory

Catalog all objects on account A to determine migration scope.

## Step 1: Database and Schema Inventory

```sql
-- List all databases
SHOW DATABASES;

-- List all schemas in each database
SHOW SCHEMAS IN DATABASE <database_name>;
```

## Step 2: Table Inventory

```sql
SELECT
    table_catalog AS database_name,
    table_schema,
    table_name,
    table_type,
    row_count,
    bytes,
    ROUND(bytes / 1024 / 1024 / 1024, 2) AS size_gb,
    created,
    last_altered
FROM account_a.information_schema.tables
WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY bytes DESC;
```

## Step 3: View Inventory

```sql
SELECT
    table_catalog AS database_name,
    table_schema,
    table_name,
    view_definition,
    is_secure
FROM account_a.information_schema.views
WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY table_catalog, table_schema, table_name;
```

## Step 4: Stored Procedures and UDFs

```sql
SHOW PROCEDURES IN ACCOUNT;
SHOW USER FUNCTIONS IN ACCOUNT;
```

## Step 5: Tasks and Streams

```sql
SHOW TASKS IN ACCOUNT;
SHOW STREAMS IN ACCOUNT;
```

## Step 6: Stages, Pipes, and File Formats

```sql
SHOW STAGES IN ACCOUNT;
SHOW PIPES IN ACCOUNT;
SHOW FILE FORMATS IN ACCOUNT;
```

## Tracking Table

| Database | Schema | Object Type | Object Name | Rows | Size (GB) | Migration Method | Status |
|----------|--------|-------------|-------------|------|-----------|-----------------|--------|
| | | | | | | export-import / re-ingest / snowDDL | |

## Classification Rules

| Criteria | Migration Method |
|----------|-----------------|
| Table > 100 GB or historical data hard to re-ingest | Export/import |
| Table with active source pipeline | Re-ingest from source |
| Views, materialized views | Recreate via snowDDL after base tables exist |
| Procedures, UDFs | Migrate code (see Phase 4) |
| Tasks, streams | Recreate on account B (see Phase 4) |

## Output

- Completed tracking table with all objects classified
- Jira stories created for each migration batch (use `templates/jira-ticket-templates/story.md`)
