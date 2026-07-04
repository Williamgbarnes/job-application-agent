# Application Code

This directory will contain the application implementation.

Planned structure:

```text
app/
  backend/       API, domain services, persistence, integrations
  frontend/      dashboard and review queue
  workers/       scheduled jobs and background processing
  shared/        schemas, constants, and reusable models
```

The first implementation milestone should be read-only and mock-data driven.
