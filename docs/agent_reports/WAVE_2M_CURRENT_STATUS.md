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
| K | `019f1d5b-7c52-7e42-be11-f21df34236f3` / Euclid | Fresh final reviewer, read-only | complete |
| B/E/H | `019f1d5c-4e07-7d42-8ee9-ff236f3a24ed` / Mill | Controller surface/adapters, read-only | complete |
| F | `019f1d5c-4eab-7512-a7cf-870f8ac476fe` / Gauss | methods/n4m execution path, read-only | complete |

## Lane K Fresh Review

Euclid confirmed the current distinction:

- `_release_roots/W2L-selected` is the only valid release-lock proof root today;
- validating the lock against `/home/delete/nirs4all` still fails as expected
  because `dag-ml-data` is dirty and current branch identities differ from the
  INT branch identities encoded in the lock;
- `nirs4all/refactor/L17-pyref` is not the V1 proof checkout. L17 remains at
  `fallback=9/native=78`, while `_worktrees/INT-nirs4all` carries the W98 strict
  proof with `fallback=0/native=87`;
- short gates passed in the review: selected-root lock validation,
  `release_lock_validation` with `N4A_RELEASE_WORKSPACE_ROOT`, release-lock unit
  tests, cutover gate manifest validation, and post-W2J state check.

Decision reinforced: do not regenerate the release lock from the current root,
and do not treat L17 as equivalent to the W98 integration tree.

## Controller Surface Audit

Mill confirmed that the T2 blocker is only partially reduced:

- `dag-ml` has a real `HostControllerSpec -> ControllerManifest` derivation
  helper in `crates/dag-ml-core/src/controller_adapter.rs`, covered for the five
  nirs4all bridge shapes;
- binding-facing helpers are still missing for Python/WASM, so consumers can
  validate manifests but cannot derive them from host specs through a stable
  binding API;
- `nirs4all` still uses a static five-manifest list in `dagml_bridge.py`, with
  no public `nirs4all.runtime.list_controller_manifests()`;
- Studio has `GET /api/operators/manifests`, but it remains a soft proxy until
  nirs4all exposes the producer;
- Web hand-authors a manifest and still lacks shared controller registration for
  multi-node scheduler coverage.

Recommended next slice: `dag-ml` only, expose the existing derivation through
binding-facing JSON helpers for Python and WASM, then gate with targeted
controller adapter/Python/WASM tests and `scripts/validate_contracts.py`.

## Methods/N4M Execution Audit

Gauss confirmed that T3 remains open:

- `nirs4all-methods` exposes working SNV/PLS ABI and Python wrappers;
- explicit `MethodsSNV` / `MethodsPLS` operators can invoke `n4m`;
- native `dag-ml` execution does not directly invoke `n4m`; it calls host
  controllers, and the nirs4all dag-ml router still maps common operators to
  sklearn/import-path handlers;
- methods-installed tests remain optional/import-skipped, no ABI/version gate is
  enforced in dag-ml routing, and portable n4m model persistence remains
  unresolved.

Recommended next slice: `nirs4all` only on the selected integration checkout,
add an opt-in safe-subset SNV route through `MethodsSNV` with explicit
availability checks and fallback before execution. Defer PLS auto-routing until
SNV proves the path because PLS has higher parameter and artifact risk.

## Next Integration Decision

Do not integrate old stopped branches or worktrees without a focused audit. The
next implementation batch is split across disjoint write scopes:

- Lane B/E/H implementation: `dag-ml` integration worktree only, binding-facing
  controller-manifest derivation helpers.
- Lane F implementation: `nirs4all` integration worktree only, opt-in SNV
  methods routing.

Full parity should run only after these implementation slices have landed and
passed their targeted gates.

## Active Implementation Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| B/E/H | `019f1d64-aea5-7310-8671-b1899f76ea74` / Popper | `_worktrees/INT-dagml` only | complete, committed as `8b226bed0b6c` |
| F | `019f1d64-af5f-7341-a3a8-335d2fd37ed5` / Aristotle | `_worktrees/INT-nirs4all` only | complete, pending coordinator review |

## Lane B/E/H Implementation Result

Committed in `_worktrees/INT-dagml`:

- commit `8b226bed0b6c` (`feat(bindings): expose controller manifest derivation`);
- additive PyO3 exports: `derive_controller_manifest_json` and
  `derive_controller_manifest_list_json`;
- additive Python facade wrappers: `HostControllerSpec`,
  `HostControllerSpecs`, `derive_controller_manifest`, and
  `derive_controller_manifests`;
- additive WASM exports for the same JSON helpers;
- Python/WASM smoke scripts now assert the new surface.

Coordinator-reviewed gates:

- `cargo test -p dag-ml-core controller_adapter` -> 18 passed;
- `PYO3_PYTHON=/usr/bin/python3.11 cargo test --manifest-path
  crates/dag-ml-py/Cargo.toml derives_controller` -> 2 passed;
- `cargo test -p dag-ml-wasm derives_controller` -> 2 passed;
- `cargo fmt --all --check` -> passed;
- `cargo fmt --manifest-path crates/dag-ml-py/Cargo.toml --all --check` ->
  passed;
- `cargo clippy -p dag-ml-wasm --all-targets -- -D warnings` -> passed;
- `PYO3_PYTHON=/usr/bin/python3.11 cargo clippy --manifest-path
  crates/dag-ml-py/Cargo.toml --all-targets -- -D warnings` -> passed;
- `python3 scripts/validate_contracts.py` -> passed;
- `DAG_ML_DATA_REPO=/home/delete/nirs4all/_worktrees/INT-dmd python3
  scripts/validate_contracts.py` -> passed;
- `python3.11 -m py_compile` on touched Python files -> passed;
- `/home/delete/.nvm/versions/node/v22.21.1/bin/node --check` on touched JS
  smoke files -> passed;
- `git diff --check` -> passed.

Risk: `_dag_ml.abi3.so` was not regenerated; consumers importing an old built
extension will not see the new PyO3 symbols until the extension/wheel is rebuilt.
