# Mock CLI Filter Examples

The mock CLI commands support local filters that make demos easier to inspect.

## Score filter

Use `--min-score` to focus on higher-scoring mock records:

```bash
job-agent mock-queue --min-score 75
job-agent mock-dashboard --min-score 75
job-agent mock-package-plan --min-score 75
job-agent mock-phase-two-summary --min-score 75
```

## Priority filter

Use `--priority` to focus on one priority band:

```bash
job-agent mock-queue --priority high
job-agent mock-dashboard --priority medium
job-agent mock-package-plan --priority low
job-agent mock-phase-two-summary --priority high
```

Repeat the flag to include more than one priority:

```bash
job-agent mock-queue --priority high --priority medium
job-agent mock-phase-two-summary --priority high --priority medium
```

## Top limit

Use `--top-limit` on summary-style commands to keep output short:

```bash
job-agent mock-dashboard --top-limit 3
job-agent mock-dashboard-report --top-limit 3
job-agent mock-package-plan --top-limit 2
job-agent mock-phase-two-summary --top-limit 2
```

## Combining filters

Filters can be combined for focused demos:

```bash
job-agent mock-dashboard --min-score 70 --priority high --top-limit 2
job-agent mock-package-plan --min-score 70 --priority high --top-limit 2
job-agent mock-phase-two-summary --min-score 70 --priority high --top-limit 2
```

Keep examples based on sanitized fixtures so command output remains safe to review in public pull requests.
