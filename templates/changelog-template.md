# Changelog

All notable changes to this <!-- TODO: replace with project type, e.g. "framework", "service", "package" --> are recorded here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the repo
uses [CalVer](https://calver.org/) versioning (`YYYY.MM.DD`) — a version
represents "the state of <!-- TODO: replace with what is governed, e.g. "the API and runtime behavior" --> as of that date."

## How to Update

Every PR that introduces a user-facing change adds one or more bullets under
`[Unreleased]` before merge. The PR template has a checklist item as a
reminder, and CI fails PRs that don't touch `CHANGELOG.md`. Non-user-facing
PRs (typo fixes, pure internal refactors, CI-only tweaks) can opt out by
including `[skip-changelog]` in any commit message on the PR.

A maintainer cuts a dated release by renaming `[Unreleased]` to
`[YYYY.MM.DD]` when enough changes have accumulated. <!-- TODO: optionally describe automation, e.g. "A scheduled pipeline opens a release-cut PR daily Mon–Thu at 18:00 UTC." -->

**Sub-section conventions** (only include what applies to the release):

- **Added** — new features, capabilities, integrations, docs
- **Changed** — modified behavior, scope, or shape of existing things
- **Deprecated** — announced but not yet removed
- **Removed** — deletions
- **Fixed** — corrections to existing behavior or docs
- **Security** — security-relevant changes (auth, permissions, input validation, etc.)

---

## [Unreleased]
