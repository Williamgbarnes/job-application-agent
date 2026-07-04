"""Small CLI helpers for local development.

These commands are intentionally read-only and log-safe.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from job_application_agent.config import RuntimeConfig
from job_application_agent.integrations.sheets import (
    DEFAULT_TRACKER_HEADER_TABS,
    build_sheets_adapter,
)
from job_application_agent.mock_dashboard import (
    DEFAULT_DASHBOARD_TOP_LIMIT,
    build_mock_dashboard,
    mock_dashboard_to_dict,
)
from job_application_agent.mock_dashboard_report import render_mock_dashboard_markdown
from job_application_agent.mock_jobs import (
    DEFAULT_MOCK_JOBS_PATH,
    mock_scored_job_to_dict,
    score_mock_jobs,
)
from job_application_agent.review_queue import (
    build_mock_review_queue,
    parse_score_priority,
    review_queue_to_dict,
)
from job_application_agent.tracker_quality import LocalTrackerQualityAnalyzer
from job_application_agent.tracker_schema import map_tracker_headers

QUALITY_GATE_FAILURE_EXIT_CODE = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Job Application Agent utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sheets_parser = subparsers.add_parser(
        "sheets-metadata", help="Print log-safe spreadsheet metadata"
    )
    sheets_parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to local env file. Defaults to .env in the current directory.",
    )

    headers_parser = subparsers.add_parser(
        "tracker-headers", help="Print log-safe tracker header metadata"
    )
    _add_header_args(headers_parser)

    schema_parser = subparsers.add_parser(
        "tracker-schema", help="Map tracker headers to canonical fields"
    )
    _add_header_args(schema_parser)

    quality_parser = subparsers.add_parser(
        "tracker-quality", help="Print log-safe tracker quality counts"
    )
    _add_header_args(quality_parser)
    quality_parser.add_argument(
        "--max-records",
        type=int,
        default=1000,
        help="Maximum non-blank records to scan per tab. Defaults to 1000.",
    )
    quality_parser.add_argument(
        "--fail-on-incomplete-schema",
        action="store_true",
        help="Return a non-zero exit code if required canonical columns are missing.",
    )
    quality_parser.add_argument(
        "--fail-on-required-blanks",
        action="store_true",
        help="Return a non-zero exit code if required canonical fields have blanks.",
    )
    quality_parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable all tracker quality gates.",
    )

    mock_score_parser = subparsers.add_parser(
        "mock-score", help="Score sanitized mock job fixtures"
    )
    _add_mock_fixture_arg(mock_score_parser)

    mock_queue_parser = subparsers.add_parser(
        "mock-queue", help="Print a sanitized mock priority queue"
    )
    _add_mock_fixture_arg(mock_queue_parser)
    _add_mock_queue_filter_args(mock_queue_parser)

    mock_dashboard_parser = subparsers.add_parser(
        "mock-dashboard", help="Print a sanitized mock dashboard summary"
    )
    _add_mock_fixture_arg(mock_dashboard_parser)
    _add_mock_queue_filter_args(mock_dashboard_parser)
    _add_mock_dashboard_top_limit_arg(mock_dashboard_parser)

    mock_dashboard_report_parser = subparsers.add_parser(
        "mock-dashboard-report",
        help="Print a sanitized mock dashboard Markdown report",
    )
    _add_mock_fixture_arg(mock_dashboard_report_parser)
    _add_mock_queue_filter_args(mock_dashboard_report_parser)
    _add_mock_dashboard_top_limit_arg(mock_dashboard_report_parser)

    args = parser.parse_args(argv)

    if args.command == "sheets-metadata":
        config = RuntimeConfig.from_env(env_file=Path(args.env_file))
        adapter = build_sheets_adapter(config)
        summary = adapter.get_metadata()
        print(
            json.dumps(
                {
                    "config": config.safe_summary(),
                    "spreadsheet": {
                        "title": summary.title,
                        "locale": summary.locale,
                        "time_zone": summary.time_zone,
                        "tabs": [tab.__dict__ for tab in summary.tabs],
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "tracker-headers":
        config = RuntimeConfig.from_env(env_file=Path(args.env_file))
        adapter = build_sheets_adapter(config)
        summary = adapter.get_headers(args.tabs, header_row=args.header_row)
        print(
            json.dumps(
                {
                    "config": config.safe_summary(),
                    "tracker_headers": {
                        "tabs": [tab.__dict__ for tab in summary.tabs],
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "tracker-schema":
        config = RuntimeConfig.from_env(env_file=Path(args.env_file))
        adapter = build_sheets_adapter(config)
        headers = adapter.get_headers(args.tabs, header_row=args.header_row)
        schema = map_tracker_headers(headers)
        print(
            json.dumps(
                {
                    "config": config.safe_summary(),
                    "tracker_schema": {
                        "is_complete": schema.is_complete,
                        "tabs": [
                            {
                                "title": tab.title,
                                "header_row": tab.header_row,
                                "is_complete": tab.is_complete,
                                "mapped_fields": [
                                    field.__dict__ for field in tab.mapped_fields
                                ],
                                "unmapped_headers": list(tab.unmapped_headers),
                                "missing_required_fields": list(
                                    tab.missing_required_fields
                                ),
                            }
                            for tab in schema.tabs
                        ],
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "tracker-quality":
        config = RuntimeConfig.from_env(env_file=Path(args.env_file))
        analyzer = LocalTrackerQualityAnalyzer.from_config(config)
        summary = analyzer.summarize(
            args.tabs,
            header_row=args.header_row,
            max_records=args.max_records,
        )
        fail_on_incomplete_schema = args.strict or args.fail_on_incomplete_schema
        fail_on_required_blanks = args.strict or args.fail_on_required_blanks
        failed_quality_gates = summary.failed_quality_gates(
            fail_on_incomplete_schema=fail_on_incomplete_schema,
            fail_on_required_blanks=fail_on_required_blanks,
        )
        print(
            json.dumps(
                {
                    "config": config.safe_summary(),
                    "tracker_quality": {
                        "is_schema_complete": summary.is_schema_complete,
                        "has_required_blanks": summary.has_required_blanks,
                        "failed_quality_gates": list(failed_quality_gates),
                        "max_records": summary.max_records,
                        "scanned_records": summary.scanned_records,
                        "tabs": [
                            {
                                "title": tab.title,
                                "scanned_records": tab.scanned_records,
                                "blank_records_skipped": tab.blank_records_skipped,
                                "is_schema_complete": tab.is_schema_complete,
                                "has_required_blanks": tab.has_required_blanks,
                                "missing_required_fields": list(
                                    tab.missing_required_fields
                                ),
                                "unmapped_headers": list(tab.unmapped_headers),
                                "required_fields": [
                                    field.__dict__ for field in tab.required_fields
                                ],
                                "truncated": tab.truncated,
                            }
                            for tab in summary.tabs
                        ],
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        if failed_quality_gates:
            return QUALITY_GATE_FAILURE_EXIT_CODE
        return 0

    if args.command == "mock-score":
        scored_jobs = score_mock_jobs(Path(args.fixture))
        print(
            json.dumps(
                {
                    "mock_score_reports": {
                        "count": len(scored_jobs),
                        "jobs": [
                            mock_scored_job_to_dict(scored_job)
                            for scored_job in scored_jobs
                        ],
                    },
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "mock-queue":
        priorities = tuple(parse_score_priority(value) for value in args.priority or ())
        queue = build_mock_review_queue(
            Path(args.fixture),
            min_score=args.min_score,
            priorities=priorities,
        )
        print(
            json.dumps(
                {
                    "mock_queue": review_queue_to_dict(
                        queue,
                        min_score=args.min_score,
                        priorities=priorities,
                    )
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "mock-dashboard":
        priorities = tuple(parse_score_priority(value) for value in args.priority or ())
        dashboard = build_mock_dashboard(
            Path(args.fixture),
            min_score=args.min_score,
            priorities=priorities,
            top_limit=args.top_limit,
        )
        print(
            json.dumps(
                {
                    "mock_dashboard": mock_dashboard_to_dict(
                        dashboard,
                        min_score=args.min_score,
                        priorities=priorities,
                    )
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "mock-dashboard-report":
        priorities = tuple(parse_score_priority(value) for value in args.priority or ())
        dashboard = build_mock_dashboard(
            Path(args.fixture),
            min_score=args.min_score,
            priorities=priorities,
            top_limit=args.top_limit,
        )
        print(
            render_mock_dashboard_markdown(
                dashboard,
                min_score=args.min_score,
                priorities=priorities,
            ),
            end="",
        )
        return 0

    return 1


def _add_header_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to local env file. Defaults to .env in the current directory.",
    )
    parser.add_argument(
        "--tab",
        action="append",
        dest="tabs",
        help=(
            "Tracker tab to inspect. Repeat for multiple tabs. Defaults to "
            f"{', '.join(DEFAULT_TRACKER_HEADER_TABS)}."
        ),
    )
    parser.add_argument(
        "--header-row",
        type=int,
        default=1,
        help="1-based row number containing headers. Defaults to 1.",
    )


def _add_mock_fixture_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--fixture",
        default=str(DEFAULT_MOCK_JOBS_PATH),
        help="Path to sanitized mock jobs JSON fixture.",
    )


def _add_mock_queue_filter_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--min-score",
        type=int,
        default=None,
        help="Only include mock queue items with this score or higher.",
    )
    parser.add_argument(
        "--priority",
        action="append",
        default=None,
        help="Priority to include. Repeat for multiple values: high, medium, low.",
    )


def _add_mock_dashboard_top_limit_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--top-limit",
        type=_non_negative_int,
        default=DEFAULT_DASHBOARD_TOP_LIMIT,
        help=(
            "Maximum ranked mock queue items to include. Defaults to "
            f"{DEFAULT_DASHBOARD_TOP_LIMIT}."
        ),
    )


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return parsed


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
