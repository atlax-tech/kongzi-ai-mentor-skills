---
name: kongzi-review
description: Run Kongzi spaced reviews, retention checks, snoozes, and operating-system reminders without confusing fluency with mastery.
---

# Kongzi review

From the Kongzi skill root, read `operating-protocol.md` and `state-schema.md` in the `references` directory.

Run `review due`. Ask one due card at a time without showing the stored answer. Record the response and source-backed feedback with `review answer`.

A poor delayed score is useful evidence: correct it and let the scheduler shorten the interval. Do not delete or rewrite failed history. Mastery requires repeated delayed performance plus application.

Use `reminder generate` to create a launchd or cron definition. Show the generated path and command. Run `reminder install` only after explicit user approval because it changes system scheduling. At every `/Kongzi` resume, due-state checking is mandatory even without OS reminders.
