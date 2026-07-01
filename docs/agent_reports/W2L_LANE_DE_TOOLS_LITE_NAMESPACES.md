# W2L Lane D/E - Tools and Lite Namespaces

## Agent

Codex Lane D/E tools + lite/package namespaces post-reset.

## Lane

D/E: `nirs4all-tools` migration goldens and CLI behavior; `nirs4all-lite`
release topology and package namespace audit.

## Files modified

- `nirs4all-lite/bindings/python/src/nirs4all_core/__init__.py`
  - Replaced a long direct re-export import list with a dynamic mirror from
    `nirs4all_lite` using the existing `CORE_FACADE_EXPORTS + TOPOLOGY_EXPORTS`
    contract. This fixes ruff F401 without changing the advertised
    `nirs4all_core.__all__` surface.
- `nirs4all-ecosystem/docs/agent_reports/W2L_LANE_DE_TOOLS_LITE_NAMESPACES.md`
  - This report.

No `nirs4all-tools` code or fixture changes were needed.

## Evidence

`nirs4all-tools` contains the W97/W104 work after reset:

- `tests/fixtures/legacy/old_workspace_mixed/sample.meta.parquet` is a valid
  reduced Parquet sidecar; `pyarrow` 24.0.0 is available and
  `test_golden_mixed_workspace_fixture_labels_are_release_honest()` reads the
  expected three rows.
- `tests/fixtures/legacy/old_workspace_mixed/store.duckdb` is explicitly an
  opaque DuckDB sentinel, not a claimed semantic DuckDB database.
- `tests/fixtures/legacy/sqlite_legacy_arrays_workspace.sql` lowers legacy
  `prediction_arrays` metadata and array rows into workspace-v2 metadata,
  Parquet sidecars, and preserved JSONL provenance.
- CLI `legacy inspect tests/fixtures/legacy/old_workspace_mixed --format json`
  reports the expected kinds: `duckdb-workspace`, `fs-runs-legacy`, and
  `loose-predictions`.
- CLI `legacy migrate ... --dry-run` reports `artifacts=3`,
  `unsupported=3`, and `would_preserve_opaque=3` without creating output.
- `duckdb` is not installed locally, matching W104's residual scope: no
  semantic DuckDB golden should be claimed from this checkout.

`nirs4all-lite` includes the W94 release topology work:

- `nirs4all_lite.release_topology_manifest()` exposes
  `nirs4all-lite` as current aggregate, `nirs4all-core` as release-gated future
  target, Python facades (`nirs4all_lite`, `n4a`, `nirs4all_core`), non-Python
  aggregate namespaces, install distribution rows, upstream component rows, and
  license/provenance/`nirs4all-methods` C ABI pointers.
- Python packaging ships only `nirs4all_lite`, `n4a`, and `nirs4all_core`; it
  does not ship or shadow `nirs4all`.
- Non-Python aggregate package names are present as current surfaces:
  Rust crate `nirs4all`, npm package `nirs4all`, R package `nirs4all`, and
  MATLAB/Octave namespace `+nirs4all`.

Remaining package namespace gaps:

- Python: final `nirs4all-core` distribution rename remains release-gated; the
  full Python `nirs4all` import remains reserved for the modelling library.
- R: aggregate `nirs4all` exists, but `dag_ml` has no declared R candidate and
  methods naming is still `n4m`/`pls4all`; public `nirs4allmethods` remains a
  governance decision.
- npm: aggregate is still unscoped `nirs4all`; upstream WASM names are mixed
  (`@nirs4all/methods-wasm` and `@nirs4all/datasets-wasm` scoped, formats/io
  and dag-ml entries unscoped). The `@nirs4all/*` migration remains open.
- Rust: the crate is named `nirs4all` and re-exports `dag-ml`/`dag-ml-data`,
  but formats/io/methods/datasets are currently marker or dynamic-delegation
  surfaces rather than first-class crate re-exports.
- MATLAB/Octave: aggregate `+nirs4all` exists, but execution still delegates to
  upstream `+pls4all`; there are no MATLAB package namespaces for formats/io,
  datasets, dag-ml, or dag-ml-data in this aggregate.

## Tests/gates run

From `nirs4all-tools`:

- `PYTHONPATH=src python3.11 -m pytest tests/test_real_golden_fixtures.py -q`
  - Passed: 5 tests.
- `PYTHONPATH=src python3.11 -m pytest tests/test_cli.py -q`
  - Passed: 10 tests.
- `PYTHONPATH=src python3.11 -m pytest -q`
  - Passed: 83 tests.
- `python3.11 -m ruff check .`
  - Passed.
- `PYTHONPATH=src python3.11 -m mypy`
  - Passed.
- `PYTHONPATH=src python3.11 -m nirs4all_tools --version`
  - Passed: `nirs4all-tools 0.0.1`.
- `legacy inspect` and `legacy migrate --dry-run` on
  `tests/fixtures/legacy/old_workspace_mixed`
  - Passed with the expected three opaque-preservation candidates.
- `git diff --check`
  - Passed.

From `nirs4all-lite`:

- `PYTHONPATH=bindings/python/src python3.11 -m unittest bindings/python/tests/test_release_topology.py -v`
  - Passed: 8 tests.
- `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests`
  - Passed: 34 tests, 1 skipped.
- `PYTHONPATH=bindings/python/src python3.11 -m ruff check bindings/python/src/nirs4all_lite/_topology.py bindings/python/tests/test_release_topology.py bindings/python/src/n4a/__init__.py bindings/python/src/nirs4all_core/__init__.py`
  - Failed before the local fix on F401 in `nirs4all_core/__init__.py`; passed
    after the fix.
- `python3.11 -m py_compile bindings/python/src/nirs4all_lite/_topology.py bindings/python/tests/test_release_topology.py bindings/python/src/n4a/__init__.py bindings/python/src/nirs4all_core/__init__.py`
  - Passed.
- `scripts/bump_version.sh --check`
  - Passed: all manifests in sync with Rust crate version `0.2.0`.
- `make test-rust`
  - Passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace` with 8 Rust tests.
- `make test-python`
  - Passed: 34 Python tests, 1 skipped.
- `npm ci && npm test` from `bindings/wasm` through a Windows `cmd.exe pushd`
  mapping to `\\wsl$`
  - Passed: 12 tests.
- `git diff --check`
  - Passed.

Not run locally:

- R package gate: no `R` binary in PATH.
- Octave/MATLAB gate: no `octave` binary in PATH.

Note: direct `make test` reached Rust/Python green, then failed at
`npm ci --prefix bindings/wasm` because the only available npm is the Windows
binary under WSL and it mishandled the UNC cwd / existing `node_modules`.
Removing the generated `bindings/wasm/node_modules` and running `npm ci &&
npm test` from a Windows-mapped `\\wsl$` path executed the actual WASM tests
successfully.

## Risks

- Do not market the DuckDB fixture as semantic DuckDB coverage; it is an opaque
  preservation sentinel until a real reduced DuckDB database can be authored
  with the optional dependency.
- The WSL checkout has Windows npm but no Linux `node`; direct npm gates can be
  misleading because one invocation returned success with 0 tests before the
  mapped-path workaround.
- R and Octave namespace/package checks still need CI or a workstation with
  those toolchains.
- `nirs4all-lite` topology is consumer-readable, but several non-Python
  upstream namespace rows are still policy declarations rather than complete
  upstream re-export implementations.

## Decisions needed

- Confirm the aggregate rename path: keep publishing Python `nirs4all-lite`
  until `nirs4all-core` is approved, with `nirs4all` reserved for the full
  Python modelling library.
- Decide R methods public naming: keep `n4m` as the low-level package only, or
  add/rename a public `nirs4allmethods` facade.
- Decide npm public naming and timing for migration to `@nirs4all/*`.
- Decide whether Rust should add first-class upstream crate re-exports for
  formats/io/methods/datasets as those crates stabilize, or keep marker/dynamic
  surfaces in the aggregate.
- Decide whether MATLAB/Octave should add a `+nirs4all` methods facade over
  `+pls4all` before public release docs.

## Recommended integration steps

- Integrate the bounded `nirs4all_core` lint fix with the W94 topology slice.
- Keep `nirs4all-tools` as-is; W97/W104 goldens and CLI behavior are present
  and realistic after reset.
- Do not update release lock from this lane.
- In CI, run the lite npm gate on a native Node/npm environment, plus R and
  Octave gates where those toolchains are installed.
- Have central release tooling consume
  `nirs4all_lite.release_topology_manifest()` rather than re-deriving package
  topology from prose.
