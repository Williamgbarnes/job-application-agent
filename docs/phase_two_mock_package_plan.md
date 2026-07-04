# Phase 2 Mock Package Plan

The Phase 2 mock package plan turns sanitized mock review queue items into human-in-the-loop package planning placeholders.

It does not generate resumes, cover letters, emails, messages, applications, submissions, or any external write action. It prints a public-safe JSON preview only.

## Command

```bash
job-agent mock-package-plan
```

By default, the command reads:

```text
examples/mock_jobs.json
```

To use another sanitized fixture:

```bash
job-agent mock-package-plan --fixture examples/mock_jobs.json
```

## Local filters

The package plan uses the same local filters as the mock review queue:

```bash
job-agent mock-package-plan --min-score 75
job-agent mock-package-plan --priority high
job-agent mock-package-plan --priority high --priority medium
```

The `--top-limit` flag controls how many ranked queue items become package plan placeholders:

```bash
job-agent mock-package-plan --top-limit 3
```

## Output

The command prints JSON with:

- selected filters
- number of package plan placeholders
- mock package IDs
- mock job IDs, companies, titles, scores, priorities, and recommendations
- package lifecycle status (`needs_review` or `blocked`)
- human review checklist items
- blocked reasons for held items
- explicit safety flags

## Human-in-the-loop boundary

A package plan is only a checklist. It is not an application package with generated documents.

A human must still:

- confirm the role is active using public information;
- review sanitized score rationale;
- select approved resume and cover-letter inputs manually;
- approve any generated materials in a private system;
- explicitly approve any external action.

## Safety constraints

- Sanitized mock fixtures only.
- No `.env` access.
- No private tracker rows.
- No resumes or generated application materials.
- No credentials, contacts, private paths, or production IDs.
- No external API calls.
- No writes.
- No submissions.
- No contacting, messaging, or emailing.

## Local checks

```bash
py -m pytest tests/test_mock_package_plan.py -q
py -m pytest
job-agent mock-package-plan
job-agent mock-package-plan --min-score 75 --priority high --top-limit 2
```
