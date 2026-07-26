# Acceptance

Status: CONFIRMED product outcomes; implementation evidence absent

## Purpose

Map the first release to observable evidence. A document, placeholder, mock, or
agent self-report does not satisfy an implementation acceptance item.

## Current phase acceptance

This product-definition phase is accepted when:

- substantive PRD and learning-science sources exist;
- the standard Harness documents trace to those sources;
- `AGENTS.md` is a concise knowledge map;
- managed Harness state validates;
- GitHub repository and `dev` branch exist;
- `main` protection is inspected and blocks direct push/force push/deletion;
- no business implementation is represented as complete.

## v0.1 acceptance matrix

| ID | Requirement | Evidence required |
| --- | --- | --- |
| AC-01 | First use with user material | Real vault session, persisted files, source locator, baseline response, plan, first next action |
| AC-02 | First use without material | Search/read log, proposed source set, approval, cited nodes, no memory-only curriculum |
| AC-03 | Cross-session resume | Fresh agent session restoring active journey, due queue, last evidence, blocker, and next action |
| AC-04 | Active learning | Stored learner output, confidence, feedback, correction, and blocked completion before output |
| AC-05 | Delayed mastery | Immediate answer remains below mastery; later delayed retrieval plus application satisfies rubric |
| AC-06 | Source traceability | Random sample of factual notes resolves claim → source → stable locator |
| AC-07 | Daily and weekly reports | Dated reports whose statements resolve to session/assessment/event IDs |
| AC-08 | Mentor isolation | On/off comparison with identical facts and scores, different labeled reasoning lens |
| AC-09 | Recovery | Corrupted index backed up and rebuilt from intact artifacts without evidence loss |
| AC-10 | Main release governance | GitHub API/UI evidence of PR-only protected `main`, admin enforcement, no force push/deletion |

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

## Manual acceptance for this phase

1. Open `AGENTS.md` and confirm every authority link resolves.
2. Read `docs/product/PRD_v0.1.md` and confirm it contains the supplied
   requirements without claiming product implementation.
3. Inspect `docs/research/LEARNING_SCIENCE.md` and follow a sample DOI.
4. Run the Harness structure validator from `docs/TESTING.md`.
5. Inspect the GitHub `main` protection response and default branch.
6. Confirm `dev` is checked out for subsequent implementation work.

## Sources

- `docs/product/PRD_v0.1.md` section 18
- `docs/TESTING.md`
- `docs/DEVELOPMENT.md`

