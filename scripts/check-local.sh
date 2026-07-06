#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

PYTHON_CMD=()
for candidate in "python3" "python" "py -3"; do
  # Split candidates such as "py -3" without using eval.
  read -r -a candidate_parts <<< "$candidate"
  if "${candidate_parts[@]}" - <<'PY' >/dev/null 2>&1
import sys

if sys.version_info < (3, 11):
    raise SystemExit(1)
PY
  then
    PYTHON_CMD=("${candidate_parts[@]}")
    break
  fi
done

if [ "${#PYTHON_CMD[@]}" -eq 0 ]; then
  echo "Python 3.11 or newer is required." >&2
  echo "Install Python, then make sure python3, python, or py -3 runs from this shell." >&2
  exit 1
fi

VENV_DIR="${VENV_DIR:-.venv}"

if [ -x "$VENV_DIR/Scripts/python.exe" ]; then
  VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
elif [ -x "$VENV_DIR/bin/python" ]; then
  VENV_PYTHON="$VENV_DIR/bin/python"
else
  "${PYTHON_CMD[@]}" -m venv "$VENV_DIR"
  if [ -x "$VENV_DIR/Scripts/python.exe" ]; then
    VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
  else
    VENV_PYTHON="$VENV_DIR/bin/python"
  fi
fi

if ! "$VENV_PYTHON" - <<'PY' >/dev/null 2>&1
import sys

if sys.version_info < (3, 11):
    raise SystemExit(1)
PY
then
  echo "The virtual environment at $VENV_DIR is not usable with Python 3.11+." >&2
  echo "Deactivate any active environment, remove $VENV_DIR, then rerun this script." >&2
  exit 1
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements-dev.txt

"$VENV_PYTHON" -m flake8 app/backend tests
"$VENV_PYTHON" -m mypy app/backend tests
"$VENV_PYTHON" -m bandit -r app/backend/job_application_agent -q
"$VENV_PYTHON" -m pytest -q

"$VENV_PYTHON" -m job_application_agent.cli tracker-summary >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli phase-three-status >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-score >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-queue >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-dashboard >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-dashboard-report >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-package-plan >/dev/null
"$VENV_PYTHON" -m job_application_agent.cli mock-phase-two-summary >/dev/null

echo "Local public-safe checks passed."
