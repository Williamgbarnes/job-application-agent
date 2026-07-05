# Local Sync Checks

Use these checks after pulling merged changes into a local checkout.

## Sync

From Git Bash inside the repository:

```bash
bash scripts/sync-local.sh
```

The script should fast-forward `main` when the working tree is clean.

## Verify

Run the public-safe check script:

```bash
bash scripts/check-local.sh
```

This installs development dependencies into the repo-local virtual environment and runs lint, type checks, security checks, tests, and mock CLI smoke checks.

## Inspect docs

For Phase 2 demo work, skim the docs changed by the merged pull requests and confirm the public demo still has a clear path from setup to command review.

## If sync stops

If the sync script reports local changes, inspect them before continuing. Commit, stash, or discard local work intentionally before running the sync again.
