# Data Directory

This directory is intentionally public-safe.

Committed data should be limited to:

- Mock fixtures.
- Synthetic examples.
- Non-sensitive test inputs.

Do not commit:

- Real job trackers.
- Real resume or cover-letter files.
- Generated application materials.
- Real application history.
- Contact lists.
- Logs from private runs.
- Production exports.

Local ignored directories are reserved for private runtime use:

```text
data/private/
data/production/
```

Those directories are ignored by `.gitignore` and should remain local/private.
