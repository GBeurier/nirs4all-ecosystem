# Wave 2P Release Proof And Parity

Date: 2026-07-01T14:25:46+02:00

## Scope

Follow-up after W2O and Faraday read-only audit. Claude is not used.
`nirs4all-drafts` and `nirs4all-lab` remain out of scope.

Full Python-reference parity is still deferred until this wave has produced a
larger batch of release-scope, conformance, methods, and runtime fixes. Do not
treat targeted W2M/W2N/W2O gates as release-equivalent to W98 full parity.

## Starting State

- Selected release root: `/home/delete/nirs4all/_release_roots/W2L-selected`.
- The selected root validates the aggregation lock after W2O.
- The current workspace root is not the proof root: primary `dag-ml`,
  `dag-ml-data`, and `nirs4all-io` states diverge from the selected pins.
- `nirs4all/refactor/L17-pyref` is not the V1 proof branch. The current
  integration proof branch is `_worktrees/INT-nirs4all` at `799f789c`.
- Historical `W*` worktrees and the Claude-era `.claude/worktrees/agent-*` tree
  are audit inputs only. They are not merge sources for this wave.
- The roadmap requirement is explicit: public `nirs4all` V1 accounting covers
  the Python oracle package, the aggregate R package, and browser/WASM
  distribution surfaces. A Python-only check cannot close `nirs4all`.

## Faraday Audit Summary

Read-only reviewer: `019f1d9d-bbfb-7d73-a424-73057432eca6`.

Findings carried into W2P:

- Release proof root must be unique. Use selected-root for gates, not the dirty
  current workspace root.
- Full Python-reference parity has not been rerun since W98
  (`804 passed, 32 skipped, 11 xfailed`, `fallback=0`).
- The release matrix is currently a pointer to the draft inventory; the
  aggregate lock covers seven components, not every public V1 product surface.
- R surface is topology-gated but skipped locally because R is unavailable.
- IO W2O did not rerun cross-CLI `dag-ml` / `dag-ml-data` conformance.
- Methods/native binding parity remains weak: SNV is opt-in, PLS is not routed,
  and installed `n4m` is not loadable locally.
- Studio Playwright and cluster e2e remain environment gates, not green proof.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| A/K | pending | `nirs4all-ecosystem` release docs/scripts only | Bound the public release matrix: aggregate lock members vs public V1 products, including Python/R/WASM `nirs4all` surfaces. |
| G | pending | `_worktrees/INT-io` only | Add or rerun cross-CLI IO -> `dag-ml-data` conformance on selected pins. |
| F | pending | `nirs4all-methods` only | Improve methods binding/loadability evidence without duplicating methods logic outside the methods repo. |
| H | pending | `_worktrees/INT-studio` only | Reduce Studio runtime e2e/Playwright environment gap without weakening existing tests. |
| J | pending | repo/benchmarks/papers read-only unless a clear isolated fix is found | Audit provider/plugin/export release gaps for `repo`, `benchmarks`, and `papers`. |

## Review Criteria

- Agents must read the local `AGENTS.md` / `CLAUDE.md` for their touched repo
  before editing.
- No agent may touch `nirs4all-drafts` or `nirs4all-lab`.
- No agent may merge or cherry-pick historical `W*` worktrees without a fresh
  diff audit and explicit integration review.
- Any pipeline, prediction, save/export, converter, runtime, or binding change
  must preserve or test parity with the current Python `nirs4all` oracle.
- R skipped because missing runtime is recorded as risk, not as a green gate.
- No tests may be reduced, xfailed, or hidden behind broad fallbacks to obtain a
  green result.

## Expected Gates

- Targeted tests for each changed repo.
- Release lock validation if a lock member changes.
- Cross-CLI `dag-ml` / `dag-ml-data` / IO conformance if Lane G changes code or
  test contracts.
- No full `pyref_oracle_full` until this wave accumulates a substantial batch.

## Integration Log

Pending.
