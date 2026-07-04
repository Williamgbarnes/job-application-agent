# Google Sheets Staging Adapter

This adapter is the first real-data boundary for the application. It is read-only and uses private runtime configuration instead of hard-coded spreadsheet IDs.

## Runtime modes

- `mock`: Uses synthetic fixtures and does not call Google APIs.
- `staging`: Reads metadata from the private staging tracker configured in `.env`.
- `production`: Reserved for future cutover and requires explicit production configuration.

The public repository must default to `mock` behavior. Local development can use `staging` through a private `.env` file.

## Local setup

Create a local `.env` file at the repo root. Do not commit it.

```bash
RUNTIME_MODE=staging
DRY_RUN=true
REQUIRE_HUMAN_APPROVAL=true
ALLOW_EXTERNAL_SUBMISSION=false
GOOGLE_SHEETS_STAGING_ID=<private-staging-sheet-id>
```

Install the local project and test dependencies:

```bash
python -m pip install -e ".[dev]"
```

For live Google API reads, install optional Google dependencies:

```bash
python -m pip install -e ".[google]"
```

Then run the read-only metadata command:

```bash
job-agent sheets-metadata --env-file .env
```

The command prints a log-safe summary. It does not print the private spreadsheet ID.

## Safety constraints

- No write methods are implemented.
- No real spreadsheet IDs are committed.
- Tests use mock/fake services only.
- The staging adapter reads from `GOOGLE_SHEETS_STAGING_ID`.
- External submission remains disabled by default.
