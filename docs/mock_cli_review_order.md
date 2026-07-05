# Mock CLI Review Order

Use this order when reviewing the public mock CLI demo.

## Recommended sequence

1. `job-agent mock-score`
2. `job-agent mock-queue`
3. `job-agent mock-dashboard`
4. `job-agent mock-dashboard-report`
5. `job-agent mock-package-plan`

## Why this order works

The sequence starts with individual scored records, then moves to ranking, summary metrics, Markdown output, and checklist placeholders.

This makes it easier to compare each command against the previous one and confirm that the public demo stays deterministic.

## Review notes

- Start with the default fixture.
- Add filters only after the default output is understood.
- Keep notes focused on command behavior and deterministic output.
