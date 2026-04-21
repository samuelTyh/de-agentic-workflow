# Phase 5: Validation

Verify account B matches account A for all migrated objects.

## Object Count Validation

Run on each account and compare:

```sql
-- Tables
SELECT COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema NOT IN ('INFORMATION_SCHEMA');

-- Views
SELECT COUNT(*) AS view_count
FROM information_schema.views
WHERE table_schema NOT IN ('INFORMATION_SCHEMA');

-- Procedures
SELECT COUNT(*) FROM information_schema.procedures
WHERE procedure_schema NOT IN ('INFORMATION_SCHEMA');

-- Functions (UDFs)
SELECT COUNT(*) FROM information_schema.functions
WHERE function_schema NOT IN ('INFORMATION_SCHEMA')
  AND function_owner IS NOT NULL;
```

## Row Count Validation

```sql
SELECT
    table_catalog,
    table_schema,
    table_name,
    row_count
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY table_catalog, table_schema, table_name;
```

## Schema Comparison

```sql
SELECT
    table_catalog,
    table_schema,
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns
WHERE table_schema NOT IN ('INFORMATION_SCHEMA')
ORDER BY table_catalog, table_schema, table_name, ordinal_position;
```

## Data Integrity Spot Checks

For critical tables, go beyond row counts:

```sql
SELECT
    COUNT(*) AS row_count,
    SUM(HASH(*)) AS row_hash,
    MIN(<date_column>) AS min_date,
    MAX(<date_column>) AS max_date
FROM <database>.<schema>.<table_name>;
```

Run on both accounts and compare `row_count` and `row_hash`.

## Procedure and UDF Validation

```sql
-- Verify procedure runs
CALL <database>.<schema>.<proc_name>(<test_args>);

-- Verify UDF returns expected result
SELECT <database>.<schema>.<udf_name>(<test_args>);
```

## Task Validation

```sql
-- Verify tasks exist and are configured (still suspended)
SHOW TASKS IN ACCOUNT;
SELECT GET_DDL('TASK', '<database>.<schema>.<task_name>');
```

## Stream Validation

```sql
SHOW STREAMS IN ACCOUNT;
```

## Validation Checklist

- [ ] Object counts match between accounts (or differences are intentional)
- [ ] Row counts match for all export/import tables
- [ ] Row counts correct for re-ingested tables (may differ if source data changed)
- [ ] Schema definitions match for all tables
- [ ] Spot-check hashes match for critical tables
- [ ] All procedures and UDFs execute successfully on account B
- [ ] All tasks exist (suspended) on account B
- [ ] All streams exist and point to correct tables
- [ ] RBAC grants verified — users can access objects per new role model
- [ ] Jira tickets updated with validation results
