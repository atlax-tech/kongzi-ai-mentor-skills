# Evidence and authority protocol

## Source hierarchy

Prefer, in order:

1. Primary research, standards, legislation, official specifications, original datasets.
2. Official institutions, maintainers, universities, or vendor documentation.
3. Systematic reviews, meta-analyses, academic textbooks, and reputable reference works.
4. High-quality secondary explanations.
5. Learner-provided notes and informal material.

The last category can define what the learner needs to understand, but cannot silently become proof of a disputed claim.

## Registration

Register every source before using it:

```bash
python3 <root>/scripts/kongzi.py source add --vault "<vault>" "<file>" \
  --authority primary --title "..."

python3 <root>/scripts/kongzi.py source fetch --vault "<vault>" "https://..." \
  --authority official --title "..."
```

Search-result snippets, model memory, and uncaptured browser text are not sources. Save the full public page or file. For a dynamic page, record the final URL, access time, HTTP status, and content hash.

## Claims

Each teaching claim must contain:

- a bounded, testable statement;
- one registered source;
- a locator: page, section, paragraph, table, figure, or timestamp;
- confidence and status (`verified`, `contested`, or `unresolved`).

Use multiple claims when a sentence combines different propositions. Keep source disagreement visible. Do not convert an unresolved claim into a verified one through repetition.

## Grading

Use source-backed claims to judge factual accuracy. A grade should distinguish:

- **retrieval** — was the core idea produced without cues?
- **accuracy** — does it match the supported claim and its conditions?
- **transfer** — can it guide a different example, decision, or procedure?

Record the learner's exact answer before giving the grade. Feedback should cite claim IDs, not merely say "correct."

Factual explanations prompted by a learner question follow the same rule: record the question, cite approved claim IDs in the explanation record, and require a restatement or application check. If no registered claim supports the answer, retrieve evidence before explaining or label the gap unresolved.

## Public web research

The Agent may search and crawl public pages using its available browser/web tools. Use primary sources for technical questions and current authoritative pages for time-sensitive facts. Register the actual opened page. If access is blocked, ask the learner for a file or choose another authoritative public source; never fill the gap with fabricated detail.

## Persona boundary

A Nuwa mentor can supply vocabulary, heuristics, questions, and decision models. It may not provide unsupported biographical facts, quotations, or domain claims. Kongzi's registered evidence always wins.
