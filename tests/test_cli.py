import json
from pathlib import Path

from openpyxl import Workbook

from job_application_agent.cli import main


def test_tracker_headers_cli_prints_log_safe_headers(
    tmp_path: Path, capsys
) -> None:
    tracker_path = tmp_path / "staging_job_tracker.xlsx"
    workbook = Workbook()
    workbook.active.title = "Dashboard"
    applications = workbook.create_sheet("Applications")
    applications.append(["Company", "Role", "Status"])
    applications.append(["Example Co", "Engineering Manager", "Applied"])
    workbook.save(tracker_path)

    env_file = _write_env_file(tmp_path, tracker_path)

    exit_code = main(
        [
            "tracker-headers",
            "--env-file",
            str(env_file),
            "--tab",
            "Applications",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["config"]["has_staging_tracker_path"] is True
    assert output["tracker_headers"]["tabs"][0]["title"] == "Applications"
    assert output["tracker_headers"]["tabs"][0]["headers"] == [
        "Company",
        "Role",
        "Status",
    ]
    assert "Example Co" not in repr(output)
    assert str(tracker_path) not in repr(output)


def test_tracker_schema_cli_prints_log_safe_mapping(
    tmp_path: Path, capsys
) -> None:
    tracker_path = tmp_path / "staging_job_tracker.xlsx"
    workbook = Workbook()
    workbook.active.title = "Dashboard"
    applications = workbook.create_sheet("Applications")
    applications.append(["Company", "Role", "Status", "Custom Notes"])
    applications.append(["Example Co", "Engineering Manager", "Applied", "private note"])
    workbook.save(tracker_path)

    env_file = _write_env_file(tmp_path, tracker_path)

    exit_code = main(
        [
            "tracker-schema",
            "--env-file",
            str(env_file),
            "--tab",
            "Applications",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    tab = output["tracker_schema"]["tabs"][0]
    assert tab["title"] == "Applications"
    assert tab["is_complete"] is True
    assert tab["mapped_fields"][0]["canonical_field"] == "company"
    assert tab["mapped_fields"][1]["canonical_field"] == "role"
    assert tab["mapped_fields"][2]["canonical_field"] == "status"
    assert tab["unmapped_headers"] == ["Custom Notes"]
    assert "Example Co" not in repr(output)
    assert "private note" not in repr(output)
    assert str(tracker_path) not in repr(output)


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
