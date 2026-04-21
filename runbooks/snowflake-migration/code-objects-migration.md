# Phase 4: Code Objects Migration

Migrate stored procedures, UDFs, tasks, and streams to account B.

## Stored Procedures and UDFs

### Step 1: Extract Definitions from Account A

```sql
-- Get procedure definitions
SELECT
    procedure_name,
    procedure_schema,
    procedure_catalog,
    argument_signature,
    procedure_definition,
    procedure_language
FROM account_a.information_schema.procedures
WHERE procedure_schema NOT IN ('INFORMATION_SCHEMA');

-- Get UDF definitions
SELECT
    function_name,
    function_schema,
    function_catalog,
    argument_signature,
    function_definition,
    function_language
FROM account_a.information_schema.functions
WHERE function_schema NOT IN ('INFORMATION_SCHEMA')
  AND function_owner IS NOT NULL;
```

### Step 2: Review and Update

Before recreating on account B:

1. **Review each definition** — is the logic still correct? Any improvements?
2. **Update references** — database names, schema names, role references that differ on account B
3. **Update grants** — new RBAC model means different role names
4. **Snowpark procedures** — rebuild and upload .whl packages to account B stage (see `templates/pipeline-templates/snowflake-artifact-upload.yaml`)

### Step 3: Deploy to Account B

**Via snowDDL (if supported):**
Add procedure/UDF definitions to your snowDDL config.

**Via SQL scripts:**
```sql
CREATE OR REPLACE PROCEDURE <database>.<schema>.<proc_name>(...)
RETURNS ...
LANGUAGE ...
AS
$$
<procedure_definition>
$$;
```

**Via Snowpark:**
```sql
CREATE OR REPLACE PROCEDURE <database>.<schema>.<proc_name>(...)
RETURNS ...
LANGUAGE PYTHON
RUNTIME_VERSION = '3.12'
PACKAGES = ('snowflake-snowpark-python')
IMPORTS = ('@<stage>/<package>.whl')
HANDLER = '<module>.<function>';
```

## Tasks

### Step 1: Extract Task Definitions

```sql
SHOW TASKS IN ACCOUNT;
SELECT GET_DDL('TASK', '<database>.<schema>.<task_name>');
```

### Step 2: Recreate on Account B

Update object references (database, schema, warehouse, role) and create in dependency order (root tasks first):

```sql
-- Create but keep suspended
CREATE OR REPLACE TASK <database>.<schema>.<task_name>
    WAREHOUSE = '<account_b_warehouse>'
    SCHEDULE = '<schedule>'
AS
<task_sql>;

-- Do NOT resume until validation is complete
```

## Streams

Streams track changes on tables. They cannot be migrated — recreate on account B after base tables exist.

```sql
CREATE OR REPLACE STREAM <database>.<schema>.<stream_name>
ON TABLE <database>.<schema>.<table_name>
SHOW_INITIAL_ROWS = TRUE;  -- capture existing rows on first consumption
```

## Checklist

- [ ] All stored procedures extracted, reviewed, and deployed to account B
- [ ] All UDFs extracted, reviewed, and deployed to account B
- [ ] Snowpark packages rebuilt and uploaded to account B stages
- [ ] All tasks created (suspended) on account B
- [ ] All streams created on account B
- [ ] Grants applied to all code objects per new RBAC model
