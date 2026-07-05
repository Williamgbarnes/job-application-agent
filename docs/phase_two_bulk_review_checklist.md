# Phase 2 Bulk Review Checklist

Use this checklist when reviewing several Phase 2 pull requests together.

## Before reviewing

- Confirm each pull request uses a `phase-<phase-number>-<implementation-slug>` branch name.
- Confirm each pull request has a focused title and summary.
- Confirm each pull request is small enough to understand from the changed files.

## Checks

For each pull request, confirm:

- `CI` completed successfully.
- `PR Review` completed successfully.
- The changed files match the pull request summary.
- Documentation examples use sanitized mock fixture paths.
- No private workflow data appears in file contents or examples.

## Merge order

When possible, merge low-conflict documentation-only pull requests first.

For pull requests that touch the same file, merge one at a time and re-check the next branch before merging.

## After merging

- Sync a local checkout from `main`.
- Run `bash scripts/check-local.sh` from Git Bash.
- Read any changed docs that are part of the public demo flow.
