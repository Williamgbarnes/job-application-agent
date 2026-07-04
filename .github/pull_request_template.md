## Summary

Describe the change and why it matters.

## Safety checklist

- [ ] Public-safe change only.
- [ ] Mock data and sanitized examples only.
- [ ] No private runtime files or local-only data.
- [ ] No personal application, resume, tracker, contact, or generated-material content.
- [ ] No production account, spreadsheet, drive, contact, job posting, or application identifiers.
- [ ] Human approval remains required before any submission, contact, message, or external write behavior.

## Workflow impact

- [ ] No workflow changes.
- [ ] Workflow changes are lightweight, mock-only, and compatible with GitHub Free.
- [ ] Workflow permissions are minimized.
- [ ] New check dependencies are added to `requirements-dev.txt` when applicable.

## Testing

Describe how this was tested.

Relevant commands, when applicable:

```bash
py -m pytest
job-agent mock-score
job-agent mock-queue
job-agent mock-queue --min-score 75 --priority high
```

## Notes for reviewers

Call out any architectural, security, workflow, or product decisions.
