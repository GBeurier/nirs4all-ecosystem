# Wave 3AP - W93 Bridge Freshness and Methods Surface Audit

Date: 2026-07-02

## Scope

This batch re-audited pre-existing W92/W93 worktrees after the reset warning:

- Lane G: W93 `nirs4all-datasets`, `nirs4all-formats`, and `nirs4all-io`.
- Lane F/E: W92/W3S `nirs4all-methods` release-surface and JS/WASM boundary.

The old worktrees were audited, not merged wholesale. Only one minimal IO
doc/test patch was integrated. Full parity was intentionally deferred.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Ampere the 2nd | `nirs4all-datasets` W93 audit | no-op, verified | W93 `20b41824` is already ancestor of current `main`; bridge remains datasets -> IO only. |
| Tesla the 2nd | `nirs4all-formats` W93 audit | no-op, verified | W93 formats branch has no delta over current `main`; formats remains parser-only. |
| Averroes the 2nd | `nirs4all-io` W93 audit/patch | integrated | Commit `9468e2e` (`test(dataset): cover bare reference io specs`). |
| Faraday the 2nd | `nirs4all-methods` W92/W3S audit | no-op, verified | W92 `d077ea5f` and W3S/W3AC `98148c14` are already ancestors of current `main`. |
| Boole the 2nd | `nirs4all-io` review | GO | Confirmed IO diff is doc/test-only, no dependency-cycle or W3AO regression. |

## Integrated Changes

### `nirs4all-io`

- Updated the Python MVP API doc signature to include the real target set:
  `spectrodataset`, `assembled`, `dataset_package`, and `dag-ml-data`.
- Kept the W3AO clarification that Python MVP `dag-ml-data` raises
  `NotImplementedError`; supported emission lives in the Rust
  `nirs4all-io-dagml` bridge.
- Added a local dataset-package regression test for any object exposing
  `to_io_spec()` that returns a bare JSON-ready spec dict with absolute canonical
  file paths, matching the `NirsDataset` seam.
- No runtime code changed.

### `nirs4all-datasets`

- No source change was needed.
- Current `main` already contains W93 and later guard/test additions, including:
  - `NirsDataset.to_io_spec()` over canonical Parquet files;
  - `NirsDataset.to_dataset_package()` delegating to IO;
  - direct `nirs4all_io.load(ds, target="dataset_package")` coverage;
  - anonymized `variables.parquet` privacy guard coverage.

### `nirs4all-formats`

- No source change was needed.
- W93 formats had no code delta and is already absorbed by current `main`.
- Formats remains the parser/vendor-reader layer; dataset canonical Parquet was
  not routed through the spectral formats reader.

### `nirs4all-methods`

- No source change was needed.
- The W92 release-surface patch and later JS/WASM smoke documentation patch are
  already present in current `main`.
- The W99 W92 blocker no longer applies to this local methods head.

## Validation

`nirs4all-io`:

- `PYTHONPATH=src pytest tests/test_dataset_package.py tests/test_load_e2e.py::test_load_dag_ml_data_target_points_to_rust_bridge tests/test_import_boundary.py -q -p no:cacheprovider` -> 8 passed.
- `PYTHONPATH=/home/delete/nirs4all/nirs4all-io/src:/home/delete/nirs4all/nirs4all-datasets/src pytest /home/delete/nirs4all/nirs4all-datasets/tests/test_dataset.py::test_nirs4all_io_load_accepts_real_reference_dataset -q -p no:cacheprovider` -> 1 passed.
- `ruff check tests/test_dataset_package.py docs/API.md` -> passed.
- Reviewer also ran `.venv/bin/python -m pytest tests/test_dataset_package.py -q` -> 5 passed, `.venv/bin/python -m pytest tests/test_import_boundary.py -q` -> 2 passed.
- `git diff --check` -> passed.

`nirs4all-datasets`:

- `pytest -q tests/test_dataset.py tests/test_anon_enforcement.py` -> 20 passed, 3 skipped.

`nirs4all-formats`:

- `cargo fmt --all --check` -> passed.
- `cargo check -p nirs4all-formats-core -p nirs4all-formats` -> passed.
- `cargo clippy -p nirs4all-formats-core -p nirs4all-formats --all-targets -- -D warnings` -> passed.
- `cargo test -p nirs4all-formats-core -p nirs4all-formats` -> passed.

`nirs4all-methods`:

- `pytest bindings/python/tests/test_release_surface_metadata.py` -> 1 passed.
- `pytest benchmarks/cross_binding/tests/test_ci_parity_gate.py` -> 12 passed.
- `py_compile` over the generator/smoke/harness scripts -> passed.
- `scripts/bump_version.sh --check` -> passed.
- `catalog/scripts/validate.py --strict-abi --check-references` -> passed,
  `702/702` ABI and `209/209` references.
- `split_legacy_methods.py --check && selftest.py` -> passed.
- `smoke_installed_nirs4all_methods.py --lib build/dev-release/...` -> passed.
- `git diff --check` -> passed.
- JS `npm test` was not conclusive in the agent environment because only Windows
  `npm` was available and no Linux `node` was installed.

## Gate Policy

- No Python-reference full parity was run in this batch.
- No Rust/dag-ml-data full conformance was run because IO changed only docs and
  a Python contract test.
- No tests were reduced, xfailed, or weakened.
- No superseded Claude/worktree branch was merged blindly.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Risks

- `nirs4all-io`: the new test covers Python MVP duck-typing and canonical
  Parquet loading, not native Rust bridge emission.
- `nirs4all-methods`: JS/WASM smoke remains to rerun in a Linux Node/Emscripten
  environment despite existing W3S coverage.
- `nirs4all-datasets` and `nirs4all-methods` are both ahead of and behind their
  remotes; remote-only deltas were not merged in this batch.
