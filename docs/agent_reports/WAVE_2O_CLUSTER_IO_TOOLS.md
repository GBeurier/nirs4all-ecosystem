# Wave 2O Cluster IO Tools

Date: 2026-07-01T14:05:00+02:00

## Scope

Follow-up after W2N. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

Full Python-reference parity is intentionally deferred until a larger core /
runtime / native batch.

## Starting State

- W2N integrated `INT-nirs4all` controller-manifest derivation through
  `799f789c`.
- W2N integrated `nirs4all-lite` Python/R/WASM public-surface gates through
  `8fa133b`.
- W2N refreshed and validated the release lock through ecosystem commit
  `6e96c24`.
- Non-full cutover gates passed with `pyref_oracle_full` skipped.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| I | pending | `_worktrees/INT-cluster` only | harden the trusted-LAN cluster permission/RBAC surface without importing `nirs4all` outside the runner |
| D | pending | `nirs4all-tools` only | add or tighten migration/converter golden coverage for legacy workspaces/predictions/pipelines |
| G | pending | `_worktrees/INT-io` only | clarify and test the IO/dag-ml-data dataset bridge contract/status without touching private repos |

## Review Criteria

- Lane I must preserve the cluster boundary: only
  `nirs4all_cluster/runners/nirs4all_run.py` may import `nirs4all`.
- Lane D must not weaken converter tests or hide failures behind xfail/skip.
- Lane G must keep dataset assembly in `nirs4all-io`, not move parser or dataset
  catalog logic across repo boundaries.
- No lane may touch `nirs4all-drafts` or `nirs4all-lab`.

## Expected Gates

- Targeted tests for each changed repo.
- No full parity in this wave.
- Release lock regeneration only if a release member commit changes.
