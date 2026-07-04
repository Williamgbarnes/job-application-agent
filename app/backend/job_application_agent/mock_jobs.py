"""Public-safe mock job fixture loading and scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from job_application_agent.domain import (
    EmploymentType,
    JobLead,
    JobPostingSnapshot,
    WorkArrangement,
)
from job_application_agent.scoring import (
    ScoringProfile,
    ScoringResult,
    TransparentScoringEngine,
)

DEFAULT_MOCK_JOBS_PATH = Path("examples/mock_jobs.json")
DEFAULT_MOCK_SCORING_PROFILE = ScoringProfile(
    target_titles=(
        "engineering manager",
        "director of software engineering",
    ),
    preferred_keywords=(
        "engineering",
        "delivery",
        "cloud",
        "lead",
        "platform",
        "stakeholders",
        "coaching",
    ),
    disqualifying_keywords=("commission only", "unpaid"),
    preferred_work_arrangements=(WorkArrangement.REMOTE, WorkArrangement.HYBRID),
    preferred_employment_types=(EmploymentType.FULL_TIME,),
    minimum_compensation=150000,
)


@dataclass(frozen=True)
class MockScoredJob:
    """Public-safe scored view of one mock job fixture."""

    lead: JobLead
    scoring_result: ScoringResult


class MockJobFixtureError(ValueError):
    """Raised when a public mock job fixture is invalid."""


def score_mock_jobs(
    fixture_path: Path = DEFAULT_MOCK_JOBS_PATH,
    *,
    profile: ScoringProfile = DEFAULT_MOCK_SCORING_PROFILE,
) -> tuple[MockScoredJob, ...]:
    """Load sanitized mock jobs and score them deterministically."""

    jobs = load_mock_jobs(fixture_path)
    engine = TransparentScoringEngine(profile)
    return tuple(
        MockScoredJob(
            lead=lead,
            scoring_result=engine.score(lead, snapshot),
        )
        for lead, snapshot in jobs
    )


def load_mock_jobs(fixture_path: Path) -> tuple[tuple[JobLead, JobPostingSnapshot], ...]:
    """Load public-safe mock jobs from JSON fixture data."""

    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MockJobFixtureError("Mock jobs fixture was not found.") from exc
    except json.JSONDecodeError as exc:
        raise MockJobFixtureError("Mock jobs fixture is not valid JSON.") from exc

    if not isinstance(payload, list):
        raise MockJobFixtureError("Mock jobs fixture must contain a list of jobs.")

    return tuple(_mock_job_from_mapping(item) for item in payload)


def mock_scored_job_to_dict(scored_job: MockScoredJob) -> dict[str, Any]:
    """Convert a scored mock job to log-safe JSON-compatible data."""

    lead = scored_job.lead
    result = scored_job.scoring_result
    return {
        "id": lead.id,
        "company": lead.company,
        "title": lead.title,
        "score": result.score,
        "priority": result.priority.value,
        "strengths": list(result.strengths),
        "gaps": list(result.gaps),
        "rules": [rule.__dict__ for rule in result.rule_results],
    }


def _mock_job_from_mapping(item: Any) -> tuple[JobLead, JobPostingSnapshot]:
    if not isinstance(item, Mapping):
        raise MockJobFixtureError("Each mock job must be an object.")

    lead = JobLead(
        id=_required_str(item, "id"),
        source=_required_str(item, "source"),
        company=_required_str(item, "company"),
        title=_required_str(item, "title"),
        location=_optional_str(item.get("location")),
        work_arrangement=_parse_work_arrangement(item.get("work_arrangement")),
        employment_type=_parse_employment_type(item.get("employment_type")),
        compensation_min=_optional_int(item.get("compensation_min")),
        compensation_max=_optional_int(item.get("compensation_max")),
        posting_url=_optional_str(item.get("posting_url")),
        posted_date=_optional_date(item.get("posted_date")),
        closing_date=_optional_date(item.get("closing_date")),
    )
    snapshot = JobPostingSnapshot(
        id=f"snapshot_{lead.id}",
        job_lead_id=lead.id,
        captured_at=datetime.now(timezone.utc),
        source_url=lead.posting_url,
        normalized_requirements=_string_sequence(item.get("requirements")),
        normalized_responsibilities=_string_sequence(item.get("responsibilities")),
    )
    return lead, snapshot


def _required_str(item: Mapping[str, Any], key: str) -> str:
    value = _optional_str(item.get(key))
    if value is None:
        raise MockJobFixtureError(f"Mock job is missing required field: {key}.")
    return value


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _optional_date(value: Any) -> date | None:
    text = _optional_str(value)
    if text is None:
        return None
    return date.fromisoformat(text)


def _parse_work_arrangement(value: Any) -> WorkArrangement:
    text = _enum_key(value)
    if not text:
        return WorkArrangement.UNKNOWN
    return WorkArrangement(text)


def _parse_employment_type(value: Any) -> EmploymentType:
    text = _enum_key(value)
    if not text:
        return EmploymentType.UNKNOWN
    return EmploymentType(text)


def _enum_key(value: Any) -> str | None:
    text = _optional_str(value)
    if text is None:
        return None
    return text.lower().replace("-", "_").replace(" ", "_")


def _string_sequence(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise MockJobFixtureError("Mock job sequence fields must be lists of strings.")
    return tuple(str(item).strip() for item in value if str(item).strip())
