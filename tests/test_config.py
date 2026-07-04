from pathlib import Path

import pytest

from job_application_agent.config import ConfigurationError, RuntimeConfig, load_env_file


def test_default_runtime_config_is_mock_and_safe() -> None:
    config = RuntimeConfig.from_mapping({})

    assert config.runtime_mode == "mock"
    assert config.dry_run is True
    assert config.require_human_approval is True
    assert config.allow_external_submission is False


def test_staging_requires_local_path_or_staging_sheet_id() -> None:
    with pytest.raises(ConfigurationError, match="STAGING_TRACKER_PATH"):
        RuntimeConfig.from_mapping({"RUNTIME_MODE": "staging"})


def test_staging_accepts_local_tracker_path() -> None:
    config = RuntimeConfig.from_mapping(
        {
            "RUNTIME_MODE": "staging",
            "STAGING_TRACKER_PATH": "C:/src/job-application-agent/data/private/staging.xlsx",
        }
    )

    assert config.staging_tracker_path == Path(
        "C:/src/job-application-agent/data/private/staging.xlsx"
    )
    assert config.google_sheets_staging_id is None


def test_production_requires_production_sheet_id() -> None:
    with pytest.raises(ConfigurationError, match="GOOGLE_SHEETS_PRODUCTION_ID"):
        RuntimeConfig.from_mapping({"RUNTIME_MODE": "production"})


def test_external_submission_requires_human_approval() -> None:
    with pytest.raises(ConfigurationError, match="human approval"):
        RuntimeConfig.from_mapping(
            {
                "ALLOW_EXTERNAL_SUBMISSION": "true",
                "REQUIRE_HUMAN_APPROVAL": "false",
            }
        )


def test_safe_summary_does_not_expose_private_ids_or_paths() -> None:
    private_id = "private-spreadsheet-id"
    private_path = "C:/private/staging_job_tracker.xlsx"
    config = RuntimeConfig.from_mapping(
        {
            "RUNTIME_MODE": "staging",
            "STAGING_TRACKER_PATH": private_path,
            "GOOGLE_SHEETS_STAGING_ID": private_id,
        }
    )

    summary = config.safe_summary()

    assert summary["has_staging_tracker_path"] is True
    assert summary["has_google_sheets_staging_id"] is True
    assert private_id not in repr(summary)
    assert private_path not in repr(summary)


def test_load_env_file_reads_simple_key_values(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\nRUNTIME_MODE=staging\nSTAGING_TRACKER_PATH='C:/private/staging.xlsx'\n",
        encoding="utf-8",
    )

    values = load_env_file(env_file)

    assert values["RUNTIME_MODE"] == "staging"
    assert values["STAGING_TRACKER_PATH"] == "C:/private/staging.xlsx"
