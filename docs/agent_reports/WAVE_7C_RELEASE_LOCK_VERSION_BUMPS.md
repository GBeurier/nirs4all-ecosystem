# Wave 7C — Release Lock Version Bumps

Date: 2026-07-06

## Scope

- Rejected the first RC2 lock because it would have locked `dag-ml` at `0.2.1` while `0.2.2` already exists on crates.io, and would have reused the published `dag-ml-data` `0.2.3`.
- Bumped publishable RC heads:
  - `dag-ml` to `0.2.3`
  - `dag-ml-data` to `0.2.4`
  - `nirs4all-core` aggregate publications to `0.2.6` because `v0.2.3`, `v0.2.4`, and `v0.2.5` already exist.
- Regenerated `aggregation-lock.n4a.lock.json` from a clean selected workspace at `/home/delete/nirs4all/_selected-rc3-20260706`.
- Regenerated the lock again after the final `nirs4all-core` RC head `715aa59076b2c978950bfc7f005fbca44f91a0c0` added the Rust dependency lock update.

## Files Changed

- `dag-ml/Cargo.toml`
- `dag-ml/Cargo.lock`
- `dag-ml/crates/dag-ml-py/Cargo.toml`
- `dag-ml/crates/dag-ml-py/pyproject.toml`
- `dag-ml/docs/contracts/abi_snapshot.v1.json`
- `dag-ml-data/Cargo.toml`
- `dag-ml-data/Cargo.lock`
- `dag-ml-data/crates/dag-ml-data-py/Cargo.toml`
- `dag-ml-data/crates/dag-ml-data-py/pyproject.toml`
- `dag-ml-data/crates/dag-ml-data-capi/bindings/python/pyproject.toml`
- `dag-ml-data/crates/dag-ml-data-capi/bindings/python/dag_ml_data_provider/__init__.py`
- `dag-ml-data/crates/dag-ml-data-r/src/rust/Cargo.toml`
- `dag-ml-data/crates/dag-ml-data-r/src/rust/Cargo.lock`
- `dag-ml-data/docs/contracts/abi_snapshot.v1.json`
- `nirs4all-core/bindings/python/pyproject.toml`
- `nirs4all-core/bindings/r/DESCRIPTION`
- `nirs4all-core/bindings/rust/nirs4all/Cargo.toml`
- `nirs4all-core/bindings/wasm/package.json`
- `nirs4all-core/bindings/wasm/package-lock.json`
- `nirs4all-core/Cargo.lock`
- `nirs4all-core/bindings/python/tests/test_release_topology.py`
- `nirs4all-ecosystem/docs/contracts/release/aggregation-lock.n4a.lock.json`

## Validation

- `dag-ml`: `python3.11 scripts/validate_release_metadata.py`
- `dag-ml`: `python3.11 scripts/release/publish_crates.py --plan-only --tag v0.2.3`
- `dag-ml`: `cargo fmt --all --check`
- `dag-ml`: `cargo test --workspace` (575 passed, 2 ignored perf probes)
- `dag-ml-data`: `python3.11 scripts/validate_release_metadata.py`
- `dag-ml-data`: `python3.11 scripts/release/publish_crates.py --plan-only --tag v0.2.4`
- `dag-ml-data`: `cargo fmt --all --check`
- `dag-ml-data`: `cargo test --workspace` (270 passed, 2 ignored perf probes)
- `nirs4all-core`: `npm run test:js --prefix bindings/wasm`
- `nirs4all-core`: `node bindings/wasm/node_modules/typescript/bin/tsc --project bindings/wasm/tsconfig.typecheck.json`
- `nirs4all-core`: direct Python metadata check for `0.2.6`
- `nirs4all-core`: `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests`
- `nirs4all-core`: `cargo test --manifest-path bindings/rust/nirs4all/Cargo.toml`
- `nirs4all-core`: `cargo publish --manifest-path bindings/rust/nirs4all/Cargo.toml --dry-run --allow-dirty`
- `nirs4all-core`: `PATH=/home/delete/miniconda3/envs/pls4all_r/bin:$PATH R CMD build bindings/r --no-build-vignettes`
- `nirs4all-core`: `python3.11 -m build bindings/python`
- `nirs4all-core`: `python3.11 -m twine check bindings/python/dist/*`
- `nirs4all-ecosystem`: `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_selected-rc3-20260706 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `nirs4all-ecosystem`: `python3 scripts/n4a_release_surface_matrix.py validate`
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate` (11 scenarios)
- `nirs4all-ecosystem`: `python3 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py` (80 passed)

## Tags

- Published `v0.2.3` for `dag-ml`.
- Published `v0.2.4` for `dag-ml-data`.
- Published `v0.2.6` for `nirs4all-core`.
- Published `n4a-v1-rc3-2026.07-refactor`, `n4a-v1-rc4-2026.07-refactor`, and `n4a-v1-rc5-2026.07-refactor` for the selected component repos. RC5 is the final coordination tag for the heads after the core release-topology test fix and Rust dependency lock update.

## Publications

- crates.io: `dag-ml-wasm 0.2.3` published; other `dag-ml 0.2.3` crates already existed.
- crates.io: `dag-ml-data-cli 0.2.4` and `dag-ml-data-capi 0.2.4` published; other `dag-ml-data 0.2.4` crates already existed.
- crates.io: `nirs4all 0.2.6` published.
- npm: `nirs4all 0.2.6` already existed, so no duplicate publish attempted.
- PyPI: `nirs4all-core 0.2.6` artifacts build and pass `twine check`, but upload is blocked because no PyPI token was provided and the unauthenticated upload is rejected with HTTP 403.
- R: `nirs4all_0.2.6.tar.gz` builds locally with the conda R toolchain; no CRAN/R-universe push is performed from this workspace.

## Risks

- PyPI still needs Trusted Publisher or a `pypi_token`; the available token list did not include one.
- The unchanged lock members have multiple tags on the same commit; `git describe --exact-match` can record an older exact tag even when RC5 also points at the commit.
