from datetime import date
from pathlib import Path

from openpyxl import Workbook

from job_application_agent.tracker_quality import LocalTrackerQualityAnalyzer


def test_quality_summary_counts_format_warnings_without_values(
    tmp_path: Path,
) -> None:
    tracker_path = tmp_path / "staging_job_tracker.xlsx"
    workbook = Workbook()
    workbook.active.title = "Dashboard"
    applications = workbook.create_sheet("Applications")
    applications.append(
        ["Company", "Role", "Status", "Date Applied", "URL", "Match Score"]
    )
    applications.append(
        [
            "Sample Company",
            "Sample Role",
            "Applied",
            date(2026, 1, 1),
            "https://example.invalid/jobs/1",
            85,
        ]
    )
    applications.append(
        [
            "Sample Company",
            "Sample Role",
            "Unknown Workflow Value",
            "invalid date value",
            "invalid url value",
            "invalid score value",
        ]
    )
    workbook.save(tracker_path)

    summary = LocalTrackerQualityAnalyzer(workbook_path=tracker_path).summarize(
        ["Applications"]
    )

    tab = summary.tabs[0]
    format_by_field = {field.canonical_field: field for field in tab.format_fields}
    assert summary.has_format_warnings is True
    assert tab.has_format_warnings is True
    assert format_by_field["status"].checked_count == 2
    assert format_by_field["status"].invalid_count == 1
    assert format_by_field["date_applied"].checked_count == 2
    assert format_by_field["date_applied"].invalid_count == 1
    assert format_by_field["job_url"].checked_count == 2
    assert format_by_field["job_url"].invalid_count == 1
    assert format_by_field["match_score"].checked_count == 2
    assert format_by_field["match_score"].invalid_count == 1
    assert summary.failed_quality_gates(fail_on_format_warnings=True) == (
        "format_warnings",
    )
    assert "Sample Company" not in repr(summary)
    assert "Sample Role" not in repr(summary)
    assert "Unknown Workflow Value" not in repr(summary)
    assert "invalid date value" not in repr(summary)
    assert "invalid url value" not in repr(summary)
    assert "invalid score value" not in repr(summary)
    assert str(tracker_path) not in repr(summary)
