"""Public-safe configurable workflow rule templates.

These contracts define generic workflow safety envelopes and configuration points.
User-specific settings belong in a separate private app or ignored local config,
not in this public portfolio repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from job_application_agent.scan_coverage import (
    DEFAULT_ADDITIONAL_SOURCE_MINIMUM,
    DEFAULT_ATS_ECOSYSTEM_COUNT,
    DEFAULT_BASELINE_DIRECT_SOURCE_COUNT,
    DEFAULT_BOARD_COUNT,
    DEFAULT_TITLE_FAMILY_COUNT,
)
from job_application_agent.scheduled_task_rules import (
    MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
)

WORKFLOW_RULES_VERSION = "2026-07-14"
DAILY_JOB_SCAN = "daily_job_scan"
ARCHIVE_JOB = "archive_job"
APPLICATION_PREP = "application_prep"

PRIVATE_CONFIGURATION_BOUNDARY = (
    "Store user-specific workflow settings in a private app, private config, "
    "or ignored local files; do not commit those values to this public repo."
)


@dataclass(frozen=True)
class WorkflowRuleContract:
    """Sanitized configurable contract for one recurring workflow template."""

    workflow_id: str
    label: str
    purpose: str
    configurable_settings: tuple[str, ...]
    allowed_inputs: tuple[str, ...]
    allowed_outputs: tuple[str, ...]
    required_controls: tuple[str, ...]
    approval_required_before: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    no_op_behavior: str
    private_configuration_boundary: str = PRIVATE_CONFIGURATION_BOUNDARY

    def to_public_dict(self) -> dict[str, Any]:
        """Return the contract without user-specific settings or workflow data."""

        return {
            "workflow_id": self.workflow_id,
            "label": self.label,
            "purpose": self.purpose,
            "configurable_settings": list(self.configurable_settings),
            "allowed_inputs": list(self.allowed_inputs),
            "allowed_outputs": list(self.allowed_outputs),
            "required_controls": list(self.required_controls),
            "approval_required_before": list(self.approval_required_before),
            "prohibited_actions": list(self.prohibited_actions),
            "no_op_behavior": self.no_op_behavior,
            "private_configuration_boundary": self.private_configuration_boundary,
        }


WORKFLOW_RULE_CONTRACTS: tuple[WorkflowRuleContract, ...] = (
    WorkflowRuleContract(
        workflow_id=DAILY_JOB_SCAN,
        label="Lead discovery workflow template",
        purpose=(
            "Collect candidate opportunities from user-approved sources and "
            "queue them for review using configurable matching and coverage rules."
        ),
        configurable_settings=(
            "source allowlist and priority",
            "mandatory baseline source groups",
            "conditional additional-source expansion",
            "title-query family rotation",
            "official-source verification policy",
            "scan cadence within the global polling limit",
            "deduplication strategy",
            "ranking or score threshold",
            "review queue destination",
            "notification behavior",
        ),
        allowed_inputs=(
            "public-safe source adapter shape",
            "sanitized sample opportunity fixtures",
            "aggregate coverage counts",
            "user criteria supplied outside the public repo",
            "public scoring and ranking extension points",
        ),
        allowed_outputs=(
            "candidate recommendation summary",
            "source coverage completion summary",
            "deduplication summary",
            "ranking or score summary",
            "review queue proposal",
        ),
        required_controls=(
            "complete mandatory baseline source groups on every run",
            "keep conditional expansion distinct from baseline coverage",
            "attempt every configured query family and discovery group",
            "verify promising results on an official source when accessible",
            "use stable posting identifiers for hard duplicate decisions",
            "block successful zero-result status when coverage is incomplete",
            "deduplicate before queueing",
            "rank or score before downstream preparation",
            "preserve source attribution without exposing user-specific identifiers",
            "keep logs aggregate and public-safe",
            "run no more often than the scheduled-task poll interval",
        ),
        approval_required_before=(
            "reading from live user-configured sources",
            "writing to a real tracker or review queue",
            "saving user-specific source identifiers",
            "triggering a downstream workflow with real data",
        ),
        prohibited_actions=(
            "submitting, applying, emailing, messaging, or contacting autonomously",
            "printing user-specific lead or tracker values",
            "committing user-specific source configuration",
            "treating normalized entity and title as a hard duplicate by itself",
            "promoting a candidate without human review",
        ),
        no_op_behavior=(
            "A zero-result run may be complete only after all required coverage "
            "groups and any triggered additional sources are complete."
        ),
    ),
    WorkflowRuleContract(
        workflow_id=ARCHIVE_JOB,
        label="Record hygiene workflow template",
        purpose=(
            "Recommend records for archive, deprioritization, or cleanup using "
            "configurable lifecycle rules."
        ),
        configurable_settings=(
            "stale-record criteria",
            "duplicate detection strategy",
            "status or lifecycle transition rules",
            "retention and recovery policy",
            "approval checklist format",
            "notification behavior",
        ),
        allowed_inputs=(
            "aggregate status or lifecycle counts",
            "sanitized sample tracker fixtures",
            "archive criteria supplied outside the public repo",
            "public record-hygiene extension points",
        ),
        allowed_outputs=(
            "archive or cleanup recommendation summary",
            "reason-category counts",
            "duplicate or stale-record summary",
            "human approval checklist",
        ),
        required_controls=(
            "recommend before mutation",
            "explain reason categories without exposing row values",
            "preserve recoverability until approved",
            "keep logs aggregate and public-safe",
            "run no more often than the scheduled-task poll interval",
        ),
        approval_required_before=(
            "changing real tracker or datastore statuses",
            "moving, hiding, deleting, or archiving real records",
            "writing to live archive destinations",
            "changing retention behavior for user records",
        ),
        prohibited_actions=(
            "mutating or deleting live data autonomously",
            "printing user-specific record identifiers or row values",
            "committing user-specific archive criteria",
            "making irreversible cleanup decisions without review",
        ),
        no_op_behavior="Use configurable quiet/no-op behavior when no archive criteria are met.",
    ),
    WorkflowRuleContract(
        workflow_id=APPLICATION_PREP,
        label="Preparation workflow template",
        purpose=(
            "Prepare draft materials or checklists from approved inputs while "
            "keeping final artifacts outside the public repo."
        ),
        configurable_settings=(
            "eligible item criteria",
            "approved source reference policy",
            "tailoring or personalization rules",
            "draft artifact types",
            "review checklist requirements",
            "notification behavior",
        ),
        allowed_inputs=(
            "approved public-safe item summary shape",
            "user source references supplied outside the public repo",
            "sanitized sample package fixtures",
            "public tailoring and review extension points",
        ),
        allowed_outputs=(
            "draft preparation plan",
            "evidence or rationale checklist",
            "human review checklist",
            "mock artifact summary",
        ),
        required_controls=(
            "separate draft preparation from submission or delivery",
            "trace draft choices to approved inputs",
            "store final user artifacts outside the public repository",
            "keep logs aggregate and public-safe",
            "run no more often than the scheduled-task poll interval",
        ),
        approval_required_before=(
            "reading user source references",
            "generating final user artifacts",
            "uploading files to external systems",
            "sending, submitting, emailing, messaging, or contacting",
            "writing live tracker or datastore updates",
        ),
        prohibited_actions=(
            "submitting, sending, uploading, or contacting autonomously",
            "committing user source materials or generated artifacts",
            "printing user-specific tailoring inputs",
            "treating a draft as approved without human review",
        ),
        no_op_behavior="Use configurable quiet/no-op behavior when no item is ready.",
    ),
)


def build_workflow_rules_status(
    *,
    dry_run: bool,
    require_human_approval: bool,
    allow_external_submission: bool,
) -> dict[str, Any]:
    """Return sanitized workflow rule alignment for recurring templates."""

    external_writes_disabled = not allow_external_submission
    read_only_first = dry_run and external_writes_disabled
    shared_checks = {
        "configurable_by_private_app": True,
        "mock_first": True,
        "read_only_first": read_only_first,
        "human_approval_required": require_human_approval,
        "external_writes_disabled": external_writes_disabled,
        "no_autonomous_submission_contact_or_message": True,
        "user_specific_values_excluded": True,
        "log_safe_output": True,
        "minimum_poll_interval_enforced": True,
    }
    workflow_statuses = [
        _build_single_workflow_status(contract, shared_checks)
        for contract in WORKFLOW_RULE_CONTRACTS
    ]

    return {
        "rules_version": WORKFLOW_RULES_VERSION,
        "configuration_model": "private app supplies user-specific settings",
        "private_configuration_boundary": PRIVATE_CONFIGURATION_BOUNDARY,
        "minimum_poll_interval_minutes": MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
        "source_coverage_policy": {
            "baseline_required_each_run": True,
            "baseline_direct_source_count": DEFAULT_BASELINE_DIRECT_SOURCE_COUNT,
            "configured_board_count": DEFAULT_BOARD_COUNT,
            "configured_title_family_count": DEFAULT_TITLE_FAMILY_COUNT,
            "configured_ats_ecosystem_count": DEFAULT_ATS_ECOSYSTEM_COUNT,
            "conditional_additional_source_minimum": (
                DEFAULT_ADDITIONAL_SOURCE_MINIMUM
            ),
            "conditional_expansion_excludes_baseline": True,
            "official_source_verification_required": True,
            "zero_result_requires_complete_coverage": True,
            "stable_identifiers_define_hard_duplicates": True,
        },
        "workflow_count": len(workflow_statuses),
        "is_aligned": all(workflow["is_aligned"] for workflow in workflow_statuses),
        "workflows": workflow_statuses,
    }


def get_workflow_rule_contract(workflow_id: str) -> WorkflowRuleContract:
    """Return one workflow template contract by id."""

    for contract in WORKFLOW_RULE_CONTRACTS:
        if contract.workflow_id == workflow_id:
            return contract
    raise ValueError(f"Unknown workflow rule contract: {workflow_id}")


def _build_single_workflow_status(
    contract: WorkflowRuleContract,
    shared_checks: dict[str, bool],
) -> dict[str, Any]:
    workflow_checks = {
        **shared_checks,
        "configuration_settings_defined": bool(contract.configurable_settings),
        "condition_watch_noop_is_configurable": True,
        "approval_required_before_real_mutation": bool(
            contract.approval_required_before
        ),
        "prohibited_actions_defined": bool(contract.prohibited_actions),
    }
    if contract.workflow_id == DAILY_JOB_SCAN:
        workflow_checks.update(
            {
                "baseline_coverage_required": True,
                "conditional_expansion_is_additional": True,
                "zero_result_requires_complete_coverage": True,
                "official_source_verification_required": True,
                "stable_identifier_deduplication": True,
            }
        )

    return {
        **contract.to_public_dict(),
        "is_aligned": all(workflow_checks.values()),
        "alignment_checks": workflow_checks,
    }
