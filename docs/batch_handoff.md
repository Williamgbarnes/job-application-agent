# Batch Handoff Notes

Use these notes when several small pull requests are ready for review.

## Review each pull request

For each pull request:

- read the title and summary;
- scan the changed files;
- confirm CI completed successfully;
- confirm PR Review completed successfully;
- merge only after the changed files match the stated scope.

## After merging a batch

From a local checkout, run:

```bash
bash scripts/sync-local.sh
bash scripts/check-local.sh
```

Then scan the changed docs and confirm the public demo path still reads clearly.

## Next work

Prefer another small branch for each follow-up. Keep branch names in the `phase-<phase-number>-<implementation-slug>` format.
