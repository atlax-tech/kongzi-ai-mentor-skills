# Development

Status: CONFIRMED governance; implementation commands UNRESOLVED

## Purpose

Define how Kongzi changes move from product evidence to development without
turning proposed behavior into unverified product claims.

## Branch policy

- `dev` is the default development and integration branch.
- Feature work branches from `dev` and returns to `dev` through review.
- `main` is the stable-release branch.
- Direct push, force push, and branch deletion on `main` are prohibited.
- A release reaches `main` through a pull request after acceptance evidence is
  recorded.
- Use Conventional Commits.

The GitHub settings are external evidence and must be checked rather than
assumed.

## Change protocol

Before changing behavior:

1. read `AGENTS.md` and relevant authority documents;
2. identify requirement and acceptance IDs;
3. list confirmed facts, inferences, unresolved decisions, and conflicts;
4. state file-level changes and verification;
5. stay within the authorized scope.

After changing behavior:

1. run proportionate tests and record actual results;
2. preserve source and learner-data boundaries;
3. update affected architecture/design/testing/acceptance docs;
4. add a Chinese development-log entry with manual acceptance steps;
5. do not claim compatibility or integration that was not exercised.

## Product-source precedence

1. `docs/product/PRD_v0.1.md` is the current product source.
2. `docs/research/LEARNING_SCIENCE.md` governs learning-method claims.
3. Focused Harness docs map those sources for implementation.
4. Architecture recommendations marked INFERRED are not existing code.
5. A later accepted decision record may resolve an explicit open question but
   may not silently reduce a confirmed requirement.

## Current verified commands

Run from the repository root:

```bash
python3 ../harness-armor/skills/harness-build/scripts/scan_repository.py .
python3 ../harness-armor/skills/harness-build/scripts/validate_harness_structure.py .
```

These paths are verified only in the owner's current sibling checkout layout.
They are not a portable install contract.

The implementation build, unit-test, lint, evaluation, install, and release
commands are UNRESOLVED because no implementation or dependency manifest
exists.

## Proposed implementation order

1. define state schemas and fixtures;
2. implement `/Kongzi` router and resume;
3. implement profile, source, claim, and knowledge-map records;
4. implement one active study/assessment loop;
5. implement review queue and reports;
6. dogfood one complete journey;
7. add upstream integrations one at a time with contract tests;
8. add reminder delivery;
9. run Darwin quality evaluation;
10. produce release README assets and acceptance evidence.

## Dependency policy

- Prefer existing, maintained capabilities where they meet the confirmed
  contract.
- Pin or record upstream version/commit for reproducibility.
- Keep upstream attribution in README and integration metadata.
- Never hide an unavailable upstream adapter behind a simulated success.
- Credentials stay outside Git and user learning notes.

## Development log

Add entries under `docs/development-log/` using:

- completed work;
- commands and actual results;
- limitations and unverified items;
- repeatable manual acceptance steps.

## Sources

- `docs/product/PRD_v0.1.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING.md`
- `docs/ACCEPTANCE.md`

