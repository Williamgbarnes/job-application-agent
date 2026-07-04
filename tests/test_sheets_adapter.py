from typing import Any

import pytest

from job_application_agent.config import RuntimeConfig
from job_application_agent.integrations.sheets import (
    GoogleSheetsAdapter,
    MockSheetsAdapter,
    build_sheets_adapter,
    spreadsheet_summary_from_google_payload,
)


EXPECTED_TABS = {
    "Dashboard",
    "Applications",
    "Daily Leads",
    "Contacts",
    "Scan Setup",
    "Lists",
    "Rejected Applications",
    "Match Score Rubric",
    "Recruiter Apply",
}


def test_mock_adapter_returns_expected_tracker_tabs() -> None:
    summary = MockSheetsAdapter().get_metadata()

    assert summary.title == "Mock Job Tracker"
    assert set(summary.tab_titles) == EXPECTED_TABS


def test_build_sheets_adapter_defaults_to_mock() -> None:
    adapter = build_sheets_adapter(RuntimeConfig.from_mapping({}))

    assert isinstance(adapter, MockSheetsAdapter)


def test_build_sheets_adapter_uses_google_for_staging() -> None:
    config = RuntimeConfig.from_mapping(
        {
            "RUNTIME_MODE": "staging",
            "GOOGLE_SHEETS_STAGING_ID": "private-id",
        }
    )

    adapter = build_sheets_adapter(config)

    assert isinstance(adapter, GoogleSheetsAdapter)


def test_spreadsheet_summary_from_google_payload_is_log_safe() -> None:
    payload = {
        "spreadsheetId": "private-id-that-should-not-be-returned",
        "properties": {
            "title": "Copy of Job Tracker",
            "locale": "en_US",
            "timeZone": "America/New_York",
        },
        "sheets": [
            {
                "properties": {
                    "sheetId": 101,
                    "title": "Applications",
                    "index": 1,
                    "gridProperties": {
                        "rowCount": 93,
                        "columnCount": 31,
                        "frozenRowCount": 1,
                    },
                }
            }
        ],
    }

    summary = spreadsheet_summary_from_google_payload(payload)

    assert summary.title == "Copy of Job Tracker"
    assert summary.time_zone == "America/New_York"
    assert summary.tabs[0].title == "Applications"
    assert summary.tabs[0].row_count == 93
    assert "private-id-that-should-not-be-returned" not in repr(summary)


def test_google_adapter_reads_metadata_with_private_id_only_in_request() -> None:
    private_id = "private-id"
    fake_service = FakeSheetsService(
        {
            "properties": {"title": "Copy of Job Tracker"},
            "sheets": [
                {
                    "properties": {
                        "sheetId": 0,
                        "title": "Dashboard",
                        "index": 0,
                        "gridProperties": {"rowCount": 100, "columnCount": 26},
                    }
                }
            ],
        }
    )
    adapter = GoogleSheetsAdapter(spreadsheet_id=private_id, service=fake_service)

    summary = adapter.get_metadata()

    assert summary.title == "Copy of Job Tracker"
    assert summary.tab_titles == ("Dashboard",)
    assert fake_service.last_get_kwargs["spreadsheetId"] == private_id
    assert fake_service.last_get_kwargs["fields"] == GoogleSheetsAdapter.METADATA_FIELDS
    assert private_id not in repr(summary)


class FakeSheetsService:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.last_get_kwargs: dict[str, Any] = {}

    def spreadsheets(self) -> "FakeSheetsService":
        return self

    def get(self, **kwargs: Any) -> "FakeRequest":
        self.last_get_kwargs = kwargs
        return FakeRequest(self.payload)


class FakeRequest:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def execute(self) -> dict[str, Any]:
        return self.payload
