# Security Model

## Security goals

- Keep public code free of personal data and credentials.
- Make unsafe automation difficult to enable accidentally.
- Require explicit approval before any external submission.
- Provide audit logs for scoring, generation, and workflow transitions.

## Secret handling

Secrets must be provided through environment variables or a local secret manager. The repository includes `.env.example` only.

Never commit:

- `.env`
- OAuth tokens
- Service account JSON
- Session cookies
- API keys
- Private documents

## Data classification

| Class | Examples | Repository policy |
|---|---|---|
| Public | Docs, mock data, architecture diagrams | Allowed |
| Internal | Local settings, staging IDs | Excluded |
| Confidential | Resume files, applications, contacts | Excluded |
| Secret | Tokens, private keys, passwords | Excluded |

## Guardrails

- Default to read-only behavior.
- Use mock data unless staging credentials are explicitly configured.
- Use dry-run mode for workflow actions.
- Require manual approval before any submission or external state change.
