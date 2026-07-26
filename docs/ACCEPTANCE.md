# Acceptance

Status: ALL v0.1 acceptance scenarios passed

## Purpose

Map the first release to observable evidence. A document, placeholder, mock, or
agent self-report does not satisfy an implementation acceptance item.

## v0.1 acceptance matrix

| ID | Status | Evidence |
| --- | --- | --- |
| AC-01 | PASS | Automated full local-source cycle plus real temporary Obsidian dogfood |
| AC-02 | PASS | PubMed page fetched at HTTP 200, stored with 6,577 extracted characters and SHA-256 |
| AC-03 | PASS | `status` reloads active journey, session, due queue, drift, mentor, and one next action only from local files |
| AC-04 | PASS | Unit test blocks finish without an answer; answer/grade/correction events persist |
| AC-05 | PASS | Unit test requires two delayed passes plus application for a procedure node |
| AC-06 | PASS | Node creation requires a claim; claim creation requires source and locator; `doctor` checks references |
| AC-07 | PASS | Real daily/weekly output plus unit test proving repeated reports do not overwrite |
| AC-08 | PASS | Unit test proves mentor enable changes no journey/source/claim/node/session/grade evidence |
| AC-09 | PASS | Corruption test rebuilds state/profile/queue from events and preserves timestamped prior files |
| AC-10 | PASS | PR #1 passed required `test` and merged; `main` enforces PR/admin/linear/conversation rules, strict status check, no force push/deletion |

## Cross-cutting acceptance gates

### Evidence gate

- No fabricated citation, quote, locator, book, paper, URL, or transcript.
- Unresolved and conflicting claims remain visible.
- Search snippets do not count as read sources.

### Learning gate

- Every substantive session has learner output.
- Mastery uses delayed and task-appropriate evidence.
- Learning-style categories are absent from personalization logic.

### State gate

- A new session can resume from local files.
- Journey data is isolated.
- Learner evidence and reports are append-auditable.
- Damaged indexes are recoverable.

### Integration gate

- Each upstream capability has success, failure, and provenance evidence.
- “Complete integration” means the upstream-supported workflow is callable
  through Kongzi and maps to Kongzi records; a link in README is insufficient.
- Upstream limitations are surfaced as deterministic fallback, never fabricated
  success.

### Release gate

- Development starts from `dev`.
- Release changes reach `main` by pull request.
- Automated and manual evidence is attached.
- README commands and animations are verified before a public stable release.
- All incorporated upstream projects are credited.

## Manual release acceptance

1. Install the release tree into a temporary Claude Code project.
2. Run `/Kongzi` in a new Obsidian vault and complete the one-question intake.
3. Register a local source and a public source; resolve one claim locator.
4. Complete one user-answer/grade session and inspect persisted events.
5. Force a review due time in a disposable vault and complete delayed evidence.
6. Open both README GIFs and confirm animation and legibility.
7. Inspect the release branch and confirm internal Harness/architecture files
   are absent.
8. Inspect `main` protection and the PR's required `test` check.

## Sources

- `docs/product/PRD_v0.1.md` section 18
- `docs/TESTING.md`
- `docs/DEVELOPMENT.md`
