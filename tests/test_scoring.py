from datetime import datetime, timezone

from job_application_agent.domain import (
    EmploymentType,
    JobLead,
    JobPostingSnapshot,
    ScorePriority,
    WorkArrangement,
)
from job_application_agent.scoring import (
    ScoringProfile,
    TransparentScoringEngine,
    priority_from_score,
)


def test_scoring_engine_scores_strong_match_as_high_priority() -> None:
    lead = JobLead(
        id="lead-1",
        source="mock",
        company="Example Company",
        title="Engineering Manager",
        location="Remote",
        work_arrangement=WorkArrangement.REMOTE,
        employment_type=EmploymentType.FULL_TIME,
        compensation_min=140000,
        compensation_max=180000,
    )
    snapshot = JobPostingSnapshot(
        id="snapshot-1",
        job_lead_id="lead-1",
        captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        normalized_requirements=("Python", "workflow automation", "team leadership"),
        normalized_responsibilities=("Build reliable internal tools",),
    )
    profile = ScoringProfile(
        target_titles=("engineering manager",),
        preferred_keywords=("python", "workflow automation", "leadership"),
        disqualifying_keywords=("commission only",),
        minimum_compensation=150000,
    )

    result = TransparentScoringEngine(profile).score(lead, snapshot)

    assert result.score == 90
    assert result.priority == ScorePriority.HIGH
    assert len(result.rule_results) == 6
    assert any("Role title matches" in strength for strength in result.strengths)
    assert any("No disqualifying" in strength for strength in result.strengths)


def test_scoring_engine_penalizes_disqualifying_keywords() -> None:
    lead = JobLead(
        id="lead-1",
        source="mock",
        company="Example Company",
        title="Engineering Manager",
        work_arrangement=WorkArrangement.REMOTE,
        employment_type=EmploymentType.FULL_TIME,
        compensation_max=180000,
    )
    snapshot = JobPostingSnapshot(
        id="snapshot-1",
        job_lead_id="lead-1",
        captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        raw_text="This is a commission only opportunity.",
    )
    profile = ScoringProfile(
        target_titles=("engineering manager",),
        disqualifying_keywords=("commission only",),
        minimum_compensation=150000,
    )

    result = TransparentScoringEngine(profile).score(lead, snapshot)

    assert result.score == 40
    assert result.priority == ScorePriority.LOW
    assert any("disqualifying" in gap for gap in result.gaps)


def test_scoring_engine_handles_unknown_fields_with_partial_credit() -> None:
    lead = JobLead(
        id="lead-1",
        source="mock",
        company="Example Company",
        title="Generalist",
        work_arrangement=WorkArrangement.UNKNOWN,
        employment_type=EmploymentType.UNKNOWN,
    )
    profile = ScoringProfile(
        target_titles=("engineering manager",),
        preferred_keywords=("python",),
        minimum_compensation=150000,
    )

    result = TransparentScoringEngine(profile).score(lead)

    assert result.score == 29
    assert result.priority == ScorePriority.LOW
    assert any("partial credit" in strength for strength in result.strengths)


def test_scoring_result_converts_to_score_report() -> None:
    lead = JobLead(
        id="lead-1",
        source="mock",
        company="Example Company",
        title="Engineering Manager",
        work_arrangement=WorkArrangement.REMOTE,
        employment_type=EmploymentType.FULL_TIME,
        compensation_max=180000,
    )
    profile = ScoringProfile(
        target_titles=("engineering manager",),
        minimum_compensation=150000,
    )
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    result = TransparentScoringEngine(profile).score(lead)
    report = result.to_score_report(
        report_id="score-1",
        job_lead_id=lead.id,
        created_at=created_at,
    )

    assert report.id == "score-1"
    assert report.job_lead_id == lead.id
    assert report.score == result.score
    assert report.priority == result.priority
    assert report.created_at == created_at
    assert report.rationale is not None
    assert "Role title matches" in report.rationale


def test_priority_from_score_boundaries() -> None:
    assert priority_from_score(100) == ScorePriority.HIGH
    assert priority_from_score(75) == ScorePriority.HIGH
    assert priority_from_score(74) == ScorePriority.MEDIUM
    assert priority_from_score(50) == ScorePriority.MEDIUM
    assert priority_from_score(49) == ScorePriority.LOW
    assert priority_from_score(0) == ScorePriority.LOW
