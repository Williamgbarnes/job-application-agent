"""Markdown report rendering for public-safe mock dashboards.

The renderer turns an in-memory mock dashboard into static Markdown for local
portfolio demos. It does not read private files, call external services, or write
any output by itself.
"""

from __future__ import annotations

from typing import Any, Iterable

from job_application_agent.domain import ScorePriority
from job_application_agent.mock_dashboard import MockDashboard, mock_dashboard_to_dict


def render_mock_dashboard_markdown(
    dashboard: MockDashboard,
    *,
    min_score: int | None = None,
    priorities: Iterable[ScorePriority] | None = None,
) -> str:
    """Render a mock dashboard as static public-safe Markdown."""

    dashboard_data = mock_dashboard_to_dict(
        dashboard,
        min_score=min_score,
        priorities=priorities,
    )
    summary = dashboard_data["summary"]
    score_summary = summary["score_summary"]
    filters = dashboard_data["filters"]

    lines = [
        "# Mock Job Review Dashboard",
        "",
        "Public-safe Phase 2 demo report generated from sanitized mock fixtures.",
        "",
        "## Filters",
        "",
        f"- Minimum score: {_format_optional(filters['min_score'])}",
        f"- Priorities: {_format_list(filters['priorities'])}",
        f"- Top item limit: {dashboard_data['top_limit']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Mock leads | {summary['count']} |",
        f"| Average score | {_format_optional(score_summary['average'])} |",
        f"| Highest score | {_format_optional(score_summary['max'])} |",
        f"| Lowest score | {_format_optional(score_summary['min'])} |",
        "",
        "## Priority Counts",
        "",
        "| Priority | Count |",
        "| --- | ---: |",
    ]
    lines.extend(_count_rows(summary["priority_counts"]))
    lines.extend(
        [
            "",
            "## Review Recommendations",
            "",
            "| Recommendation | Count |",
            "| --- | ---: |",
        ]
    )
    lines.extend(_count_rows(summary["recommendation_counts"]))
    lines.extend(
        [
            "",
            "## Top Review Queue Items",
            "",
            (
                "| Rank | Mock job | Company | Title | Score | Priority | "
                "Recommendation | Rationale |"
            ),
            "| ---: | --- | --- | --- | ---: | --- | --- | --- |",
        ]
    )
    lines.extend(_top_item_rows(dashboard_data["top_items"]))
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "",
            (
                "This report is generated from sanitized mock fixtures only. It "
                "does not read `.env`, private tracker exports, resumes, "
                "credentials, contacts, production IDs, or generated application "
                "materials."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def _count_rows(counts: dict[str, int]) -> list[str]:
    return [f"| {_humanize_key(key)} | {value} |" for key, value in counts.items()]


def _top_item_rows(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return [
            (
                "| — | No mock queue items matched the selected filters. | — | "
                "— | — | — | — | — |"
            )
        ]

    return [
        _top_item_row(item)
        for item in items
    ]


def _top_item_row(item: dict[str, Any]) -> str:
    return (
        "| {rank} | {job_id} | {company} | {title} | {score} | {priority} | "
        "{recommendation} | {rationale} |"
    ).format(
        rank=item["rank"],
        job_id=_escape_cell(item["job_id"]),
        company=_escape_cell(item["company"]),
        title=_escape_cell(item["title"]),
        score=item["score"],
        priority=_escape_cell(item["priority"]),
        recommendation=_escape_cell(item["recommendation"]),
        rationale=_escape_cell(item["rationale"]),
    )


def _format_optional(value: object | None) -> str:
    if value is None:
        return "not set"
    return str(value)


def _format_list(values: list[str]) -> str:
    if not values:
        return "all"
    return ", ".join(values)


def _humanize_key(value: str) -> str:
    return value.replace("_", " ").title()


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()
