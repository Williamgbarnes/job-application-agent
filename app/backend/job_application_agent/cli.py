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
    headers_parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to local env file. Defaults to .env in the current directory.",
    )
    headers_parser.add_argument(
        "--tab",
        action="append",
        dest="tabs",
        help=(
            "Tracker tab to inspect. Repeat for multiple tabs. Defaults to "
            f"{', '.join(DEFAULT_TRACKER_HEADER_TABS)}."
        ),
    )
    headers_parser.add_argument(
        "--header-row",
        type=int,
        default=1,
        help="1-based row number containing headers. Defaults to 1.",
    )

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

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
