# Job Application Agent

A portfolio-safe job application copilot that demonstrates workflow automation, rules-based scoring, LLM-assisted document generation, and human-in-the-loop review.

This repository uses mock data and sanitized examples only. It does not contain private resume files, real job applications, personal job-search data, API keys, OAuth tokens, production Google Sheet IDs, or generated application materials.

## Project Goals

- Discover and normalize job leads from approved sources.
- Score roles using transparent, testable rules.
- Generate tailored application packages from approved source content.
- Keep humans in control before any application submission.
- Track application status, follow-ups, and outcomes.
- Demonstrate secure, production-minded architecture.

## Current Public Demo

The current public demo path uses sanitized mock fixtures only:

```bash
py -m pip install -e ".[dev]"
py -m pytest
job-agent mock-score
job-agent mock-queue
```

These commands read `examples/mock_jobs.json`, apply deterministic scoring rules, and print a mock review queue. They do not read private tracker exports, `.env`, resumes, credentials, or production systems.

Useful docs:

- `docs/scoring.md`
- `docs/phase_two_mock_queue.md`
- `docs/security_model.md`
- `docs/real_data_boundary.md`
- `docs/human_in_the_loop_policy.md`

## Local Staging Checks

For local-only staging work, keep real tracker exports under ignored paths such as `data/private/` and point `.env` at the local file.

Useful commands:

```bash
job-agent sheets-metadata --env-file .env
job-agent tracker-headers --env-file .env
job-agent tracker-schema --env-file .env
job-agent tracker-quality --env-file .env
```

Do not commit `.env`, tracker exports, resume files, generated materials, credentials, IDs, or private notes.

## Safety Model

This project is public portfolio code. Real credentials, private documents, personal workflow data, and production integrations must live outside the repository.
