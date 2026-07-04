import pytest

from job_application_agent.domain import JobLead, ScorePriority, WorkArrangement
from job_application_agent.mock_jobs import MockScoredJob
from job_application_agent.review_queue import (
    ReviewRecommendation,
    build_review_queue,
    filter_review_queue,
    parse_score_priority,
    review_queue_to_dict,
)
from job_application_agent.scoring import RuleResult, ScoringResult


def test_review_queue_sorts_by_priority_and_score() -> None:
    queue = build_review_queue(
        (
            _scored_job("low", 30, ScorePriority.LOW),
            _scored_job("high", 90, ScorePriority.HIGH),
            _scored_job("medium", 65, ScorePriority.MEDIUM),
        )
    )

    assert [item.job_id for item in queue.items] == ["high", "medium", "low"]
    assert [item.rank for item in queue.items] == [1, 2, 3]
    assert queue.items[0].recommendation == ReviewRecommendation.REVIEW_NOW
    assert queue.items[1].recommendation == ReviewRecommendation.REVIEW_LATER
    assert queue.items[2].recommendation == ReviewRecommendation.HOLD


def test_filter_review_queue_filters_by_min_score_and_reranks() -> None:
    queue = build_review_queue(
        (
            _scored_job("low", 30, ScorePriority.LOW),
            _scored_job("high", 90, ScorePriority.HIGH),
            _scored_job("medium", 65, ScorePriority.MEDIUM),
        )
    )

    filtered = filter_review_queue(queue, min_score=60)

    assert [item.job_id for item in filtered.items] == ["high", "medium"]
    assert [item.rank for item in filtered.items] == [1, 2]


def test_filter_review_queue_filters_by_priority_and_reranks() -> None:
    queue = build_review_queue(
        (
            _scored_job("low", 30, ScorePriority.LOW),
            _scored_job("high", 90, ScorePriority.HIGH),
            _scored_job("medium", 65, ScorePriority.MEDIUM),
        )
    )

    filtered = filter_review_queue(
        queue, priorities=(ScorePriority.HIGH, ScorePriority.MEDIUM)
    )

    assert [item.job_id for item in filtered.items] == ["high", "medium"]
    assert [item.rank for item in filtered.items] == [1, 2]


def test_review_queue_to_dict_is_public_safe() -> None:
    queue = build_review_queue((_scored_job("high", 90, ScorePriority.HIGH),))

    output = review_queue_to_dict(
        queue, min_score=80, priorities=(ScorePriority.HIGH,)
    )

    assert output["count"] == 1
    assert output["filters"] == {"min_score": 80, "priorities": ["high"]}
    assert output["items"][0]["job_id"] == "high"
    assert output["items"][0]["recommendation"] == "review_now"
    assert output["items"][0]["rationale"]


def test_parse_score_priority_accepts_supported_values() -> None:
    assert parse_score_priority("high") == ScorePriority.HIGH
    assert parse_score_priority("MEDIUM") == ScorePriority.MEDIUM
    assert parse_score_priority("low") == ScorePriority.LOW


def test_parse_score_priority_rejects_unsupported_values() -> None:
    with pytest.raises(ValueError, match="Unsupported priority"):
        parse_score_priority("urgent")


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
                    rationale="Synthetic scoring result for queue tests.",
                ),
            ),
        ),
    )
