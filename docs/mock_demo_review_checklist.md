# Mock Demo Review Checklist

Use this checklist when reviewing the public mock demo path.

## Before running commands

- Confirm the checkout is on the intended branch.
- Confirm Python 3.11 or newer is available.
- Confirm no local env file is required for the mock CLI path.
- Confirm the demo uses `examples/mock_jobs.json`.

## Commands to review

```bash
py -m pytest
job-agent mock-score
job-agent mock-queue
job-agent mock-dashboard
job-agent mock-dashboard-report
job-agent mock-package-plan
```

## Expected behavior

- Commands complete without external service access.
- Output is based on sanitized mock records.
- CLI output avoids local private paths and production identifiers.
- Any ranked or summarized output remains deterministic for the fixture.

## Review notes

- Treat failing tests as a blocker before merging.
- Prefer small follow-up PRs for code changes.
- Keep future examples sanitized and deterministic.
