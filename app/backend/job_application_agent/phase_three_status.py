"""Phase 3 read-only local staging readiness summaries.

Phase 3 starts with manually exported local Excel tracker files. This module
summarizes staging readiness without exposing local file paths, workbook titles,
row values, contacts, URLs, notes, credentials, or production identifiers.
"""

from __future__ import annotations

from typing import Any, Sequence

from job_application_agent.config import RuntimeConfig
from job_application_agent.integrations.sheets import (
    DEFAULT_TRACKER_HEADER_TABS,
    LocalExcelTrackerAdapter,
    SheetsAdapterError,
)
from job_application_agent.scheduled_task_rules import build_scheduled_task_rules_status
from job_application_agent.tracker_quality import (
    LocalTrackerQualityAnalyzer,
    TabQualitySummary,
    TrackerQualitySummary,
)
from job_application_agent.workflow_rules import build_workflow_rules_status

DEFAULT_STAGING_MAX_RECORDS = 1000


def build_tracker_summary(
    config: RuntimeConfig,
    *,
    tab_titles: Sequence[str] | None = None,
    header_row: int = 1,
    max_records: int = DEFAULT_STAGING_MAX_RECORDS,
    fail_on_incomplete_schema: bool = False,
    fail_on_required_blanks: bool = False,
) -> dict[str, Any]:
    """Build a public-safe local staging tracker summary."""

    selected_tabs = tuple(tab_titles or DEFAULT_TRACKER_HEADER_TABS)
    source = {
        "type": "local_excel_export",
        "configured": bool(config.staging_tracker_path),
        "readable": False,
        "path_disclosed": False,
        "workbook_title_disclosed": False,
        "row_values_disclosed": False,
        "uses_google_api": False,
    }

    if not config.staging_tracker_path:
        return _tracker_summary_payload(
            config=config,
            selected_tabs=selected_tabs,
            source=source,
            quality=None,
            failed_quality_gates=(),
            error_codes=("missing_staging_tracker_path",),
        )

    try:
        adapter = LocalExcelTrackerAdapter.from_config(config)
        metadata = adapter.get_metadata()
        quality = LocalTrackerQualityAnalyzer.from_config(config).summarize(
            selected_tabs,
            header_row=header_row,
            max_records=max_records,
        )
    except SheetsAdapterError as exc:
        return _tracker_summary_payload(
            config=config,
            selected_tabs=selected_tabs,
            source={**source, "configured": True, "readable": False},
            quality=None,
            failed_quality_gates=(),
            error_codes=(_safe_error_code(exc),),
        )

    failed_quality_gates = quality.failed_quality_gates(
        fail_on_incomplete_schema=fail_on_incomplete_schema,
        fail_on_required_blanks=fail_on_required_blanks,
    )

    return _tracker_summary_payload(
        config=config,
        selected_tabs=selected_tabs,
        source={**source, "configured": True, "readable": True},
        quality=quality,
        failed_quality_gates=failed_quality_gates,
        error_codes=(),
        discovered_tabs=metadata.tab_titles,
    )


def build_phase_three_status(
    config: RuntimeConfig,
    *,
    tab_titles: Sequence[str] | None = None,
    header_row: int = 1,
    max_records: int = DEFAULT_STAGING_MAX_RECORDS,
    fail_on_incomplete_schema: bool = False,
    fail_on_required_blanks: bool = False,
    config_error_code: str | None = None,
) -> dict[str, Any]:
    """Build a public-safe Phase 3 readiness status."""

    tracker_summary = build_tracker_summary(
        config,
        tab_titles=tab_titles,
        header_row=header_row,
        max_records=max_records,
        fail_on_incomplete_schema=fail_on_incomplete_schema,
        fail_on_required_blanks=fail_on_required_blanks,
    )
    if config_error_code:
        tracker_summary["error_codes"] = _append_unique(
            tracker_summary["error_codes"], config_error_code
        )
        tracker_summary["status"] = "not_ready"

    source = tracker_summary["source"]
    quality = tracker_summary["quality"]
    scheduled_task_rules = build_scheduled_task_rules_status(
        runtime_mode=config.runtime_mode,
        dry_run=config.dry_run,
        require_human_approval=config.require_human_approval,
        allow_external_submission=config.allow_external_submission,
    )
    workflow_rules = build_workflow_rules_status(
        dry_run=config.dry_run,
        require_human_approval=config.require_human_approval,
        allow_external_submission=config.allow_external_submission,
    )
    acceptance_criteria = {
        "local_excel_tracker_configured": source["configured"],
        "local_excel_tracker_readable": source["readable"],
        "schema_quality_checked": quality is not None,
        "read_only_first": True,
        "manual_export_model": True,
        "google_api_not_required": True,
        "external_writes_disabled": not config.allow_external_submission,
        "requires_human_approval": config.require_human_approval,
        "log_safe_output": True,
        "scheduled_task_rules_loaded": True,
        "scheduled_task_rules_aligned": scheduled_task_rules["is_aligned"],
        "private_scheduled_workflows_source_of_truth": scheduled_task_rules[
            "current_private_workflows_remain_source_of_truth"
        ],
        "scheduled_task_external_actions_disabled": scheduled_task_rules[
            "external_writes_disabled_by_default"
        ],
        "workflow_rules_loaded": True,
        "workflow_rules_aligned": workflow_rules["is_aligned"],
    }
    phase_status = "ready" if all(acceptance_criteria.values()) else "not_ready"
    if phase_status == "ready" and tracker_summary["status"] != "ready":
        phase_status = "needs_attention"

    return {
        "phase": "phase_3",
        "status": phase_status,
        "acceptance_criteria": acceptance_criteria,
        "scheduled_task_rules": scheduled_task_rules,
        "workflow_rules": workflow_rules,
        "tracker_summary": tracker_summary,
        "next_steps": _next_steps(tracker_summary),
        "safety": {
            "reads_local_excel_export": source["configured"],
            "prints_private_paths": False,
            "prints_row_values": False,
            "prints_company_names": False,
            "prints_job_titles": False,
            "prints_urls": False,
            "prints_contacts": False,
            "uses_google_api": False,
            "performs_external_writes": False,
            "submits_applications": False,
            "contacts_people": False,
            "requires_human_approval_before_external_action": True,
            "scheduled_tasks_use_private_payloads": False,
            "scheduled_tasks_mutate_external_systems": False,
            "condition_watches_emit_noop_notifications": False,
            "minimum_scheduled_poll_interval_minutes": scheduled_task_rules[
                "minimum_poll_interval_minutes"
            ],
        },
    }


def _tracker_summary_payload(
    *,
    config: RuntimeConfig,
    selected_tabs: tuple[str, ...],
    source: dict[str, Any],
    quality: TrackerQualitySummary | None,
    failed_quality_gates: tuple[str, ...],
    error_codes: tuple[str, ...],
    discovered_tabs: tuple[str, ...] = (),
) -> dict[str, Any]:
    quality_payload = _quality_to_dict(quality) if quality else None
    status = _tracker_status(source, quality, failed_quality_gates, error_codes)
    return {
        "status": status,
        "config": config.safe_summary(),
        "source": source,
        "selected_tabs": list(selected_tabs),
        "discovered_tabs": list(discovered_tabs),
        "quality": quality_payload,
        "failed_quality_gates": list(failed_quality_gates),
        "error_codes": list(error_codes),
        "safety": {
            "path_disclosed": False,
            "row_values_disclosed": False,
            "private_identifiers_disclosed": False,
            "external_writes_performed": False,
        },
    }


def _tracker_status(
    source: dict[str, Any],
    quality: TrackerQualitySummary | None,
    failed_quality_gates: tuple[str, ...],
    error_codes: tuple[str, ...],
) -> str:
    if error_codes or not source["configured"] or not source["readable"]:
        return "not_ready"
    if quality is None:
        return "not_ready"
    if (
        failed_quality_gates
        or not quality.is_schema_complete
        or quality.has_required_blanks
        or quality.has_format_warnings
    ):
        return "needs_attention"
    return "ready"


def _quality_to_dict(summary: TrackerQualitySummary) -> dict[str, Any]:
    return {
        "is_schema_complete": summary.is_schema_complete,
        "has_required_blanks": summary.has_required_blanks,
        "has_format_warnings": summary.has_format_warnings,
        "max_records": summary.max_records,
        "scanned_records": summary.scanned_records,
        "tabs": [_tab_quality_to_dict(tab) for tab in summary.tabs],
    }


def _tab_quality_to_dict(tab: TabQualitySummary) -> dict[str, Any]:
    return {
        "title": tab.title,
        "scanned_records": tab.scanned_records,
        "blank_records_skipped": tab.blank_records_skipped,
        "is_schema_complete": tab.is_schema_complete,
        "has_required_blanks": tab.has_required_blanks,
        "has_format_warnings": tab.has_format_warnings,
        "missing_required_fields": list(tab.missing_required_fields),
        "unmapped_header_count": len(tab.unmapped_headers),
        "required_fields": [
            {
                "canonical_field": field.canonical_field,
                "populated_count": field.populated_count,
                "blank_count": field.blank_count,
            }
            for field in tab.required_fields
        ],
        "format_fields": [
            {
                "canonical_field": field.canonical_field,
                "value_kind": field.value_kind,
                "checked_count": field.checked_count,
                "blank_count": field.blank_count,
                "invalid_count": field.invalid_count,
            }
            for field in tab.format_fields
        ],
        "truncated": tab.truncated,
    }


def _safe_error_code(exc: SheetsAdapterError) -> str:
    message = str(exc).lower()
    if "not found" in message:
        return "tracker_file_not_found"
    if "valid .xlsx" in message:
        return "tracker_file_unreadable"
    if "missing expected tabs" in message:
        return "missing_expected_tabs"
    if "openpyxl" in message:
        return "missing_excel_dependency"
    return "tracker_unavailable"


def _next_steps(tracker_summary: dict[str, Any]) -> list[str]:
    if "missing_staging_tracker_path" in tracker_summary["error_codes"]:
        return ["Set STAGING_TRACKER_PATH in a private local .env file."]
    if tracker_summary["error_codes"]:
        return ["Confirm the private local tracker export exists and is readable."]
    if tracker_summary["status"] == "needs_attention":
        return ["Review aggregate schema, required-field, and format quality counts locally."]
    return ["Continue with read-only staging workflow review."]


def _append_unique(values: list[str], value: str) -> list[str]:
    if value in values:
        return values
    return [*values, value]
