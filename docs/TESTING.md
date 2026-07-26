# Testing

Status: INFERRED test strategy; Harness validation commands CONFIRMED

## Purpose

Verify that Kongzi produces trustworthy learning behavior, durable state, and
honest integration results—not merely well-formed Markdown.

## Current repository checks

No business implementation exists. The only runnable checks currently validate
the documentation Harness:

```bash
python3 ../harness-armor/skills/harness-build/scripts/validate_harness_structure.py .
```

The exact result must be recorded after every run. The sibling path is
environment-specific and is not the future portable test command.

## Future test layers

### 1. Schema and state tests

- valid profile, journey, source, claim, node, event, queue, and report records;
- malformed JSON/JSONL recovery;
- schema migration backup and rollback;
- stable ID and timestamp rules;
- index rebuild from Markdown/evidence;
- journey isolation;
- append-only learner answers and reports.

### 2. Router tests

- first use;
- one active journey;
- multiple journeys;
- paused or completed journey;
- due and overdue reviews;
- missing source coverage;
- malformed state;
- clear intent fast path;
- bare `/Kongzi` one-next-action output.

### 3. Learning-loop tests

- no session completes without learner output;
- hint use is recorded and reduces independence evidence;
- confidence is captured before feedback;
- correction requires a new attempt;
- one immediate answer cannot produce mastery;
- delayed retrieval and application can satisfy the node rubric;
- confident wrong answers create misconception evidence;
- physical skills do not receive chat-only mastery.

### 4. Evidence tests

- every accepted claim resolves to source and locator;
- search snippet alone is rejected;
- unavailable source becomes a gap;
- time-sensitive source carries an as-of date;
- source conflict is preserved;
- fabricated locator fixture is detected;
- generated summaries remain extraction artifacts, not primary sources.

### 5. Scheduling tests

- review intervals expand/contract from recorded performance;
- snooze does not complete;
- failed delivery leaves due state intact;
- timezone and daylight changes preserve intended local time;
- session-start fallback surfaces overdue work;
- report generation does not mutate mastery evidence.

### 6. Report tests

- daily/weekly claims trace to event IDs;
- no-data periods are reported honestly;
- superseded claims remain auditable;
- plan drift has an evidence-backed reason;
- exactly one recommended focus is present.

### 7. Integration contract tests

#### cangjie

- full text and metadata enter;
- accepted/rejected artifacts and continuation state return;
- every accepted unit maps to original source locators;
- missing text fails without memory-based distillation.

#### video-downloader

- provider-specific fixtures for Douyin, Bilibili, YouTube, and Xiaohongshu;
- metadata-only, no-ASR, local ASR, and API ASR paths;
- actual output files and ASR engine recorded;
- unsupported/provider failure produces local-file fallback, not fake
  transcript.

#### nuwa

- persona enable/disable leaves facts and grades unchanged;
- sourced statements and perspective inferences are distinct;
- thin evidence narrows the lens;
- mentor output cannot write mastery directly.

#### Darwin

- independent test prompts include positive, negative, and boundary triggers;
- only validated skill changes are retained;
- quality branch cannot access learner-data fixtures outside its sandbox;
- results distinguish full test from dry run.

### 8. Dogfood acceptance

Use one real learning journey with real user-provided and public sources.
Capture:

- time to first active practice;
- source traceability sample;
- cross-session resume;
- delayed review after at least one real interval;
- daily and weekly report;
- roadmap adjustment from observed performance;
- user judgment of whether the next action was useful.

## Required test fixtures

- clean Obsidian vault;
- non-vault directory;
- existing populated vault;
- two isolated journeys;
- conflicting sources;
- stale web source;
- corrupted index with intact Markdown evidence;
- novice, intermediate, and falsely confident learner responses;
- missed sessions and overdue reviews;
- mentor on/off comparison;
- upstream adapter success and failure artifacts.

## Release evidence

A release PR to `main` must include:

- requirement and acceptance IDs;
- exact commands and outputs;
- automated test results;
- manual dogfood steps and observations;
- known gaps;
- integration versions/commits tested;
- README installation and demo verification when release-facing.

## Unresolved

- Implementation language and test runner.
- Portable `test`, `lint`, and evaluation commands.
- Quantitative mastery thresholds per knowledge type.
- Runtime matrix for v0.1.

## Sources

- `docs/product/PRD_v0.1.md` acceptance scenarios
- `docs/research/LEARNING_SCIENCE.md`
- `docs/ARCHITECTURE.md`

