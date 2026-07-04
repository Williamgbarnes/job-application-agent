"""Runtime configuration helpers.

Configuration is intentionally environment-variable driven so private values
never need to be committed to the public repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import os

_TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


class ConfigurationError(ValueError):
    """Raised when runtime configuration is invalid or unsafe."""


def parse_bool(value: str | bool | None, *, default: bool) -> bool:
    """Parse common environment-style booleans."""

    if value is None:
        return default
    if isinstance(value, bool):
        return value

    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise ConfigurationError(f"Invalid boolean value: {value!r}")


def load_env_file(path: str | Path = ".env") -> dict[str, str]:
    """Load a simple KEY=VALUE env file without mutating os.environ.

    This lightweight parser is enough for local development and avoids making
    the public scaffold depend on python-dotenv. It intentionally ignores blank
    lines and comments and does not support shell expansion.
    """

    env_path = Path(path)
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigurationError(f"Invalid .env line: {raw_line!r}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


@dataclass(frozen=True)
class RuntimeConfig:
    """Application runtime configuration.

    The default configuration is intentionally safe for public/demo runs.
    """

    app_env: str = "development"
    runtime_mode: str = "mock"
    dry_run: bool = True
    require_human_approval: bool = True
    allow_external_submission: bool = False
    google_sheets_staging_id: str | None = None
    google_sheets_production_id: str | None = None

    @classmethod
    def from_mapping(cls, values: Mapping[str, str | bool | None]) -> "RuntimeConfig":
        config = cls(
            app_env=str(values.get("APP_ENV") or "development"),
            runtime_mode=str(values.get("RUNTIME_MODE") or "mock").lower(),
            dry_run=parse_bool(values.get("DRY_RUN"), default=True),
            require_human_approval=parse_bool(
                values.get("REQUIRE_HUMAN_APPROVAL"), default=True
            ),
            allow_external_submission=parse_bool(
                values.get("ALLOW_EXTERNAL_SUBMISSION"), default=False
            ),
            google_sheets_staging_id=_blank_to_none(values.get("GOOGLE_SHEETS_STAGING_ID")),
            google_sheets_production_id=_blank_to_none(
                values.get("GOOGLE_SHEETS_PRODUCTION_ID")
            ),
        )
        config.validate_safety()
        return config

    @classmethod
    def from_env(cls, *, env_file: str | Path | None = None) -> "RuntimeConfig":
        merged: dict[str, str | bool | None] = {}
        if env_file is not None:
            merged.update(load_env_file(env_file))
        merged.update(os.environ)
        return cls.from_mapping(merged)

    def validate_safety(self) -> None:
        allowed_modes = {"mock", "staging", "production"}
        if self.runtime_mode not in allowed_modes:
            raise ConfigurationError(
                f"RUNTIME_MODE must be one of {sorted(allowed_modes)}, "
                f"got {self.runtime_mode!r}"
            )

        if self.allow_external_submission and not self.require_human_approval:
            raise ConfigurationError(
                "External submission cannot be enabled without human approval."
            )

        if self.runtime_mode == "staging" and not self.google_sheets_staging_id:
            raise ConfigurationError(
                "GOOGLE_SHEETS_STAGING_ID is required when RUNTIME_MODE=staging."
            )

        if self.runtime_mode == "production" and not self.google_sheets_production_id:
            raise ConfigurationError(
                "GOOGLE_SHEETS_PRODUCTION_ID is required when RUNTIME_MODE=production."
            )

    def safe_summary(self) -> dict[str, str | bool]:
        """Return a log-safe summary without private identifiers."""

        return {
            "app_env": self.app_env,
            "runtime_mode": self.runtime_mode,
            "dry_run": self.dry_run,
            "require_human_approval": self.require_human_approval,
            "allow_external_submission": self.allow_external_submission,
            "has_google_sheets_staging_id": bool(self.google_sheets_staging_id),
            "has_google_sheets_production_id": bool(self.google_sheets_production_id),
        }


def _blank_to_none(value: str | bool | None) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    stripped = value.strip()
    return stripped or None
