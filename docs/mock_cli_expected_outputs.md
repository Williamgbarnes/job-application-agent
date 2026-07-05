# Mock CLI Expected Outputs

This guide summarizes the expected shape of each public mock CLI command.

## Commands

| Command | Output shape |
| --- | --- |
| `job-agent mock-score` | JSON scoring reports for the sanitized mock fixture. |
| `job-agent mock-queue` | JSON queue data sorted by score and priority. |
| `job-agent mock-dashboard` | JSON summary metrics and top ranked mock items. |
| `job-agent mock-dashboard-report` | Markdown summary report. |
| `job-agent mock-package-plan` | JSON checklist-style planning placeholders. |

## Filter examples

| Example | Purpose |
| --- | --- |
| `job-agent mock-queue --min-score 75` | Show higher-scoring mock items. |
| `job-agent mock-dashboard --priority high` | Show dashboard data for high-priority mock items. |
| `job-agent mock-package-plan --top-limit 2` | Limit the number of planning placeholders. |

## Fixture

All commands use `examples/mock_jobs.json` by default. Reviewers can pass `--fixture` to point at another sanitized mock fixture.

## Review notes

- Keep examples deterministic.
- Keep examples public-safe.
- Keep fixture records sanitized.
