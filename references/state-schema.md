# Durable state contract

Kongzi stores machine state under `<vault>/.kongzi/` and human-readable notes under `<vault>/Kongzi/`.

## Machine state

- `config.json` — vault, locale, active journey, knowledge base, reminder configuration.
- `profile.json` — self-reported fields, interview facts, observed calibration evidence.
- `state.json` — journeys, sources, claims, nodes, plans, sessions, answers, grades, notes, mentor.
- `events.jsonl` — append-only evidence ledger.
- `review-queue.json` — cards, due times, interval history.
- `integrations.json` — prepared and completed upstream runs.

Writes are atomic for JSON snapshots. Events and reports are append-only evidence. IDs are opaque; never derive meaning from their suffix.

`doctor` detects broken JSON, missing references, invalid due dates, and graph cycles. With explicit learner approval, `repair --component ...` copies the old index to a timestamped `pre-repair` file and rebuilds state, profile, and/or review cards from `events.jsonl`.

`bundle export` writes `.kongzi/` plus `Kongzi/` into a versioned ZIP manifest with a SHA-256 for every file. `bundle import` accepts only an uninitialized target, rejects unsafe archive paths or bad hashes, restores the data, and rebases vault-local source and mentor paths. `migrate` verifies every schema version and refuses unknown upgrade paths instead of guessing.

## Obsidian notes

- `Kongzi/Dashboard.md`
- `Kongzi/Sources/`
- `Kongzi/Journeys/<journey>/Journey.md`
- `Kongzi/Journeys/<journey>/Knowledge Map.md`
- `Kongzi/Journeys/<journey>/Learning Plan.md`
- `Kongzi/Journeys/<journey>/Notes/`
- `Kongzi/Reports/Daily/`
- `Kongzi/Reports/Weekly/`
- `Kongzi/Mentors/`

Do not hand-edit machine state unless repairing with a backup and an explicit migration. Use the CLI.

## Mastery levels

- 0 — unseen
- 1 — attempted
- 2 — immediate performance passed
- 3 — delayed retrieval passed
- 4 — at least two delayed passes plus application evidence

Immediate confidence never upgrades mastery. A low delayed score resets the schedule while preserving history.
