# 0001 — Public repository for protected `main`

Status: ACCEPTED  
Date: 2026-07-26

## Context

The confirmed product requirement says development occurs on `dev` and `main`
must reject casual direct pushes, force pushes, and deletion. The repository
was initially created private because the user had not separately specified
visibility.

The `atlax-tech` organization is on GitHub Free. GitHub returned HTTP 403 when
classic branch protection was applied to the private repository, and returned
the same plan restriction for repository rulesets. GitHub's official
documentation states that GitHub Free organizations can use protected branches
and rulesets for public repositories, while private-repository protection
requires a paid plan.

The repository contained only product and Harness documentation intended for
the Kongzi project. A tracked-file credential-pattern scan found no hits before
the visibility change.

## Decision

Make `atlax-tech/kongzi-ai-mentor-skills` public and configure `main` with:

- changes required through pull requests;
- stale review dismissal enabled;
- zero required approvals so the single owner is not permanently blocked from
  self-managed stable releases;
- administrators subject to the same rule;
- linear history required;
- conversation resolution required;
- force pushes disabled;
- deletion disabled.

Keep `dev` as the repository default branch.

## Evidence

- Repository:
  <https://github.com/atlax-tech/kongzi-ai-mentor-skills>
- GitHub protected-branch availability:
  <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>
- GitHub ruleset availability:
  <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets>
- API readback on 2026-07-26:
  `pr_required=true`, `admins_enforced=true`, `linear_history=true`,
  `conversation_resolution=true`, `force_push_allowed=false`,
  `deletion_allowed=false`.
- Direct-push probe on 2026-07-26: rejected with GitHub `GH006` and
  “Changes must be made through a pull request.”

## Consequences

- The confirmed branch-protection requirement is enforceable on the current
  plan.
- Product and Harness documentation are publicly readable.
- Future commits must not include user learning data, credentials, or private
  source material.
- A release PR is possible for a single owner because it does not require a
  second person's approval.
- Required status checks remain UNRESOLVED until CI exists; PR-only protection
  is already enforced.

## Requirements affected

- `docs/product/PRD_v0.1.md` AC-10
- `docs/DEVELOPMENT.md` branch policy
- `docs/ACCEPTANCE.md` release gate

