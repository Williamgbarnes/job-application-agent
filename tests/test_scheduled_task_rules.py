from job_application_agent.scheduled_task_rules import (
    MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
    build_scheduled_task_rules_status,
)


def test_scheduled_task_rules_are_public_safe_and_aligned_by_default() -> None:
    status = build_scheduled_task_rules_status(
        runtime_mode="mock",
        dry_run=True,
        require_human_approval=True,
        allow_external_submission=False,
    )

    assert status["is_aligned"] is True
    assert status["current_private_workflows_remain_source_of_truth"] is True
    assert status["mock_data_only_in_repo"] is True
    assert status["read_only_first"] is True
    assert status["human_approval_required_before_external_action"] is True
    assert status["external_writes_disabled_by_default"] is True
    assert status["no_autonomous_apply_submit_contact_or_message_actions"] is True
    assert status["no_private_task_payloads_in_repo"] is True
    assert status["condition_watches_notify_only_on_match"] is True
    assert status["minimum_poll_interval_enforced"] is True
    assert (
        status["minimum_poll_interval_minutes"]
        == MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES
    )


def test_scheduled_task_rules_reject_disabled_human_approval() -> None:
    status = build_scheduled_task_rules_status(
        runtime_mode="production",
        dry_run=True,
        require_human_approval=False,
        allow_external_submission=False,
    )

    assert status["is_aligned"] is False
    assert status["human_approval_required_before_external_action"] is False


def test_scheduled_task_rules_reject_enabled_external_submission() -> None:
    status = build_scheduled_task_rules_status(
        runtime_mode="production",
        dry_run=False,
        require_human_approval=True,
        allow_external_submission=True,
    )

    assert status["is_aligned"] is False
    assert status["read_only_first"] is False
    assert status["external_writes_disabled_by_default"] is False
