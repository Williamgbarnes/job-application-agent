# Data Model

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

### ApplicationPackage

Represents generated or proposed application materials.

Fields:

- `id`
- `job_lead_id`
- `resume_variant_id`
- `cover_letter_variant_id`
- `status`
- `review_notes`

### ApplicationEvent

Tracks state changes.

Fields:

- `id`
- `application_id`
- `event_type`
- `event_date`
- `notes`
