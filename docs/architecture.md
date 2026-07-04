# Architecture

## Principles

- Public code, private configuration.
- Deterministic rules before generative text.
- Human approval before external actions.
- Integration adapters isolated from domain logic.
- Every score and generated recommendation should be auditable.

## Proposed components

```text
Job Sources
   ↓
Ingestion Adapters
   ↓
Job Normalizer
   ↓
Posting Snapshot Store
   ↓
Scoring Engine
   ↓
Application Package Builder
   ↓
Human Review Queue
   ↓
Tracker / Follow-up Workflow
```

## Backend modules

```text
backend/
  domain/
    jobs.py
    scoring.py
    applications.py
    followups.py
  services/
    ingestion_service.py
    scoring_service.py
    package_service.py
    review_service.py
  integrations/
    sheets_client.py
    drive_client.py
    job_source_clients/
  persistence/
    models.py
    repositories.py
```

## Frontend modules

```text
frontend/
  dashboard/
  review_queue/
  lead_detail/
  settings/
```

## Data boundaries

Public repository:

- Mock jobs.
- Mock resume profile.
- Sanitized examples.
- Test fixtures.
- Documentation.

Private runtime:

- Credentials.
- Real job tracker.
- Resume source documents.
- Generated application materials.
- Application history.
