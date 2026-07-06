# Mock CLI Quickstart

This quickstart shows the public demo path for the local mock commands.

## Setup

```bash
py -m pip install -e ".[dev]"
```

## Run checks

```bash
py -m pytest
```

## Run mock commands

```bash
job-agent mock-score
job-agent mock-queue
job-agent mock-dashboard
job-agent mock-dashboard-report
job-agent mock-package-plan
job-agent mock-phase-two-summary
```

The commands use the sanitized fixture at `examples/mock_jobs.json` by default.

## Useful filters

```bash
job-agent mock-queue --min-score 75
job-agent mock-dashboard --priority high --top-limit 3
job-agent mock-package-plan --priority high --top-limit 2
job-agent mock-phase-two-summary --priority high --top-limit 2
```

## Phase 2 completion check

Use the final summary command to confirm the public mock workflow covers the Phase 2 reviewer path:

```bash
job-agent mock-phase-two-summary
```

## Public demo boundary

The mock CLI path is designed for portfolio review with sanitized fixtures. It does not require a local env file, private tracker exports, credentials, resumes, contacts, production identifiers, or external service access.
