# Scoring Engine

The scoring engine is deterministic, transparent, and public-safe. It is designed for mock and sanitized inputs only.

## Goals

- Score job leads with explainable rules.
- Produce a `ScoreReport` that can be displayed in a review queue.
- Keep scoring deterministic and unit-tested.
- Avoid external services, private files, secrets, or production data.

## Inputs

The engine accepts:

- `JobLead`
- optional `JobPostingSnapshot`
- `ScoringProfile`

The `ScoringProfile` contains public-safe preferences:

- target titles
- preferred keywords
- disqualifying keywords
- preferred work arrangements
- preferred employment types
- minimum compensation

## Rules

The initial scoring rules are intentionally simple:

| Rule | Max points | Notes |
| --- | ---: | --- |
| Title match | 20 | Full credit when the lead title matches a configured target title. |
| Work arrangement | 15 | Full credit for preferred arrangements, partial credit for unknown. |
| Employment type | 10 | Full credit for preferred types, partial credit for unknown. |
| Compensation | 15 | Full credit when the range can meet the configured minimum, partial credit when unknown. |
| Preferred keywords | 25 | Adds points for matched public-safe keywords in the lead or posting snapshot. |
| Disqualifying keywords | 15 or penalty | Full credit when none are found; applies a penalty when found. |

Scores are clamped to the `0` to `100` range.

## Priority buckets

| Score | Priority |
| ---: | --- |
| `75` to `100` | `high` |
| `50` to `74` | `medium` |
| `0` to `49` | `low` |

## Safety constraints

- No external API calls.
- No private tracker rows.
- No resumes or generated application materials.
- No autonomous application behavior.
- Rule rationales should explain scoring without exposing private data.

## Local tests

```bash
py -m pytest tests/test_scoring.py -q
py -m pytest
```
