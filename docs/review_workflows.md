# Review Workflows

This repository uses lightweight GitHub Actions checks that stay compatible with GitHub Free and the public-safe project boundary.

## CI workflow

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`.

It:

- uses `ubuntu-latest`;
- uses Python 3.12;
- installs the project with development dependencies;
- runs the public test suite with `python -m pytest`.

The CI workflow must remain mock-only. It must not read `.env`, `data/private/`, tracker exports, resumes, credentials, IDs, contacts, generated materials, or private files.

## PR Review workflow

`.github/workflows/pr-review.yml` runs on pull requests.

It:

- installs development check dependencies from `requirements-dev.txt`;
- reports `flake8` findings through reviewdog as pull request review annotations;
- reports `mypy` findings through reviewdog as pull request review annotations;
- runs Bandit against `app/backend/job_application_agent` only;
- runs the public pytest suite.

Reviewdog is used for inline review feedback. Bandit and pytest remain normal failing workflow steps.

## Dependency management

Development check dependencies live in `requirements-dev.txt` so CI and local review checks use the same tools.

Run the closest local equivalent from Git Bash:

```bash
python -m pip install -r requirements-dev.txt
python -m flake8 .
python -m mypy .
python -m bandit -r app/backend/job_application_agent -q
python -m pytest -q
```

On Windows, `py` may also be used for local Python commands:

```bash
py -m pip install -r requirements-dev.txt
py -m pytest
```

## Review expectations

Before merging workflow changes, confirm that:

- the public demo still runs without private credentials;
- workflows stay mock-only and deterministic;
- jobs have `timeout-minutes` where applicable;
- workflow permissions are read-only unless write access is explicitly required;
- any write permission is limited to repository review/check feedback;
- no secrets, private files, tracker exports, resumes, IDs, or generated application materials are added;
- no external submission, contacting, messaging, deployment, or publishing behavior is introduced.
