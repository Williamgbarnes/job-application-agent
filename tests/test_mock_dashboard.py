import json
from pathlib import Path

import pytest

from job_application_agent.cli import main
from job_application_agent.domain import JobLead, ScorePriority, WorkArrangement
from job_application_agent.mock_dashboard import (
    MockDashboardError,
    build_dashboard_from_queue,
    mock_dashboard_to_dict,
)
from job_application_agent.mock_jobs import MockScoredJob
from job_application_agent.review_queue import ReviewQueue, build_review_queue
from job_application_agent.scoring import RuleResult, ScoringResult


def test_dashboard_summary_counts_scores_and_recommendations() -> None:
    dashboard = build_dashboard_from_queue(
        build_review_queue(
            (
                _scored_job("low", 30, ScorePriority.LOW),
                _scored_job("high", 90, ScorePriority.HIGH),
                _scored_job("medium", 65, ScorePriority.MEDIUM),
            )
        ),
        top_limit=2,
    )

    output = mock_dashboard_to_dict(
        dashboard,
        min_score=50,
        priorities=(ScorePriority.HIGH, ScorePriority.MEDIUM),
    )

    assert output["filters"] == {
        "min_score": 50,
        "priorities": ["high", "medium"],
    }
    assert output["summary"]["count"] == 3
    assert output["summary"]["priority_counts"] == {
        "high": 1,
        "medium": 1,
        "low": 1,
    }
    assert output["summary"]["recommendation_counts"] == {
        "review_now": 1,
        "review_later": 1,
        "hold": 1,
    }
    assert output["summary"]["score_summary"] == {
        "average": 61.67,
        "max": 90,
        "min": 30,
    }
    assert [item["job_id"] for item in output["top_items"]] == [
        "high",
        "medium",
    ]


def test_dashboard_handles_empty_queue() -> None:
    dashboard = build_dashboard_from_queue(ReviewQueue(items=()))

    output = mock_dashboard_to_dict(dashboard)

    assert output["summary"]["count"] == 0
    assert output["summary"]["priority_counts"] == {
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    assert output["summary"]["score_summary"] == {
        "average": None,
        "max": None,
        "min": None,
    }
    assert output["top_items"] == []


def test_dashboard_rejects_negative_top_limit() -> None:
    with pytest.raises(MockDashboardError, match="top_limit"):
        build_dashboard_from_queue(ReviewQueue(items=()), top_limit=-1)


def test_mock_dashboard_cli_prints_sanitized_summary(
    tmp_path: Path, capsys
) -> None:
    fixture_path = _write_mock_dashboard_fixture(tmp_path)

    exit_code = main(
        [
            "mock-dashboard",
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
    dashboard = output["mock_dashboard"]
    assert dashboard["filters"] == {
        "min_score": 50,
        "priorities": ["high", "medium"],
    }
    assert dashboard["summary"]["count"] == 2
    assert dashboard["summary"]["priority_counts"]["high"] == 1
    assert dashboard["summary"]["priority_counts"]["medium"] == 1
    assert dashboard["top_limit"] == 1
    assert [item["job_id"] for item in dashboard["top_items"]] == [
        "job_mock_high",
    ]
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
                    rationale="Synthetic scoring result for dashboard tests.",
                ),
            ),
        ),
    )


def _write_mock_dashboard_fixture(tmp_path: Path) -> Path:
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
