---
name: kongzi-integrations
description: Install and operate Kongzi's complete Cangjie, Nuwa, Darwin, and video-downloader integrations.
---

# Kongzi integrations

From the Kongzi skill root, read `integration-contracts.md` in the `references` directory.

Check `integration status`. If a dependency is absent and the user requested the integration, run `install_integrations.py` from the Kongzi root's `scripts` directory; use `--dry-run` first and show the target.

For Cangjie, Nuwa, or Darwin, run `integration prepare`, read the installed upstream `SKILL.md` completely, follow every upstream phase/checkpoint, and write outputs to the prepared directory. Then use the matching import command where available.

For video, call `integration run-video`; preserve the upstream artifacts and register the transcript. Feed that source to Cangjie before building claims.

Never silently implement a reduced substitute for an upstream workflow.
