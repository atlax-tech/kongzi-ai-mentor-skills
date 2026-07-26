# Design

Status: INFERRED interaction and information design

## Purpose

Translate the PRD into a consistent command-line mentoring experience that
feels like a demanding, evidence-aware teacher rather than a content generator.

## Experience model

Kongzi has three simultaneous roles:

1. **Navigator** — identifies the next highest-value action.
2. **Teacher** — provides minimal source-backed explanation and asks the learner
   to work.
3. **Recorder** — preserves sources, answers, errors, evidence, and decisions.

The teacher role never hides the navigator or recorder state.

## Interaction rules

### Progressive onboarding

- Ask no more than three high-information questions in one turn.
- Say how the answer changes goal, source, pace, or task selection.
- Run a small baseline early instead of trusting a long self-assessment.
- Keep “user says” separate from “performance shows.”
- Offer defaults for non-critical fields and mark them inferred.

### Question-first teaching

Use this sequence unless prerequisites are absent:

1. ask for retrieval, prediction, or a solution;
2. capture confidence;
3. diagnose the response;
4. give the smallest useful feedback or hint;
5. ask for a corrected response;
6. only then show a complete model answer if needed;
7. schedule a delayed variant.

### Hint ladder

1. retrieval cue;
2. relevant principle;
3. identify the wrong step;
4. partial solution;
5. full worked solution with a required self-explanation.

Hints do not count as independent success.

### One-next-action ending

Every router, report, and status output ends with:

```markdown
Next: `/Kongzi-<command> ...`
Why: <one evidence-based sentence>
Expected output: <one inspectable artifact or performance>
```

## Bare `/Kongzi` screen

Target structure:

```markdown
# Kongzi — <journey name>

State: active · Week 2 of 4
Due now: 3 reviews · 1 overdue
Latest evidence: <specific delayed retrieval or application>
Blocker: <one blocker or none>

Recommended next move: `/Kongzi-review`
Why: two prerequisite nodes are overdue and block today's planned task.

Other available actions:
- `/Kongzi-study` — continue the current milestone
- `/Kongzi-progress` — inspect evidence and plan drift
```

On first use, the same command gives a one-screen explanation and starts with
the goal, not a catalog of all commands.

## Knowledge-map design

Every visible node shows:

- name and stable ID;
- knowledge type;
- why it matters to the user's goal;
- prerequisites;
- authoritative source links;
- mastery evidence required;
- current evidence state;
- due-review indicator;
- conflicts or unresolved coverage.

Offer three views:

- roadmap outline for sequencing;
- Mermaid graph for relationships;
- table for evidence and review operations.

These are views over the same records, not independently edited copies.

## Assessment design

Assessment types:

| Type | Learner sees | Product learns |
| --- | --- | --- |
| Diagnostic | Small representative tasks | Prerequisite gaps and compression opportunities |
| Retrieval | Recall without open notes | Accessibility of memory |
| Formative | Worked task with feedback | Error type and next instruction |
| Discrimination | Mixed/confusable cases | Strategy-selection quality |
| Transfer | New context or inference | Flexible use beyond rehearsed prompt |
| Milestone | Authentic artifact and rubric | Readiness to advance |

Open-answer feedback has four fields:

```markdown
Verdict: correct | partial | incorrect | ungradable
Evidence: <learner response locator>
Gap: <specific missing or incorrect element>
Next attempt: <one actionable instruction>
```

The answer key cites approved claims and sources.

## Report design

Reports are concise decision artifacts, not congratulatory diaries.

Daily report order:

1. planned vs completed output;
2. evidence gained;
3. errors/misconceptions;
4. due and overdue reviews;
5. plan change, if any;
6. next action.

Weekly report order:

1. milestone movement;
2. delayed retrieval and transfer evidence;
3. strongest/weakest nodes;
4. calibration trend;
5. plan drift and cause;
6. source gaps/conflicts;
7. one next-week focus.

No source evidence means the report says no evidence was recorded.

## Obsidian design

- `Dashboard.md` links to active journeys, due reviews, latest reports, and
  unresolved source gaps.
- `Profile.md` is readable and editable by the learner.
- Journey notes use wiki links between sources, claims, nodes, sessions, and
  reports.
- Mermaid is the no-plugin default for maps.
- Core behavior never depends on Dataview or another community plugin.
- Generated YAML fields are stable and documented before implementation.

## Mentor-lens presentation

Mentor output uses a visible block:

```markdown
> [MENTOR LENS — <name>]
> <reasoning based on the persona skill>
>
> Evidence basis: <source-backed claims or "perspective inference">
```

The neutral teacher then provides the task and rubric. Disabling the mentor
changes framing, not facts, progress, or grading.

## Error and recovery experience

Errors state:

1. what failed;
2. which files or source IDs are affected;
3. what remains safe;
4. the recovery action;
5. whether any validation is still unrun.

Do not bury a failed write or source fetch inside otherwise successful prose.

## Tone

- Calm, direct, specific, and demanding.
- Explain learning-method choices in plain language.
- Do not shame missed work.
- Do not overpraise routine completion.
- Prefer “show me” and “try again” to long lectures.
- Admit evidence gaps.

## Accessibility

- Permit preferred language and response format.
- Offer text alternatives for diagrams.
- Allow shorter sessions and chunked questions.
- Treat sensory format as an access/preference setting, not a learning-style
  diagnosis.

## Sources

- `docs/product/PRD_v0.1.md` sections 5–15
- `docs/research/LEARNING_SCIENCE.md`

