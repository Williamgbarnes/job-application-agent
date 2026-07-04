# Phase 2 Mock Queue

The Phase 2 mock queue shows how sanitized mock job scores can be organized for human review.

It uses public fixtures only and does not read private tracker exports, `.env`, resumes, generated materials, credentials, or production systems.

## Command

```bash
job-agent mock-queue
```

By default, the command reads:

```text
examples/mock_jobs.json
```

To use another sanitized fixture:

```bash
job-agent mock-queue --fixture examples/mock_jobs.json
```

## Local filters

The command can narrow the displayed mock items by score or priority:

```bash
job-agent mock-queue --min-score 75
job-agent mock-queue --priority high
job-agent mock-queue --priority high --priority medium
```

Filtered output is re-ranked from `1` so the JSON remains easy to read.

## Output

The command prints JSON with:

- queue item rank
- mock job ID
- mock company and title
- score
- priority
- review bucket
- rationale
- selected filters

Review buckets are intentionally limited to:

| Priority | Bucket |
| --- | --- |
| `high` | `review_now` |
| `medium` | `review_later` |
| `low` | `hold` |

## Safety constraints

- No external API calls.
- No writes.
- No submissions.
- No contacting or messaging.
- No private tracker rows.
- No private paths, IDs, or credentials.
- Sanitized mock fixtures only.

## Local checks

```bash
py -m pytest tests/test_review_queue.py -q
py -m pytest
job-agent mock-queue
job-agent mock-queue --min-score 75 --priority high
```
