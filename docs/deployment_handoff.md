# Deployment Handoff

This public repository is the portfolio template. Use it to demonstrate the architecture, tests, mock workflows, and read-only runtime inspection boundary.

## Public portfolio repository

Keep this repository generic:

- mock fixtures only;
- sanitized examples only;
- configurable adapters;
- aggregate-safe command output;
- no environment-specific files;
- no write-capable behavior enabled by default.

Before considering the portfolio repository complete, verify:

```bash
bash scripts/check-local.sh
```

## Separate runtime repository

For actual use, clone or fork the portfolio repository into a separate runtime repository. Configure environment-specific files there, outside committed files.

Recommended setup:

```bash
git clone https://github.com/Williamgbarnes/job-application-agent.git job-application-agent-runtime
cd job-application-agent-runtime
bash scripts/check-local.sh
```

Then configure runtime inputs with an untracked `.env` file and ignored local files.

## Readiness checklist

Before using a runtime repository operationally, confirm that:

- `bash scripts/check-local.sh` passes;
- runtime files are ignored by Git;
- `job-agent tracker-summary --env-file .env` produces aggregate-safe output;
- `job-agent phase-three-status --env-file .env` reports expected readiness gates;
- write-capable behavior remains disabled unless a reviewed approval workflow is implemented;
- human approval remains required before any external action.

## Next development phase

The next repository should focus on runtime-specific behavior:

- local runtime configuration;
- operator-specific tracker schema mapping;
- local report views;
- approval files for proposed updates;
- optional write adapters guarded by explicit approvals.

Keep those deployment choices out of the portfolio repository unless they are generalized, sanitized, and tested as reusable abstractions.
