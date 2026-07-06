# Wave 7M - RC10 release lock and WASM metadata

Date: 2026-07-06

## Scope

Coordinate the post-parity release cleanup without touching `nirs4all-ui` or
`nirs4all-quality`, which are owned by another active agent.

## Integrated heads

| Component | Repo | Commit | Tag | Decision |
| --- | --- | --- | --- | --- |
| `dag_ml_data` | `dag-ml-data` | `0ba4cf68` | `n4a-v1-rc10-2026.07-refactor` | R DESCRIPTION aligned to `0.2.4`; release metadata validator now checks R. |
| `io` | `nirs4all-io` | `ccf9a7d2` | `n4a-v1-rc10-2026.07-refactor` | `dag-ml-data` pin aligned to `0.2.4`; dagml bridge follows workspace `0.1.6`; web WASM bundles rebuilt. |
| `datasets` | `nirs4all-datasets` | `f7b9caa1` | `n4a-v1-rc10-2026.07-refactor` | WASM lock aligned to `0.3.4`. |

Unchanged selected heads retained from the previous lock: `dag_ml`, `formats`,
`methods`, and `lite`/`nirs4all-core`.

## Files changed by lane

- `dag-ml-data`: `crates/dag-ml-data-r/DESCRIPTION`,
  `scripts/validate_release_metadata.py`.
- `nirs4all-io`: root and WASM Cargo locks, `Cargo.toml`,
  `crates/nirs4all-io-dagml/Cargo.toml`, removal of the stale local dagml lock,
  version docs, `scripts/bump_version.sh`, `web/make-standalone.mjs`, and the
  tracked web WASM bundles/metadata.
- `nirs4all-datasets`: `bindings/wasm/Cargo.lock`.
- `nirs4all-org`: public tools badge text for `nirs4all-tools v0.0.2`.
- `nirs4all-ecosystem`: `aggregation-lock.n4a.lock.json` regenerated from an
  isolated RC10 selected root.

## Validation

- `nirs4all`: full parity already green in this wave:
  `799 passed, 0 skipped, 0 xfailed`.
- `nirs4all-io`:
  - `scripts/bump_version.sh --check`
  - `cargo check -p nirs4all-io-dagml`
  - `cargo test -p nirs4all-io-dagml` (8 tests)
  - `cargo check --manifest-path bindings/wasm/Cargo.toml --target wasm32-unknown-unknown --locked`
  - `node web/make-standalone.mjs`
  - `node web/tests/standalone-smoke.mjs`
  - `node web/tests/standalone-formats-smoke.mjs` (51 real fixtures)
- `nirs4all-datasets`:
  - `scripts/bump_version.sh --check`
  - `cargo check --manifest-path bindings/wasm/Cargo.toml --target wasm32-unknown-unknown --locked`
  - `cargo test --manifest-path bindings/wasm/Cargo.toml`
- `dag-ml-data`:
  - `/usr/bin/python3.11 scripts/validate_release_metadata.py`
  - `/usr/bin/python3.11 -m py_compile scripts/validate_release_metadata.py`
  - `cargo fmt --all --check`
- `nirs4all-formats`:
  - `cargo metadata --manifest-path bindings/wasm/Cargo.toml --locked --no-deps`
  - `cargo check --manifest-path bindings/wasm/Cargo.toml --target wasm32-unknown-unknown --no-default-features --locked`
  - `scripts/bump_version.sh --check`
- `nirs4all-ecosystem`:
  - `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-selected-rc10-20260706 validate ...`
  - `python3 scripts/n4a_release_surface_matrix.py validate`
  - `/usr/bin/python3.11 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -p no:cacheprovider` (22 passed)

## Risks and notes

- `nirs4all-ui` and `nirs4all-quality` were left untouched by this wave.
- `nirs4all-formats` default WASM build needs Emscripten for zstd/Parquet; the
  `nirs4all-io` web build used `/home/delete/emsdk/upstream/emscripten/emcc`
  and preserved `formats` features `hdf5=true`, `matlab=true`, `parquet=true`.
- PyPI Trusted Publisher blockers for `nirs4all-core` and
  `nirs4all-providers` remain external registry configuration blockers.
- No new full parity run was launched after this mechanical release-lock batch;
  the last full Python parity remains the wave reference.
