---
name: kongzi-progress
description: Show Kongzi learning progress and generate append-only evidence-backed daily or weekly reports with one next move.
---

# Kongzi progress

From the Kongzi skill root, read `state-schema.md` in the `references` directory.

Use `status` for a live dashboard. Use `report daily` and `report weekly` for periodic records. Reports must derive from event/session/grade/review IDs; do not infer effort or mastery from chat prose.

Summarize minutes, completed sessions, graded outputs, delayed reviews, scores, not-mastered nodes, due reviews, and exactly one recommended next move. Preserve old reports. If the learner changes goals, create a new journey rather than overwriting the old evidence.

For portability, use `bundle export`; import only into an uninitialized target vault so journeys cannot be silently merged. Run `migrate` before changing runtime versions. Use `repair` only after explicit approval and only for the named corrupt component.
