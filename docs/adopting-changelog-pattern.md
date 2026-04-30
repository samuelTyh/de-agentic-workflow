# Adopting the CHANGELOG Pattern

A short guide for adding the CalVer CHANGELOG pattern to another team repo.

## When to adopt

Adopt this pattern when a repo is **CalVer-versioned** (versions are dates, not semantic). For SemVer-versioned packages or unversioned scratch repos, use a different model.

## What you get

- A `CHANGELOG.md` users can scan to learn what changed and when
- A PR template checklist that reminds authors to record their change
- A CI check that fails PRs which don't touch `CHANGELOG.md` (opt-out via `[skip-changelog]`)
- Optional: a scheduled pipeline that auto-opens release-cut PRs (see "Optional automation" below)

## Step 1: Add the CHANGELOG file

Copy `templates/changelog-template.md` from `agent-workflow-dev` into your repo as `CHANGELOG.md`.

Customize the placeholders:

- The first sentence — describe what kind of project this is ("framework", "service", "package", etc.)
- The CalVer rationale sentence — describe what the version represents in your repo's context

If the repo already has commit history worth preserving, **backfill** dated releases by reading `git log --reverse` and grouping commits by date. The team's reference example is the agent-workflow-dev `CHANGELOG.md`.

## Step 2: Add the CI check

Copy `templates/pipeline-templates/changelog-check.yaml` from `agent-workflow-dev` into your repo at the same path (`templates/pipeline-templates/changelog-check.yaml`) or another location of your choosing.

Reference it from your `azure-pipelines.yml`:

```yaml
stages:
  - stage: Lint
    jobs:
      - template: templates/pipeline-templates/changelog-check.yaml
        # Optional — defaults shown
        # parameters:
        #   changelogPath: CHANGELOG.md
        #   skipMarker: '[skip-changelog]'
```

The check runs on every PR. Branch protection should require this pipeline to pass before merge — configure that once per repo via the Azure DevOps branch policy UI.

## Step 3: Update the PR template

In your repo's PR template (typically `.azuredevops/pull_request_template.md` and/or `.github/pull_request_template.md`), add a checklist item:

```markdown
- [ ] `CHANGELOG.md` updated under `[Unreleased]` if the change is user-facing
```

This is a reminder, not enforcement — the CI check is what enforces it.

## Step 4 (optional): Automation

If you want releases cut without anyone remembering to do it manually, also adopt the scheduled release pipeline and the post-merge tagger.

### Scheduled release-cut

1. Copy `scripts/cut_release.py` from `agent-workflow-dev` into your repo
2. Copy `azure-pipelines-release.yml` from `agent-workflow-dev` into your repo, updating the `--repository` argument in the `az repos pr create` step to your repo's name
3. Register the pipeline in Azure DevOps UI (one-time admin step — point it at the YAML file)

The scheduled pipeline opens a release-cut PR; a maintainer reviews and merges per normal branch policy.

### Post-merge tagging

1. Copy `scripts/extract_release_notes.py` from `agent-workflow-dev` into your repo
2. Copy `azure-pipelines-tag-release.yml` from `agent-workflow-dev` into your repo (no per-repo edits required)
3. Register the pipeline in Azure DevOps UI (point it at the YAML file)

After a release-cut PR merges, the tagger creates an annotated tag `vYYYYMMDD` at the new `main` HEAD. Use the tags as rollback markers and as compact references for tracking. The tagger is a no-op for non-release commits, so it's safe to run on every push.

## Verifying the adoption

After steps 1–3:

1. Open a small test PR that intentionally does NOT touch `CHANGELOG.md` — the CI check should fail with a clear error message
2. Update the same PR to add a bullet under `[Unreleased]` — CI should pass
3. Try the opt-out: amend a commit message to include `[skip-changelog]` and remove the CHANGELOG change — CI should pass with a "skipping" log line

## Troubleshooting

**`fatal: could not read Password for ...`** — the consuming pipeline is missing `persistCredentials: true` on `checkout: self`. The template handles this internally; this error means the consumer is overriding the checkout step incorrectly.

**Check passes when it shouldn't** — the three-dot diff (`origin/$TARGET...HEAD`) reports only files the PR introduces. If the consumer has nested submodules or unusual checkout behavior, the diff may be empty. Verify with `git diff --name-only` locally against the same target.

**Branch policy doesn't gate the merge** — branch protection is configured per-repo in Azure DevOps. The CI check itself doesn't enforce — it only fails. Ensure the branch policy lists this pipeline as a required check.
