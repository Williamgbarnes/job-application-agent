# Scheduled Task Rules

This repository mirrors the operating rules of the existing scheduled-task workflow without committing private task names, task prompts, tracker data, credentials, contacts, application details, or generated materials.

## Source-of-truth boundary

The existing ChatGPT scheduled tasks and private workflows remain the production/source-of-truth system until an explicit cutover is approved. The public app may model, test, and report rule alignment, but it must not become the production scheduler by accident.

## Required behavior

Future scheduled-task implementation must satisfy these rules before cutover:

- Use sanitized mock fixtures in the public repository.
- Keep real tracker exports, resumes, generated packages, contacts, notes, IDs, and credentials outside the repository.
- Default to read-only and dry-run behavior.
- Treat local staging as a manually exported Excel workflow unless a later phase explicitly changes that boundary.
- Avoid Google API usage for the current local staging phase.
- Do not apply, submit, contact, email, message, upload, or mutate external systems autonomously.
- Require explicit human approval before any external write, application submission, recruiter contact, generated-material upload, or production tracker mutation.
- Do not print private paths, IDs, row values, company names, job titles, URLs, contacts, notes, credentials, resumes, or generated application materials in CLI output or logs.
- Use condition-watch behavior only for meaningful changes: notify when the watched condition is met, and stay quiet when there is no meaningful change.
- Enforce a minimum scheduled polling interval of 60 minutes unless a later, reviewed runtime explicitly supports a stricter safe limit.

## Current encoded contract

The sanitized rule contract lives in `job_application_agent.scheduled_task_rules` and is surfaced by `phase-three-status` under `scheduled_task_rules`.

The current public-safe status command can verify the rule envelope:

```bash
job-agent phase-three-status --env-file .env
```

The command reports booleans and aggregate safety metadata only. It must not disclose private scheduled-task payloads or production workflow data.

## Cutover criteria

Before the public app replaces any existing private scheduled workflow, it must have:

- explicit runtime mode selection;
- dry-run behavior enabled by default;
- log-safe outputs;
- human approval gates;
- auditability for proposed actions;
- rollback or no-write behavior for failed or rejected actions;
- tests proving that disabled approval gates or enabled external writes fail the scheduled-task alignment check.
