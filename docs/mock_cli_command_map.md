# Mock CLI Command Map

This map connects each public mock command to the demo capability it shows.

| Command | Capability shown |
| --- | --- |
| `job-agent mock-score` | Rules-based scoring over sanitized records. |
| `job-agent mock-queue` | Ranked review queue construction. |
| `job-agent mock-dashboard` | Summary metrics for review planning. |
| `job-agent mock-dashboard-report` | Markdown report rendering for a human reviewer. |
| `job-agent mock-package-plan` | Checklist planning placeholders for selected mock records. |

## Suggested review order

1. Run `job-agent mock-score` to inspect the scored records.
2. Run `job-agent mock-queue` to inspect ranking and recommendations.
3. Run `job-agent mock-dashboard` to inspect aggregate counts.
4. Run `job-agent mock-dashboard-report` to inspect Markdown output.
5. Run `job-agent mock-package-plan` to inspect checklist placeholders.

## Notes

The command set is intentionally local and fixture-based. Keep new commands deterministic, small, and easy to verify in CI.
