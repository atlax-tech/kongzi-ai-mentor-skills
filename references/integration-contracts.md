# Upstream integration contracts

## Discovery and installation

Run:

```bash
python3 <root>/scripts/kongzi.py integration status --vault "<vault>"
python3 <root>/scripts/install_integrations.py --target ~/.claude/skills --dry-run
python3 <root>/scripts/install_integrations.py --target ~/.claude/skills
```

The installer brings in the complete upstream skill directories:

- `kangarooking/cangjie-skill`
- `alchaincyf/nuwa-skill`
- `alchaincyf/darwin-skill`
- `kangarooking/kangarooking-skills/video-downloader`

Kongzi does not replace their workflow instructions. The Agent must read the installed upstream `SKILL.md` completely and execute it.

## Cangjie

1. Register full input text and metadata in Kongzi.
2. Run `integration prepare cangjie`.
3. Execute all Cangjie phases and checkpoints.
4. Preserve pipeline state, verified/rejected/candidate claims, source locators, overview, index, glossary, digest, atomic skills, and test prompts.
5. Run `integration import-cangjie --output-dir ...`.
6. Review auto-detected claims; unmatched content remains a registered, traceable distillation source.

No distillation from model memory.

## Video downloader

Use for Douyin, Bilibili, YouTube, and Xiaohongshu URLs supported by the upstream. Preserve `metadata.json`, captions, transcript, ASR backend, timestamps, and failure output. For unsupported/blocked platforms, accept a learner-provided local video/audio file; do not invent a transcript.

The transcript becomes a source, not automatically a verified claim. Combine with Cangjie for distillation.

## Nuwa

1. Disambiguate the requested mentor.
2. Run `integration prepare nuwa`.
3. Complete all six research dimensions with more than half primary sources.
4. Encode 3–7 usable decision models, provenance, and honest boundaries.
5. Import the persona with `integration import-nuwa`.

Nuwa controls mentor behavior. Kongzi claims remain governed by registered sources.

## Darwin

1. Maintain representative test prompts for `/Kongzi`, source ingestion, planning, study, review, reports, and each integration.
2. Run `integration prepare darwin`.
3. Preserve the baseline and nine-dimensional independent-judge scores.
4. Respect Darwin's checkpoint before modifying behavior.
5. Apply only changes that pass the ratchet; preserve the evaluation artifact and commit/branch evidence.

Darwin may improve the skill but may not loosen evidence, learner-output, or append-only invariants.
