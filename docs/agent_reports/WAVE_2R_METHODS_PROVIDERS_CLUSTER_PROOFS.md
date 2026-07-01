# Wave 2R Methods Providers Cluster Proofs

Date: 2026-07-01T15:25:07+02:00

## Scope

Follow-up after W2Q. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2Q produced three useful diagnostics but not all release proofs:

- `nirs4all` can now report installed `n4m` binding status, but the local
  `INT-nirs4all` environment lacks `n4m`, so installed-binding parity is not
  green there.
- `nirs4all-providers` now has a strict release gate, but the local providers
  environment lacks the four sibling extras, so the gate correctly reports
  missing backings.
- Cluster has a release e2e scheduler proof, but the long-running worker agent
  loop remains outside that test.

The public V1 surface matrix must continue to include `nirs4all` Python, R, and
browser/WASM surfaces:

- `nirs4all.python.oracle`
- `nirs4all.r.aggregate`
- `nirs4all.browser_wasm.aggregate`
- `nirs4all.browser_wasm.methods_scoped`
- `nirs4all.browser_wasm.datasets_scoped`

Full Python-reference parity remains deferred until a large enough core/native
batch or final `LOCK-DROP` proof. W2R targets repeatable proof harnesses and
gaps; it must not claim full parity unless that long gate is explicitly run.

## Starting State

- W2Q integrated:
  - `nirs4all-ecosystem` `c13e7ba`
  - `_worktrees/INT-nirs4all` `27da2c80`
  - `_worktrees/INT-cluster` `2da60953`
  - `_worktrees/INT-providers` `7a9839b5`
- The selected release root validates the aggregation lock.
- The final W2Q non-full cutover gate passed with `pyref_oracle_full` skipped.
- Historical `W*` worktrees and Claude-era trees remain audit inputs only, not
  merge sources.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| C/F | pending | `_worktrees/INT-nirs4all` only, read `nirs4all-methods` | Build a repeatable installed-`n4m` proof path for `nirs4all` or report a precise blocker; do not move numerical logic into Python. |
| J/G | pending | `_worktrees/INT-providers` only, read sibling provider repos | Make the providers release gate runnable against local sibling packages or document the exact packaging blockers without weakening the gate. |
| I | pending | `_worktrees/INT-cluster` only | Add a bounded worker-agent loop proof or document the minimal blocker; keep cluster as scheduler/client/server, not core logic. |
| K | pending | `nirs4all-ecosystem` docs/scripts only | Final W2R reviewer after lanes finish; do not code until C/F, J/G, and I are ready for audit. |

## Review Criteria

- Agents must read local `AGENTS.md` / `CLAUDE.md` before editing.
- No agent may touch `nirs4all-drafts` or `nirs4all-lab`.
- No agent may merge or cherry-pick historical `W*` worktrees without fresh
  diff audit and coordinator review.
- Any pipeline, prediction, runtime, binding, or provider-execution change must
  preserve or test parity against the current Python `nirs4all` oracle.
- No tests may be weakened, hidden behind silent passes, xfailed, or skipped to
  manufacture green status. Optional missing dependencies must be explicit
  diagnostics, and strict release modes must fail when proof prerequisites are
  missing.
- R unavailable locally is a risk, not a release proof.

## Expected Gates

- Targeted tests per changed repo.
- Providers gate must either pass with real local siblings or fail with a precise
  blocker that can be acted on.
- Installed `n4m` proof must either pass in a reproducible harness or fail with
  a precise environment/package blocker.
- Cluster worker-agent proof must be bounded and deterministic.
- Release lock regeneration only if a lock member commit changes.
- Non-full cutover gate after integration.
- No full `pyref_oracle_full` unless the coordinator explicitly decides the
  accumulated changes justify the long run.

## Integration Log

Pending.
