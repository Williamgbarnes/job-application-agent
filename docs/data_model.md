# Data Model

The public codebase defines a small, dependency-free domain layer in `app/backend/job_application_agent/domain.py`.

The models are intentionally immutable and public-safe. They are suitable for mock workflows, tests, and later normalization/scoring layers, but they must not contain private resumes, private contacts, generated application materials, production identifiers, or raw private tracker exports.

## Core entities

### JobLead

Represents a discovered job before application.

Fields:

- `id`
- `source`
- `company`
- `title`
- `location`
- `work_arrangement`
- `employment_type`
- `compensation_min`
- `compensation_max`
- `posting_url`
- `posted_date`
- `closing_date`
- `status`

Validation:

- `id`, `source`, `company`, and `title` are required.
- Compensation values cannot be negative.
- `compensation_min` cannot exceed `compensation_max`.
- URLs must be `http` or `https`.
- `closing_date` cannot be before `posted_date`.

### JobPostingSnapshot

Immutable snapshot of the posting used for scoring.

Fields:

- `id`
- `job_lead_id`
- `captured_at`
- `source_url`
- `raw_text`
- `normalized_requirements`
- `normalized_responsibilities`

Validation:

- `id` and `job_lead_id` are required.
- `captured_at` must include timezone information.
- `source_url`, when present, must be `http` or `https`.
- Normalized requirement and responsibility items cannot be blank.

### ScoreReport

Explains why a role was prioritized.

Fields:

- `id`
- `job_lead_id`
- `score`
- `priority`
- `strengths`
- `gaps`
- `rationale`
- `created_at`

Validation:

- `id` and `job_lead_id` are required.
- `score` must be between `0` and `100`.
- `created_at` must include timezone information.
- Strength and gap items cannot be blank.

### ApplicationPackage

Represents generated or proposed application materials.

Fields:

- `id`
- `job_lead_id`
- `resume_variant_id`
- `cover_letter_variant_id`
- `status`
- `review_notes`

Validation:

- `id` and `job_lead_id` are required.
- Package status remains review-first and does not imply external submission.

### ApplicationEvent

Tracks state changes.

Fields:

- `id`
- `application_id`
- `event_type`
- `event_date`
- `notes`

Validation:

- `id` and `application_id` are required.

## Enumerations

The domain layer also defines public-safe enums for:

- work arrangement
- employment type
- lead status
- score priority
- application package status
- application event type

These enums are deliberately narrow so future scoring and workflow rules can be deterministic and testable.
