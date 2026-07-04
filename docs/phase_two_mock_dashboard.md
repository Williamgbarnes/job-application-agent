# Phase 2 Mock Dashboard

The Phase 2 mock dashboard aggregates sanitized mock job scores into a recruiter-friendly public demo summary.

It uses public fixtures only and does not read private tracker exports, `.env`, resumes, generated materials, credentials, production Google Sheets, or production systems.

## Command

```bash
job-agent mock-dashboard
```

By default, the command reads:

```text
examples/mock_jobs.json
```

To use another sanitized fixture:

```bash
job-agent mock-dashboard --fixture examples/mock_jobs.json
```

## Local filters

The dashboard uses the same local filters as the mock review queue:

```bash
job-agent mock-dashboard --min-score 75
job-agent mock-dashboard --priority high
job-agent mock-dashboard --priority high --priority medium
```

The `--top-limit` flag controls how many ranked queue items appear in the dashboard preview:

```bash
job-agent mock-dashboard --top-limit 5
```

## Output

The command prints JSON with:

- selected filters
- total filtered mock lead count
- priority counts
- human-review recommendation counts
- score summary with min, max, and average score
- top ranked mock queue items with rationale

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
py -m pytest tests/test_mock_dashboard.py -q
py -m pytest
job-agent mock-dashboard
job-agent mock-dashboard --min-score 75 --priority high --top-limit 2
```
