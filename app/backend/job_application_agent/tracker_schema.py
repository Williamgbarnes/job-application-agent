"""Public-safe tracker schema mapping helpers.

This module maps discovered tracker headers to canonical field names. It does
not read row data and does not store private tracker exports.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from job_application_agent.integrations.sheets import SheetHeaders, TrackerHeadersSummary


@dataclass(frozen=True)
class CanonicalField:
    """Definition for one public-safe canonical tracker field."""

    name: str
    required: bool
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class HeaderFieldMapping:
    """Mapping from one source header to a canonical field."""

    source_header: str
    column_index: int
    canonical_field: str | None
    confidence: str


@dataclass(frozen=True)
class TabSchemaMapping:
    """Public-safe schema mapping for one tracker tab."""

    title: str
    header_row: int
    mapped_fields: tuple[HeaderFieldMapping, ...]
    unmapped_headers: tuple[str, ...]
    missing_required_fields: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing_required_fields


@dataclass(frozen=True)
class TrackerSchemaMapping:
    """Public-safe schema mapping for tracker tabs."""

    tabs: tuple[TabSchemaMapping, ...]

    @property
    def is_complete(self) -> bool:
        return all(tab.is_complete for tab in self.tabs)


TRACKER_TAB_SCHEMAS: dict[str, tuple[CanonicalField, ...]] = {
    "Applications": (
        CanonicalField("company", True, ("company", "employer", "organization")),
        CanonicalField("role", True, ("role", "title", "job title", "position")),
        CanonicalField("status", True, ("status", "application status")),
        CanonicalField(
            "date_applied",
            False,
            ("date applied", "applied date", "application date"),
        ),
        CanonicalField("job_url", False, ("url", "job url", "posting url", "link")),
        CanonicalField("match_score", False, ("match score", "score", "fit score")),
        CanonicalField("contact_date", False, ("contact date", "follow-up date")),
    ),
    "Daily Leads": (
        CanonicalField("company", True, ("company", "employer", "organization")),
        CanonicalField("role", True, ("role", "title", "job title", "position")),
        CanonicalField("job_url", True, ("url", "job url", "posting url", "link")),
        CanonicalField("match_score", False, ("match score", "score", "fit score")),
        CanonicalField("source", False, ("source", "job board", "site")),
    ),
    "Contacts": (
        CanonicalField("contact_name", True, ("name", "contact", "contact name")),
        CanonicalField("company", False, ("company", "employer", "organization")),
        CanonicalField("email", False, ("email", "email address")),
        CanonicalField("last_contacted", False, ("last contacted", "contacted", "contact date")),
    ),
    "Rejected Applications": (
        CanonicalField("company", True, ("company", "employer", "organization")),
        CanonicalField("role", True, ("role", "title", "job title", "position")),
        CanonicalField("status", False, ("status", "application status")),
        CanonicalField("archive_reason", False, ("archive reason", "reason", "rejection reason")),
    ),
    "Recruiter Apply": (
        CanonicalField("company", True, ("company", "employer", "organization")),
        CanonicalField("role", True, ("role", "title", "job title", "position")),
        CanonicalField("recruiter", False, ("recruiter", "recruiter name", "contact")),
        CanonicalField("next_step", False, ("next step", "action", "todo")),
    ),
}


def map_tracker_headers(headers_summary: TrackerHeadersSummary) -> TrackerSchemaMapping:
    """Map discovered tracker headers to public-safe canonical fields."""

    return TrackerSchemaMapping(
        tabs=tuple(map_sheet_headers(sheet_headers) for sheet_headers in headers_summary.tabs)
    )


def map_sheet_headers(sheet_headers: SheetHeaders) -> TabSchemaMapping:
    """Map one sheet's discovered headers to public-safe canonical fields."""

    schema = TRACKER_TAB_SCHEMAS.get(sheet_headers.title, ())
    alias_index = _build_alias_index(schema)
    mapped_fields = tuple(
        _map_header(header, column_index, alias_index)
        for column_index, header in enumerate(sheet_headers.headers, start=1)
    )
    mapped_canonical_fields = {
        field.canonical_field for field in mapped_fields if field.canonical_field
    }
    required_fields = {field.name for field in schema if field.required}

    return TabSchemaMapping(
        title=sheet_headers.title,
        header_row=sheet_headers.header_row,
        mapped_fields=mapped_fields,
        unmapped_headers=tuple(
            field.source_header for field in mapped_fields if field.canonical_field is None
        ),
        missing_required_fields=tuple(
            sorted(required_fields.difference(mapped_canonical_fields))
        ),
    )


def _map_header(
    header: str,
    column_index: int,
    alias_index: dict[str, str],
) -> HeaderFieldMapping:
    normalized_header = _normalize_header_key(header)
    canonical_field = alias_index.get(normalized_header)
    return HeaderFieldMapping(
        source_header=header,
        column_index=column_index,
        canonical_field=canonical_field,
        confidence="exact_alias" if canonical_field else "unmapped",
    )


def _build_alias_index(schema: tuple[CanonicalField, ...]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for field in schema:
        aliases[_normalize_header_key(field.name)] = field.name
        for alias in field.aliases:
            aliases[_normalize_header_key(alias)] = field.name
    return aliases


def _normalize_header_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())
