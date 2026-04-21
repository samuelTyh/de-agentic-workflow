# Connection Management

Managing Airflow connections, variables, and secrets on Astronomer.

## Connections

### Viewing Connections

- **UI:** Admin → Connections
- **CLI:** `astro run airflow connections list`

### Adding/Updating Connections

**Via Astronomer UI (preferred for manual changes):**
1. Admin → Connections → + (add) or edit existing
2. Fill in: Conn Id, Conn Type, Host, Schema, Login, Password, Port, Extra
3. Save

**Via CLI:**
```bash
astro run airflow connections add '<conn_id>' \
    --conn-type '<type>' \
    --conn-host '<host>' \
    --conn-login '<user>' \
    --conn-password '<pass>' \
    --conn-port <port> \
    --conn-schema '<schema>'
```

**Via environment variables (recommended for CI/CD):**
```bash
AIRFLOW_CONN_<CONN_ID>=<conn_type>://<user>:<pass>@<host>:<port>/<schema>
```

Set these in Astronomer's environment variables UI or deployment config.

### Key Connections

| Conn ID | Type | Used By |
|---------|------|---------|
| `snowflake_default` | Snowflake | Most data pipelines |
| `snowflake_account_b` | Snowflake | Migration pipelines (account B) |

## Variables

### Viewing Variables

- **UI:** Admin → Variables
- **CLI:** `astro run airflow variables list`

### Adding/Updating Variables

**Via UI:** Admin → Variables → + (add) or edit existing

**Via CLI:**
```bash
astro run airflow variables set '<key>' '<value>'
```

### Guidelines

- Use variables for values that change between environments (dev/staging/prod)
- Do NOT store secrets in variables — use connections or Astronomer's secret backend
- Prefix variables by domain: `snowflake__warehouse`, `pipeline__batch_size`

## Secrets

Astronomer supports secret backends (e.g., Azure Key Vault, HashiCorp Vault).

**Current setup:** Secrets stored in Airflow connections and Astronomer environment variables.

**Best practice:** Migrate to a secret backend when available to centralize credential management.

## Audit

When changing connections or variables:
1. Document the change in the Teams channel
2. If production connection → requires approval per security policy
3. Update any affected DAGs if connection ID changes
