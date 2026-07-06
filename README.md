# Job Application Agent

A configurable portfolio job-application copilot that demonstrates workflow automation, rules-based scoring, read-only tracker inspection, and human-in-the-loop review.

This repository uses mock data and sanitized examples only. Runtime-specific inputs are intentionally kept out of committed files.

## Project Goals

- Discover and normalize job leads from approved sources.
- Score roles using transparent, testable rules.
- Generate reviewable application-package plans from approved source content.
- Keep humans in control before any application submission.
- Track application status, follow-ups, and outcomes through configurable adapters.
- Demonstrate secure, production-minded architecture.

## Run From Any Computer

Use Git Bash from a fresh machine with Git and Python 3.11 or newer installed:

```bash
git clone https://github.com/Williamgbarnes/job-application-agent.git
cd job-application-agent
bash scripts/check-local.sh
```

The local check script creates a repo-local `.venv`, installs development dependencies from `requirements-dev.txt`, and runs the portfolio-safe lint, type, security, test, and CLI smoke checks. It does not require runtime configuration or external write access.

## Run Tests Locally

Use the full portfolio-safe check before opening a pull request:

```bash
bash scripts/check-local.sh
```

The script runs these gates in order:

```bash
python -m flake8 app/backend tests
python -m mypy app/backend tests
python -m bandit -r app/backend/job_application_agent -q
python -m pytest -q
```

It also smoke-checks the public mock and portfolio-safe status commands without printing their output:

```bash
python -m job_application_agent.cli tracker-summary
python -m job_application_agent.cli phase-three-status
python -m job_application_agent.cli mock-score
python -m job_application_agent.cli mock-queue
python -m job_application_agent.cli mock-dashboard
python -m job_application_agent.cli mock-dashboard-report
python -m job_application_agent.cli mock-package-plan
python -m job_application_agent.cli mock-phase-two-summary
```

For focused test iteration after the script has created `.venv`, activate the environment and run the needed tests directly:

```bash
if [ -f .venv/Scripts/activate ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

python -m pytest -q
python -m pytest tests/test_cli.py -q
python -m pytest tests/test_mock_package_plan.py -q
python -m pytest tests/test_phase_two_summary.py -q
python -m pytest tests/test_phase_three_status.py -q
```

To recreate the local test environment manually:

```bash
python -m venv .venv
if [ -f .venv/Scripts/activate ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

These local test commands use sanitized fixtures only and should not require runtime configuration.

## Sync an Existing Checkout

Keep GitHub as the source of truth and sync local machines with Git instead of ZIP files:

```bash
bash scripts/sync-local.sh
bash scripts/check-local.sh
```

The sync script fetches and fast-forwards `main` by default. It exits before syncing if the working tree has uncommitted changes. New work should use `phase-<phase-number>-<implementation-slug>` branch names. See `docs/local_sync_workflow.md` for the full synced handoff model and branch naming convention.

## Current Public Demo

The current public demo path uses sanitized mock fixtures only:

```bash
py -m pip install -e ".[dev]"
py -m pytest
job-agent mock-score
job-agent mock-queue
job-agent mock-dashboard
job-agent mock-dashboard-report
job-agent mock-package-plan
job-agent mock-phase-two-summary
```

These commands read `examples/mock_jobs.json`, apply deterministic scoring rules, print mock review queue, dashboard JSON, Markdown report, package plan output, and a Phase 2 completion summary.

## Configurable Runtime Status

Phase 3 demonstrates read-only inspection of a user-provided Excel tracker export. Keep runtime inputs outside committed files and point an untracked `.env` file at the workbook with `STAGING_TRACKER_PATH`.

Useful read-only status commands:

```bash
job-agent tracker-summary --env-file .env
job-agent phase-three-status --env-file .env
```

These commands are portfolio-safe by design. They report configuration booleans, tab names, aggregate record counts, schema completeness, required-field blank counts, format warning counts, quality gate status, scheduled-task rule alignment, and safety flags. They do not print local paths or row-level tracker values.

Useful docs:

- `docs/mock_cli_quickstart.md`
- `docs/mock_demo_review_checklist.md`
- `docs/mock_cli_expected_outputs.md`
- `docs/scoring.md`
- `docs/phase_two_mock_queue.md`
- `docs/phase_two_mock_dashboard.md`
- `docs/phase_two_mock_package_plan.md`
- `docs/phase_two_completion.md`
- `docs/phase_three_staging_plan.md`
- `docs/portfolio_configuration.md`
- `docs/local_sync_workflow.md`
- `docs/agent_verification.md`
- `docs/security_model.md`
- `docs/real_data_boundary.md`
- `docs/human_in_the_loop_policy.md`
- `docs/scheduled_task_rules.md`
- `docs/github_free_plan.md`
- `docs/review_workflows.md`

## GitHub Free Plan Boundary

Repository automation and implementation choices must stay compatible with GitHub Free. CI should remain lightweight and mock-only, package publishing should not be part of the default path, and Codespaces support should remain optional rather than required.

Current budget assumptions:

- 2,000 GitHub Actions minutes per month.
- 500 MB GitHub Packages storage.
- 120 Codespaces core-hours per developer.
- 15 GB Codespaces storage per developer.
- Community support only.

See `docs/github_free_plan.md` for the full policy and review checklist. See `docs/review_workflows.md` for the current CI, PR Review, reviewdog, Bandit, and pytest behavior.

## Runtime Tracker Checks

For configurable runtime checks, keep runtime-specific files out of committed files.

Useful commands:

```bash
job-agent sheets-metadata --env-file .env
job-agent tracker-headers --env-file .env
job-agent tracker-schema --env-file .env
job-agent tracker-quality --env-file .env
job-agent tracker-summary --env-file .env
job-agent phase-three-status --env-file .env
```

## Safety Model

This project is public portfolio code. Runtime configuration and user-specific integrations must live outside the repository.
