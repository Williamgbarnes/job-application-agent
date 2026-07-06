# Portfolio Configuration Guide

This repository is intended to be reusable as a public portfolio project. The committed code, tests, examples, and documentation should describe configurable behavior rather than a single operator's workflow.

## Configuration model

The public repository should contain:

- mock fixtures;
- sanitized examples;
- adapter interfaces;
- validation and summary logic;
- documentation for runtime configuration keys.

Runtime-specific inputs should stay outside committed files and be supplied through environment variables or untracked local files.

## Default public mode

The default public mode is mock-first and read-only-first:

```bash
job-agent mock-score
job-agent mock-queue
job-agent mock-dashboard
job-agent mock-package-plan
```

These commands should run without runtime configuration.

## Configurable runtime mode

Runtime inspection commands may read a configured Excel workbook when `STAGING_TRACKER_PATH` is supplied:

```bash
job-agent tracker-summary --env-file .env
job-agent phase-three-status --env-file .env
```

These commands must keep output aggregate-only. They may report counts, booleans, tab names, status values from the public schema, and quality gate names. They must not print row-level tracker values or local filesystem paths.

## Forking for actual use

A user who wants to run the project for an actual workflow should fork or clone the portfolio repository into a separate deployment repository and configure runtime-specific files there. The portfolio repository should remain generic, sanitized, and suitable for public review.

## Review checklist

When adding features, confirm that:

- new examples use mock or synthetic values;
- tests generate their own fixtures;
- command output is safe for public logs by default;
- external-write behavior is disabled unless a reviewed approval path is added;
- documentation explains how to configure behavior without encoding one user's workflow.
