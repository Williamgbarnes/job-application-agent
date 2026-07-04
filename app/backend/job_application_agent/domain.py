"""Public-safe domain models for job application workflows.

These models are intentionally small, immutable, and dependency-free. They are
safe for tests and demos because they do not include private resume content,
contact details, generated application materials, or production identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Iterable
from urllib.parse import urlparse


class DomainValidationError(ValueError):
    """Raised when a public-safe domain model is invalid."""


class WorkArrangement(StrEnum):
    """Supported work arrangement values."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNKNOWN = "unknown"


class EmploymentType(StrEnum):
    """Supported employment type values."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class LeadStatus(StrEnum):
    """Read-only status values for discovered or tracked leads."""

    NEW = "new"
    REVIEW = "review"
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ScorePriority(StrEnum):
    """Priority buckets derived from transparent scoring rules."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ApplicationPackageStatus(StrEnum):
    """Human-in-the-loop package lifecycle states."""

    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    BLOCKED = "blocked"


class ApplicationEventType(StrEnum):
    """Public-safe event types for application workflow history."""

    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    FOLLOW_UP_DUE = "follow_up_due"
    HUMAN_REVIEWED = "human_reviewed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class JobLead:
    """A discovered or tracked role before downstream package generation."""

    id: str
    source: str
    company: str
    title: str
    location: str | None = None
    work_arrangement: WorkArrangement = WorkArrangement.UNKNOWN
    employment_type: EmploymentType = EmploymentType.UNKNOWN
    compensation_min: int | None = None
    compensation_max: int | None = None
    posting_url: str | None = None
    posted_date: date | None = None
    closing_date: date | None = None
    status: LeadStatus = LeadStatus.NEW

    def __post_init__(self) -> None:
        _require_text(self.id, "id")
        _require_text(self.source, "source")
        _require_text(self.company, "company")
        _require_text(self.title, "title")
        _validate_compensation_range(self.compensation_min, self.compensation_max)
        _validate_url(self.posting_url, "posting_url")
        _validate_date_order(self.posted_date, self.closing_date)


@dataclass(frozen=True)
class JobPostingSnapshot:
    """Immutable public-safe snapshot used for scoring and auditability."""

    id: str
    job_lead_id: str
    captured_at: datetime
    source_url: str | None = None
    raw_text: str | None = None
    normalized_requirements: tuple[str, ...] = field(default_factory=tuple)
    normalized_responsibilities: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(self.id, "id")
        _require_text(self.job_lead_id, "job_lead_id")
        _validate_aware_datetime(self.captured_at, "captured_at")
        _validate_url(self.source_url, "source_url")
        _validate_text_items(self.normalized_requirements, "normalized_requirements")
        _validate_text_items(
            self.normalized_responsibilities, "normalized_responsibilities"
        )


@dataclass(frozen=True)
class ScoreReport:
    """Transparent score explanation for prioritizing a role."""

    id: str
    job_lead_id: str
    score: int
    priority: ScorePriority
    strengths: tuple[str, ...] = field(default_factory=tuple)
    gaps: tuple[str, ...] = field(default_factory=tuple)
    rationale: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        _require_text(self.id, "id")
        _require_text(self.job_lead_id, "job_lead_id")
        if not 0 <= self.score <= 100:
            raise DomainValidationError("score must be between 0 and 100.")
        _validate_text_items(self.strengths, "strengths")
        _validate_text_items(self.gaps, "gaps")
        _validate_aware_datetime(self.created_at, "created_at")


@dataclass(frozen=True)
class ApplicationPackage:
    """Proposed application package awaiting human review or approval."""

    id: str
    job_lead_id: str
    resume_variant_id: str | None = None
    cover_letter_variant_id: str | None = None
    status: ApplicationPackageStatus = ApplicationPackageStatus.DRAFT
    review_notes: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "id")
        _require_text(self.job_lead_id, "job_lead_id")


@dataclass(frozen=True)
class ApplicationEvent:
    """Public-safe application workflow event."""

    id: str
    application_id: str
    event_type: ApplicationEventType
    event_date: date
    notes: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "id")
        _require_text(self.application_id, "application_id")


def _require_text(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise DomainValidationError(f"{field_name} is required.")


def _validate_text_items(values: Iterable[str], field_name: str) -> None:
    for value in values:
        if not value or not value.strip():
            raise DomainValidationError(f"{field_name} cannot contain blank values.")


def _validate_compensation_range(
    compensation_min: int | None, compensation_max: int | None
) -> None:
    for field_name, value in (
        ("compensation_min", compensation_min),
        ("compensation_max", compensation_max),
    ):
        if value is not None and value < 0:
            raise DomainValidationError(f"{field_name} cannot be negative.")

    if (
        compensation_min is not None
        and compensation_max is not None
        and compensation_min > compensation_max
    ):
        raise DomainValidationError(
            "compensation_min cannot be greater than compensation_max."
        )


def _validate_url(value: str | None, field_name: str) -> None:
    if value is None:
        return
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DomainValidationError(f"{field_name} must be an http(s) URL.")


def _validate_date_order(start_date: date | None, end_date: date | None) -> None:
    if start_date is not None and end_date is not None and end_date < start_date:
        raise DomainValidationError("closing_date cannot be before posted_date.")


def _validate_aware_datetime(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainValidationError(f"{field_name} must include timezone information.")
