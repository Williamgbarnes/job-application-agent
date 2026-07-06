# Phase 3 Local Staging Plan

Phase 3 introduces a read-only local staging readiness layer. The current source-of-truth workflow remains outside the public repository until an explicit cutover.

## Current operating model

- The staging tracker is a manually exported local Excel workbook.
- A private local env file points to that workbook with `STAGING_TRACKER_PATH`.
- The workbook must stay under ignored local paths such as `data/private/`.
- Direct Google Sheets API access is not required for this phase.
- Production automations and private workflows remain outside this repository.
- Existing scheduled tasks and private workflows remain the source of truth until explicit cutover.

## Phase 3 acceptance criteria

Phase 3 foundation work is acceptable when it can:

- read a local Excel staging tracker in read-only mode;
- report whether a local tracker path is configured without printing the path;
- report whether the workbook is readable without printing the workbook title;
- summarize selected tabs without printing row values;
- summarize schema completeness and required-field blank counts;
- summarize aggregate format warnings for mapped fields without printing values;
- return deterministic quality gate status;
- surface sanitized scheduled-task rule alignment;
- surface sanitized workflow-specific rule alignment;
- avoid Google API usage;
- avoid external writes, submissions, emails, messaging, or contact actions;
- keep human approval required before any external action.

## Commands

Use `tracker-summary` for aggregate tracker readiness:

```bash
job-agent tracker-summary --env-file .env
```

Use `phase-three-status` for the broader Phase 3 readiness envelope:

```bash
job-agent phase-three-status --env-file .env
```

Both commands support the same tab and quality-gate controls used by the existing tracker inspection commands:

```bash
job-agent phase-three-status --env-file .env --tab Applications --max-records 1000
job-agent tracker-summary --env-file .env --tab Applications --strict
```

## Aggregate quality checks

The local staging summary reports counts for:

- required canonical fields that are populated or blank;
- blank records skipped during scanning;
- unmapped header counts;
- mapped date, URL, email, score, and status fields with checked, blank, and invalid counts.

Format checks are intentionally aggregate-only. Invalid dates, URLs, emails, scores, and statuses are counted, but the command output does not include the cell values that failed validation.

## Output boundary

The Phase 3 status commands may print aggregate information such as configuration booleans, selected tab names, discovered tab names, scanned record counts, blank record counts, required canonical field names, populated counts, blank counts, mapped field names, format categories, invalid format counts, schema completeness booleans, quality gate names, scheduled-task rule booleans, workflow rule booleans, safe error codes, and safety flags.

The commands must not print private configuration contents, local file paths, workbook titles derived from private filenames, company names, role titles, URLs, contact details, notes, row values, tracker identifiers, spreadsheet identifiers, credentials, scheduled-task names, scheduled-task prompts, resumes, or generated application materials.

## Scheduled-task compatibility policy

The final app must preserve the same operating rules as the existing scheduled-task workflow:

- Current scheduled tasks and private workflows remain the production/source-of-truth system until explicit cutover.
- Scheduled work must be mock-first in the public repository and read-only-first in staging.
- Condition watches should notify only when the watched condition is met; no-op checks should stay quiet.
- Scheduled polling must not be more frequent than once per hour in the public-safe contract.
- Human approval is required before any external write, application submission, contact action, generated-material upload, or production tracker mutation.

See `docs/scheduled_task_rules.md` for the full public-safe contract.

## Workflow-specific rules

The daily job scan, archive job, and application prep workflows each have a public-safe contract that defines allowed inputs, allowed outputs, required controls, approval gates, prohibited actions, and no-op behavior.

- Daily job scan may recommend deduplicated and scored leads, but cannot write real tracker rows or submit applications before approval.
- Archive job may recommend stale, duplicate, closed, or inactive leads for archive, but cannot mutate production tracker records before approval.
- Application prep may prepare draft package plans and review checklists, but cannot upload, send, contact, submit, or write production updates before approval.

See these docs for the workflow-specific contracts:

- `docs/workflow_rule_contracts.md`
- `docs/daily_job_scan_rules.md`
- `docs/archive_job_rules.md`
- `docs/application_prep_rules.md`

## Read-only-first policy

Phase 3 is inspection-only. It does not add write adapters, status updates, application submissions, generated materials, emails, messages, contact actions, or production mutations.

Future write paths must be designed separately, remain disabled by default, and require explicit human approval before any external action.

## Local verification

Run the full public-safe check:

```bash
bash scripts/check-local.sh
```

Run focused tests:

```bash
python -m pytest tests/test_phase_three_status.py tests/test_tracker_quality.py tests/test_tracker_format_quality.py tests/test_scheduled_task_rules.py tests/test_workflow_rules.py -q
```
