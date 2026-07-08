# WAVE 10G - Core/Methods/IO release and cockpit refresh

Date: 2026-07-08

## Scope

Release and cockpit integration batch after the formats/IO/core-web strict evidence lane.

## Files / repos changed

- `nirs4all-methods`
  - `6a3f6c15` / `v1.0.8`: version manifests bumped from `1.0.7` to `1.0.8`.
- `nirs4all-core`
  - `ba78a63a` / `v0.3.6`: Python/R/Rust/WASM manifests bumped from `0.3.5` to `0.3.6`.
- `nirs4all-io`
  - `d0de3c3d` / `v0.1.10`: Rust/Python/R/WASM manifests bumped from `0.1.9` to `0.1.10`.
- `nirs4all-ecosystem`
  - `c2aa321`: aggregation manifest/lock pinned to `methods v1.0.8`, `core v0.3.6`, `io v0.1.10`.
- `nirs4all-cockpit`
  - `9dcafbf`: refreshed `data/current.json` after release workflows completed.
  - `5259b54`: manual actions and target reasons aligned with latest release versions; R-universe stale items exposed as explicit important actions.

## Tests / gates run

- `nirs4all-methods`
  - `python3.11 -m pytest scripts/e2e/test_cross_binding_methods_parity.py benchmarks/cross_binding/tests/test_ci_parity_gate.py -q`
  - `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH make test-js-wasm`
- `nirs4all-core`
  - `PYTHONPATH=bindings/python/src:/home/delete/nirs4all/nirs4all-methods/bindings/python/src LD_LIBRARY_PATH=/home/delete/nirs4all/nirs4all-methods/build/dev-release/cpp/src:$LD_LIBRARY_PATH python3.11 -m unittest discover -s bindings/python/tests`
  - `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH NIRS4ALL_CORE_REQUIRE_METHODS_PARITY=1 npm test --prefix bindings/wasm`
- `nirs4all-io`
  - `python3.11 -m pytest tests/test_dataset_package.py tests/e2e/test_formats_io_datasets_methods.py::test_assemble_reference_datasets -q --artifacts-dir=/tmp/n4a-io-validation-version-bump`
- `nirs4all-ecosystem`
  - `python3.11 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - `python3.11 -m pytest tests/test_release_lock.py tests/test_gitmodules_topology.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py -q`
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 scripts/n4a_release_surface_matrix.py validate`
- `nirs4all-cockpit`
  - `python3.11 -m pytest -q`
  - `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  - `python3.11 scripts/smoke_dashboard_dom.py`

## Publication evidence

- GitHub Actions:
  - `nirs4all-methods` tag `v1.0.8`: release source, Python, npm, R, MATLAB, and wheels workflows completed successfully.
  - `nirs4all-core` tag `v0.3.6`: release source, Python, npm, crates, R, MATLAB, and CI workflows completed successfully. The main-branch `version-guard` was rerun after tag publication and completed successfully.
  - `nirs4all-io` tag `v0.1.10`: release, crates, npm, R, MATLAB, and source workflows completed successfully.
- Cockpit snapshot after refresh:
  - `green=92`, `stale=5`, `pending=4`, `missing=0`, `broken=0`, `unknown=0`, `excluded=1`.
  - `methods`, `core`, and `io` source heads have `ahead=0` against their latest production tags.

## Remaining risks / decisions

- R-universe remains externally stale:
  - `n4m` and `pls4all` still at `1.0.7`.
  - `nirs4allio` still at `0.1.9`.
  - `nirs4all` aggregate still at `0.3.5`.
  - Attempted dispatch of `r-universe/gbeurier` `sync.yml` failed with `403 Resource not accessible by personal access token`; this remains an external/manual rebuild wait.
- CRAN remains manual:
  - `n4m`, `pls4all`, `nirs4allio`, and `nirs4all` are pending/unpublished.
  - `nirs4alldatasets` remains stale at CRAN `0.2.0`.
- Full strict E2E is still not complete:
  - Remaining hybrid scenarios are multimodal Python/R/WASM roundtrip and multisource branching/stacking replay.
- Full Python-reference parity was not rerun for this release batch; targeted parity and binding gates passed, and full parity should remain a final large-batch gate before production cutover of `nirs4all` Python and `nirs4all-studio`.

