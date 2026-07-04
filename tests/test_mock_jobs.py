import json
from pathlib import Path

import pytest

from job_application_agent.mock_jobs import (
    MockJobFixtureError,
    load_mock_jobs,
    mock_scored_job_to_dict,
    score_mock_jobs,
)


def test_load_mock_jobs_converts_fixture_to_domain_models(tmp_path: Path) -> None:
    fixture_path = _write_mock_jobs_fixture(tmp_path)

    jobs = load_mock_jobs(fixture_path)

    lead, snapshot = jobs[0]
    assert lead.id == "job_mock_001"
    assert lead.company == "Example Systems"
    assert lead.employment_type.value == "full_time"
    assert snapshot.job_lead_id == lead.id
    assert snapshot.normalized_requirements == ("Lead engineering teams",)


def test_score_mock_jobs_returns_public_safe_scored_jobs(tmp_path: Path) -> None:
    fixture_path = _write_mock_jobs_fixture(tmp_path)

    scored_jobs = score_mock_jobs(fixture_path)

    assert len(scored_jobs) == 1
    scored_job = scored_jobs[0]
    output = mock_scored_job_to_dict(scored_job)
    assert output["id"] == "job_mock_001"
    assert output["score"] >= 0
    assert output["priority"] in {"high", "medium", "low"}
    assert output["rules"]
    assert str(fixture_path) not in repr(output)


def test_load_mock_jobs_rejects_invalid_payload(tmp_path: Path) -> None:
    fixture_path = tmp_path / "mock_jobs.json"
    fixture_path.write_text('{"not": "a list"}', encoding="utf-8")

    with pytest.raises(MockJobFixtureError, match="list"):
        load_mock_jobs(fixture_path)


def _write_mock_jobs_fixture(tmp_path: Path) -> Path:
    fixture_path = tmp_path / "mock_jobs.json"
    fixture_path.write_text(
        json.dumps(
            [
                {
                    "id": "job_mock_001",
                    "source": "mock",
                    "company": "Example Systems",
                    "title": "Engineering Manager",
                    "location": "Remote, United States",
                    "work_arrangement": "remote",
                    "employment_type": "full-time",
                    "compensation_min": 150000,
                    "compensation_max": 180000,
                    "posting_url": "https://example.com/jobs/engineering-manager",
                    "posted_date": "2026-07-01",
                    "closing_date": "2026-07-22",
                    "requirements": ["Lead engineering teams"],
                    "responsibilities": ["Improve delivery systems"],
                }
            ]
        ),
        encoding="utf-8",
    )
    return fixture_path
