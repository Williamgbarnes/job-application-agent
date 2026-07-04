# GitHub Free Plan Policy

This repository must remain usable on GitHub Free. Do not introduce repository features, CI behavior, storage patterns, or development workflows that assume a paid GitHub plan.

## Plan envelope

| Area | Free plan rule for this repo |
|---|---|
| Repositories | Unlimited public/private repositories are available; do not add paid multi-repo governance as a hard dependency. |
| Collaborators | Unlimited collaborators are available; keep contribution workflows simple and public-repo friendly. |
| Actions | Budget for 2,000 GitHub Actions minutes per month. |
| Packages | Budget for 500 MB of GitHub Packages storage. |
| Codespaces compute | Budget for 120 core-hours per developer. |
| Codespaces storage | Budget for 15 GB per developer. |
| Support | Assume community support only; document local diagnosis and recovery steps. |

## GitHub Actions rules

- Use GitHub Actions for lightweight validation only.
- Prefer one `ubuntu-latest` test job over OS/version matrices.
- Avoid scheduled workflows, polling jobs, deployment jobs, browser suites, load tests, and integration tests in default CI.
- Require explicit approval before adding jobs that use external services, secrets, packages, artifacts, or long-running setup.
- Set `timeout-minutes` on every job.
- Use `concurrency` with `cancel-in-progress: true` so stale pushes do not keep consuming minutes.
- Keep default workflow permissions read-only unless a write permission is explicitly required and approved.
- Do not upload large artifacts by default. If artifacts are needed, keep retention short and document expected size.

## GitHub Packages and artifact rules

- Do not publish default builds to GitHub Packages.
- Do not require GHCR images, package registries, or release bundles for the public demo path.
- Keep generated files, model artifacts, browser binaries, dependency bundles, exports, and screenshots out of the repository and package storage.
- Prefer source installs and small synthetic fixtures over stored binary assets.

## Codespaces rules

- Codespaces support is optional, not the primary path.
- Local Git Bash commands must remain documented and supported.
- Do not require services that consume long-running compute just to run tests.
- Keep any future devcontainer lightweight and reproducible.
- Do not store private tracker exports, resumes, credentials, generated application materials, or bulky caches in Codespaces.

## Implementation review checklist

Before merging changes that touch CI, packaging, development environments, or generated assets, confirm that:

- The public demo still runs locally without private credentials.
- CI remains mock-only and deterministic.
- New workflows have timeouts and concurrency controls.
- No default workflow uses paid runners, larger runners, GPUs, or self-hosted infrastructure.
- No default path publishes packages or stores large artifacts.
- Any expected Actions, Packages, or Codespaces consumption is described in the PR.
