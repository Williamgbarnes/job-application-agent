"""Deterministic, public-safe scoring rules for job leads.

The scoring engine is intentionally simple and transparent. It works with mock
or sanitized inputs, produces a `ScoreReport`, and does not call external
services or inspect private files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re

from job_application_agent.domain import (
    EmploymentType,
    JobLead,
    JobPostingSnapshot,
    ScorePriority,
    ScoreReport,
    WorkArrangement,
)


@dataclass(frozen=True)
class ScoringProfile:
    """Public-safe scoring preferences for deterministic role prioritization."""

    target_titles: tuple[str, ...] = field(default_factory=tuple)
    preferred_keywords: tuple[str, ...] = field(default_factory=tuple)
    disqualifying_keywords: tuple[str, ...] = field(default_factory=tuple)
    preferred_work_arrangements: tuple[WorkArrangement, ...] = (
        WorkArrangement.REMOTE,
        WorkArrangement.HYBRID,
    )
    preferred_employment_types: tuple[EmploymentType, ...] = (
        EmploymentType.FULL_TIME,
    )
    minimum_compensation: int | None = None


@dataclass(frozen=True)
class RuleResult:
    """Transparent result from one scoring rule."""

    rule_name: str
    points: int
    max_points: int
    rationale: str


@dataclass(frozen=True)
class ScoringResult:
    """Score plus rule-level explanations before conversion to ScoreReport."""

    score: int
    priority: ScorePriority
    rule_results: tuple[RuleResult, ...]

    @property
    def strengths(self) -> tuple[str, ...]:
        return tuple(result.rationale for result in self.rule_results if result.points > 0)

    @property
    def gaps(self) -> tuple[str, ...]:
        return tuple(result.rationale for result in self.rule_results if result.points <= 0)

    def to_score_report(
        self,
        *,
        report_id: str,
        job_lead_id: str,
        created_at: datetime | None = None,
    ) -> ScoreReport:
        """Convert the scoring result into the public-safe domain report."""

        return ScoreReport(
            id=report_id,
            job_lead_id=job_lead_id,
            score=self.score,
            priority=self.priority,
            strengths=self.strengths,
            gaps=self.gaps,
            rationale=_join_rationale(self.rule_results),
            created_at=created_at or datetime.now(timezone.utc),
        )


class TransparentScoringEngine:
    """Deterministic scoring engine with rule-level explanations."""

    def __init__(self, profile: ScoringProfile) -> None:
        self._profile = profile

    def score(self, lead: JobLead, snapshot: JobPostingSnapshot | None = None) -> ScoringResult:
        searchable_text = _searchable_text(lead, snapshot)
        rule_results = (
            _score_title_match(lead, self._profile),
            _score_work_arrangement(lead, self._profile),
            _score_employment_type(lead, self._profile),
            _score_compensation(lead, self._profile),
            _score_preferred_keywords(searchable_text, self._profile),
            _score_disqualifying_keywords(searchable_text, self._profile),
        )
        score = _clamp_score(sum(result.points for result in rule_results))
        return ScoringResult(
            score=score,
            priority=priority_from_score(score),
            rule_results=rule_results,
        )


def priority_from_score(score: int) -> ScorePriority:
    """Map a numeric score to a priority bucket."""

    if score >= 75:
        return ScorePriority.HIGH
    if score >= 50:
        return ScorePriority.MEDIUM
    return ScorePriority.LOW


def _score_title_match(lead: JobLead, profile: ScoringProfile) -> RuleResult:
    if not profile.target_titles:
        return RuleResult(
            "title_match",
            10,
            20,
            "No target titles configured; neutral title score.",
        )

    if _contains_any(lead.title, profile.target_titles):
        return RuleResult("title_match", 20, 20, "Role title matches a target title.")
    return RuleResult("title_match", 0, 20, "Role title does not match target titles.")


def _score_work_arrangement(lead: JobLead, profile: ScoringProfile) -> RuleResult:
    if lead.work_arrangement in profile.preferred_work_arrangements:
        return RuleResult(
            "work_arrangement",
            15,
            15,
            "Work arrangement matches preferred arrangements.",
        )
    if lead.work_arrangement == WorkArrangement.UNKNOWN:
        return RuleResult(
            "work_arrangement",
            5,
            15,
            "Work arrangement is unknown; partial credit only.",
        )
    return RuleResult(
        "work_arrangement",
        0,
        15,
        "Work arrangement does not match preferred arrangements.",
    )


def _score_employment_type(lead: JobLead, profile: ScoringProfile) -> RuleResult:
    if lead.employment_type in profile.preferred_employment_types:
        return RuleResult(
            "employment_type",
            10,
            10,
            "Employment type matches preferred types.",
        )
    if lead.employment_type == EmploymentType.UNKNOWN:
        return RuleResult(
            "employment_type",
            4,
            10,
            "Employment type is unknown; partial credit only.",
        )
    return RuleResult(
        "employment_type",
        0,
        10,
        "Employment type does not match preferred types.",
    )


def _score_compensation(lead: JobLead, profile: ScoringProfile) -> RuleResult:
    if profile.minimum_compensation is None:
        return RuleResult(
            "compensation",
            10,
            15,
            "No minimum compensation configured; neutral compensation score.",
        )
    if lead.compensation_max is None:
        return RuleResult(
            "compensation",
            5,
            15,
            "Compensation is unknown; partial credit only.",
        )
    if lead.compensation_max >= profile.minimum_compensation:
        return RuleResult(
            "compensation",
            15,
            15,
            "Compensation range can meet the configured minimum.",
        )
    return RuleResult(
        "compensation",
        0,
        15,
        "Compensation range is below the configured minimum.",
    )


def _score_preferred_keywords(text: str, profile: ScoringProfile) -> RuleResult:
    if not profile.preferred_keywords:
        return RuleResult(
            "preferred_keywords",
            10,
            25,
            "No preferred keywords configured; neutral keyword score.",
        )

    matched_keywords = _matched_terms(text, profile.preferred_keywords)
    if not matched_keywords:
        return RuleResult(
            "preferred_keywords",
            0,
            25,
            "No preferred keywords were found in the lead or posting snapshot.",
        )

    points = min(25, 5 * len(matched_keywords))
    return RuleResult(
        "preferred_keywords",
        points,
        25,
        f"Matched {len(matched_keywords)} preferred keyword(s).",
    )


def _score_disqualifying_keywords(text: str, profile: ScoringProfile) -> RuleResult:
    matched_keywords = _matched_terms(text, profile.disqualifying_keywords)
    if not matched_keywords:
        return RuleResult(
            "disqualifying_keywords",
            15,
            15,
            "No disqualifying keywords were found.",
        )
    return RuleResult(
        "disqualifying_keywords",
        -30,
        15,
        f"Found {len(matched_keywords)} disqualifying keyword(s).",
    )


def _searchable_text(lead: JobLead, snapshot: JobPostingSnapshot | None) -> str:
    parts = [lead.company, lead.title, lead.location or ""]
    if snapshot is not None:
        parts.extend(snapshot.normalized_requirements)
        parts.extend(snapshot.normalized_responsibilities)
        if snapshot.raw_text:
            parts.append(snapshot.raw_text)
    return " ".join(parts)


def _contains_any(value: str, terms: tuple[str, ...]) -> bool:
    return bool(_matched_terms(value, terms))


def _matched_terms(text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    normalized_text = _normalize_text(text)
    return tuple(
        term for term in terms if _normalize_text(term) and _normalize_text(term) in normalized_text
    )


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def _join_rationale(rule_results: tuple[RuleResult, ...]) -> str:
    return " ".join(result.rationale for result in rule_results)
