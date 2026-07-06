# Phase 3 Local Staging Plan

Phase 3 introduces a read-only local staging readiness layer. The current source-of-truth workflow remains outside the public repository until an explicit cutover.

## Current operating model

- The staging tracker is a manually exported local Excel workbook.
- A private local env file points to that workbook with `STAGING_TRACKER_PATH`.
- The workbook must stay under ignored local paths such as `data/private/`.
- Direct Google Sheets API access is not required for this phase.
- Production automations and private workflows remain outside this repository.

## Phase 3 acceptance criteria

Phase 3 foundation work is acceptable when it can:

- read a local Excel staging tracker in read-only mode;
- report whether a local tracker path is configured without printing the path;
- report whether the workbook is readable without printing the workbook title;
- summarize selected tabs without printing row values;
- summarize schema completeness and required-field blank counts;
- return deterministic quality gate status;
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

## Output boundary

The Phase 3 status commands may print aggregate information such as configuration booleans, selected tab names, discovered tab names, scanned record counts, blank record counts, required canonical field names, populated counts, blank counts, schema completeness booleans, quality gate names, safe error codes, and safety flags.

The commands must not print private configuration contents, local file paths, workbook titles derived from private filenames, company names, role titles, URLs, contact details, notes, row values, tracker identifiers, spreadsheet identifiers, credentials, resumes, or generated application materials.

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
python -m pytest tests/test_phase_three_status.py -q
```
