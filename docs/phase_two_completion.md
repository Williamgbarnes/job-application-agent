# Phase 2 Completion

Phase 2 is complete when the public mock workflow can demonstrate the end-to-end reviewer path without private data or external writes.

## Completion criteria

The completed Phase 2 demo must:

- read sanitized mock leads from `examples/mock_jobs.json`;
- score mock leads with deterministic, transparent scoring rules;
- display score rationale for review;
- rank scored mock leads into a human review queue;
- aggregate dashboard metrics as JSON;
- render a static Markdown dashboard report;
- create application package planning placeholders only;
- provide one completion summary command for reviewers;
- keep all external actions behind explicit human approval.

## Completion command

Run the Phase 2 completion summary locally:

```bash
job-agent mock-phase-two-summary
```

Focused demo filters use the same score, priority, and top-limit options as the other Phase 2 commands:

```bash
job-agent mock-phase-two-summary --min-score 75 --priority high --top-limit 2
```

The command prints JSON with:

- phase and completion status;
- completion criteria booleans;
- selected filters;
- mock input requirements;
- workflow steps;
- public mock CLI command map;
- scored job count;
- review queue output;
- dashboard output;
- package plan output;
- explicit safety flags.

## Phase 2 command set

| Command | Purpose |
| --- | --- |
| `job-agent mock-score` | Score sanitized mock leads and show rule rationale. |
| `job-agent mock-queue` | Rank scored mock leads for human review. |
| `job-agent mock-dashboard` | Print dashboard JSON from the mock review queue. |
| `job-agent mock-dashboard-report` | Print a static Markdown dashboard report. |
| `job-agent mock-package-plan` | Print package planning placeholders without generated materials. |
| `job-agent mock-phase-two-summary` | Print Phase 2 completion status and safety boundaries. |

## Safety boundary

Phase 2 remains public-safe and mock-only. It does not read `.env`, private tracker exports, resumes, credentials, contacts, production IDs, generated materials, or private notes. It does not call external services, write to production systems, submit applications, email, message, or contact people.

Package plan output is only a planning placeholder. A human must still review scoring rationale, select approved private source inputs outside the public repo, approve generated materials in a private system, and explicitly approve any external action.

## Local verification

Run the full local check:

```bash
bash scripts/check-local.sh
```

For focused iteration:

```bash
python -m pytest tests/test_phase_two_summary.py -q
job-agent mock-phase-two-summary
```
