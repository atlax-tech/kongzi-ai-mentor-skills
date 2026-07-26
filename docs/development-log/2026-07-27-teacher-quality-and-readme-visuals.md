# 2026-07-27 · Teacher quality and README visuals

## Outcome

This pass replaced the decorative README animations with two reproducible,
meaningful assets and closed two core learning-product gaps: learner questions
were not durable records, and plan personalization was too shallow.

## Visuals

- `assets/hero.png` was generated with the built-in image-generation tool as a
  16:9 Confucius-inspired learning loop: sourced material, individualized paths,
  learner output, spaced review, and growth.
- `scripts/render_hero.py` turns that key art into a 60-frame, 10.2-second concept
  animation with five explicit stages: evidence, personalization, questions,
  review, and transfer.
- `scripts/render_demo.py` now runs a real disposable SQL journey and renders an
  18.8-second product narrative. The generated state includes six profile
  fields, one official-style source, three claims, three prerequisite nodes, a
  20-session plan, two learner answers, one learner question, one grounded
  explanation, one understanding check, a review card, and a daily report.

The image-generation prompt required a respectful Confucius-inspired teacher,
an actively writing learner, a jade/gold learning loop, no logos or generated
labels, and a dark indigo/ink-wash visual language. Exact labels and motion are
added deterministically by Pillow.

## Teacher behavior added

New state records:

- `learner_questions`
- `explanations`
- `session.question_ids`
- `session.explanation_ids`

New commands:

- `session question`
- `session explain`
- `session answer --explanation-id`

Invariants:

1. Knowledge explanations require registered claim IDs.
2. Every explanation includes a learner check question.
3. The Agent must stop and wait for the learner's own restatement/application.
4. A session cannot finish with an unanswered learner question or unchecked
   explanation.
5. Daily and weekly reports count answered learner questions.

## Planning quality added

Each generated session now contains:

- knowledge-type-specific method;
- `learn`, `practice`, or `integrate` mode;
- inspectable required output and success criterion;
- minimum viable minutes for a busy day.

Each plan stores profile/source/claim evidence used to build it. Replanning
supersedes rather than deletes the prior plan, and human-readable plan versions
receive unique filenames.

## README policy

The owner made the final README editorial decision: all cited open-source
projects are listed together under `构建参考`, without a separate integration
catalog or a dedicated Darwin section. Upstream installation commands and
feature-by-feature descriptions remain absent.

## Evidence

- Unit suite: 16/16 passed after the final regression fixes.
- `quick_validate.py`: passed.
- Live public source: PostgreSQL SELECT documentation, HTTP 200, 62,372
  extracted characters, final URL and SHA-256 persisted.
- Disposable upstream installation and discovery:
  - cangjie `355dd47a97eeb87d249bf7d32aab561405b6de76`
  - nuwa `72857dc720f4d1dd3e68a40a544341dfc65ea33e`
  - darwin `7c7b7909b630dc3b5cbb91bd4bcb1b10bfb1f894`
  - video-downloader repository `fb327e91bf4f1887a63c3143cb2223b6b09e5185`
- Three independent fresh-vault forward tests covered novice onboarding,
  learner questions, and delayed resume/report behavior. They exposed and then
  verified fixes for structured first status, profile-first routing, localized
  time, single-action dashboards, inferred schedule provenance, live dashboard
  and map refresh, truthful journey status, source-scoped explanations,
  readable report Markdown, overdue severity, and no phantom planned session.
- The last forward-test finding was also fixed: an omitted constraint is now
  written as `未提供，待确认`, never as a confirmed `无`.

## Honest remaining boundary

The deterministic core is complete enough for manual self-use testing. It is
not yet honest to claim proven long-term learning impact: that requires the
owner to use Kongzi across real delayed intervals. Full book distillation,
public-person mentor research, independent-judge optimization, real long-video
ASR, and additional runtime UX remain manual dogfood items even though the
installation, discovery, and hand-off contracts are implemented.
