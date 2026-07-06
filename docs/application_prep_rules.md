# Application Prep Rules

The application prep workflow prepares draft package plans and review checklists. It must never submit an application, contact a person, upload a file, or write production tracker updates without explicit human approval.

## Allowed inputs

- Approved job summary fields.
- Approved resume or profile source references.
- Sanitized mock package fixtures in the public repository.
- Public tailoring and scoring rules.

Real resumes, private profile content, generated application materials, company names, job titles, contacts, URLs, notes, tracker row values, and production document IDs must stay outside the public repository.

## Required behavior

- Cite evidence for tailoring choices.
- Separate draft preparation from submission.
- Store real generated materials outside the public repository.
- Emit only aggregate, log-safe preparation summaries.
- Stay quiet when no approved job is ready for preparation.
- Run no more frequently than the scheduled-task minimum polling interval.

## Allowed outputs before approval

- Draft package plan.
- Tailoring evidence checklist.
- Human review checklist.
- Mock generated-material summaries.

## Approval required before

- Generating final private application materials.
- Uploading files to external systems.
- Sending emails or messages.
- Submitting applications.
- Writing production tracker updates.

## Prohibited actions

- Submitting applications autonomously.
- Contacting people autonomously.
- Committing resumes or generated materials.
- Printing private tailoring inputs.
