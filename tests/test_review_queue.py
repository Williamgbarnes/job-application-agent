from job_application_agent.domain import JobLead, ScorePriority, WorkArrangement
from job_application_agent.mock_jobs import MockScoredJob
from job_application_agent.review_queue import (
    ReviewRecommendation,
    build_review_queue,
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


def test_review_queue_to_dict_is_public_safe() -> None:
    queue = build_review_queue((_scored_job("high", 90, ScorePriority.HIGH),))

    output = review_queue_to_dict(queue)

    assert output["count"] == 1
    assert output["items"][0]["job_id"] == "high"
    assert output["items"][0]["recommendation"] == "review_now"
    assert output["items"][0]["rationale"]


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
