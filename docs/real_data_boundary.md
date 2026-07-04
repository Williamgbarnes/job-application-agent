# Real Data Boundary

The application separates public code from private runtime data.

## Boundary model

```text
Public repository
  - Application code
  - Tests
  - Mock fixtures
  - Sanitized documentation
  - Example configuration with placeholders

Private runtime
  - Real tracker IDs
  - Resume source documents
  - Generated application packages
  - Application history
  - OAuth credentials
  - Private job-search notes
```

## Data access pattern

Real data should be accessed through adapters that read configuration from environment variables. The adapters should not hard-code private IDs or paths.

Example:

```text
GOOGLE_SHEETS_STAGING_ID -> read staging tracker
GOOGLE_DRIVE_STAGING_FOLDER_ID -> write staging outputs
GOOGLE_SHEETS_PRODUCTION_ID -> read/write production tracker only after approval
```

## Repository policy

The repository may include:

- Interface definitions.
- Adapter code.
- Mock integration clients.
- Example configuration keys.
- Tests using synthetic fixtures.

The repository may not include:

- Real private values.
- Real exported tracker data.
- Real documents.
- Production screenshots with personal data.
- Logs from real application runs.

## Production-readiness rule

Before production data is used, the application must support:

- Explicit runtime mode selection.
- Dry-run execution.
- Audit logging.
- Human approval gates.
- Clear rollback or no-write behavior.
