# Workflow Rule Contracts

The workflow rule contracts define what the daily job scan, archive job, and application prep workflows may do before any scheduler implementation exists. They extend the global scheduled-task contract with workflow-specific controls.

## Contract location

The executable public-safe contract lives in `job_application_agent.workflow_rules`.

The contract exposes:

- `daily_job_scan`
- `archive_job`
- `application_prep`

Each workflow defines allowed inputs, allowed outputs, required controls, approval gates, prohibited actions, and no-op behavior.

## Shared rules

Every workflow must remain:

- mock-first in the public repository;
- read-only-first in staging;
- human-gated before real mutations;
- external-write-disabled by default;
- log-safe;
- quiet when no meaningful condition is met;
- no more frequent than the scheduled-task minimum polling interval.

## Workflow docs

- `docs/daily_job_scan_rules.md`
- `docs/archive_job_rules.md`
- `docs/application_prep_rules.md`

## Implementation boundary

This PR-level contract does not implement a scheduler, source crawler, archive writer, document generator, email sender, uploader, or production tracker writer. Future workflow commands must call or mirror this contract before they run against real private data.
