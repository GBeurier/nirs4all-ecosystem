# Wave 2M Current Status

Date: 2026-07-01T13:07:04+02:00

## Scope

Post-W2L coordination after the workspace reset and after the post-reset
alignment commits. Claude was not used. `nirs4all-drafts` and `nirs4all-lab`
remain out of scope.

## Current Release Evidence

Selected release root:

`/home/delete/nirs4all/_release_roots/W2L-selected`

Members:

- `dag-ml -> ../../_worktrees/INT-dagml`
- `dag-ml-data -> ../../_worktrees/INT-dmd`
- `nirs4all-io -> ../../_worktrees/INT-io`
- `nirs4all-lite -> ../../nirs4all-lite`
- `nirs4all-methods -> ../../nirs4all-methods`
- `nirs4all-datasets -> ../../nirs4all-datasets`
- `nirs4all-formats -> ../../nirs4all-formats`

Short validation:

- `python3 scripts/n4a_release_lock.py --workspace-root
  /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest
  docs/contracts/release/aggregation-manifest.n4a.json --lock
  docs/contracts/release/aggregation-lock.n4a.lock.json` -> passed.
- `docs/contracts/cutover/drop-gates.n4a.json` uses `_worktrees/INT-*` for
  parity/runtime gates and allows `N4A_RELEASE_WORKSPACE_ROOT` for
  `release_lock_validation`.

The full Python-reference parity gate was not rerun in this status slice. The
current full-parity evidence remains W98: `804 passed, 32 skipped, 11 xfailed`
from `/tmp/w98_full_parity.log`.

## Current Primary Checkout Audit

Clean current checkouts:

- `nirs4all-ecosystem/main` is clean after the W2M board commits
- `dag-ml/refactor/L20-lockstep@618ffb220b5f`
- `nirs4all-io/refactor/L7-io-dagml-sibling@e52eecd827a0`
- `nirs4all-lite/main@922fdd114231`
- `nirs4all-studio/main@83aab1c18108`
- `nirs4all-web/main@ee8ea7a95946`
- `nirs4all-cluster/main@eac4d0b8a62a`
- `nirs4all-providers/main@1e289a9ee96d`
- `nirs4all-tools/main@9dc0c628c97d`
- `nirs4all-datasets/main@ac455f321144`
- `nirs4all-formats/main@89231b2786ef`
- `nirs4all-methods/main@469124855ff1`

Dirty current checkout:

- `dag-ml-data/refactor/L20-lockstep@818616e9a2c2` has the preexisting modified
  generated binary
  `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`.

Core oracle checkout:

- `nirs4all/refactor/L17-pyref@13157d79d378` is clean but divergent from
  `_worktrees/INT-nirs4all@17ed929eeb77`.
- L17 source-concat work is functionally superseded by the INT series but not
  mechanically cherry-equivalent. Do not merge or reset L17 mechanically.
- Cutover gates intentionally use `_worktrees/INT-nirs4all` for the proof.

## Current Blockers

1. Current-root release-lock proof is still not clean because primary branch
   identities differ from selected integration branches and `dag-ml-data` is
   dirty.
2. `nirs4all` primary is not the selected V1 proof checkout. A release checkout,
   if needed, should be created from `17ed929eeb77` rather than by normal-merging
   INT into L17.
3. The critical-review blockers for controller unification and methods/n4m
   execution-path integration need a fresh post-W2L audit before selecting the
   next implementation batch.
4. Full parity should remain deferred until a substantial core/runtime/native
   batch lands.

## Active Codex Agents

| Lane | Agent | Scope | Status |
| --- | --- | --- | --- |
| K | `019f1d5b-7c52-7e42-be11-f21df34236f3` / Euclid | Fresh final reviewer, read-only | running |
| B/E/H | `019f1d5c-4e07-7d42-8ee9-ff236f3a24ed` / Mill | Controller surface/adapters, read-only | running |
| F | `019f1d5c-4eab-7512-a7cf-870f8ac476fe` / Gauss | methods/n4m execution path, read-only | running |

## Next Integration Decision

Do not integrate old stopped branches or worktrees without a focused audit. The
next safe implementation batch should be chosen after the three active Codex
audits return, with disjoint write ownership and short targeted gates. Full
parity should run only after that larger implementation batch, not for this
status/documentation update.
