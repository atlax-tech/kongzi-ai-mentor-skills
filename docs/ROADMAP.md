# Roadmap

Status: Phases 0–5 implemented; Phase 6 validation and Phase 7 release active

## Purpose

Deliver a useful personal learning loop quickly, prove it through dogfooding,
and defer GUI or platform work until the command-driven system creates durable
value.

## Phase 0 — Product definition and governance

Status: COMPLETE

Deliver:

- PRD and learning-science basis;
- Harness architecture and `AGENTS.md`;
- test and acceptance strategy;
- GitHub repository, `dev` branch, protected `main`.

Exit:

- Harness validation passes;
- repository governance is verified;
- no product implementation is claimed.

## Phase 1 — State foundation and router

Status: COMPLETE

Deliver:

- versioned local state schemas;
- Obsidian path detection and initialization;
- journey isolation;
- `/Kongzi`, `/Kongzi-start`, `/Kongzi-status`, and `/Kongzi-resume`;
- corrupted-index recovery fixtures.

Exit:

- first use and cross-session resume pass;
- bare `/Kongzi` recommends one next action;
- state is inspectable and rebuildable.

## Phase 2 — Evidence, map, and plan

Status: COMPLETE

Deliver:

- progressive learner profile and baseline;
- local file/URL source registry;
- source authority and claim ledger;
- knowledge map and prerequisite graph;
- personalized roadmap and re-plan rules.

Exit:

- real source locators resolve;
- no-source flow obtains an approved public source set;
- one real journey reaches `planned`.

## Phase 3 — Active learning loop

Status: COMPLETE

Deliver:

- guided study session;
- question/hint/feedback/correction protocol;
- diagnostic, retrieval, and transfer assessment;
- transparent evidence-state transitions;
- misconception records.

Exit:

- no-output completion is blocked;
- immediate correctness cannot produce mastery;
- real user completes one source-backed session.

## Phase 4 — Review and reports

Status: COMPLETE

Deliver:

- review queue and scheduling policy;
- due surfacing on `/Kongzi`;
- daily and weekly reports;
- plan-drift detection;
- one local reminder delivery adapter.

Exit:

- one real delayed review is completed;
- failed delivery preserves due state;
- daily and weekly reports trace to evidence.

## Phase 5 — Full upstream integrations

Status: IMPLEMENTED; complete Agent-driven Cangjie/Nuwa/Darwin manual runs
remain release evidence

Deliver:

- cangjie long-form distillation adapter;
- supported video-downloader acquisition/ASR adapter;
- nuwa mentor-lens adapter;
- exact upstream version/commit tracking;
- success/failure/provenance contract tests.

Exit:

- each adapter completes its supported end-to-end flow through Kongzi records;
- mentor on/off leaves facts and grades unchanged;
- failed acquisition never fabricates an artifact.

## Phase 6 — Dogfood hardening and skill evolution

Status: ACTIVE

Deliver:

- complete real learning journey;
- Darwin test prompts and independent quality evaluation;
- state migrations and export/import;
- runtime compatibility evidence;
- resolved usability failures.

Exit:

- v0.1 acceptance matrix passes with actual evidence;
- known gaps are explicit;
- improvements are validation gated.

## Phase 7 — Stable release

Status: ACTIVE

Deliver:

- installation flow;
- README matching the required nuwa-style module order, without author section;
- hero animation and demo animation;
- complete open-source credits;
- stable release PR from `dev` to `main`.

Exit:

- README commands and animations are verified;
- release acceptance evidence is attached;
- protected `main` contains the stable release.

## Deferred

- GUI;
- hosted backend;
- multi-user or team features;
- marketplace/commercial features;
- learning analytics sent outside the local environment.

## Remaining release work

- Complete the release PR and required CI check.
- Record full Agent-driven Cangjie/Nuwa/Darwin runs when those workflows are
  invoked for real learner content.
- Expand runtime evidence beyond the verified Claude Code local install.

## Sources

- `docs/product/PRD_v0.1.md` section 17
- `docs/ARCHITECTURE.md`
- `docs/ACCEPTANCE.md`
