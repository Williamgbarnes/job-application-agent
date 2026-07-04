import json
from pathlib import Path

import pytest

from job_application_agent.cli import main
from job_application_agent.domain import JobLead, ScorePriority, WorkArrangement
from job_application_agent.mock_jobs import MockScoredJob
from job_application_agent.mock_package_plan import (
    MockPackagePlanError,
    build_package_plan_from_queue,
    mock_package_plan_to_dict,
)
from job_application_agent.review_queue import ReviewQueue, build_review_queue
from job_application_agent.scoring import RuleResult, ScoringResult


def test_package_plan_maps_queue_items_to_human_review_placeholders() -> None:
    plan = build_package_plan_from_queue(
        build_review_queue(
            (
                _scored_job("low", 30, ScorePriority.LOW),
                _scored_job("high", 90, ScorePriority.HIGH),
                _scored_job("medium", 65, ScorePriority.MEDIUM),
            )
        ),
        top_limit=2,
    )

    output = mock_package_plan_to_dict(
        plan,
        min_score=50,
        priorities=(ScorePriority.HIGH, ScorePriority.MEDIUM),
    )

    assert output["filters"] == {
        "min_score": 50,
        "priorities": ["high", "medium"],
    }
    assert output["count"] == 2
    assert output["top_limit"] == 2
    assert output["safety"] == {
        "generates_application_materials": False,
        "performs_external_writes": False,
        "requires_human_approval": True,
    }
    assert output["items"][0]["package_id"] == "package_high"
    assert output["items"][0]["job_id"] == "high"
    assert output["items"][0]["package_status"] == "needs_review"
    assert output["items"][0]["checklist"][0] == (
        "Prioritize this mock role for human review."
    )
    assert output["items"][1]["package_id"] == "package_medium"
    assert output["items"][1]["package_status"] == "needs_review"


def test_package_plan_marks_hold_items_as_blocked() -> None:
    plan = build_package_plan_from_queue(
        build_review_queue((_scored_job("low", 30, ScorePriority.LOW),)),
        top_limit=1,
    )

    output = mock_package_plan_to_dict(plan)

    assert output["items"][0]["package_status"] == "blocked"
    assert output["items"][0]["blocked_reasons"] == [
        "Queue recommendation is hold.",
        "Human review is required before package preparation.",
    ]


def test_package_plan_rejects_negative_top_limit() -> None:
    with pytest.raises(MockPackagePlanError, match="top_limit"):
        build_package_plan_from_queue(ReviewQueue(items=()), top_limit=-1)


def test_mock_package_plan_cli_prints_sanitized_preview(
    tmp_path: Path, capsys
) -> None:
    fixture_path = _write_mock_package_plan_fixture(tmp_path)

    exit_code = main(
        [
            "mock-package-plan",
            "--fixture",
            str(fixture_path),
            "--min-score",
            "50",
            "--priority",
            "high",
            "--priority",
            "medium",
            "--top-limit",
            "1",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    plan = output["mock_package_plan"]
    assert plan["filters"] == {
        "min_score": 50,
        "priorities": ["high", "medium"],
    }
    assert plan["count"] == 1
    assert plan["items"][0]["package_id"] == "package_job_mock_high"
    assert plan["items"][0]["job_id"] == "job_mock_high"
    assert plan["items"][0]["package_status"] == "needs_review"
    assert plan["safety"]["generates_application_materials"] is False
    assert str(fixture_path) not in repr(output)


def _scored_job(job_id: str, score: int, priority: ScorePriority) -> MockScoredJob:
    return MockScoredJob(
        lead=JobLead(
            id=job_id,
            source="mock",
            company=f"Example {job_id.title()}",
            title="Engineering Manager",
            work_arrangement=WorkArrangement.REMOTE,
        ),
        scoring_result=ScoringResult(
            score=score,
            priority=priority,
            rule_results=(
                RuleResult(
                    rule_name="fixture",
                    points=score,
                    max_points=100,
                    rationale="Synthetic scoring result for package plan tests.",
                ),
            ),
        ),
    )


def _write_mock_package_plan_fixture(tmp_path: Path) -> Path:
    fixture_path = tmp_path / "mock_jobs.json"
    fixture_path.write_text(
        json.dumps(
            [
                {
                    "id": "job_mock_low",
                    "source": "mock",
                    "company": "Example Retail",
                    "title": "Retail Associate",
                    "location": "Onsite, United States",
                    "work_arrangement": "onsite",
                    "employment_type": "part-time",
                    "compensation_max": 50000,
                    "posting_url": "https://example.com/jobs/retail-associate",
                    "requirements": ["Provide customer support"],
                    "responsibilities": ["Maintain public demo inventory"],
                },
                {
                    "id": "job_mock_high",
                    "source": "mock",
                    "company": "Example Systems",
                    "title": "Engineering Manager",
                    "location": "Remote, United States",
                    "work_arrangement": "remote",
                    "employment_type": "full-time",
                    "compensation_max": 180000,
                    "posting_url": "https://example.com/jobs/engineering-manager",
                    "requirements": ["Lead engineering teams"],
                    "responsibilities": ["Improve delivery systems"],
                },
                {
                    "id": "job_mock_medium",
                    "source": "mock",
                    "company": "Example Studio",
                    "title": "Engineering Manager",
                    "location": "United States",
                    "work_arrangement": "unknown",
                    "employment_type": "unknown",
                    "posting_url": "https://example.com/jobs/mock-manager",
                    "requirements": ["Coordinate public-safe planning"],
                    "responsibilities": ["Keep review notes sanitized"],
                },
            ]
        ),
        encoding="utf-8",
    )
    return fixture_path
