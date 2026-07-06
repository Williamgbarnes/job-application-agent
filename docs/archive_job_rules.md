# Archive Job Rules

The archive job workflow recommends stale, duplicate, closed, or inactive leads for archive. It must not mutate production tracker data without human approval.

## Allowed inputs

- Aggregate tracker status counts.
- Sanitized mock tracker fixtures in the public repository.
- Age and stale-status thresholds.
- Closed or duplicate lead signals.

Real tracker row values, company names, job titles, URLs, contacts, notes, private archive history, and production tracker identifiers must stay outside the public repository.

## Required behavior

- Recommend archive candidates before any mutation.
- Explain archive reason categories without printing private row values.
- Preserve recoverability until a human approves the archive action.
- Emit only aggregate, log-safe archive summaries.
- Stay quiet when no leads meet archive criteria.
- Run no more frequently than the scheduled-task minimum polling interval.

## Allowed outputs before approval

- Archive recommendations.
- Stale lead counts.
- Duplicate lead counts.
- Human approval checklist.

## Approval required before

- Changing real tracker statuses.
- Moving real tracker rows.
- Deleting or hiding real tracker records.
- Mutating production archives.

## Prohibited actions

- Deleting production data autonomously.
- Printing company names or job titles.
- Printing URLs, contacts, or notes.
- Committing real archive exports.
