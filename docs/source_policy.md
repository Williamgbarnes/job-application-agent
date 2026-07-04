# Source Policy

## Allowed public-demo sources

The public demo may use:

- Mock JSON job fixtures.
- Synthetic company names.
- Publicly documented API shapes.
- Sanitized posting excerpts created for examples.

## Private/local-only sources

The following must never be committed:

- Real job tracker exports.
- Real resume or cover-letter source files.
- Real recruiter or company contact data.
- Real application outcomes.
- Real source URLs tied to an active personal search.
- API responses that include personal identifiers.

## Automation policy

The project may support source adapters, but they must respect:

- Terms of service.
- Robots and rate limits.
- Login and access restrictions.
- CAPTCHA and anti-bot controls.
- User approval requirements.

The default public implementation should run entirely from mock fixtures.
