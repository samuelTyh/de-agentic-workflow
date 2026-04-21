# PR Review

**Agent:** Code Review Agent

## Inputs
- PR number or URL
- (Optional) Focus area: security, performance, correctness, style

## Steps
1. Read the PR diff and commit messages
2. Cross-reference the related Jira ticket for requirement context
3. Review for:
   - **Correctness:** Logic errors, edge cases, missing null checks
   - **Security:** Credential leaks, injection risks, excessive permissions
   - **Style:** Team conventions, naming, code organization
   - **Impact:** Blast radius, downstream dependencies, breaking changes
4. For domain-specific code, defer to the relevant agent:
   - Snowflake SQL → Snowflake SQL Agent checklist
   - Snowpark Python → Snowpark Dev Agent checklist
   - Airflow DAGs → General DE Agent checklist
   - Azure DevOps YAML → Platform Engineering Agent checklist
5. Check test coverage — are new/changed paths tested?

## Output Format

### PR Review: [PR Title]

**Verdict:** [Approve / Request Changes / Needs Discussion]

### Issues
| Severity | File:Line | Issue | Suggestion |
|----------|-----------|-------|------------|

### Positive Notes
- [What's done well — acknowledge good patterns]

### Test Coverage
[Assessment of whether changes are adequately tested]
