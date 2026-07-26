# Development

Status: CONFIRMED governance and portable implementation commands

## Purpose

Define how Kongzi changes move from product evidence to development without
turning proposed behavior into unverified product claims.

## Branch policy

- `main` is the remote default and stable-release branch.
- `dev` is the active development and integration branch.
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
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/install_integrations.py --target /tmp/kongzi-skills --dry-run
python3 scripts/kongzi.py doctor --vault /path/to/test-vault
python3 scripts/package_release.py --source . --output /empty/release-dir
npx skills add . --list --full-depth
```

The sibling Harness validator remains useful when the owner supplies a
`<harness-armor-checkout>` path:

```bash
python3 <harness-armor-checkout>/skills/harness-build/scripts/validate_harness_structure.py .
```

## Release workflow

1. implement and verify on `dev`;
2. update PRD/Harness mapping and Chinese development log;
3. build a clean allowlisted release tree;
4. confirm the tree omits `.harness/`, `AGENTS.md`, and `docs/`;
5. create a release branch from `main`, replace its public allowlisted files,
   and open a PR;
6. require the `test` status check and merge through protected `main`;
7. tag only after README installation, assets, and dogfood evidence pass.

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
