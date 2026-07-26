# Kongzi AI Mentor Skills — PRD v0.1

Status: CONFIRMED product requirements; v0.1–v0.3 command-first scope implemented on `dev`
Date: 2026-07-26  
Stage: Product definition; no business implementation is authorized in this phase

## 1. Product definition

Kongzi is a local-first, command-driven AI learning coach for learning any
knowledge domain. It does not replace a professional course. It helps a
self-directed learner:

1. turn a vague learning intention into a measurable goal;
2. establish a learner profile and baseline;
3. ingest user-provided and authoritative public sources;
4. build a source-backed knowledge map and personalized roadmap;
5. study through explanation, practice, questioning, feedback, and review;
6. retain knowledge through scheduled retrieval practice;
7. preserve progress in an Obsidian-friendly knowledge base;
8. inspect daily and weekly evidence of learning;
9. know the single best next action whenever `/Kongzi` is invoked.

The first product form is an Agent Skills suite. The primary first-use
environment is Claude Code operating inside the user's Obsidian vault. The
design SHOULD remain compatible with the open Agent Skills convention so a
future GUI or another compatible runtime can reuse the same learning records.

## 2. Product goal

### 2.1 Primary outcome

Reduce the time and uncertainty required for one person to independently learn
a new domain, while increasing durable recall, ability to explain, ability to
solve problems, and ability to transfer knowledge to unfamiliar situations.

### 2.2 User promise

> Give Kongzi a learning goal and credible material. Kongzi will help determine
> what you already know, what you need to learn, how to practice it, when to
> review it, and what to do next—without pretending that reading an answer is
> the same as learning.

### 2.3 Success definition for the first real user

For a learning journey selected by the owner:

- onboarding and baseline diagnosis finish in 15 minutes or less;
- a source-backed knowledge map and first-week plan are generated in the same
  session;
- every taught factual claim can be traced to a source and locator;
- every study session requires meaningful learner output;
- the system resumes from disk in a new agent session without re-onboarding;
- due reviews are surfaced and recorded;
- the user can see daily and weekly reports based on stored evidence;
- `/Kongzi` always reports current state and recommends one next action.

## 3. Context and constraints

### 3.1 Confirmed constraints

- The tool is for personal use, not commercialization.
- It must work for arbitrary learning domains, not one fixed subject.
- It must be highly personalized.
- User-provided material is a first-class source.
- Public web research and authoritative public sources are required.
- Obsidian is the default knowledge-base experience.
- The learner must answer questions and produce work; one-way AI exposition is
  insufficient.
- Progress, review history, and periodic reports must survive across sessions.
- All user-facing commands use the `Kongzi` prefix.
- Bare `/Kongzi` starts or resumes the full flow and recommends the next step.
- Existing open-source skills should be reused to reduce build time.
- This phase produces product and engineering design only, not the working
  learning product.

### 3.2 Non-goals

- Creating or selling courses.
- Replacing accredited education, supervised professional training, or
  hands-on safety instruction.
- Multi-user accounts, billing, growth analytics, teams, or cloud sync.
- A GUI in the first release.
- Treating chat length, time spent, pages read, or AI output volume as proof of
  learning.
- Creating a fixed personality label such as “visual learner.”
- Letting a simulated mentor's voice override evidence.

## 4. Target user and jobs to be done

### 4.1 Primary user

A self-directed adult learner who wants to learn quickly but does not trust
their own study method, does not know how to structure the domain, and wants to
avoid unnecessary courses and low-quality information.

### 4.2 Jobs to be done

When I want to learn an unfamiliar subject, help me:

- clarify what “learn it” means in observable behavior;
- understand prerequisites and the shape of the domain;
- identify credible source material and missing evidence;
- choose an achievable path for my available time;
- stop passively consuming and make me retrieve, explain, compare, and apply;
- notice misconceptions early;
- remember material after the first week;
- keep my notes, evidence, and progress under my control;
- resume immediately after an interruption;
- decide whether I need a paid course only after I have identified a real gap.

## 5. Product principles

### P1. Learning requires learner output

Every substantive study session MUST include at least one learner-generated
artifact: an answer, explanation, derivation, solution, comparison, prediction,
worked example, critique, or project increment.

### P2. Evidence before fluency

A polished answer without traceable evidence is not acceptable. The system MUST
separate source facts, source interpretations, learner conclusions, mentor-lens
advice, and unresolved claims.

### P3. Personalization is behavioral, not typological

Adapt from prior knowledge, goal, performance, errors, time horizon, available
time, domain type, and observed retention. Do not assign unsupported
visual/auditory/kinesthetic learning-style labels.

### P4. Optimize for durable capability

Prefer delayed recall, correct application, transfer, and error correction over
immediate familiarity or completion percentage.

### P5. One next action

The router may show context and options, but it MUST end with one recommended
next action and a reason.

### P6. Local files are the durable memory

Conversation history is not the source of truth. Learning state, sources,
assessments, reports, and decisions MUST be persisted inside or alongside the
user's vault in inspectable formats.

### P7. Difficulty must be productive

The coach should not reveal full answers before a reasonable retrieval attempt.
It should reduce task difficulty when failure shows missing prerequisites, not
when the learner merely feels effort.

## 6. Learning-science policy

The detailed evidence review is in
`docs/research/LEARNING_SCIENCE.md`. Kongzi uses a method portfolio rather than
one universal technique:

| Method | Default product use | Important boundary |
| --- | --- | --- |
| Retrieval practice | Questions before re-exposure; delayed re-test | Requires correction of errors |
| Spaced practice | Schedule future retrieval by retention target and performance | Fixed intervals are a starting heuristic, not proof of mastery |
| Interleaving | Mix confusable concepts or problem types after initial understanding | Premature mixing can overload a novice |
| Self-explanation | Ask “why,” “how,” and “what would change?” | Fluency of explanation can still hide factual error |
| Worked examples and fading | Show annotated examples, then progressively remove steps | Especially useful for novices and structured problems |
| Mastery learning | Gate prerequisite nodes on evidence of performance | Self-paced work can stall without cadence and follow-up |
| Feedback and error correction | Task/process feedback, misconception record, re-attempt | Praise alone is not corrective feedback |
| Self-regulated learning | Plan → perform → reflect cycle | Reflection must change the next plan |
| Deliberate practice | Isolate weak subskills with feedback for performance domains | Contribution varies greatly by domain |

The popular “Feynman technique” is not treated as a universal scientific
learning theory. Kongzi implements its useful core as source-checked
self-explanation plus retrieval, gap detection, feedback, and re-explanation.

## 7. Knowledge types and method selection

Kongzi MUST classify each knowledge node by the capability required. A node may
have more than one type.

| Type | Evidence of learning | Primary practice |
| --- | --- | --- |
| Fact | Accurate delayed recall with source | Free recall, short answer, spaced retrieval |
| Concept | Explanation, distinction, example and non-example | Self-explanation, compare/contrast, concept questions |
| Procedure | Correct execution in representative tasks | Worked example → completion problem → independent problem |
| Judgment | Decision with explicit criteria under uncertainty | Cases, prediction, critique, mentor-lens comparison |
| Physical/perceptual skill | Observable performance outside chat | Practice log, external evidence, coach/user verification |
| Creative synthesis | Novel artifact satisfying a rubric | Project work, critique, revision, transfer task |

The system MUST NOT claim mastery of a physical or perceptual skill from a text
answer alone.

## 8. End-to-end user journey

### Stage 0 — Enter or resume

The user invokes `/Kongzi`.

- If no state exists, explain the flow in one screen and begin onboarding.
- If one active journey exists, show due reviews, current evidence, blockers,
  and the recommended next action.
- If multiple journeys exist, resume the most recently active journey unless
  the user names another one.
- If state is malformed, preserve it, report the exact problem, and offer a
  recoverable repair or backup path.

### Stage 1 — Define the destination

Convert “I want to learn X” into:

- target capability;
- target context;
- desired depth;
- deadline or retention horizon;
- proof artifact or performance;
- exclusions;
- available hours and cadence.

Example: “Learn SQL” is insufficient. “Within four weeks, independently answer
analytical questions against a medium relational dataset, explain query plans,
and produce a documented analysis” is testable.

### Stage 2 — Build learner profile and baseline

Use a progressive interview, not a long static questionnaire:

1. ask at most three high-information questions at a time;
2. explain why each answer changes the plan;
3. permit “unknown” and infer only from observed performance;
4. run a small baseline task early;
5. store confidence and evidence for each profile field;
6. update the profile when behavior contradicts self-report.

Profile dimensions:

- goal and proof of capability;
- prior knowledge and prerequisites;
- typical errors or blockers;
- available time, session length, timezone, and blackout periods;
- motivation and preferred project context;
- reading/language/accessibility preferences;
- available tools and knowledge base;
- source materials already owned;
- confidence and calibration history;
- desired mentor lens, if any.

### Stage 3 — Establish the source set

The user can provide files, directories, URLs, papers, books, transcripts,
course notes, official documentation, or an existing vault.

If the user provides no material, Kongzi MUST:

1. explain that a source set is needed before a trustworthy roadmap;
2. search for public authoritative sources;
3. propose a small source set with authority and relevance reasons;
4. record access status and locators;
5. ask the user to approve or adjust the set.

Discovery snippets are not teaching evidence. The actual source page, document,
or transcript MUST be captured or read before extracting claims.

### Stage 4 — Distill and map

Produce:

- a domain boundary;
- prerequisite graph;
- knowledge-point inventory;
- concept relations;
- source coverage and gaps;
- confidence and conflict flags;
- an Obsidian-compatible Mermaid mind map or graph view;
- a prioritized “minimum useful path.”

Every knowledge node receives a stable ID, knowledge type, prerequisites,
source links, intended evidence of mastery, and current mastery state.

### Stage 5 — Plan the cycle

Generate a time-boxed roadmap from the goal, map, baseline, and calendar:

- milestones and exit evidence;
- weekly focus;
- session-level tasks;
- review windows;
- buffer and recovery rules;
- a minimum viable session for busy days;
- an explicit re-plan trigger.

The plan MUST present workload in hours and outputs, not only chapter counts.

### Stage 6 — Run a study session

Default session protocol:

1. retrieve prior knowledge before showing notes;
2. state the session outcome and why it matters;
3. teach only the minimum missing explanation from sources;
4. request learner output;
5. diagnose the response against a rubric;
6. give task/process feedback with source citations;
7. require correction or a second attempt;
8. schedule future retrieval;
9. save evidence and the next action.

The learner can request hints. Hints SHOULD progress from cue → principle →
partial step → worked answer. The full answer should not be the first response.

### Stage 7 — Review and adapt

Review items are generated from knowledge nodes and learner errors. Scheduling
considers:

- desired retention horizon;
- last result;
- response latency and confidence;
- number and recency of successful retrievals;
- error type;
- prerequisite importance;
- overdue status.

Wrong or lucky answers return sooner. Correct, confident, delayed retrievals
expand the interval. Every schedule change is inspectable.

### Stage 8 — Report and continue

Daily and weekly reports are evidence-backed, append-only artifacts. `/Kongzi`
uses the latest report and due queue to recommend the next action.

## 9. Command model

User-facing commands are case-preserving and all begin with `Kongzi`.
Implementations MAY use lowercase filesystem names internally.

| Command | Purpose |
| --- | --- |
| `/Kongzi` | Start, resume, show state, and recommend one next action |
| `/Kongzi-start <goal>` | Create a new learning journey and run the full intake |
| `/Kongzi-profile` | Inspect or update learner profile and constraints |
| `/Kongzi-sources` | Add, inspect, approve, refresh, or challenge sources |
| `/Kongzi-map` | Build or inspect the knowledge map and prerequisites |
| `/Kongzi-plan` | Create or revise the roadmap and study cycle |
| `/Kongzi-study` | Run the next guided learning session |
| `/Kongzi-quiz` | Run a diagnostic, retrieval, transfer, or mastery assessment |
| `/Kongzi-review` | Process due review items |
| `/Kongzi-mentor <person>` | Select, distill, or disable a mentor lens |
| `/Kongzi-note` | Capture an atomic learning, misconception, or question |
| `/Kongzi-progress` | Show evidence by knowledge node and milestone |
| `/Kongzi-report daily|weekly` | Generate or inspect a periodic report |
| `/Kongzi-status` | Show active journeys, due work, data health, and blockers |
| `/Kongzi-resume [journey]` | Restore a journey from durable state |

Natural-language triggers MUST route to the same skills. Users should not need
to memorize the full command list.

## 10. Functional requirements

### KZ-001 — Router and next-step engine

- Bare `/Kongzi` detects first-use, active, paused, due-review, plan-drift, and
  damaged-state conditions.
- It loads durable state before asking questions.
- It recommends one next command with an evidence-based reason.
- It never claims a sub-skill ran when it only recommended it.

### KZ-010 — Progressive learner profile

- Profile fields include epistemic status, source, timestamp, and confidence.
- Self-report and observed performance remain distinct.
- The system asks only questions that can change the next decision.
- Profile updates are append-auditable; prior values are not silently erased.

### KZ-020 — Source intake and provenance

- Accept local files, folders, URLs, transcripts, and existing Obsidian notes.
- Store source ID, title, author/issuer, date/version, retrieval time, source
  type, local path/URL, content hash when local, and authority tier.
- Preserve exact locators such as page, section, paragraph, timestamp, or
  symbol.
- Record inaccessible, stale, contradicted, or low-authority sources.
- Never promote an AI-generated summary into a primary source.

### KZ-021 — Authority policy

Default authority tiers:

1. official standards, specifications, laws, documentation, and primary data;
2. peer-reviewed systematic reviews, meta-analyses, and primary studies;
3. recognized textbooks, scholarly books, and university course materials;
4. first-party expert books, talks, interviews, and technical articles;
5. reputable secondary analysis;
6. unverified community or search-discovery material.

Tier is contextual. A first-party tutorial may be authoritative for tool usage
but not for independent efficacy claims. Conflicting credible sources are
preserved, not blended into false certainty.

### KZ-022 — Claim ledger

Each distilled claim MUST include:

- stable claim ID;
- concise statement;
- knowledge node IDs;
- source IDs and locators;
- evidence type;
- epistemic status: supported, inferred, unresolved, or conflicted;
- extraction date;
- agent/process that extracted it.

Teaching output cites claim IDs or direct sources. Unsupported factual claims
are explicitly marked and excluded from mastery assessment until resolved.

### KZ-030 — Knowledge map

- Supports graph, outline, and checklist views from the same node records.
- Tracks prerequisites and prevents circular prerequisites.
- Separates “important” from “required for the user's goal.”
- Identifies source coverage gaps.
- Supports manual user correction.

### KZ-040 — Personalized roadmap

- Uses the goal, baseline, node graph, retention horizon, and availability.
- Includes estimated effort ranges and assumptions.
- Provides normal, compressed, and recovery paths.
- Re-plans when two sessions are missed, prerequisite failure repeats, the
  deadline changes, or the user changes the target capability.
- Never hides reduced scope when fitting a tighter deadline.

### KZ-050 — Active study session

- Requires output before completion.
- Uses source-backed explanations and questions.
- Saves session intent, prompts, answers, rubric scores, feedback, corrections,
  misconceptions, evidence, duration, and next action.
- Allows pause/resume without losing the current question or attempt.

### KZ-060 — Assessment and mastery

- Supports diagnostic, formative, retrieval, transfer, and milestone
  assessments.
- Distinguishes recognition from free recall.
- Uses explicit rubrics for open responses.
- Stores learner confidence before feedback to measure calibration.
- A node cannot reach “mastered” from one immediate correct answer.
- Mastery requires at least one delayed retrieval and, where relevant, an
  application or transfer task.
- The user can challenge grading; the challenge and resolution are stored.

### KZ-070 — Review scheduler and reminders

- Stores an explicit queue with `due_at`, timezone, reason, and source node.
- Supports session-start reminders in compatible agents.
- Supports a local scheduler adapter for reminders when the agent is not open.
- Reminders deep-link or point to `/Kongzi-review`.
- Snooze records a new due date and reason; it is not treated as a completed
  review.
- Missed reminders remain due and appear in the next status.

### KZ-080 — Progress and reports

Progress uses evidence states:

- `unseen`;
- `introduced`;
- `attempted`;
- `retrieved`;
- `applied`;
- `mastered`;
- `decaying`;
- `blocked`.

Daily report:

- planned versus completed outputs;
- nodes attempted and evidence gained;
- due/overdue reviews;
- misconceptions created or resolved;
- time spent, if available;
- one recommended action for the next session.

Weekly report:

- milestone movement;
- delayed-retrieval and transfer evidence;
- strongest and weakest nodes;
- calibration trend;
- plan adherence and causes of drift;
- source gaps or conflicts;
- roadmap changes with reasons;
- one focus for the next week.

Reports are append-only and cite source session/assessment IDs.

### KZ-090 — Obsidian knowledge base

- On first use, detect whether the current directory is an Obsidian vault.
- If not, explain the benefit and offer to initialize a minimal vault entry
  structure or connect an existing vault.
- Never require community plugins for core behavior.
- Write human-readable Markdown with stable YAML fields and wiki links.
- Store machine-oriented queues/indexes in JSON or JSONL without duplicating
  the canonical learning record.
- All paths are configurable; default paths are documented in section 12.

### KZ-100 — Web research

- Use available network/search/browser tools for public research.
- Prefer primary and authoritative sources.
- Record the exact URL, access date, title, issuer, and relevant locator.
- Search results are candidates; content is read before use.
- For time-sensitive subjects, store “as of” dates and revalidation rules.
- Robots, authentication, paywalls, or unavailable pages produce a recorded
  gap and an alternate-source search; they do not produce fabricated content.

### KZ-110 — Mentor lens

- A mentor lens is optional and visibly named in output.
- The learner can choose a public figure, a domain-neutral framework mentor, or
  no persona.
- Mentor output distinguishes sourced positions from model inference.
- Factual research occurs through the source pipeline before persona analysis.
- The persona cannot modify source authority, assessment scores, or stored
  learner answers.
- Multiple mentor lenses MAY compare reasoning, but the default is one lens to
  avoid noise.

### KZ-120 — Multi-journey isolation

- Each learning goal has a stable journey ID and isolated map, plan, sessions,
  review queue, and reports.
- Learner-wide preferences can be shared.
- Domain claims and mastery evidence do not leak between journeys unless a
  source node is explicitly linked.

## 11. Open-source integration contracts

These integrations are planned as first-class adapters, not vague links.
Their upstream code is not copied in this product-design phase.

### 11.1 cangjie-skill

Source: <https://github.com/kangarooking/cangjie-skill>

Role:

- distill books, transcripts, courses, podcasts, and other long-form material;
- preserve candidates, rejected units, verified units, glossary, and pipeline
  continuation state;
- produce reusable method skills when the source contains executable methods.

Kongzi adapter contract:

- input: registered source IDs, local text paths, metadata, learner goal, and
  knowledge-map boundary;
- output: source-located candidate concepts/methods, rejection reasons,
  glossary, and process status;
- mapping: every accepted unit maps back to Kongzi claim and node IDs;
- failure: missing full text stops distillation for that source and records a
  source gap;
- trust boundary: cangjie output is an extraction artifact, not independent
  proof. Original-source locators remain mandatory.

### 11.2 video-downloader

Source:
<https://github.com/kangarooking/kangarooking-skills/tree/main/video-downloader>

Role:

- capture video, post caption, audio, transcript, and normalized metadata;
- supported upstream routes currently cover Douyin, Bilibili, YouTube, and
  Xiaohongshu;
- provide local ASR or SiliconFlow ASR options and platform-specific fallback.

Kongzi adapter contract:

- input: video URL or later local-file path, destination source directory, ASR
  language, and optional terminology prompt;
- output: `metadata.json`, `post_caption.txt`, transcript, audio, and source
  media when requested;
- mapping: transcript timestamps become source locators;
- quality: ASR engine/model and raw response are recorded; uncertain terms are
  marked for review;
- failure: unsupported or failed provider routes fall back to user-supplied
  local media and local ASR. A transcript is never fabricated.

### 11.3 nuwa-skill

Source: <https://github.com/alchaincyf/nuwa-skill>

Role:

- distill how a public figure reasons, including mental models, heuristics,
  expression patterns, counter-patterns, tensions, and honest boundaries;
- keep multi-source research and validation artifacts.

Kongzi adapter contract:

- input: mentor identity or learner need, focus domain, source set, desired
  research depth, and Kongzi evidence policy;
- output: an installable perspective skill plus research provenance and
  fidelity evidence;
- runtime: selected perspective is loaded only for mentor-lens steps;
- trust boundary: persona inference is labeled; source-backed curriculum and
  grading remain persona-independent;
- failure: thin or contradictory evidence produces a narrower mentor lens with
  explicit uncertainty, not invented certainty.

### 11.4 darwin-skill

Source: <https://github.com/alchaincyf/darwin-skill>

Role:

- evaluate and improve Kongzi skill quality through a rubric, test prompts,
  independent evaluation, validation-gated edits, and Git history.

Kongzi adapter contract:

- operates on one Kongzi `SKILL.md` at a time in a dedicated branch;
- requires positive and negative trigger tests plus representative learning
  journey tests;
- compares actual outputs, not only static structure;
- retains improvements only when the defined score and critical acceptance
  gates improve;
- never rewrites user learning records;
- remains a development-quality tool, not the algorithm that declares the
  learner mastered a subject.

### 11.5 Reference patterns, not runtime dependencies

- `iamzifei/show-me-the-money`: append-only snapshots, project isolation,
  fixed state schemas, evidence-based reports, atomic learnings, supersession,
  and “one next move.”
- `XBuilderLAB/cheat-on-content`: progressive onboarding, explicit state,
  immutable evidence records, periodic retro, and calibration loops.
- `atlax-tech/harness-armor`: repository knowledge placement, epistemic
  statuses, traceability, validation, and managed harness state.

README attribution for every incorporated upstream project is a release
requirement. The final README must follow the section order and presentation
format of the referenced `nuwa-skill` README, omit the author section, include a
hero animation and demo animation, and focus on installation, purpose, usage,
examples, integrations, repository structure, and license/credits rather than
internal implementation theory.

## 12. Durable data design

Default layout inside an Obsidian vault:

```text
<vault>/
├── .kongzi/
│   ├── config.json
│   ├── state.json
│   ├── events.jsonl
│   └── scheduler/
│       ├── review-queue.json
│       └── reminder-state.json
└── Kongzi/
    ├── Profile.md
    ├── Dashboard.md
    └── journeys/
        └── <journey-id>/
            ├── Journey.md
            ├── Roadmap.md
            ├── Knowledge Map.md
            ├── Sources.md
            ├── Claims.md
            ├── Questions.md
            ├── nodes/
            ├── sources/
            ├── sessions/
            ├── assessments/
            ├── misconceptions/
            └── reports/
                ├── daily/
                └── weekly/
```

Design rules:

- Markdown is the human-readable source of truth for learning artifacts.
- JSON/JSONL indexes make routing and scheduling deterministic.
- Stable IDs link records; filenames are not the only identity.
- Event records are append-only.
- Corrections supersede prior claims without deleting history.
- Paths in generated notes are relative to the vault when practical.
- Writes use temporary files and atomic rename where the runtime permits.
- Before schema migration, back up `.kongzi/` and record the migration result.

Minimum state machine for a journey:

```text
new → profiling → sourcing → mapped → planned → active
active ↔ paused
active → milestone-review → active
active → completed
any state → blocked
blocked → previous valid state after resolution
```

## 13. Reminder design

The review queue is the source of truth; delivery is an adapter.

Delivery order:

1. runtime-native recurring automation, when available;
2. local macOS `launchd` adapter for the first owner;
3. session-start hook that shows overdue items;
4. `/Kongzi` status fallback.

The scheduler MUST remain useful even when delivery fails. No review is marked
complete until a learner response is saved.

Default schedule is unresolved until first-user onboarding captures:

- timezone;
- allowed reminder windows;
- maximum reminders per day;
- daily report time;
- weekly report day/time;
- quiet days.

## 14. Hallucination and evidence controls

### 14.1 Required output labels

Teaching artifacts distinguish:

- `SOURCE`: directly supported by a locator;
- `INFERENCE`: reasoned from named sources;
- `MENTOR LENS`: simulated reasoning, not a factual citation;
- `LEARNER`: the user's own statement or artifact;
- `UNRESOLVED`: insufficient evidence;
- `CONFLICT`: credible sources disagree.

### 14.2 Answer protocol

For factual or time-sensitive questions:

1. resolve relevant knowledge nodes;
2. retrieve approved claims and sources;
3. search/revalidate if coverage is missing or stale;
4. answer with citations;
5. record new claims or gaps;
6. ask the learner to use or retrieve the answer.

### 14.3 Prohibited behaviors

- citing a search snippet as if the underlying source was read;
- inventing page numbers, timestamps, papers, books, or quotes;
- hiding credible source conflict;
- grading an answer against a mentor persona rather than a rubric;
- treating model confidence as source authority;
- teaching from an unapproved generated summary when primary material exists;
- converting “completed session” into “mastered node” without evidence.

## 15. Failure handling

| Trigger | First response | Fallback |
| --- | --- | --- |
| No learning material | Propose a small authoritative source set | Start only after approved accessible sources exist |
| Source cannot be read | Record access failure and seek equivalent primary source | Ask user for a local copy or narrow the claim |
| Sources conflict | Preserve both claims and identify decision impact | Teach the conflict and defer unsupported resolution |
| Baseline too hard | Diagnose missing prerequisites | Insert prerequisite path and re-plan |
| Baseline too easy | Sample transfer and edge cases | Compress mastered sections |
| User misses sessions | Offer minimum viable recovery session | Re-plan scope without pretending schedule is unchanged |
| Repeated wrong answers | Classify misconception or prerequisite gap | Show a worked example, fade support, and retest later |
| Reminder delivery fails | Keep item overdue in queue | Surface on next `/Kongzi` or session start |
| State file malformed | Stop writes to the affected record | Back up, validate, repair or restore with audit entry |
| Persona research is thin | Narrow the mentor lens | Use a neutral evidence-first coach |
| Web unavailable | Use approved local sources | Record missing coverage for later revalidation |

## 16. Metrics for personal use

The product avoids vanity metrics. Useful measures include:

- delayed retrieval accuracy by node;
- transfer/application success;
- confidence calibration error;
- misconception recurrence;
- review completion and overdue duration;
- roadmap forecast versus actual effort;
- source coverage ratio for required nodes;
- time from intent to first meaningful practice;
- percentage of sessions containing learner output;
- number of previously blocked nodes resolved.

Metrics do not leave the local system by default.

## 17. Release scope

### v0.1 — First complete learning loop

Must include:

- `/Kongzi` router;
- journey creation and progressive profile;
- source registration for local text/PDF/URL/transcript;
- authority and claim ledger;
- knowledge map and roadmap;
- guided session with learner output;
- quiz, rubric feedback, correction, and delayed review queue;
- Obsidian layout;
- local durable state;
- daily/weekly report generation on command;
- due-review surfacing on `/Kongzi`;
- recovery from a new agent session;
- one real end-to-end dogfood journey.

### v0.2 — Integrated acquisition and mentors

- complete cangjie adapter;
- complete supported video-downloader adapter;
- nuwa mentor-lens adapter;
- runtime/local reminder delivery adapter;
- source refresh and conflict workflows.

### v0.3 — Quality and portability

- Darwin evaluation loop for every Kongzi skill;
- multi-runtime compatibility evidence;
- schema migration and export/import;
- README hero and demo animations;
- release-ready attribution and documentation.

GUI work is explicitly deferred until the command-driven dogfood loop proves
useful.

## 18. Acceptance scenarios

### AC-01 — First use with user material

Given a new Obsidian vault and a local source file, when the user runs
`/Kongzi-start`, then within one session Kongzi creates a profile, registers the
source, runs a baseline, produces a cited map and first plan, asks at least one
question, saves the answer, and recommends the next action.

### AC-02 — First use without material

Given no material, Kongzi does not improvise a curriculum from memory. It finds
and proposes authoritative public sources, records them, obtains approval, and
only then creates source-backed nodes.

### AC-03 — Cross-session resume

Given a closed conversation and a new agent session in the same vault, bare
`/Kongzi` restores the active journey, due reviews, last evidence, blockers, and
one next action without repeating completed onboarding.

### AC-04 — Active learning

Given a study session, the session cannot be completed until learner output and
feedback are stored. Requesting a hint does not silently count as a correct
answer.

### AC-05 — Delayed mastery

Given one immediate correct answer, the node remains below `mastered`. After a
correct delayed retrieval and required application evidence, the node can reach
`mastered` under its rubric.

### AC-06 — Source traceability

Given any factual knowledge note, a reviewer can navigate from the claim to an
accessible source and stable locator. If no source exists, the note is visibly
unresolved.

### AC-07 — Daily and weekly reports

Given saved sessions and assessments, reports contain only traceable activity,
show plan drift and misconceptions, and end with one next focus.

### AC-08 — Mentor lens isolation

Given an enabled mentor persona, sourced facts and assessment results remain
the same when the persona is disabled; only the reasoning lens and expression
change.

### AC-09 — Recovery

Given one corrupted machine index but intact Markdown artifacts, Kongzi backs
up the damaged state and can rebuild the index without deleting learner
evidence.

### AC-10 — Main release governance

Development occurs on `dev`. `main` rejects direct pushes, force pushes, and
deletion; changes reach `main` through a pull request after release acceptance.

## 19. Product risks

| Risk | Product response |
| --- | --- |
| AI fluency creates false confidence | Require learner output, delayed evidence, and confidence capture |
| Over-personalization reinforces weak habits | Adapt from performance; prohibit learning-style labels |
| Source volume overwhelms the learner | Minimum useful source set and goal-bounded map |
| Persona becomes fake authority | Visible mentor-lens label and evidence-independent grading |
| Reminder fatigue | User-defined windows, capped reminders, and one due queue |
| Progress becomes gamification theater | Evidence states instead of points or streaks |
| Agent sessions lose memory | Local durable state and resume acceptance test |
| Scope grows into a learning platform | Command-first, single-user, local-first release boundary |

## 20. Unresolved product decisions

Resolved for the first owner:

- Daily report/reminder check defaults to 20:00 local time; the user can choose
  another `HH:MM`. Weekly auto-report is generated on Sunday.
- A scheduled check can notify at most once per day. No notification is sent
  when nothing is due; the review queue remains the source of truth.
- First dogfood topic: retrieval practice and learning science, using the
  internal evidence review plus a fetched PubMed primary-paper page.
- Node criteria are stored per knowledge type. Default thresholds are 0.80–0.85,
  with two delayed passes and application/transfer evidence.
- First reminder adapter: macOS `launchd`; cron is the portable fallback.
- Generated notes use `<vault>/Kongzi/`; an existing Obsidian vault remains the
  default knowledge-base entry.
- Installation: `npx skills add atlax-tech/kongzi-ai-mentor-skills`; complete
  peer integrations use `scripts/install_integrations.py`.
- Repository is public. `main` is the protected default stable branch; `dev`
  retains internal Harness/product material.

## 21. Sources

- User requirements supplied in the 2026-07-26 project-init conversation.
- `docs/research/LEARNING_SCIENCE.md`.
- cangjie-skill:
  <https://github.com/kangarooking/cangjie-skill>
- nuwa-skill: <https://github.com/alchaincyf/nuwa-skill>
- darwin-skill: <https://github.com/alchaincyf/darwin-skill>
- video-downloader:
  <https://github.com/kangarooking/kangarooking-skills/tree/main/video-downloader>
- show-me-the-money:
  <https://github.com/iamzifei/show-me-the-money>
- cheat-on-content:
  <https://github.com/XBuilderLAB/cheat-on-content>
- harness-armor: <https://github.com/atlax-tech/harness-armor>
