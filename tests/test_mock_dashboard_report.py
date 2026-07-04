import json
from pathlib import Path

from job_application_agent.cli import main
from job_application_agent.domain import JobLead, ScorePriority, WorkArrangement
from job_application_agent.mock_dashboard import build_dashboard_from_queue
from job_application_agent.mock_dashboard_report import render_mock_dashboard_markdown
from job_application_agent.mock_jobs import MockScoredJob
from job_application_agent.review_queue import ReviewQueue, build_review_queue
from job_application_agent.scoring import RuleResult, ScoringResult


def test_render_mock_dashboard_markdown_includes_summary_and_top_items() -> None:
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

    report = render_mock_dashboard_markdown(
        dashboard,
        min_score=50,
        priorities=(ScorePriority.HIGH, ScorePriority.MEDIUM),
    )

    assert report.startswith("# Mock Job Review Dashboard\n")
    assert "- Minimum score: 50" in report
    assert "- Priorities: high, medium" in report
    assert "| Mock leads | 3 |" in report
    assert "| Average score | 61.67 |" in report
    assert "| High | 1 |" in report
    assert "| Review Now | 1 |" in report
    assert (
        "| 1 | high | Example High | Engineering Manager | 90 | high |"
        in report
    )
    assert (
        "| 2 | medium | Example Medium | Engineering Manager | 65 | medium |"
        in report
    )
    assert "| 3 | low |" not in report


def test_render_mock_dashboard_markdown_handles_empty_queue() -> None:
    dashboard = build_dashboard_from_queue(ReviewQueue(items=()), top_limit=5)

    report = render_mock_dashboard_markdown(dashboard)

    assert "- Minimum score: not set" in report
    assert "- Priorities: all" in report
    assert "| Mock leads | 0 |" in report
    assert "| Average score | not set |" in report
    assert "No mock queue items matched the selected filters" in report


def test_mock_dashboard_report_cli_prints_markdown(tmp_path: Path, capsys) -> None:
    fixture_path = _write_mock_dashboard_fixture(tmp_path)

    exit_code = main(
        [
            "mock-dashboard-report",
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
    report = capsys.readouterr().out
    assert report.startswith("# Mock Job Review Dashboard\n")
    assert "- Minimum score: 50" in report
    assert "- Priorities: high, medium" in report
    assert "| Mock leads | 2 |" in report
    assert "| 1 | job_mock_high | Example Systems | Engineering Manager |" in report
    assert "job_mock_medium" not in report
    assert str(fixture_path) not in report


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
                    rationale="Synthetic scoring result for report tests.",
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
