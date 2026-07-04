# Private Runtime Setup

This project is designed as a public portfolio repository with a private runtime boundary.

The public repository contains source code, tests, documentation, mock data, and sanitized examples. Real data and credentials must live outside Git.

## Real data locations

Use private storage for real workflow data:

- Google Sheets for the live job tracker.
- Google Drive for resume source documents and generated application packages.
- A local or hosted private database for runtime state when the application is deployed.
- Environment variables or a secret manager for credentials and integration IDs.

## What never belongs in this repository

- Real resume files.
- Real cover letters.
- Real job applications.
- Real recruiter or company contacts.
- Production Google Sheet IDs.
- Production Google Drive folder IDs.
- OAuth tokens, cookies, API keys, or service account files.
- Generated application materials.
- Private scoring notes tied to a personal search.

## Local development flow

1. Copy `.env.example` to `.env`.
2. Fill in private values locally.
3. Keep `.env` untracked.
4. Use mock fixtures by default.
5. Enable staging integrations only when explicitly testing real private data.
6. Keep production writes disabled until a human approves a cutover.

## Recommended runtime modes

- `mock`: Uses only committed examples and tests.
- `staging`: Uses private staging Sheets/Drive/database resources.
- `production`: Uses real resources and requires stronger approval gates.

The public demo should default to `mock` mode.

## Safety defaults

- Read-only integrations by default.
- Dry-run mode by default.
- Human approval required for external actions.
- Production write operations disabled unless explicitly configured.
