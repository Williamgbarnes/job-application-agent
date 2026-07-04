"""Public-safe mock application package planning.

This module converts sanitized mock review queue items into human-in-the-loop
package plans. A plan is only a review checklist and lifecycle placeholder; it
does not generate resumes, cover letters, emails, messages, submissions, or any
external write action.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from job_application_agent.domain import (
    ApplicationPackage,
    ApplicationPackageStatus,
    ScorePriority,
)
from job_application_agent.review_queue import (
    ReviewQueue,
    ReviewQueueItem,
    ReviewRecommendation,
    build_mock_review_queue,
)

DEFAULT_PACKAGE_PLAN_LIMIT = 3


@dataclass(frozen=True)
class MockPackagePlanItem:
    """A public-safe package planning placeholder for one mock queue item."""

    package: ApplicationPackage
    job_id: str
    company: str
    title: str
    score: int
    priority: ScorePriority
    recommendation: ReviewRecommendation
    checklist: tuple[str, ...]
    blocked_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class MockPackagePlan:
    """Collection of package plan items derived from a mock review queue."""

    items: tuple[MockPackagePlanItem, ...]
    top_limit: int = DEFAULT_PACKAGE_PLAN_LIMIT

    @property
    def count(self) -> int:
        return len(self.items)


class MockPackagePlanError(ValueError):
    """Raised when mock package plan arguments are invalid."""


def build_mock_package_plan(
    fixture_path: Path,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
    top_limit: int = DEFAULT_PACKAGE_PLAN_LIMIT,
) -> MockPackagePlan:
    """Build a package plan preview from sanitized mock jobs."""

    return build_package_plan_from_queue(
        build_mock_review_queue(
            fixture_path,
            min_score=min_score,
            priorities=priorities,
        ),
        top_limit=top_limit,
    )


def build_package_plan_from_queue(
    queue: ReviewQueue,
    *,
    top_limit: int = DEFAULT_PACKAGE_PLAN_LIMIT,
) -> MockPackagePlan:
    """Build package plan items from an already-filtered review queue."""

    if top_limit < 0:
        raise MockPackagePlanError("top_limit must be zero or greater.")

    items = tuple(_package_plan_item(item) for item in queue.items[:top_limit])
    return MockPackagePlan(items=items, top_limit=top_limit)


def mock_package_plan_to_dict(
    plan: MockPackagePlan,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
) -> dict[str, Any]:
    """Convert a package plan preview to JSON-compatible safe output."""

    return {
        "filters": {
            "min_score": min_score,
            "priorities": [priority.value for priority in priorities or ()],
        },
        "count": plan.count,
        "top_limit": plan.top_limit,
        "items": [_package_plan_item_to_dict(item) for item in plan.items],
        "safety": {
            "generates_application_materials": False,
            "performs_external_writes": False,
            "requires_human_approval": True,
        },
    }


def _package_plan_item(item: ReviewQueueItem) -> MockPackagePlanItem:
    return MockPackagePlanItem(
        package=ApplicationPackage(
            id=f"package_{item.job_id}",
            job_lead_id=item.job_id,
            status=_package_status(item.recommendation),
            review_notes="Mock package plan only; no materials generated.",
        ),
        job_id=item.job_id,
        company=item.company,
        title=item.title,
        score=item.score,
        priority=item.priority,
        recommendation=item.recommendation,
        checklist=_checklist_for_item(item),
        blocked_reasons=_blocked_reasons_for_item(item),
    )


def _package_plan_item_to_dict(item: MockPackagePlanItem) -> dict[str, Any]:
    return {
        "package_id": item.package.id,
        "job_id": item.job_id,
        "company": item.company,
        "title": item.title,
        "score": item.score,
        "priority": item.priority.value,
        "recommendation": item.recommendation.value,
        "package_status": item.package.status.value,
        "checklist": list(item.checklist),
        "blocked_reasons": list(item.blocked_reasons),
    }


def _package_status(
    recommendation: ReviewRecommendation,
) -> ApplicationPackageStatus:
    if recommendation == ReviewRecommendation.HOLD:
        return ApplicationPackageStatus.BLOCKED
    return ApplicationPackageStatus.NEEDS_REVIEW


def _checklist_for_item(item: ReviewQueueItem) -> tuple[str, ...]:
    checklist = [
        "Confirm the role is still active using public information.",
        "Review sanitized score rationale before preparing materials.",
        "Select approved resume and cover-letter inputs manually.",
        "Require explicit human approval before any external action.",
    ]
    if item.recommendation == ReviewRecommendation.REVIEW_NOW:
        checklist.insert(0, "Prioritize this mock role for human review.")
    elif item.recommendation == ReviewRecommendation.REVIEW_LATER:
        checklist.insert(0, "Defer until higher-priority mock roles are reviewed.")
    else:
        checklist.insert(0, "Do not prepare materials until blockers are resolved.")
    return tuple(checklist)


def _blocked_reasons_for_item(item: ReviewQueueItem) -> tuple[str, ...]:
    if item.recommendation != ReviewRecommendation.HOLD:
        return ()
    return (
        "Queue recommendation is hold.",
        "Human review is required before package preparation.",
    )
