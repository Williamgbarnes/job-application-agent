# Daily Job Scan Rules

The daily job scan workflow finds candidate leads, deduplicates them, scores them, and queues review items. It must remain recommendation-only until a human approves any real tracker or external-system change.

## Allowed inputs

- Approved source adapter configuration.
- Sanitized mock job fixtures in the public repository.
- Aggregate tracker state for deduplication.
- Public scoring rules.

Real source credentials, source account identifiers, tracker row values, company names, job titles, contacts, URLs, notes, and private lead history must stay outside the public repository.

## Required behavior

- Deduplicate leads before queueing them for review.
- Preserve source attribution without committing private source IDs.
- Score leads before any application-prep workflow can use them.
- Emit only aggregate, log-safe scan summaries.
- Stay quiet when no meaningful new leads are found.
- Run no more frequently than the scheduled-task minimum polling interval.

## Allowed outputs before approval

- New-lead recommendations.
- Deduplication summaries.
- Score summaries.
- Human review queue entries.

## Approval required before

- Writing real tracker lead rows.
- Saving production source identifiers.
- Using paid or authenticated sourcing APIs.
- Promoting scan results into a production workflow.

## Prohibited actions

- Submitting applications.
- Contacting recruiters or hiring teams.
- Printing private tracker values.
- Committing real job-search data.
