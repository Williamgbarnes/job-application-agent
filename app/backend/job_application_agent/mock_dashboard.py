"""Public-safe Phase 2 mock dashboard helpers.

The mock dashboard aggregates deterministic mock scoring and review queue output for
local demos. It never reads private tracker exports, credentials, resumes,
generated materials, or production systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from job_application_agent.domain import ScorePriority
from job_application_agent.review_queue import (
    ReviewQueue,
    ReviewQueueItem,
    ReviewRecommendation,
    build_mock_review_queue,
    review_queue_to_dict,
)

DEFAULT_DASHBOARD_TOP_LIMIT = 3


@dataclass(frozen=True)
class MockDashboard:
    """Aggregated, public-safe dashboard view over a mock review queue."""

    queue: ReviewQueue
    top_limit: int = DEFAULT_DASHBOARD_TOP_LIMIT

    @property
    def top_items(self) -> tuple[ReviewQueueItem, ...]:
        """Return the highest-ranked queue items for dashboard display."""

        return self.queue.items[: self.top_limit]


class MockDashboardError(ValueError):
    """Raised when mock dashboard arguments are invalid."""


def build_mock_dashboard(
    fixture_path: Path,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
    top_limit: int = DEFAULT_DASHBOARD_TOP_LIMIT,
) -> MockDashboard:
    """Build a public-safe dashboard summary from sanitized mock jobs."""

    return build_dashboard_from_queue(
        build_mock_review_queue(
            fixture_path,
            min_score=min_score,
            priorities=priorities,
        ),
        top_limit=top_limit,
    )


def build_dashboard_from_queue(
    queue: ReviewQueue,
    *,
    top_limit: int = DEFAULT_DASHBOARD_TOP_LIMIT,
) -> MockDashboard:
    """Build a dashboard from an already-filtered review queue."""

    if top_limit < 0:
        raise MockDashboardError("top_limit must be zero or greater.")
    return MockDashboard(queue=queue, top_limit=top_limit)


def mock_dashboard_to_dict(
    dashboard: MockDashboard,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
) -> dict[str, Any]:
    """Convert a mock dashboard to JSON-compatible public-safe output."""

    priority_values = tuple(priority.value for priority in priorities or ())
    return {
        "filters": {
            "min_score": min_score,
            "priorities": list(priority_values),
        },
        "summary": _summary_for_queue(dashboard.queue),
        "top_limit": dashboard.top_limit,
        "top_items": _queue_items_to_dict(dashboard.top_items),
    }


def _summary_for_queue(queue: ReviewQueue) -> dict[str, Any]:
    scores = [item.score for item in queue.items]
    return {
        "count": queue.count,
        "priority_counts": _priority_counts(queue),
        "recommendation_counts": _recommendation_counts(queue),
        "score_summary": {
            "average": _average_score(scores),
            "max": max(scores) if scores else None,
            "min": min(scores) if scores else None,
        },
    }


def _priority_counts(queue: ReviewQueue) -> dict[str, int]:
    counts = {priority.value: 0 for priority in ScorePriority}
    for item in queue.items:
        counts[item.priority.value] += 1
    return counts


def _recommendation_counts(queue: ReviewQueue) -> dict[str, int]:
    counts = {recommendation.value: 0 for recommendation in ReviewRecommendation}
    for item in queue.items:
        counts[item.recommendation.value] += 1
    return counts


def _average_score(scores: list[int]) -> float | None:
    if not scores:
        return None
    return round(sum(scores) / len(scores), 2)


def _queue_items_to_dict(items: tuple[ReviewQueueItem, ...]) -> list[dict[str, Any]]:
    return review_queue_to_dict(ReviewQueue(items=items))["items"]
