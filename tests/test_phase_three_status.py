import json
from pathlib import Path

from openpyxl import Workbook

from job_application_agent.cli import QUALITY_GATE_FAILURE_EXIT_CODE, main
from job_application_agent.config import RuntimeConfig
from job_application_agent.phase_three_status import (
    build_phase_three_status,
    build_tracker_summary,
)


def test_tracker_summary_reports_ready_local_excel_without_private_values(
    tmp_path: Path,
) -> None:
    tracker_path = _write_tracker(
        tmp_path,
        rows=[["Example Co", "Engineering Manager", "Applied"]],
    )
    config = RuntimeConfig.from_mapping(
        {
            "RUNTIME_MODE": "staging",
            "STAGING_TRACKER_PATH": str(tracker_path),
        }
    )

    summary = build_tracker_summary(
        config,
        tab_titles=("Applications",),
        fail_on_incomplete_schema=True,
        fail_on_required_blanks=True,
    )

    assert summary["status"] == "ready"
    assert summary["source"] == {
        "type": "local_excel_export",
        "configured": True,
        "readable": True,
        "path_disclosed": False,
        "workbook_title_disclosed": False,
        "row_values_disclosed": False,
        "uses_google_api": False,
    }
    assert summary["selected_tabs"] == ["Applications"]
    assert "Applications" in summary["discovered_tabs"]
    assert summary["quality"]["is_schema_complete"] is True
    assert summary["quality"]["has_required_blanks"] is False
    assert summary["quality"]["scanned_records"] == 1
    assert summary["failed_quality_gates"] == []
    assert summary["error_codes"] == []
    assert "Example Co" not in repr(summary)
    assert "Engineering Manager" not in repr(summary)
    assert str(tracker_path) not in repr(summary)


def test_tracker_summary_reports_schema_and_blank_attention_without_values(
    tmp_path: Path,
) -> None:
    tracker_path = _write_tracker(tmp_path, headers=["Company"], rows=[["Example Co"]])
    config = RuntimeConfig.from_mapping(
        {
            "RUNTIME_MODE": "staging",
            "STAGING_TRACKER_PATH": str(tracker_path),
        }
    )

    summary = build_tracker_summary(
        config,
        tab_titles=("Applications",),
        fail_on_incomplete_schema=True,
        fail_on_required_blanks=True,
    )

    assert summary["status"] == "needs_attention"
    assert summary["quality"]["is_schema_complete"] is False
    assert summary["quality"]["has_required_blanks"] is True
    assert summary["failed_quality_gates"] == [
        "incomplete_schema",
        "required_blanks",
    ]
    tab = summary["quality"]["tabs"][0]
    assert tab["missing_required_fields"] == ["role", "status"]
    assert tab["unmapped_header_count"] == 0
    assert "Example Co" not in repr(summary)
    assert str(tracker_path) not in repr(summary)


def test_phase_three_status_reports_missing_local_tracker_without_private_data() -> None:
    status = build_phase_three_status(RuntimeConfig())

    assert status["phase"] == "phase_3"
    assert status["status"] == "not_ready"
    assert status["acceptance_criteria"]["local_excel_tracker_configured"] is False
    assert status["acceptance_criteria"]["local_excel_tracker_readable"] is False
    assert status["acceptance_criteria"]["read_only_first"] is True
    assert status["tracker_summary"]["error_codes"] == [
        "missing_staging_tracker_path"
    ]
    assert status["safety"] == {
        "reads_local_excel_export": False,
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
    }


def test_phase_three_status_cli_prints_ready_sanitized_output(
    tmp_path: Path,
    capsys,
) -> None:
    tracker_path = _write_tracker(
        tmp_path,
        rows=[["Example Co", "Engineering Manager", "Applied"]],
    )
    env_file = _write_env_file(tmp_path, tracker_path)

    exit_code = main(
        [
            "phase-three-status",
            "--env-file",
            str(env_file),
            "--tab",
            "Applications",
            "--strict",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    status = output["phase_three_status"]
    assert status["status"] == "ready"
    assert status["tracker_summary"]["status"] == "ready"
    assert status["tracker_summary"]["quality"]["scanned_records"] == 1
    assert status["tracker_summary"]["source"]["path_disclosed"] is False
    assert "Example Co" not in repr(output)
    assert "Engineering Manager" not in repr(output)
    assert str(tracker_path) not in repr(output)
    assert str(env_file) not in repr(output)


def test_tracker_summary_cli_strict_fails_for_required_blanks(
    tmp_path: Path,
    capsys,
) -> None:
    tracker_path = _write_tracker(
        tmp_path,
        rows=[[None, "Engineering Manager", "Applied"]],
    )
    env_file = _write_env_file(tmp_path, tracker_path)

    exit_code = main(
        [
            "tracker-summary",
            "--env-file",
            str(env_file),
            "--tab",
            "Applications",
            "--strict",
        ]
    )

    assert exit_code == QUALITY_GATE_FAILURE_EXIT_CODE
    output = json.loads(capsys.readouterr().out)
    summary = output["tracker_summary"]
    assert summary["status"] == "needs_attention"
    assert summary["failed_quality_gates"] == ["required_blanks"]
    assert summary["quality"]["has_required_blanks"] is True
    assert "Engineering Manager" not in repr(output)
    assert str(tracker_path) not in repr(output)
    assert str(env_file) not in repr(output)


def test_phase_three_status_cli_handles_invalid_staging_configuration(
    tmp_path: Path,
    capsys,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("RUNTIME_MODE=staging\n", encoding="utf-8")

    exit_code = main(["phase-three-status", "--env-file", str(env_file)])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    status = output["phase_three_status"]
    assert status["status"] == "not_ready"
    assert status["tracker_summary"]["error_codes"] == [
        "missing_staging_tracker_path",
        "invalid_runtime_configuration",
    ]
    assert str(env_file) not in repr(output)


def _write_env_file(tmp_path: Path, tracker_path: Path) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "RUNTIME_MODE=staging",
                f"STAGING_TRACKER_PATH={tracker_path}",
            ]
        ),
        encoding="utf-8",
    )
    return env_file


def _write_tracker(
    tmp_path: Path,
    *,
    headers: list[str] | None = None,
    rows: list[list[str | None]],
) -> Path:
    tracker_path = tmp_path / "staging_job_tracker.xlsx"
    workbook = Workbook()
    workbook.active.title = "Dashboard"
    applications = workbook.create_sheet("Applications")
    applications.append(headers or ["Company", "Role", "Status"])
    for row in rows:
        applications.append(row)
    workbook.save(tracker_path)
    return tracker_path
