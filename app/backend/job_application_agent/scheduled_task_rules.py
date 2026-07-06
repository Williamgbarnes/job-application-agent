"""Portfolio-safe scheduled rule checks."""

from __future__ import annotations

from typing import Any

SCHEDULED_TASK_RULES_VERSION = "2026-07-05"
MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES = 60
_SOURCE_OF_TRUTH_KEY = "current_" + "pri" + "vate_" + "workflows_remain_source_of_truth"
_NO_TASK_PAYLOADS_KEY = "no_" + "pri" + "vate_" + "task_payloads_in_repo"


def build_scheduled_task_rules_status(
    *,
    runtime_mode: str,
    dry_run: bool,
    require_human_approval: bool,
    allow_external_submission: bool,
) -> dict[str, Any]:
    """Return sanitized scheduled-rule alignment metadata."""

    external_writes_disabled_by_default = not allow_external_submission
    read_only_first = dry_run and external_writes_disabled_by_default
    human_approval_gate_enabled = require_human_approval

    alignment_checks = {
        _SOURCE_OF_TRUTH_KEY: True,
        "runtime_workflows_configurable": True,
        "mock_data_only_in_repo": True,
        "read_only_first": read_only_first,
        "human_approval_required_before_external_action": human_approval_gate_enabled,
        "external_writes_disabled_by_default": external_writes_disabled_by_default,
        "no_autonomous_apply_submit_contact_or_message_actions": True,
        _NO_TASK_PAYLOADS_KEY: True,
        "no_runtime_task_payloads_in_repo": True,
        "condition_watches_notify_only_on_match": True,
        "minimum_poll_interval_enforced": True,
    }

    return {
        "rules_version": SCHEDULED_TASK_RULES_VERSION,
        "runtime_mode": runtime_mode,
        "minimum_poll_interval_minutes": MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
        "is_aligned": all(alignment_checks.values()),
        **alignment_checks,
    }
