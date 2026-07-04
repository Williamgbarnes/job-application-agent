# Human-in-the-Loop Policy

## Policy statement

The system may assist with job search workflows, but it must not submit applications, contact employers, or modify production records without explicit human approval.

## Approval gates

Human approval is required before:

- Submitting an application.
- Sending a message to a recruiter or hiring contact.
- Uploading a resume or cover letter to an external site.
- Marking a real application as applied, withdrawn, rejected, or no response.
- Writing to production trackers.
- Using real credentials or private documents.

## Review queue requirements

Every proposed application package should show:

- Job title and company.
- Source URL.
- Posting snapshot timestamp.
- Score and score rationale.
- Strengths.
- Gaps.
- Proposed resume changes.
- Proposed cover-letter evidence.
- Required user decision.

## Decision options

- Approve.
- Edit.
- Skip.
- Archive.
- Needs research.
