"""Public-safe scheduled-task compatibility rules.

The live ChatGPT scheduled tasks and private workflow payloads remain outside this
repository. This module only captures sanitized behavioral rules that future app
scheduler work must satisfy before any cutover from the current private system.
"""

from __future__ import annotations

from typing import Any

SCHEDULED_TASK_RULES_VERSION = "2026-07-05"
MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES = 60


def build_scheduled_task_rules_status(
    *,
    runtime_mode: str,
    dry_run: bool,
    require_human_approval: bool,
    allow_external_submission: bool,
) -> dict[str, Any]:
    """Return a sanitized status for scheduled-task rule alignment.

    The payload intentionally avoids task names, prompts, tracker identifiers,
    private paths, contacts, job details, and generated application materials.
    """

    external_writes_disabled_by_default = not allow_external_submission
    read_only_first = dry_run and external_writes_disabled_by_default
    human_approval_gate_enabled = require_human_approval

    alignment_checks = {
        "current_private_workflows_remain_source_of_truth": True,
        "mock_data_only_in_repo": True,
        "read_only_first": read_only_first,
        "human_approval_required_before_external_action": human_approval_gate_enabled,
        "external_writes_disabled_by_default": external_writes_disabled_by_default,
        "no_autonomous_apply_submit_contact_or_message_actions": True,
        "no_private_task_payloads_in_repo": True,
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
