---
name: kongzi-start
description: Start, resume, diagnose, and personalize a Kongzi learning journey, including Obsidian setup and learner-profile intake.
---

# Kongzi start

From the Kongzi skill root, read `operating-protocol.md` and `state-schema.md` in the `references` directory.

For a new vault, explain that Kongzi writes ordinary Markdown usable by Obsidian. Ask for an existing vault path or permission to initialize the current directory. Run `init` without `--force`.

Run `profile questionnaire`. Ask one question at a time, record each answer with `profile set`, and require a closed-book diagnostic output. Keep self-report separate from observed evidence.

Create a journey when the goal is a demonstrable outcome, available time is known, and the learner has named materials or agreed that the Agent will retrieve authoritative public sources:

```bash
python3 <kongzi-skill-root>/<scripts-dir>/kongzi.py journey create --vault "<vault>" \
  --goal "..." --outcome "..." --prior-knowledge "..." \
  --daily-minutes 30 --days-per-week 5 --constraints "..."
```

Do not delay first value for exhaustive profiling. Resume later with `status`.
