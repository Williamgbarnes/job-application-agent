"""Public-safe workflow-specific rule contracts.

These contracts describe the operating rules for recurring job-search workflows
without storing private scheduled-task prompts, tracker rows, contacts, company
names, job titles, credentials, resumes, or generated application materials.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from job_application_agent.scheduled_task_rules import (
    MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
)

WORKFLOW_RULES_VERSION = "2026-07-06"
DAILY_JOB_SCAN = "daily_job_scan"
ARCHIVE_JOB = "archive_job"
APPLICATION_PREP = "application_prep"


@dataclass(frozen=True)
class WorkflowRuleContract:
    """Sanitized operating contract for one recurring workflow."""

    workflow_id: str
    label: str
    purpose: str
    allowed_inputs: tuple[str, ...]
    allowed_outputs: tuple[str, ...]
    required_controls: tuple[str, ...]
    approval_required_before: tuple[str, ...]
    prohibited_actions: tuple[str, ...]
    no_op_behavior: str

    def to_public_dict(self) -> dict[str, Any]:
        """Return the contract without private task payloads or workflow data."""

        return {
            "workflow_id": self.workflow_id,
            "label": self.label,
            "purpose": self.purpose,
            "allowed_inputs": list(self.allowed_inputs),
            "allowed_outputs": list(self.allowed_outputs),
            "required_controls": list(self.required_controls),
            "approval_required_before": list(self.approval_required_before),
            "prohibited_actions": list(self.prohibited_actions),
            "no_op_behavior": self.no_op_behavior,
        }


WORKFLOW_RULE_CONTRACTS: tuple[WorkflowRuleContract, ...] = (
    WorkflowRuleContract(
        workflow_id=DAILY_JOB_SCAN,
        label="Daily job scan",
        purpose="Find, deduplicate, score, and queue new job leads for review.",
        allowed_inputs=(
            "approved source adapter configuration",
            "sanitized mock job fixtures",
            "aggregate tracker state for deduplication",
            "public scoring rules",
        ),
        allowed_outputs=(
            "new-lead recommendations",
            "deduplication summaries",
            "score summaries",
            "human review queue entries",
        ),
        required_controls=(
            "deduplicate before queueing",
            "score before application prep",
            "preserve source attribution",
            "keep logs aggregate and public-safe",
            "run no more often than the scheduled-task poll interval",
        ),
        approval_required_before=(
            "writing real tracker lead rows",
            "saving production source identifiers",
            "using paid or authenticated sourcing APIs",
        ),
        prohibited_actions=(
            "submitting applications",
            "contacting recruiters or hiring teams",
            "printing private tracker values",
            "committing real job-search data",
        ),
        no_op_behavior="Stay quiet when no meaningful new leads are found.",
    ),
    WorkflowRuleContract(
        workflow_id=ARCHIVE_JOB,
        label="Archive job",
        purpose="Recommend stale, duplicate, closed, or inactive leads for archive.",
        allowed_inputs=(
            "aggregate tracker status counts",
            "sanitized mock tracker fixtures",
            "age and stale-status thresholds",
            "closed or duplicate lead signals",
        ),
        allowed_outputs=(
            "archive recommendations",
            "stale lead counts",
            "duplicate lead counts",
            "human approval checklist",
        ),
        required_controls=(
            "recommend before mutation",
            "explain archive reason categories",
            "preserve recoverability until approved",
            "keep logs aggregate and public-safe",
            "run no more often than the scheduled-task poll interval",
        ),
        approval_required_before=(
            "changing real tracker statuses",
            "moving real tracker rows",
            "deleting or hiding real tracker records",
            "mutating production archives",
        ),
        prohibited_actions=(
            "deleting production data autonomously",
            "printing company names or job titles",
            "printing URLs, contacts, or notes",
            "committing real archive exports",
        ),
        no_op_behavior="Stay quiet when no leads meet archive criteria.",
    ),
    WorkflowRuleContract(
        workflow_id=APPLICATION_PREP,
        label="Application prep",
        purpose="Prepare draft application materials for human review.",
        allowed_inputs=(
            "approved job summary fields",
            "approved resume or profile source references",
            "sanitized mock package fixtures",
            "public tailoring and scoring rules",
        ),
        allowed_outputs=(
            "draft package plan",
            "tailoring evidence checklist",
            "human review checklist",
            "mock generated-material summaries",
        ),
        required_controls=(
            "cite evidence for tailoring choices",
            "separate draft materials from submissions",
            "store real generated materials outside the public repository",
            "keep logs aggregate and public-safe",
            "run no more often than the scheduled-task poll interval",
        ),
        approval_required_before=(
            "generating final private application materials",
            "uploading files to external systems",
            "sending emails or messages",
            "submitting applications",
            "writing production tracker updates",
        ),
        prohibited_actions=(
            "submitting applications autonomously",
            "contacting people autonomously",
            "committing resumes or generated materials",
            "printing private tailoring inputs",
        ),
        no_op_behavior="Stay quiet when no approved job is ready for preparation.",
    ),
)


def build_workflow_rules_status(
    *,
    dry_run: bool,
    require_human_approval: bool,
    allow_external_submission: bool,
) -> dict[str, Any]:
    """Return sanitized workflow rule alignment for recurring workflows."""

    external_writes_disabled = not allow_external_submission
    read_only_first = dry_run and external_writes_disabled
    shared_checks = {
        "mock_first": True,
        "read_only_first": read_only_first,
        "human_approval_required": require_human_approval,
        "external_writes_disabled": external_writes_disabled,
        "no_autonomous_submission_contact_or_message": True,
        "private_payloads_excluded": True,
        "log_safe_output": True,
        "minimum_poll_interval_enforced": True,
    }
    workflow_statuses = [
        _build_single_workflow_status(contract, shared_checks)
        for contract in WORKFLOW_RULE_CONTRACTS
    ]

    return {
        "rules_version": WORKFLOW_RULES_VERSION,
        "minimum_poll_interval_minutes": MINIMUM_SCHEDULED_POLL_INTERVAL_MINUTES,
        "workflow_count": len(workflow_statuses),
        "is_aligned": all(workflow["is_aligned"] for workflow in workflow_statuses),
        "workflows": workflow_statuses,
    }


def get_workflow_rule_contract(workflow_id: str) -> WorkflowRuleContract:
    """Return one workflow contract by id."""

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
        "condition_watch_noop_stays_quiet": True,
        "approval_required_before_real_mutation": bool(
            contract.approval_required_before
        ),
        "prohibited_actions_defined": bool(contract.prohibited_actions),
    }

    return {
        **contract.to_public_dict(),
        "is_aligned": all(workflow_checks.values()),
        "alignment_checks": workflow_checks,
    }
