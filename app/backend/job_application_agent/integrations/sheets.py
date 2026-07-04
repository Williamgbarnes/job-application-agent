"""Read-only Google Sheets metadata adapter.

The adapter intentionally starts with spreadsheet metadata and tab discovery only.
It does not expose write methods and does not hard-code private spreadsheet IDs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from job_application_agent.config import ConfigurationError, RuntimeConfig


class SheetsAdapterError(RuntimeError):
    """Raised when a Sheets adapter cannot complete a read-only operation."""


@dataclass(frozen=True)
class SheetTab:
    """Public-safe summary of one spreadsheet tab."""

    title: str
    sheet_id: int
    index: int
    row_count: int | None = None
    column_count: int | None = None
    frozen_row_count: int | None = None


@dataclass(frozen=True)
class SpreadsheetSummary:
    """Public-safe spreadsheet metadata.

    The spreadsheet ID is deliberately excluded so summaries are safe to log.
    """

    title: str
    locale: str | None
    time_zone: str | None
    tabs: tuple[SheetTab, ...]

    @property
    def tab_titles(self) -> tuple[str, ...]:
        return tuple(tab.title for tab in self.tabs)


class SheetsMetadataProvider(Protocol):
    """Protocol shared by mock and Google-backed adapters."""

    def get_metadata(self) -> SpreadsheetSummary:
        """Return read-only spreadsheet metadata."""


class MockSheetsAdapter:
    """Mock adapter for public demos and tests."""

    def __init__(self, summary: SpreadsheetSummary | None = None) -> None:
        self._summary = summary or SpreadsheetSummary(
            title="Mock Job Tracker",
            locale="en_US",
            time_zone="America/New_York",
            tabs=(
                SheetTab(title="Dashboard", sheet_id=0, index=0),
                SheetTab(title="Applications", sheet_id=101, index=1),
                SheetTab(title="Daily Leads", sheet_id=102, index=2),
                SheetTab(title="Contacts", sheet_id=103, index=3),
                SheetTab(title="Scan Setup", sheet_id=104, index=4),
                SheetTab(title="Lists", sheet_id=105, index=5),
                SheetTab(title="Rejected Applications", sheet_id=106, index=6),
                SheetTab(title="Match Score Rubric", sheet_id=107, index=7),
                SheetTab(title="Recruiter Apply", sheet_id=108, index=8),
            ),
        )

    def get_metadata(self) -> SpreadsheetSummary:
        return self._summary


class GoogleSheetsAdapter:
    """Read-only Google Sheets adapter for staging/private runtime use."""

    METADATA_FIELDS = (
        "properties(title,locale,timeZone),"
        "sheets(properties(sheetId,title,index,gridProperties(rowCount,columnCount,frozenRowCount)))"
    )

    def __init__(self, *, spreadsheet_id: str, service: Any | None = None) -> None:
        if not spreadsheet_id:
            raise ConfigurationError("A spreadsheet ID is required for GoogleSheetsAdapter.")
        self._spreadsheet_id = spreadsheet_id
        self._service = service

    @classmethod
    def from_config(cls, config: RuntimeConfig) -> "GoogleSheetsAdapter":
        if config.runtime_mode == "staging":
            spreadsheet_id = config.google_sheets_staging_id
        elif config.runtime_mode == "production":
            spreadsheet_id = config.google_sheets_production_id
        else:
            raise ConfigurationError(
                "GoogleSheetsAdapter requires RUNTIME_MODE=staging or production."
            )

        if not spreadsheet_id:
            raise ConfigurationError(
                "Configured runtime mode is missing its Google Sheets spreadsheet ID."
            )

        return cls(spreadsheet_id=spreadsheet_id)

    def get_metadata(self) -> SpreadsheetSummary:
        service = self._service or _build_google_sheets_service()
        try:
            payload = (
                service.spreadsheets()
                .get(spreadsheetId=self._spreadsheet_id, fields=self.METADATA_FIELDS)
                .execute()
            )
        except Exception as exc:  # pragma: no cover - depends on Google client behavior
            raise SheetsAdapterError(
                "Failed to read Google Sheets metadata. Confirm credentials and access."
            ) from exc

        return spreadsheet_summary_from_google_payload(payload)


def build_sheets_adapter(config: RuntimeConfig) -> SheetsMetadataProvider:
    """Build the right adapter for the selected runtime mode."""

    if config.runtime_mode == "mock":
        return MockSheetsAdapter()
    return GoogleSheetsAdapter.from_config(config)


def spreadsheet_summary_from_google_payload(
    payload: Mapping[str, Any]
) -> SpreadsheetSummary:
    """Convert a Google Sheets API spreadsheet payload to a safe summary."""

    properties = payload.get("properties") or {}
    tabs: list[SheetTab] = []

    for sheet in payload.get("sheets") or []:
        sheet_properties = sheet.get("properties") or {}
        grid_properties = sheet_properties.get("gridProperties") or {}
        tabs.append(
            SheetTab(
                title=str(sheet_properties.get("title") or ""),
                sheet_id=int(sheet_properties.get("sheetId") or 0),
                index=int(sheet_properties.get("index") or 0),
                row_count=_optional_int(grid_properties.get("rowCount")),
                column_count=_optional_int(grid_properties.get("columnCount")),
                frozen_row_count=_optional_int(grid_properties.get("frozenRowCount")),
            )
        )

    return SpreadsheetSummary(
        title=str(properties.get("title") or "Untitled spreadsheet"),
        locale=_optional_str(properties.get("locale")),
        time_zone=_optional_str(properties.get("timeZone")),
        tabs=tuple(tabs),
    )


def _build_google_sheets_service() -> Any:
    """Build a Google Sheets service using application default credentials."""

    try:
        import google.auth
        from googleapiclient.discovery import build
    except ImportError as exc:  # pragma: no cover - import depends on optional deps
        raise SheetsAdapterError(
            "Google Sheets support requires the optional 'google' dependencies. "
            "Install with: pip install -e '.[google]'"
        ) from exc

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
