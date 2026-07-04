# Wave 6B - Active goal constraints

Date: 2026-07-04

## Scope

This report records the additional root workspace instructions that are now part
of the active V1 refactor goal coordination.

## Active Constraints

- Workspace root is `/home/delete/nirs4all`, a multi-repository workspace.
- Do not touch `nirs4all-drafts` or `nirs4all-lab`.
- Preserve user and agent work; do not revert unrelated changes.
- Use `apply_patch` for manual edits.
- Use CodeGraph first for code exploration when a touched repository has a
  `.codegraph/` index.
- For Claude Code MCP calls, always pass explicit `allowedTools`; answer
  permission requests with `allow_for_session` only when the requested tool is
  appropriate for the assigned task.
- Do not print or commit local token values. The workspace may contain local
  token files named `cratesio_token`, `github_token`, `goatcounter_token`,
  `npm_token`, `rtd_token`, `sentryio_token`, and `zenodo_token`.
- Keep `nirs4all` Python and `nirs4all-studio` out of final production
  releases/tags until their progressive validation gates are explicitly met.
- Do not make parity artificially green by reducing tests, adding unjustified
  skips/xfails, or weakening fallbacks.
- Run full parity only after substantial batches because it is slow.

## Current Operational State

- Full Python-reference parity is running from `nirs4all` and writing to
  `/tmp/nirs4all_full_parity_20260704.log`.
- A Claude Code release/cockpit audit is running read-only.
- A second Claude Code read-only audit is classifying visible parity
  `SKIPPED`/`XFAIL` cases before any code changes are made.

## Risks

- The goal tool does not support mutating active objective text after creation;
  these constraints are therefore recorded in the coordination board and treated
  as active execution constraints for the existing goal.
- Publication decisions remain blocked on the release/cockpit audit result and
  the known `dag-ml` branch/tag divergence until reviewed.
