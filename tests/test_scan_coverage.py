import pytest

from job_application_agent.scan_coverage import (
    CoveragePolicy,
    CoverageProgress,
    assess_coverage,
)


def _complete_progress(**overrides: int) -> CoverageProgress:
    values = {
        "approved_source_required": 2,
        "approved_source_completed": 2,
        "baseline_direct_source_completed": 20,
        "boards_completed": 12,
        "title_families_completed": 13,
        "ats_ecosystems_completed": 10,
        "active_item_count": 50,
        "initial_candidate_count": 3,
        "additional_distinct_sources_completed": 0,
        "candidates_added": 1,
    }
    values.update(overrides)
    return CoverageProgress(**values)


def test_baseline_direct_sources_are_always_required() -> None:
    result = assess_coverage(
        _complete_progress(baseline_direct_source_completed=19)
    )

    assert result.expansion_required is False
    assert result.coverage_complete is False
    assert "incomplete_baseline_direct_sources" in result.blockers


def test_conditional_expansion_is_separate_from_baseline() -> None:
    result = assess_coverage(
        _complete_progress(
            active_item_count=49,
            additional_distinct_sources_completed=19,
        )
    )

    assert result.expansion_required is True
    assert result.required_counts["baseline_direct_sources"] == 20
    assert result.required_counts["additional_distinct_sources"] == 20
    assert result.coverage_complete is False


def test_zero_results_are_complete_only_after_full_coverage() -> None:
    result = assess_coverage(_complete_progress(candidates_added=0))

    assert result.coverage_complete is True
    assert result.status == "complete_no_results"
    assert result.blockers == ()


def test_policy_is_configurable_without_source_identifiers() -> None:
    policy = CoveragePolicy(
        baseline_direct_source_count=3,
        board_count=2,
        title_family_count=2,
        ats_ecosystem_count=1,
        additional_source_minimum=4,
        active_item_threshold=5,
        initial_candidate_threshold=2,
    )
    progress = CoverageProgress(
        approved_source_required=1,
        approved_source_completed=1,
        baseline_direct_source_completed=3,
        boards_completed=2,
        title_families_completed=2,
        ats_ecosystems_completed=1,
        active_item_count=4,
        initial_candidate_count=2,
        additional_distinct_sources_completed=4,
        candidates_added=0,
    )

    payload = assess_coverage(progress, policy=policy).to_public_dict()

    assert payload["coverage_complete"] is True
    assert payload["safety"] == {
        "uses_aggregate_counts_only": True,
        "contains_source_names": False,
        "contains_live_identifiers": False,
        "performs_external_writes": False,
    }


def test_negative_policy_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="board_count"):
        CoveragePolicy(board_count=-1)
