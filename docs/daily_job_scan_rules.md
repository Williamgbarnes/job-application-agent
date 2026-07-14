# Lead Discovery Coverage Template

This public template demonstrates how a lead-discovery workflow can enforce complete source coverage without committing user-specific source names, URLs, credentials, tracker identifiers, or workflow payloads.

Configure concrete source values outside this repository.

## Coverage groups

A deployment should configure these aggregate groups:

- approved or allowlisted sources;
- mandatory baseline direct sources checked on every run;
- discovery boards and aggregators;
- title-query families;
- direct ATS ecosystems;
- conditional additional sources used only when expansion triggers.

The public example defaults to 20 mandatory baseline direct sources, 12 boards, 13 title families, 10 ATS ecosystems, and a minimum of 20 additional distinct sources when expansion is required. These are configurable counts; the public repository does not contain the live source list.

## Baseline and expansion separation

Mandatory baseline sources are unconditional. Finding enough candidates early does not waive them.

Conditional expansion is separate. Sources completed for the baseline do not count toward the additional-source minimum.

## Completion gate

A run may report complete results, including a complete zero-result outcome, only after every configured required group and any triggered expansion group is complete. Otherwise the result remains partial.

The aggregate model in `job_application_agent.scan_coverage` reports only required counts, completed counts, expansion state, and blocker codes.

## Verification and deduplication

Promising results should be verified against an official employer or ATS source when accessible. A credible mirror may be used as a documented fallback by a private deployment.

Hard duplicate decisions should use stable posting identifiers such as an exact requisition identifier or canonical direct-apply URL. Normalized organization and title values are candidate-match signals, not sufficient hard-duplicate evidence by themselves.

## Safety boundary

The public implementation is mock-first, read-only-first, aggregate-only, and human-gated. It does not crawl live sources, store source identifiers, mutate a tracker, submit applications, or contact people.
