# Local Sync Workflow

GitHub is the source of truth for this public portfolio repository.

Use a real Git checkout for synced work. Do not use uploaded ZIP files as a long-lived working copy, because a ZIP is only a snapshot and will not receive later GitHub changes.

## Fresh computer setup

From Git Bash:

```bash
git clone https://github.com/Williamgbarnes/job-application-agent.git
cd job-application-agent
bash scripts/check-local.sh
```

## Sync an existing checkout

From Git Bash inside the repository:

```bash
bash scripts/sync-local.sh
bash scripts/check-local.sh
```

The sync script defaults to `main`. To sync another public branch:

```bash
bash scripts/sync-local.sh branch-name
```

## Branch naming convention

Use branch names that tie the work to the project phase and implementation area:

```text
phase-<phase-number>-<implementation-slug>
```

Examples:

- `phase-2-branch-naming-convention`
- `phase-2-mock-dashboard-report`
- `phase-2-tracker-schema-check`
- `phase-3-package-review-flow`

Rules:

- Use lowercase letters, numbers, and hyphens only.
- Start with `phase-` followed by the numeric project phase.
- End with a concise implementation slug that names the feature, doc, test, chore, or workflow being changed.
- Do not use spaces, slashes, underscores, uppercase letters, issue titles, private company names, private job titles, tracker IDs, URLs, or other private data.
- Keep the name public-safe and specific enough for PR review.

For repo maintenance that is not tied to a user-facing feature, choose the nearest active phase and use an implementation slug such as `docs`, `ci`, `sync`, `security`, or `workflow`.

## Safety rules

Before syncing, the script checks for uncommitted local changes and exits if the working tree is dirty. This prevents accidental overwrites of local work.

Keep real tracker exports, `.env`, resumes, generated materials, credentials, IDs, private notes, and production data outside committed files. Store local-only files under ignored private paths such as `data/private/`.

## ChatGPT handoff rule

When ChatGPT cannot access a live Git checkout, use GitHub as the handoff point:

1. ChatGPT creates a branch and pull request through GitHub.
2. GitHub Actions runs the public-safe checks.
3. You merge the pull request after review.
4. Any computer with a clone runs `bash scripts/sync-local.sh` to pull the merged changes.

This avoids ZIP drift and keeps local machines, GitHub, and CI aligned around the same commit history.
