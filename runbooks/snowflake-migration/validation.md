# Phase 2: Data Parity Validation & Rehearsals

Build automated parity checks and execute two rehearsal runs before cutover. Ticket: [TVF-141](https://enpal.atlassian.net/browse/TVF-141).

## Part A: Parity-Check Script

### Requirements

A script that compares Account A vs Account B for every in-scope table and produces a structured diff report.

### Checks to Run

**1. Row Count**
```sql
-- Run on both accounts
SELECT COUNT(*) AS row_count
FROM <database>.<schema>.<table>;
```
Compare: exact match OR within documented tolerance.

**2. Hash-Based Content Diff**
Use `HASH_AGG` or equivalent on a rolling recent window (e.g., last 7 days):

```sql
-- Hash recent rows — same window on both accounts
SELECT HASH_AGG(*) AS content_hash
FROM <database>.<schema>.<table>
WHERE <date_column> >= DATEADD(day, -7, CURRENT_DATE);
```
Compare: hashes match exactly.

Alternative for tables without a date column:
```sql
SELECT
    COUNT(*) AS row_count,
    SUM(HASH(*)) AS row_hash_sum
FROM <database>.<schema>.<table>;
```

**3. Schema Diff**
```sql
-- Compare column definitions
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns
WHERE table_catalog = '<db>'
  AND table_schema = '<schema>'
  AND table_name = '<table>'
ORDER BY ordinal_position;
```
Compare: column types, order, nullability match.

### Script Location

- Check the script into a suitable repo (e.g., `vpp-data-warehouse/tools/parity_check/` or a new `dcm_mvp/tools/` directory)
- Parameterize: takes a list of tables (or schema patterns) to check
- Outputs: structured report (CSV/JSON) + pass/fail summary
- Automate via Airflow DAG or scheduled Azure DevOps pipeline

### Tolerance Documentation

Some tables may legitimately have small diffs during the parallel window (e.g., late-arriving data, rounding in aggregations). Document tolerance per table in the migration tracker:

| Table | Row Count Tolerance | Hash Tolerance | Notes |
|-------|---------------------|----------------|-------|
| feature_store.feature_a | 0 (exact) | exact | Deterministic ETL |
| forecasts.daily_forecast | ±5 rows | within tolerance | Late arrivals |

### Part A Exit Criteria

- [ ] Parity-check script committed to repo
- [ ] Script automated via Airflow or Azure DevOps schedule
- [ ] Tolerance per table documented
- [ ] Parity check runs daily during Phase 2
- [ ] Dashboard or notification for parity failures

---

## Part B: Rehearsal #1 — Narrow Scope

Purpose: validate the mechanics of pointing a DAG at B and prove the parity check detects real issues.

### Steps

1. **Pick 1-2 low-risk DAGs** from `vpp-airflow` to flip
2. **Set up a scratch DB in B** (not production) for the rehearsal run
3. **Point the chosen DAGs at the scratch DB** in B (via connection override or duplicated DAG)
4. **Run the DAGs for a full day**
5. **Diff results against A** using the parity-check script
6. **Document findings** — every mismatch is either a real bug or a tolerance case
7. **Fix issues found** before proceeding to Rehearsal #2

### Exit Criteria

- [ ] 1-2 DAGs ran successfully against B for a full day
- [ ] Parity check diffs documented with resolutions
- [ ] Any real bugs fixed and re-verified
- [ ] Team sign-off to proceed to Rehearsal #2

---

## Part C: Rehearsal #2 — Broader Scope (Cutover Dry-Run)

Purpose: full dry-run of the cutover runbook. Validate that the cutover sequence works end-to-end and that all services land correctly on B.

### Steps

1. **Broaden scope** — all critical DAGs, Snowpark sprocs, Streamlit apps
2. **Execute the cutover runbook** (see `cutover.md`) in full, against a rehearsal timeline
3. **Exercise the promote command** — `ALTER DATABASE <db> PRIMARY;` on the replica
4. **Run smoke tests** — every critical service must pass
5. **Document**:
   - Timings per step (how long did freeze + final refresh + promote actually take?)
   - Issues encountered
   - Runbook gaps (missing steps, unclear instructions)
6. **Update cutover runbook** to address gaps found

### Exit Criteria

- [ ] Full cutover runbook executed end-to-end
- [ ] All smoke tests passed on B
- [ ] Rehearsal timings documented (basis for actual cutover window estimate)
- [ ] All runbook gaps addressed
- [ ] Rehearsal #2 sign-off by DS tech lead + Platform/Cloud owner

---

## Cutover Go/No-Go Decision

After Rehearsal #2:

**Go if:**
- All parity checks passing within tolerance
- All smoke tests passed during Rehearsal #2
- Rollback procedure validated
- All stakeholders signed off (DS tech lead, Platform/Cloud owner, BI for shares)

**No-go if:**
- Unresolved parity failures
- Rehearsal #2 surfaced critical issues not yet fixed
- Any key stakeholder has not signed off
- Rollback procedure not validated

Decision logged in [TVF-7](https://enpal.atlassian.net/browse/TVF-7) with supporting evidence.

## Phase 2 Validation Overall Exit Criteria

- [ ] Parity-check script deployed and running daily
- [ ] Rehearsal #1 complete with documented findings
- [ ] Rehearsal #2 complete; all findings addressed or explicitly accepted
- [ ] Go/no-go decision recorded
- [ ] Cutover scheduled if go
