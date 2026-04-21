# Pipeline Troubleshoot

**Agent:** Platform Engineering Agent

## Inputs
- Pipeline name or URL
- Build/run number (if specific failure)
- Error message or symptom

## Steps
1. Read the pipeline YAML definition
2. Check the failing build log for:
   - Which stage/step failed
   - Error message and exit code
   - Whether it's a flaky failure (check last N runs for the same step)
3. Common failure categories:
   - **Dependency issues:** Package version conflicts, missing dependencies
   - **Authentication:** Expired tokens, service principal issues, permission changes
   - **Resource:** Timeout, out of memory, disk space
   - **Code:** Test failures, lint errors, build errors
   - **Infrastructure:** Agent pool unavailable, network issues
4. Check if the failure correlates with a recent change (last commits on the branch)

## Output Format

### Pipeline: [Name] — Build #[N]

**Failed Stage:** [Stage name]
**Error:** [Key error message]

### Root Cause
[Analysis of what went wrong]

### Fix
[Specific steps to resolve]

### Prevention
[How to prevent this from recurring — guard, test, or monitoring suggestion]
