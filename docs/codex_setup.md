# Codex Setup

Codex is configured for public repository development only. Use it for code, tests, documentation, refactors, and sanitized mock workflows.

Do not connect Codex to private job-search data, local tracker exports, resumes, credentials, production systems, or external write actions.

## Safe task types

Good Codex tasks for this repository:

- add unit tests for existing modules
- refactor public-safe domain or scoring code
- improve CLI output for sanitized mock fixtures
- update documentation
- add mock-only examples
- explain unfamiliar code paths
- propose small pull requests for review

Avoid broad tasks that mix product design, private data, and external integrations in one prompt.

## Forbidden task types

Do not ask Codex to:

- inspect `.env`
- inspect `data/private/`
- parse real tracker exports
- use real resumes, contacts, private notes, or application materials
- add API keys, OAuth tokens, cookies, Google Sheet IDs, or Google Drive IDs
- send emails, messages, applications, form submissions, or external write requests
- bypass website terms, CAPTCHAs, login restrictions, anti-automation controls, or rate limits
- implement unattended applying or contacting

## Initial local checks

From the repository root:

```bash
py -m pip install -e ".[dev]"
py -m pytest
job-agent mock-score
job-agent mock-queue
job-agent mock-queue --min-score 75 --priority high
```

These commands use public code and sanitized mock fixtures only.

## Optional staging checks

Only run staging commands when you are working locally and have a private `.env` that points to ignored local files.

```bash
job-agent sheets-metadata --env-file .env
job-agent tracker-headers --env-file .env
job-agent tracker-schema --env-file .env
job-agent tracker-quality --env-file .env
```

Staging output must remain log-safe. It must not print private paths, IDs, row values, company names, job titles, notes, URLs, contacts, or generated materials.

## Suggested Codex prompts

Use prompts like these:

```text
Read AGENTS.md first. Add unit tests for the scoring boundary conditions. Keep the PR small and public-safe. Run py -m pytest.
```

```text
Read AGENTS.md first. Refactor the mock queue filtering code for clarity without changing behavior. Add or update tests. Do not touch private data paths.
```

```text
Read AGENTS.md first. Improve README documentation for the public demo commands. Do not add private paths, IDs, credentials, or real job-search examples.
```

## Review requirements

Before merging Codex-authored changes:

- review the diff manually
- confirm no private data or secrets were added
- confirm no external write behavior was added
- run `py -m pytest`
- run relevant CLI demo commands
- keep pull requests small

Codex output is a proposal, not an approval. Human review remains required before merge.
