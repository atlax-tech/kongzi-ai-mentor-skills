# Kongzi AI Mentor Skills

Kongzi is a local-first, command-driven AI learning coach. The `dev` branch
contains the implemented Agent Skills product plus the internal Harness. The
protected `main` branch contains only allowlisted stable-release files.

Read before changing behavior:

- Product source: `docs/product/PRD_v0.1.md`
- Product map: `docs/PRODUCT.md`
- Learning evidence: `docs/research/LEARNING_SCIENCE.md`
- Architecture: `docs/ARCHITECTURE.md`
- Design: `docs/DESIGN.md`
- Development: `docs/DEVELOPMENT.md`
- Testing: `docs/TESTING.md`
- Acceptance: `docs/ACCEPTANCE.md`
- Roadmap: `docs/ROADMAP.md`
- Current implementation evidence:
  `docs/development-log/2026-07-26-complete-command-first-implementation.md`

Verified commands are listed in `docs/DEVELOPMENT.md` and
`docs/TESTING.md`. Preserve user-owned product sources, cite project facts, keep
learning claims traceable to authoritative sources, and report unrun checks
honestly. Develop on `dev`; `main` is the protected stable-release branch.
Use `apply_patch` for edits, preserve append-only evidence contracts, run the
portable unit suite, and build public releases through
`scripts/package_release.py` so internal documents never reach `main`.
