# Job Application Agent

A portfolio-safe job application copilot that demonstrates workflow automation, rules-based scoring, LLM-assisted document generation, and human-in-the-loop review.

This repository uses mock data and sanitized examples only. It does not contain private resume files, real job applications, personal job-search data, API keys, OAuth tokens, production Google Sheet IDs, or generated application materials.

## Project Goals

- Discover and normalize job leads from approved sources.
- Score roles using transparent, testable rules.
- Generate tailored application packages from approved source content.
- Keep humans in control before any application submission.
- Track application status, follow-ups, and outcomes.
- Demonstrate secure, production-minded architecture.

## Run From Any Computer

Use Git Bash from a fresh machine with Git and Python 3.11 or newer installed:

```bash
git clone https://github.com/Williamgbarnes/job-application-agent.git
cd job-application-agent
bash scripts/check-local.sh
```

The local check script creates a repo-local `.venv`, installs development dependencies from `requirements-dev.txt`, and runs the public-safe lint, type, security, test, and mock CLI smoke checks. It does not require `.env`, private tracker exports, resumes, credentials, production IDs, or external write access.

## Run Tests Locally

Use the full public-safe check before opening a pull request:

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

It also smoke-checks the public mock CLI commands without printing their output:

```bash
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

These local test commands use sanitized fixtures only. They should not require `.env`, private tracker exports, resume files, credentials, production IDs, or external write access.

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

These commands read `examples/mock_jobs.json`, apply deterministic scoring rules, print mock review queue, dashboard JSON, Markdown report, package plan output, and a Phase 2 completion summary. They do not read private tracker exports, `.env`, resumes, credentials, or production systems.

Useful docs:

- `docs/mock_cli_quickstart.md`
- `docs/mock_demo_review_checklist.md`
- `docs/mock_cli_expected_outputs.md`
- `docs/scoring.md`
- `docs/phase_two_mock_queue.md`
- `docs/phase_two_mock_dashboard.md`
- `docs/phase_two_mock_package_plan.md`
- `docs/phase_two_completion.md`
- `docs/local_sync_workflow.md`
- `docs/agent_verification.md`
- `docs/security_model.md`
- `docs/real_data_boundary.md`
- `docs/human_in_the_loop_policy.md`
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

## Local Staging Checks

For local-only staging work, keep real tracker exports under ignored paths such as `data/private/` and point `.env` at the local file.

Useful commands:

```bash
job-agent sheets-metadata --env-file .env
job-agent tracker-headers --env-file .env
job-agent tracker-schema --env-file .env
job-agent tracker-quality --env-file .env
```

Do not commit `.env`, tracker exports, resume files, generated materials, credentials, IDs, or private notes.

## Safety Model

This project is public portfolio code. Real credentials, private documents, personal workflow data, and production integrations must live outside the repository.
