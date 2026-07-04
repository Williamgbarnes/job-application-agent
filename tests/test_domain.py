from datetime import date, datetime, timezone

import pytest

from job_application_agent.domain import (
    ApplicationEvent,
    ApplicationEventType,
    ApplicationPackage,
    ApplicationPackageStatus,
    DomainValidationError,
    EmploymentType,
    JobLead,
    JobPostingSnapshot,
    LeadStatus,
    ScorePriority,
    ScoreReport,
    WorkArrangement,
)


def test_job_lead_accepts_public_safe_fields() -> None:
    lead = JobLead(
        id="lead-1",
        source="mock",
        company="Example Company",
        title="Engineering Manager",
        location="Remote",
        work_arrangement=WorkArrangement.REMOTE,
        employment_type=EmploymentType.FULL_TIME,
        compensation_min=120000,
        compensation_max=160000,
        posting_url="https://example.com/jobs/1",
        posted_date=date(2026, 1, 1),
        closing_date=date(2026, 2, 1),
        status=LeadStatus.REVIEW,
    )

    assert lead.id == "lead-1"
    assert lead.work_arrangement == WorkArrangement.REMOTE
    assert lead.status == LeadStatus.REVIEW


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"id": ""}, "id is required"),
        ({"posting_url": "not-a-url"}, "posting_url"),
        ({"compensation_min": -1}, "compensation_min"),
        (
            {"compensation_min": 200000, "compensation_max": 100000},
            "compensation_min",
        ),
        (
            {"posted_date": date(2026, 2, 1), "closing_date": date(2026, 1, 1)},
            "closing_date",
        ),
    ],
)
def test_job_lead_validation_rejects_invalid_values(
    kwargs: dict[str, object], message: str
) -> None:
    values = {
        "id": "lead-1",
        "source": "mock",
        "company": "Example Company",
        "title": "Engineering Manager",
    }
    values.update(kwargs)

    with pytest.raises(DomainValidationError, match=message):
        JobLead(**values)  # type: ignore[arg-type]


def test_job_posting_snapshot_requires_timezone_aware_capture_time() -> None:
    with pytest.raises(DomainValidationError, match="captured_at"):
        JobPostingSnapshot(
            id="snapshot-1",
            job_lead_id="lead-1",
            captured_at=datetime(2026, 1, 1, 12, 0),
        )


def test_job_posting_snapshot_rejects_blank_normalized_items() -> None:
    with pytest.raises(DomainValidationError, match="normalized_requirements"):
        JobPostingSnapshot(
            id="snapshot-1",
            job_lead_id="lead-1",
            captured_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
            normalized_requirements=("Python", " "),
        )


def test_score_report_validates_score_bounds() -> None:
    report = ScoreReport(
        id="score-1",
        job_lead_id="lead-1",
        score=88,
        priority=ScorePriority.HIGH,
        strengths=("Relevant leadership scope",),
        gaps=("Compensation not listed",),
        created_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    assert report.priority == ScorePriority.HIGH

    with pytest.raises(DomainValidationError, match="score"):
        ScoreReport(
            id="score-2",
            job_lead_id="lead-1",
            score=101,
            priority=ScorePriority.HIGH,
        )


def test_application_package_and_events_are_public_safe() -> None:
    package = ApplicationPackage(
        id="package-1",
        job_lead_id="lead-1",
        resume_variant_id="mock-resume-variant",
        cover_letter_variant_id="mock-cover-letter-variant",
        status=ApplicationPackageStatus.NEEDS_REVIEW,
        review_notes="Use mock review notes only.",
    )
    event = ApplicationEvent(
        id="event-1",
        application_id=package.id,
        event_type=ApplicationEventType.HUMAN_REVIEWED,
        event_date=date(2026, 1, 2),
        notes="Approved by reviewer in mock workflow.",
    )

    assert package.status == ApplicationPackageStatus.NEEDS_REVIEW
    assert event.event_type == ApplicationEventType.HUMAN_REVIEWED


def test_application_package_requires_ids() -> None:
    with pytest.raises(DomainValidationError, match="job_lead_id"):
        ApplicationPackage(id="package-1", job_lead_id="")
