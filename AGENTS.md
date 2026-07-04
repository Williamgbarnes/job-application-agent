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

## Engineering expectations

- Prefer small, testable modules over monolithic scripts.
- Make business rules explicit and covered by tests.
- Separate domain logic from I/O integrations.
- Store external job postings as snapshots before scoring.
- Log decisions with enough context for audit and debugging.
- Keep examples runnable without private credentials.

## Public portfolio goal

The project should demonstrate:

- Workflow automation architecture.
- Rules-based job scoring.
- LLM-assisted document generation with guardrails.
- Human-in-the-loop review.
- Secure handling of private data.
- Clean documentation, tests, and maintainable design.
