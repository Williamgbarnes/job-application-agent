import pytest

from job_application_agent.workflow_rules import (
    APPLICATION_PREP,
    ARCHIVE_JOB,
    DAILY_JOB_SCAN,
    MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
    WORKFLOW_RULE_CONTRACTS,
    build_workflow_rules_status,
    get_workflow_rule_contract,
)


def test_workflow_rule_contracts_cover_expected_recurring_workflows() -> None:
    workflow_ids = {contract.workflow_id for contract in WORKFLOW_RULE_CONTRACTS}

    assert workflow_ids == {DAILY_JOB_SCAN, ARCHIVE_JOB, APPLICATION_PREP}


def test_workflow_rules_are_aligned_in_safe_default_mode() -> None:
    status = build_workflow_rules_status(
        dry_run=True,
        require_human_approval=True,
        allow_external_submission=False,
    )

    assert status["is_aligned"] is True
    assert status["workflow_count"] == 3
    assert (
        status["minimum_poll_interval_minutes"]
        == MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES
    )
    for workflow in status["workflows"]:
        assert workflow["is_aligned"] is True
        assert workflow["alignment_checks"] == {
            "mock_first": True,
            "read_only_first": True,
            "human_approval_required": True,
            "external_writes_disabled": True,
            "no_autonomous_submission_contact_or_message": True,
            "private_payloads_excluded": True,
            "log_safe_output": True,
            "minimum_poll_interval_enforced": True,
            "condition_watch_noop_stays_quiet": True,
            "approval_required_before_real_mutation": True,
            "prohibited_actions_defined": True,
        }


def test_workflow_rules_reject_external_submission_or_disabled_approval() -> None:
    unsafe_status = build_workflow_rules_status(
        dry_run=False,
        require_human_approval=False,
        allow_external_submission=True,
    )

    assert unsafe_status["is_aligned"] is False
    for workflow in unsafe_status["workflows"]:
        assert workflow["is_aligned"] is False
        assert workflow["alignment_checks"]["read_only_first"] is False
        assert workflow["alignment_checks"]["human_approval_required"] is False
        assert workflow["alignment_checks"]["external_writes_disabled"] is False


def test_daily_job_scan_contract_is_review_queue_only_before_approval() -> None:
    contract = get_workflow_rule_contract(DAILY_JOB_SCAN)
    payload = contract.to_public_dict()

    assert "new-lead recommendations" in payload["allowed_outputs"]
    assert "human review queue entries" in payload["allowed_outputs"]
    assert "writing real tracker lead rows" in payload["approval_required_before"]
    assert "submitting applications" in payload["prohibited_actions"]


def test_archive_job_contract_is_recommendation_only_before_approval() -> None:
    contract = get_workflow_rule_contract(ARCHIVE_JOB)
    payload = contract.to_public_dict()

    assert "archive recommendations" in payload["allowed_outputs"]
    assert "recommend before mutation" in payload["required_controls"]
    assert "changing real tracker statuses" in payload["approval_required_before"]
    assert "deleting production data autonomously" in payload["prohibited_actions"]


def test_application_prep_contract_blocks_submission_and_contact() -> None:
    contract = get_workflow_rule_contract(APPLICATION_PREP)
    payload = contract.to_public_dict()

    assert "draft package plan" in payload["allowed_outputs"]
    assert "tailoring evidence checklist" in payload["allowed_outputs"]
    assert "submitting applications" in payload["approval_required_before"]
    assert "sending emails or messages" in payload["approval_required_before"]
    assert "submitting applications autonomously" in payload["prohibited_actions"]
    assert "contacting people autonomously" in payload["prohibited_actions"]


def test_unknown_workflow_contract_raises() -> None:
    with pytest.raises(ValueError, match="Unknown workflow rule contract"):
        get_workflow_rule_contract("unknown")
