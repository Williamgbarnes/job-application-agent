# Agent Instructions

This repository is a public portfolio project. Treat it as code that may be reviewed by recruiters, hiring managers, and engineering leaders.

## Non-negotiable safety rules

- Do not commit secrets, tokens, cookies, OAuth credentials, API keys, private keys, or service account files.
- Do not commit real resumes, cover letters, job applications, contact lists, recruiter messages, private tracker data, or production spreadsheet IDs.
- Use mock data and sanitized examples only.
- Do not implement unattended job submission.
- Do not bypass website terms of service, CAPTCHAs, rate limits, login restrictions, or anti-automation controls.
- Keep all production integrations behind explicit configuration and human approval gates.
- Never fabricate resume claims, credentials, employment history, compensation, certifications, or application outcomes.

## Codex operating mode

Codex may help with public repository code, tests, documentation, refactors, and sanitized mock workflows.

Codex must not:

- read or request `.env` contents;
- read files under `data/private/`;
- use real tracker exports, resumes, contacts, application materials, or private notes;
- add Google Sheet IDs, Google Drive IDs, API keys, OAuth tokens, cookies, or service account files;
- send email, messages, applications, form submissions, or external write requests;
- add production integrations without explicit configuration gates and human approval.

## GitHub Free plan constraints

Design repository automation and implementation choices to work on GitHub Free without paid infrastructure assumptions.

Allowed assumptions:

- Unlimited public and private repositories.
- Unlimited collaborators.
- Community support only.

Budgeted limits to protect:

- GitHub Actions: 2,000 minutes per month.
- GitHub Packages: 500 MB storage.
- Codespaces compute: 120 core-hours per developer.
- Codespaces storage: 15 GB per developer.

Implementation rules:

- Keep CI small, deterministic, and mock-only; prefer one Linux test job over large matrices.
- Do not add scheduled, polling, long-running, or deployment workflows unless explicitly approved.
- Give every workflow job a practical timeout and cancel superseded runs with concurrency controls.
- Do not require paid runners, larger runners, GPU runners, self-hosted runners, or Team/Enterprise-only controls.
- Do not make GitHub Packages, container registries, release artifacts, or large workflow artifacts part of the default path.
- Avoid committed generated assets, dependency caches, model files, browser binaries, private exports, or bulky test fixtures that pressure repository, package, artifact, or Codespaces storage.
- Keep Codespaces optional; local Git Bash development must remain the primary documented path.
- Prefer local commands, small fixtures, and unit tests over cloud services for public validation.
- Any workflow that could consume meaningful monthly minutes, package storage, or Codespaces compute needs an explicit note in the PR explaining why it fits the Free plan.

## Standard local commands

Use Git Bash commands by default.

Install the package and development dependencies:

```bash
py -m pip install -e ".[dev]"
```

Run the full test suite:

```bash
py -m pytest
```

Run public demo commands:

```bash
job-agent mock-score
job-agent mock-queue
job-agent mock-queue --min-score 75 --priority high
```

Run local staging checks only when a private `.env` exists locally and the user explicitly asks for staging verification:

```bash
job-agent sheets-metadata --env-file .env
job-agent tracker-headers --env-file .env
job-agent tracker-schema --env-file .env
job-agent tracker-quality --env-file .env
```

These staging commands must not print private paths, IDs, row values, company names, job titles, notes, URLs, contacts, or generated materials.

## Engineering expectations

- Prefer small, testable modules over monolithic scripts.
- Make business rules explicit and covered by tests.
- Separate domain logic from I/O integrations.
- Store external job postings as snapshots before scoring.
- Log decisions with enough context for audit and debugging.
- Keep examples runnable without private credentials.
- Use small pull requests with tests and documentation.

## Public portfolio goal

The project should demonstrate:

- Workflow automation architecture.
- Rules-based job scoring.
- LLM-assisted document generation with guardrails.
- Human-in-the-loop review.
- Secure handling of private data.
- Clean documentation, tests, and maintainable design.
