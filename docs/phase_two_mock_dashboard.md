# Phase 2 Mock Dashboard

The Phase 2 mock dashboard aggregates sanitized mock job scores into a recruiter-friendly public demo summary.

It uses public fixtures only and does not read private tracker exports, `.env`, resumes, generated materials, credentials, production Google Sheets, or production systems.

## Commands

Print dashboard JSON:

```bash
job-agent mock-dashboard
```

Print a static Markdown report:

```bash
job-agent mock-dashboard-report
```

By default, both commands read:

```text
examples/mock_jobs.json
```

To use another sanitized fixture:

```bash
job-agent mock-dashboard --fixture examples/mock_jobs.json
job-agent mock-dashboard-report --fixture examples/mock_jobs.json
```

## Local filters

The dashboard uses the same local filters as the mock review queue:

```bash
job-agent mock-dashboard --min-score 75
job-agent mock-dashboard --priority high
job-agent mock-dashboard --priority high --priority medium
```

The `--top-limit` flag controls how many ranked queue items appear in the dashboard preview or Markdown report:

```bash
job-agent mock-dashboard --top-limit 5
job-agent mock-dashboard-report --top-limit 5
```

## JSON output

`job-agent mock-dashboard` prints JSON with:

- selected filters
- total filtered mock lead count
- priority counts
- human-review recommendation counts
- score summary with min, max, and average score
- top ranked mock queue items with rationale

## Markdown report output

`job-agent mock-dashboard-report` prints a static Markdown report with:

- selected filters
- summary table
- priority-count table
- review-recommendation table
- top ranked mock queue item table
- explicit safety boundary

The Markdown report is intended for quick local demos, PR descriptions, and portfolio screenshots. It writes only to stdout, so redirecting it to a file remains an explicit local shell action:

```bash
job-agent mock-dashboard-report > mock-dashboard-report.md
```

The dashboard is intentionally aggregate-first. It is safe for a public portfolio because it reads sanitized fixtures and never prints local private paths, tracker rows, contacts, notes, credentials, or real application details.

## Safety constraints

- No external API calls.
- No writes.
- No submissions.
- No contacting or messaging.
- No private tracker rows.
- No private paths, IDs, credentials, resumes, or generated materials.
- Sanitized mock fixtures only.

## Local checks

```bash
py -m pytest tests/test_mock_dashboard.py tests/test_mock_dashboard_report.py -q
py -m pytest
job-agent mock-dashboard
job-agent mock-dashboard-report
job-agent mock-dashboard --min-score 75 --priority high --top-limit 2
job-agent mock-dashboard-report --min-score 75 --priority high --top-limit 2
```
