"""Public-safe review queue helpers for scored mock jobs.

The review queue is deliberately human-in-the-loop. It prioritizes sanitized mock
jobs for review and never performs external write, application, or contact
actions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable

from job_application_agent.domain import ScorePriority
from job_application_agent.mock_jobs import MockScoredJob, score_mock_jobs


class ReviewRecommendation(StrEnum):
    """Human-review-only recommendation buckets."""

    REVIEW_NOW = "review_now"
    REVIEW_LATER = "review_later"
    HOLD = "hold"


@dataclass(frozen=True)
class ReviewQueueItem:
    """Public-safe item for a human review queue."""

    rank: int
    job_id: str
    company: str
    title: str
    score: int
    priority: ScorePriority
    recommendation: ReviewRecommendation
    rationale: str


@dataclass(frozen=True)
class ReviewQueue:
    """Public-safe review queue summary."""

    items: tuple[ReviewQueueItem, ...]

    @property
    def count(self) -> int:
        return len(self.items)


def build_mock_review_queue(
    fixture_path: Path,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
) -> ReviewQueue:
    """Score sanitized mock jobs and return a sorted human review queue."""

    queue = build_review_queue(score_mock_jobs(fixture_path))
    return filter_review_queue(queue, min_score=min_score, priorities=priorities)


def build_review_queue(scored_jobs: tuple[MockScoredJob, ...]) -> ReviewQueue:
    """Build a sorted review queue from scored mock jobs."""

    sorted_jobs = sorted(
        scored_jobs,
        key=lambda scored_job: (
            _priority_rank(scored_job.scoring_result.priority),
            scored_job.scoring_result.score,
            scored_job.lead.title.lower(),
        ),
        reverse=True,
    )
    return ReviewQueue(
        items=tuple(
            _queue_item(rank=rank, scored_job=scored_job)
            for rank, scored_job in enumerate(sorted_jobs, start=1)
        )
    )


def filter_review_queue(
    queue: ReviewQueue,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
) -> ReviewQueue:
    """Filter a review queue and re-rank the remaining items."""

    priority_set = set(priorities or ())
    items = queue.items
    if min_score is not None:
        items = tuple(item for item in items if item.score >= min_score)
    if priority_set:
        items = tuple(item for item in items if item.priority in priority_set)
    return ReviewQueue(
        items=tuple(replace(item, rank=rank) for rank, item in enumerate(items, start=1))
    )


def review_queue_to_dict(
    queue: ReviewQueue,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
) -> dict[str, Any]:
    """Convert a review queue to JSON-compatible public-safe output."""

    priority_values = tuple(priority.value for priority in priorities or ())
    return {
        "count": queue.count,
        "filters": {
            "min_score": min_score,
            "priorities": list(priority_values),
        },
        "items": [
            {
                "rank": item.rank,
                "job_id": item.job_id,
                "company": item.company,
                "title": item.title,
                "score": item.score,
                "priority": item.priority.value,
                "recommendation": item.recommendation.value,
                "rationale": item.rationale,
            }
            for item in queue.items
        ],
    }


def parse_score_priority(value: str) -> ScorePriority:
    """Parse a CLI priority value."""

    normalized_value = value.strip().lower().replace("-", "_")
    try:
        return ScorePriority(normalized_value)
    except ValueError as exc:
        allowed = ", ".join(priority.value for priority in ScorePriority)
        raise ValueError(f"Unsupported priority '{value}'. Allowed values: {allowed}.") from exc


def _queue_item(rank: int, scored_job: MockScoredJob) -> ReviewQueueItem:
    result = scored_job.scoring_result
    recommendation = _recommendation_for_priority(result.priority)
    return ReviewQueueItem(
        rank=rank,
        job_id=scored_job.lead.id,
        company=scored_job.lead.company,
        title=scored_job.lead.title,
        score=result.score,
        priority=result.priority,
        recommendation=recommendation,
        rationale=_queue_rationale(result.priority, recommendation),
    )


def _recommendation_for_priority(priority: ScorePriority) -> ReviewRecommendation:
    if priority == ScorePriority.HIGH:
        return ReviewRecommendation.REVIEW_NOW
    if priority == ScorePriority.MEDIUM:
        return ReviewRecommendation.REVIEW_LATER
    return ReviewRecommendation.HOLD


def _queue_rationale(
    priority: ScorePriority, recommendation: ReviewRecommendation
) -> str:
    if recommendation == ReviewRecommendation.REVIEW_NOW:
        return "High-priority mock lead; place near the top of the human review queue."
    if recommendation == ReviewRecommendation.REVIEW_LATER:
        return "Medium-priority mock lead; review after higher-scoring items."
    return "Low-priority mock lead; hold unless review capacity is available."


def _priority_rank(priority: ScorePriority) -> int:
    return {
        ScorePriority.HIGH: 3,
        ScorePriority.MEDIUM: 2,
        ScorePriority.LOW: 1,
    }[priority]
