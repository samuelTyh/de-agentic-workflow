# Azure DevOps Incidents

## Common Failure Scenarios

### Pipeline Failure — Build Stage

**Symptoms:** CI pipeline fails during lint, test, or build steps.

**Steps:**
1. Open the failed build in Azure DevOps → check which stage/step failed
2. Read the error log:
   - **Lint failure** → code style issue, fix in the PR
   - **Test failure** → failing test, check if it's a real regression or flaky test
   - **Build failure** → dependency issue, missing module, version conflict
3. If flaky test → check test history, mark as flaky if pattern is clear, fix the test
4. If dependency issue → check `pyproject.toml` / `requirements.txt` for version pins

### Pipeline Failure — Deploy Stage

**Symptoms:** Deployment to dev/staging/prod fails.

**Steps:**
1. Check which environment failed
2. Common causes:
   - **Authentication** → expired PAT or service principal, renew credentials
   - **Resource** → target environment unavailable, check Azure status
   - **Configuration** → environment variables missing or wrong
3. If prod deploy fails → do NOT retry blindly. Check what was partially deployed.
4. If rollback needed → use the previous successful deployment artifact

### Pipeline Stuck / Queuing

**Symptoms:** Pipeline runs queued indefinitely, no agent available.

**Steps:**
1. Check agent pool status in Azure DevOps → Organization Settings → Agent Pools
2. If all agents busy → wait or cancel lower-priority runs
3. If agent is offline → check the agent machine, restart agent service
4. If using Microsoft-hosted agents → check Azure DevOps status page for capacity issues

### Deployment Gate Timeout

**Symptoms:** Pipeline waiting for approval that never comes.

**Steps:**
1. Check who the approver is in the environment settings
2. Notify the approver via Teams
3. If approver is unavailable → check if there's an alternate approver configured
4. If urgent (P1) → escalate to team lead for emergency approval

## Recovery Checklist

After resolving any Azure DevOps incident:
- [ ] Root cause identified and fixed
- [ ] Pipeline re-run successfully
- [ ] Deployed artifacts verified in target environment
- [ ] Teams thread updated with resolution
- [ ] Postmortem created if P1 or P2
