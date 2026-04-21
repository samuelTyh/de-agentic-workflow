# Templates — Design Spec

## Overview

Populate the three template directories with practical, team-ready templates.

## Jira Ticket Templates (4)

Markdown files in `templates/jira-ticket-templates/`. Structured fields the PMO agent uses when creating tickets.

- `story.md` — feature work
- `bug.md` — defect tracking
- `epic.md` — large initiative grouping
- `task.md` — smaller work items / sub-tasks

## Prompt Templates (7)

Markdown files in `templates/prompt-templates/`. Each defines the agent, inputs, steps, and output format for a common interaction.

- `sprint-summary.md` — PMO Agent: summarize current sprint
- `dag-review.md` — General DE Agent: review an Airflow DAG
- `sql-review.md` — Snowflake SQL Agent: review SQL for performance
- `migration-status.md` — Migration Agent: current state of Snowflake A→B
- `ml-context-digest.md` — DS/ML Liaison Agent: recent ML/DS changes
- `pr-review.md` — Code Review Agent: review a PR
- `pipeline-troubleshoot.md` — Platform Engineering Agent: debug a failing Azure DevOps pipeline

## Pipeline Templates (5)

Azure DevOps YAML in `templates/pipeline-templates/`. Parameterized stage templates.

- `ci-build-test.yaml` — lint, test, build on PR
- `cd-deploy.yaml` — deploy to dev/staging/prod with approval gates
- `python-package-build.yaml` — build and publish internal Python packages
- `snowflake-artifact-upload.yaml` — build and upload Snowpark Python packages (.whl)
- `git-change-detection-deploy.yaml` — detect modified paths, deploy only changed components (DAGs, SQL, Snowpark)

## Total: 16 template files
