# Wave 2Q Core Methods Providers Cluster

Date: 2026-07-01T15:00:45+02:00

## Scope

Follow-up after W2P. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

Full Python-reference parity remains deferred until a core/native behavior batch
or final `LOCK-DROP` proof. This wave targets smaller blockers that W2P left
explicit:

- `n4m` installed binding evidence exists in `nirs4all-methods`, but
  `nirs4all` still needs a targeted installed-methods proof or a clear remaining
  route blocker.
- Cluster has RBAC/client coverage but still lacks a release e2e proof.
- Providers/repo/benchmarks/papers now have a read-slice provider layer, but no
  end-to-end reproducible execution gate.
- W98 full parity remains the last full Python-reference proof; post-W2P needs a
  delta ledger before any release claim.

## Starting State

- W2P integrated:
  - `nirs4all-ecosystem` `021f33d`
  - `_worktrees/INT-io` `eae8263`
  - `nirs4all-methods` `00ca8467`
  - `_worktrees/INT-studio` `17dfe69`
- The selected release root validates the aggregation lock.
- The current workspace root still differs from selected-root for release-lock
  validation and must not be used as the proof root.
- Historical `W*` worktrees and the Claude-era `.claude/worktrees/agent-*` tree
  are audit inputs only. They are not merge sources for this wave.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| C/F | pending | `_worktrees/INT-nirs4all` only | Add targeted proof around installed `n4m` methods binding consumption from `nirs4all`, without broad parity or duplicating methods logic. |
| I | pending | `_worktrees/INT-cluster` only | Add or harden minimal cluster e2e proof for scheduler/client/server behavior under release boundaries. |
| J | pending | `nirs4all-providers` only, read siblings | Turn provider read-slice status into a concrete conformance/release gate or a precise blocker report. |
| K | pending | `nirs4all-ecosystem` docs/scripts only | Publish a W98 -> post-W2P delta ledger without claiming full parity rerun. |

## Review Criteria

- Agents must read local `AGENTS.md` / `CLAUDE.md` for their touched repo before
  editing.
- No agent may touch `nirs4all-drafts` or `nirs4all-lab`.
- No agent may merge or cherry-pick historical `W*` worktrees without fresh
  diff audit and explicit review.
- Any pipeline, prediction, save/export, converter, runtime, or binding change
  must preserve or test parity with the current Python `nirs4all` oracle.
- No tests may be weakened, skipped, xfailed, or hidden behind fallbacks to make
  the wave green.
- R unavailable locally is a risk, not a green release proof.

## Expected Gates

- Targeted tests per changed repo.
- Release lock regeneration only if a lock member commit changes.
- Non-full cutover gate after integration.
- No full `pyref_oracle_full` in this wave unless the coordinator explicitly
  decides the accumulated core/native changes justify the long run.

## Integration Log

Pending.
