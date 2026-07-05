# Mock Fixture Authoring

Use this guide when adding or editing public mock job fixtures.

## Goals

Mock fixtures should be:

- deterministic;
- small enough for fast tests;
- easy to read in pull request diffs;
- representative of common scoring and review paths;
- safe for a public portfolio repository.

## Required qualities

Each fixture should use invented example records only. Prefer short, generic company names, titles, skills, locations, and notes that cannot be confused with private workflow data.

Keep values stable so scoring tests and CLI examples remain deterministic.

## Coverage ideas

A useful fixture usually includes examples across:

- high, medium, and low score ranges;
- remote, hybrid, and onsite work arrangements;
- strong and weak skill matches;
- complete and incomplete optional fields;
- queue items that should be reviewed now, reviewed later, or held.

## Review checklist

Before merging fixture changes, confirm:

- tests still pass;
- CLI examples still run against the fixture;
- no private identifiers are present;
- fixture values are concise and readable;
- expected scoring behavior is documented in nearby tests or docs.
