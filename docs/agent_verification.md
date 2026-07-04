# Agent Verification Workflow

Future ChatGPT, Codex, and other coding-agent sessions should treat GitHub as the verification source when no live checkout is mounted locally.

## Problem

A chat session may be able to read and patch GitHub files through connectors, but it may not have:

- the repository mounted under `/mnt/data`;
- outbound `git clone` access;
- a persistent working tree shared with the user's computer.

In that case, local tests cannot honestly be run from the chat runtime.

## Required verification path

Use this hierarchy:

1. If a live checkout is mounted in the session, run:

   ```bash
   bash scripts/check-local.sh
   ```

2. If no live checkout is mounted, make changes on a GitHub branch and open or update a pull request.
3. Wait for GitHub Actions on the pull request head SHA.
4. Treat these public-safe checks as the verification source:

   - `CI`
   - `PR Review`

5. If a check fails, inspect the failing step/log, patch the branch, and verify the next head SHA.
6. Report the exact verification source in the final response.

## Status language

Use precise status language:

- `Ran locally: bash scripts/check-local.sh`
- `Verified remotely: CI and PR Review passed on <head-sha>`
- `Not run: no mounted checkout and no workflow result was available`

Do not write vague claims such as `tests should pass` when checks were not actually run.

## ZIP uploads

Uploaded ZIP files are snapshot-only. They are useful for reading or generating patches, but they are not synchronized with GitHub after upload.

Do not use a ZIP upload as the durable verification path. Prefer GitHub branches, pull requests, and Actions.

## Safety boundary

All verification must stay public-safe and mock-only. Do not require `.env`, `data/private/`, tracker exports, resumes, credentials, contact details, production IDs, or generated application materials.
