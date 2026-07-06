"""Phase 2 completion summary for the public mock demo.

The summary composes existing mock scoring, review queue, dashboard, and package
planning helpers into one read-only portfolio status object. It reads sanitized
mock fixtures only and never reads private tracker exports, resumes,
credentials, generated materials, or production systems.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from job_application_agent.domain import ScorePriority
from job_application_agent.mock_dashboard import (
    DEFAULT_DASHBOARD_TOP_LIMIT,
    build_mock_dashboard,
    mock_dashboard_to_dict,
)
from job_application_agent.mock_jobs import DEFAULT_MOCK_JOBS_PATH, score_mock_jobs
from job_application_agent.mock_package_plan import (
    build_mock_package_plan,
    mock_package_plan_to_dict,
)
from job_application_agent.review_queue import (
    build_mock_review_queue,
    review_queue_to_dict,
)

DEFAULT_PHASE_TWO_TOP_LIMIT = DEFAULT_DASHBOARD_TOP_LIMIT

PHASE_TWO_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "command": "job-agent mock-score",
        "capability": "Score sanitized mock leads with deterministic rules.",
    },
    {
        "command": "job-agent mock-queue",
        "capability": "Rank scored mock leads for human review.",
    },
    {
        "command": "job-agent mock-dashboard",
        "capability": "Aggregate queue metrics into public-safe dashboard JSON.",
    },
    {
        "command": "job-agent mock-dashboard-report",
        "capability": "Render the dashboard as static Markdown for demos.",
    },
    {
        "command": "job-agent mock-package-plan",
        "capability": "Preview human-in-the-loop package planning placeholders.",
    },
    {
        "command": "job-agent mock-phase-two-summary",
        "capability": "Show Phase 2 completion status and safety boundaries.",
    },
)


def build_phase_two_summary(
    fixture_path: Path = DEFAULT_MOCK_JOBS_PATH,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
    top_limit: int = DEFAULT_PHASE_TWO_TOP_LIMIT,
) -> dict[str, Any]:
    """Build a JSON-compatible Phase 2 completion summary."""

    priority_values = tuple(priorities or ())
    scored_jobs = score_mock_jobs(fixture_path)
    queue = build_mock_review_queue(
        fixture_path,
        min_score=min_score,
        priorities=priority_values,
    )
    dashboard = build_mock_dashboard(
        fixture_path,
        min_score=min_score,
        priorities=priority_values,
        top_limit=top_limit,
    )
    package_plan = build_mock_package_plan(
        fixture_path,
        min_score=min_score,
        priorities=priority_values,
        top_limit=top_limit,
    )

    return {
        "phase": "phase_2",
        "status": "complete",
        "completion_criteria": {
            "reads_mock_leads": len(scored_jobs) > 0,
            "displays_scores_and_rationale": _has_score_rationale(scored_jobs),
            "shows_review_queue": True,
            "publishes_dashboard_outputs": True,
            "keeps_human_in_the_loop": True,
            "uses_sanitized_mock_data_only": True,
        },
        "filters": {
            "min_score": min_score,
            "priorities": [priority.value for priority in priority_values],
            "top_limit": top_limit,
        },
        "mock_inputs": {
            "default_fixture": str(DEFAULT_MOCK_JOBS_PATH),
            "fixture_type": "sanitized_mock_jobs_json",
            "requires_env_file": False,
            "requires_private_tracker_export": False,
            "requires_external_services": False,
        },
        "workflow": [
            "Load sanitized mock leads.",
            "Apply deterministic transparent scoring rules.",
            "Rank scored leads for human review.",
            "Aggregate dashboard metrics and report output.",
            "Prepare package planning placeholders without generating materials.",
        ],
        "commands": list(PHASE_TWO_COMMANDS),
        "outputs": {
            "scored_job_count": len(scored_jobs),
            "review_queue": review_queue_to_dict(
                queue,
                min_score=min_score,
                priorities=priority_values,
            ),
            "dashboard": mock_dashboard_to_dict(
                dashboard,
                min_score=min_score,
                priorities=priority_values,
            ),
            "package_plan": mock_package_plan_to_dict(
                package_plan,
                min_score=min_score,
                priorities=priority_values,
            ),
        },
        "safety": {
            "reads_private_tracker_rows": False,
            "reads_resumes": False,
            "reads_env_file": False,
            "uses_credentials": False,
            "generates_application_materials": False,
            "performs_external_writes": False,
            "submits_applications": False,
            "contacts_people": False,
            "requires_human_approval_before_external_action": True,
        },
    }


def _has_score_rationale(scored_jobs: tuple[Any, ...]) -> bool:
    return all(scored_job.scoring_result.rule_results for scored_job in scored_jobs)
