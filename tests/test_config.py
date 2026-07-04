from pathlib import Path

import pytest

from job_application_agent.config import ConfigurationError, RuntimeConfig, load_env_file


def test_default_runtime_config_is_mock_and_safe() -> None:
    config = RuntimeConfig.from_mapping({})

    assert config.runtime_mode == "mock"
    assert config.dry_run is True
    assert config.require_human_approval is True
    assert config.allow_external_submission is False


def test_staging_requires_staging_sheet_id() -> None:
    with pytest.raises(ConfigurationError, match="GOOGLE_SHEETS_STAGING_ID"):
        RuntimeConfig.from_mapping({"RUNTIME_MODE": "staging"})


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


def test_safe_summary_does_not_expose_private_ids() -> None:
    private_id = "private-spreadsheet-id"
    config = RuntimeConfig.from_mapping(
        {
            "RUNTIME_MODE": "staging",
            "GOOGLE_SHEETS_STAGING_ID": private_id,
        }
    )

    summary = config.safe_summary()

    assert summary["has_google_sheets_staging_id"] is True
    assert private_id not in repr(summary)


def test_load_env_file_reads_simple_key_values(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\nRUNTIME_MODE=staging\nGOOGLE_SHEETS_STAGING_ID='private-id'\n",
        encoding="utf-8",
    )

    values = load_env_file(env_file)

    assert values["RUNTIME_MODE"] == "staging"
    assert values["GOOGLE_SHEETS_STAGING_ID"] == "private-id"
