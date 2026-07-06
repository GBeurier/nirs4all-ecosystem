# WAVE 7P - DAG-ML main alignment and dagmldata R-universe fix

Date: 2026-07-06
Agent: Codex, with read-only audit by Locke
Lane: release/cockpit/R-universe coordination

## Scope

- Aligned `dag-ml` and `dag-ml-data` default branches with the RC code paths needed by downstream release services.
- Fixed the stale committed `dag-ml` Python extension binary after the `main` merge.
- Fixed `dagmldata` R packaging so the R-universe subdirectory build no longer depends on sibling Rust crates missing from the R tarball.
- Kept `nirs4all-ui` and `nirs4all-quality` untouched; both remain reserved for the active quality/UI work.

## Repositories and commits

- `dag-ml`
  - `b449bf3` - merge `refactor/L20-lockstep` into `main`.
  - `b3f34bf` - refresh committed `crates/dag-ml-py/python/dag_ml/_dag_ml.abi3.so`.
- `dag-ml-data`
  - `e3551d9` - merge `rc/v1-full-refactor` into `main`.
  - `bfe6431` - make `dagmldata` Rust deps registry-based on `rc/v1-full-refactor`.
  - `c53ee46` - merge the `dagmldata` fix into `main`.
- `nirs4all-cockpit`
  - `ops/targets.yaml`
  - `data/current.json`

## Validation

- `dag-ml`
  - `python scripts/validate_release_metadata.py`
  - `cargo check -p dag-ml-core -p dag-ml-capi -p dag-ml-wasm --all-targets`
  - `maturin build --release --features extension-module`
  - `python scripts/smoke_python_wheel_metadata.py /tmp/dag-ml-main-wheels/dag_ml-0.2.3-cp311-abi3-manylinux_2_34_x86_64.whl`
  - `python scripts/check_so_freshness.py`
  - GitHub Actions `main` CI run `28824831901`: success.
- `dag-ml-data`
  - `python scripts/validate_release_metadata.py`
  - `cargo check -p dag-ml-data-core -p dag-ml-data-capi -p dag-ml-data-provider -p dag-ml-data-wasm --all-targets`
  - `maturin build --release --features extension-module`
  - `python scripts/smoke_python_wheel_metadata.py /tmp/dag-ml-data-main-wheels/dag_ml_data-0.2.4-cp311-abi3-manylinux_2_34_x86_64.whl`
  - isolated R subdir metadata check:
    `cargo metadata --manifest-path /tmp/dagmldata-r-package/src/rust/Cargo.toml --locked --format-version 1 --no-deps`
  - GitHub Actions `rc/v1-full-refactor` CI run `28824909904`: success.
  - GitHub Actions `main` CI run `28824918011`: success.
- `nirs4all-cockpit`
  - `python -m cockpit.cli collect --only dag-ml,dag-ml-data`
    - Result: `green=15 stale=0 pending=0 missing=2 broken=1 unknown=0 excluded=0`
  - `python -m cockpit.cli collect --out data/current.json`
    - Result: `green=85 stale=2 pending=4 missing=7 broken=1 unknown=0 excluded=1`
  - `python -m pytest -q tests/test_targets_topology.py tests/test_cli.py tests/test_reconcile.py -p no:cacheprovider`
    - Result: `33 passed`
  - `python -m cockpit.cli validate-targets`
    - Result: `OK: ops/targets.yaml - 21 packages, 100 targets`
  - `python -m cockpit.cli summarize data/current.json`
    - Result: `green=85 stale=2 pending=4 missing=7 broken=1 unknown=0 excluded=1`
  - `git diff --check`

## Decisions

- `dagmldata` is now cockpit `tracked`, not `planned`, because the package is configured in R-universe and should be treated as an active release surface.
- The current R-universe registry result remains `broken` until R-universe rebuilds from the corrected `dag-ml-data/main`.
- `dag-ml` and `dag-ml-data` PyPI bindings remain `planned/missing`; there is no local PyPI token and no completed PyPI Trusted Publisher setup for those names.

## Remaining risks / blockers

- Direct `workflow_dispatch` of `r-universe/gbeurier` build workflow failed with GitHub `403 Resource not accessible by personal access token`. The fix is pushed, but the rebuild must be triggered by R-universe polling/webhook or by a token with Actions permission on `r-universe/gbeurier`.
- Local R validation could not run because `R` is not installed in the WSL environment. The isolated Cargo metadata check verifies the previous missing sibling-crate failure mode is removed.
- The cockpit now intentionally shows `dagmldata` as `broken` until the remote rebuild succeeds.
