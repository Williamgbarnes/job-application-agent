"""Portfolio-safe source coverage policy for lead discovery demos.

The public model represents aggregate coverage groups only. Concrete source names,
URLs, credentials, tracker identifiers, and live workflow payloads belong outside
this repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_BASELINE_DIRECT_SOURCE_COUNT = 20
DEFAULT_BOARD_COUNT = 12
DEFAULT_TITLE_FAMILY_COUNT = 13
DEFAULT_ATS_ECOSYSTEM_COUNT = 10
DEFAULT_ADDITIONAL_SOURCE_MINIMUM = 20
DEFAULT_ACTIVE_ITEM_THRESHOLD = 50
DEFAULT_INITIAL_CANDIDATE_THRESHOLD = 3


@dataclass(frozen=True)
class CoveragePolicy:
    """Configurable aggregate coverage requirements for a discovery run."""

    baseline_direct_source_count: int = DEFAULT_BASELINE_DIRECT_SOURCE_COUNT
    board_count: int = DEFAULT_BOARD_COUNT
    title_family_count: int = DEFAULT_TITLE_FAMILY_COUNT
    ats_ecosystem_count: int = DEFAULT_ATS_ECOSYSTEM_COUNT
    additional_source_minimum: int = DEFAULT_ADDITIONAL_SOURCE_MINIMUM
    active_item_threshold: int = DEFAULT_ACTIVE_ITEM_THRESHOLD
    initial_candidate_threshold: int = DEFAULT_INITIAL_CANDIDATE_THRESHOLD

    def __post_init__(self) -> None:
        for field_name, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative.")


@dataclass(frozen=True)
class CoverageProgress:
    """Sanitized aggregate progress for one mock or read-only discovery run."""

    approved_source_required: int
    approved_source_completed: int
    baseline_direct_source_completed: int
    boards_completed: int
    title_families_completed: int
    ats_ecosystems_completed: int
    active_item_count: int
    initial_candidate_count: int
    additional_distinct_sources_completed: int
    candidates_added: int

    def __post_init__(self) -> None:
        for field_name, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative.")


@dataclass(frozen=True)
class CoverageResult:
    """Public-safe completion result containing counts and blocker codes only."""

    status: str
    coverage_complete: bool
    expansion_required: bool
    blockers: tuple[str, ...]
    required_counts: dict[str, int]
    completed_counts: dict[str, int]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "coverage_complete": self.coverage_complete,
            "expansion_required": self.expansion_required,
            "blockers": list(self.blockers),
            "required_counts": dict(self.required_counts),
            "completed_counts": dict(self.completed_counts),
            "safety": {
                "uses_aggregate_counts_only": True,
                "contains_source_names": False,
                "contains_live_identifiers": False,
                "performs_external_writes": False,
            },
        }


def assess_coverage(
    progress: CoverageProgress,
    *,
    policy: CoveragePolicy = CoveragePolicy(),
) -> CoverageResult:
    """Apply baseline and separate conditional expansion completion gates."""

    expansion_required = (
        progress.active_item_count < policy.active_item_threshold
        or progress.initial_candidate_count < policy.initial_candidate_threshold
    )
    required_counts = {
        "approved_sources": progress.approved_source_required,
        "baseline_direct_sources": policy.baseline_direct_source_count,
        "boards": policy.board_count,
        "title_families": policy.title_family_count,
        "ats_ecosystems": policy.ats_ecosystem_count,
        "additional_distinct_sources": (
            policy.additional_source_minimum if expansion_required else 0
        ),
    }
    completed_counts = {
        "approved_sources": progress.approved_source_completed,
        "baseline_direct_sources": progress.baseline_direct_source_completed,
        "boards": progress.boards_completed,
        "title_families": progress.title_families_completed,
        "ats_ecosystems": progress.ats_ecosystems_completed,
        "additional_distinct_sources": progress.additional_distinct_sources_completed,
    }
    blockers = tuple(
        f"incomplete_{name}"
        for name, required in required_counts.items()
        if completed_counts[name] < required
    )
    coverage_complete = not blockers
    if blockers:
        status = "partial"
    elif progress.candidates_added == 0:
        status = "complete_no_results"
    else:
        status = "complete"

    return CoverageResult(
        status=status,
        coverage_complete=coverage_complete,
        expansion_required=expansion_required,
        blockers=blockers,
        required_counts=required_counts,
        completed_counts=completed_counts,
    )
