#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=(python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD=(python)
elif command -v py >/dev/null 2>&1; then
  PYTHON_CMD=(py -3)
else
  echo "Python 3.11 or newer is required." >&2
  exit 1
fi

"${PYTHON_CMD[@]}" - <<'PY'
import sys

if sys.version_info < (3, 11):
    version = ".".join(str(part) for part in sys.version_info[:3])
    raise SystemExit(f"Python 3.11 or newer is required; found {version}.")
PY

VENV_DIR="${VENV_DIR:-.venv}"
"${PYTHON_CMD[@]}" -m venv "$VENV_DIR"

if [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
else
  VENV_PYTHON="$VENV_DIR/bin/python"
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements-dev.txt

"$VENV_PYTHON" -m flake8 app/backend tests
"$VENV_PYTHON" -m mypy app/backend tests
"$VENV_PYTHON" -m bandit -r app/backend/job_application_agent -q
"$VENV_PYTHON" -m pytest -q

"$VENV_PYTHON" -m job_application_agent.cli mock-score >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-queue >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-dashboard >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-dashboard-report >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-package-plan >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-phase-two-summary >/dev/null

echo "Local public-safe checks passed."
