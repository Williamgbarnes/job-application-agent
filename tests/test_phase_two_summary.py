import json
from pathlib import Path

from job_application_agent.cli import main
from job_application_agent.domain import ScorePriority
from job_application_agent.phase_two_summary import build_phase_two_summary


def test_phase_two_summary_reports_complete_public_safe_status(
    tmp_path: Path,
) -> None:
    fixture_path = _write_phase_two_fixture(tmp_path)

    summary = build_phase_two_summary(
        fixture_path,
        min_score=50,
        priorities=(ScorePriority.HIGH,),
        top_limit=1,
    )

    assert summary["phase"] == "phase_2"
    assert summary["status"] == "complete"
    assert summary["completion_criteria"] == {
        "reads_mock_leads": True,
        "displays_scores_and_rationale": True,
        "shows_review_queue": True,
        "publishes_dashboard_outputs": True,
        "keeps_human_in_the_loop": True,
        "uses_sanitized_mock_data_only": True,
    }
    assert summary["filters"] == {
        "min_score": 50,
        "priorities": ["high"],
        "top_limit": 1,
    }
    assert summary["mock_inputs"] == {
        "default_fixture": "examples/mock_jobs.json",
        "fixture_type": "sanitized_mock_jobs_json",
        "requires_env_file": False,
        "requires_private_tracker_export": False,
        "requires_external_services": False,
    }
    assert summary["outputs"]["scored_job_count"] == 3
    assert summary["outputs"]["review_queue"]["count"] == 1
    assert summary["outputs"]["dashboard"]["summary"]["count"] == 1
    assert summary["outputs"]["package_plan"]["count"] == 1
    assert summary["safety"]["performs_external_writes"] is False
    assert summary["safety"]["requires_human_approval_before_external_action"] is True
    assert "job-agent mock-phase-two-summary" in {
        command["command"] for command in summary["commands"]
    }
    assert str(fixture_path) not in repr(summary)


def test_phase_two_summary_cli_prints_sanitized_json(
    tmp_path: Path,
    capsys,
) -> None:
    fixture_path = _write_phase_two_fixture(tmp_path)

    exit_code = main(
        [
            "mock-phase-two-summary",
            "--fixture",
            str(fixture_path),
            "--min-score",
            "50",
            "--priority",
            "high",
            "--top-limit",
            "1",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    summary = output["mock_phase_two_summary"]
    assert summary["status"] == "complete"
    assert summary["outputs"]["review_queue"]["count"] == 1
    assert summary["outputs"]["dashboard"]["top_limit"] == 1
    assert summary["outputs"]["package_plan"]["top_limit"] == 1
    assert summary["safety"]["reads_env_file"] is False
    assert str(fixture_path) not in repr(output)


def _write_phase_two_fixture(tmp_path: Path) -> Path:
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
