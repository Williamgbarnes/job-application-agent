# Product Spec

## Product name

Job Application Agent

## One-line description

A human-in-the-loop job application copilot that discovers roles, scores fit, prepares tailored application packages, and tracks follow-up workflows.

## Portfolio framing

This public repository demonstrates the architecture and implementation approach using mock data. Private resumes, real job applications, production trackers, credentials, and personal workflow data are intentionally excluded.

## Primary users

- Job seekers managing a high-volume but quality-focused search.
- Engineering leaders who want transparent scoring and controlled automation.
- Developers evaluating workflow automation and LLM guardrail design.

## Core workflows

1. Ingest job leads from approved sources.
2. Normalize postings into a common data model.
3. Snapshot job descriptions for auditability.
4. Score roles against transparent, testable rules.
5. Generate a review package with strengths, gaps, and suggested materials.
6. Require human approval before any external action.
7. Track application status, follow-ups, and outcomes.

## Out of scope for the public project

- Real credentials.
- Real job applications.
- Private resume files.
- Production spreadsheet IDs or Drive folders.
- Automated submission to restricted third-party job platforms.
- Circumventing website access controls.
