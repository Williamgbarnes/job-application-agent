# Staging Tracker Metadata Adapter

This adapter is the first real-data boundary for the application. It is read-only and uses private runtime configuration instead of committed tracker exports.

## Runtime modes

- `mock`: Uses synthetic fixtures and does not read private files.
- `staging`: Reads metadata from the private staging tracker configured in `.env`.
- `production`: Reserved for future cutover and requires explicit production configuration.

The public repository must default to `mock` behavior. Local development can use `staging` through a private `.env` file.

## Recommended local setup

During development, use a private local Excel export instead of live API credentials.

Download the staging tracker manually:

```text
Google Sheet -> File -> Download -> Microsoft Excel (.xlsx)
```

Save it outside committed data:

```text
C:/src/job-application-agent/data/private/staging_job_tracker.xlsx
```

Create a local `.env` file at the repo root. Do not commit it.

```bash
RUNTIME_MODE=staging
DRY_RUN=true
REQUIRE_HUMAN_APPROVAL=true
ALLOW_EXTERNAL_SUBMISSION=false
STAGING_TRACKER_PATH=C:/src/job-application-agent/data/private/staging_job_tracker.xlsx
```

Install the local project and test dependencies:

```bash
py -m pip install -e ".[dev]"
```

Then run the read-only metadata command:

```bash
job-agent sheets-metadata --env-file .env
```

The command prints a log-safe summary. It does not print the private local path.

## Safety constraints

- No write methods are implemented.
- No real spreadsheet IDs are committed.
- No local tracker exports are committed.
- Tests use mock/fake/local temporary workbooks only.
- External submission remains disabled by default.
