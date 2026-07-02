# RC-O Release Lock Topology

Date: 2026-07-02
Scope: `nirs4all-ecosystem` only

## Decision

GO for the ecosystem-only release-lock/topology correction.

The aggregation manifest now names the selected RC worktrees explicitly through
`selected_workspace_path` while preserving canonical public `repo_path` values
in the lock. Lock generation and validation now require selected branches to
match `rc/v1-*`, so old main/refactor tag checkouts are not accepted as RC V1
selection evidence.

The public V1 surface matrix now explicitly accounts for:

- `nirs4all-python` as the outside-lock Python oracle surface.
- `nirs4all-core` as the selected aggregate/core surface behind the `lite` lock
  member alias.
- Required R, JavaScript/WASM, Rust, and MATLAB/Octave aggregate surfaces.

## Files Modified

- `docs/contracts/release/aggregation-manifest.n4a.json`
  - Added release selection policy and per-member `selected_workspace_path`.
  - Added `nirs4all-core` alias/target metadata for the `lite` member.
  - Added MATLAB/Octave package metadata for the aggregate member.
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
  - Regenerated from `/home/delete/nirs4all/_worktrees` using selected RC heads.
- `docs/contracts/release/public-v1-surface-matrix.n4a.json`
  - Added explicit `nirs4all-python`, `nirs4all-core`, Rust, and MATLAB/Octave
    required surfaces.
  - Renamed WASM accounting to explicit `javascript_wasm` surface ids.
- `scripts/n4a_release_lock.py`
  - Added selected workspace path support and RC branch-pattern validation.
- `scripts/n4a_release_surface_matrix.py`
  - Added `javascript_wasm` and `matlab_octave` package checks.
  - Allows lock-member target paths and aliases such as `nirs4all-core`.
- `tests/test_release_lock.py`
  - Added selected-worktree and non-RC branch rejection coverage.
- `tests/test_release_surface_matrix.py`
  - Updated required surface assertions and added Rust-required accounting
    coverage.

## Selected RC Pins

- `dag_ml`: `RC-v1-dagml` `rc/v1-full-refactor@7f86a9b3db66`
- `dag_ml_data`: `RC-v1-dmd` `rc/v1-full-refactor@e68168543653`
- `formats`: `RC-v1-formats` `rc/v1-full-refactor@86218e633d13`
- `io`: `RC-v1-io` `rc/v1-full-refactor@90fe63066b1d`
- `lite`: `RC-v1-nirs4all-core` `rc/v1-full-refactor-core@29d6d04a5bb0`
- `methods`: `RC-v1-methods` `rc/v1-full-refactor@09adf881aef5`
- `datasets`: `RC-v1-datasets` `rc/v1-full-refactor@28d08977912d`

## Tests Run

- `python3 -m json.tool docs/contracts/release/aggregation-manifest.n4a.json`
  -> passed.
- `python3 -m json.tool docs/contracts/release/public-v1-surface-matrix.n4a.json`
  -> passed.
- `python3 -m py_compile scripts/n4a_release_lock.py scripts/n4a_release_surface_matrix.py tests/test_release_lock.py tests/test_release_surface_matrix.py`
  -> passed.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> passed.
- `python3 scripts/n4a_release_surface_matrix.py validate`
  -> passed.
- `python3 scripts/n4a_release_surface_matrix.py report`
  -> passed and lists Python/core/R/JavaScript-WASM/Rust/MATLAB required
  surfaces.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> passed.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`
  -> passed.
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -q -p no:cacheprovider`
  -> 19 passed.
- `python3 -m py_compile scripts/n4a_release_lock.py scripts/n4a_release_surface_matrix.py scripts/n4a_cutover_gates.py tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py`
  -> passed.
- `git diff --check`
  -> passed.

## Risks

- Remote fetchability is still not green. `python3 scripts/n4a_release_lock.py
  audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json
  --lock docs/contracts/release/aggregation-lock.n4a.lock.json
  --fail-on-unfetchable` returned non-zero: 3/7 fetchable, with `datasets`,
  `io`, `lite`, and `methods` not advertised by their configured remotes.
- `dag_ml`, `dag_ml_data`, and `formats` RC heads are also exact-matched by the
  historical `n4a-v1-2026.07-refactor` tag, but they are now selected via
  `rc/v1-*` branches. The branch-pattern gate is the release selection
  authority, not the old tag name.
- Full parity, Studio/Web strict runtime gates, and release-infrastructure
  R/MATLAB proofs were not run in this topology pass.
