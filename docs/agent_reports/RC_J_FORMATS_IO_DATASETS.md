# RC-J — Formats / IO / Datasets Reference Bridge

Date: 2026-07-02

Lane: RC-J (formats/io/datasets worker).
Worktrees:

- `/home/delete/nirs4all/_worktrees/RC-v1-io`
- `/home/delete/nirs4all/_worktrees/RC-v1-datasets`
- `/home/delete/nirs4all/_worktrees/RC-v1-formats`

## Summary

Advanced the IO/datasets reference bridge by fixing a multi-source assembly edge
case that could silently drop a secondary feature source when row-aligned sources
shared wavelength column names. The fix is mirrored in the Python MVP and Rust
core assembly paths.

The bridge now recognizes both duplicate-column namespace forms:

- keyed joins: `wavelength__source`
- row-order feature concatenation: `source__wavelength`

Because multi-source payloads remain separate blocks, feature headers are
restored to each source's native labels instead of leaking join suffix/prefix
names into `DatasetPackage` / `AssembledDataset` headers.

No `nirs4all-formats` code was changed. The relevant formats alignment remains
through IO's existing decoded-record and vendor-reader contracts; no reader or
benchmark path writes ecosystem artifacts.

## Changed Files

IO:

- `crates/nirs4all-io-core/src/materialize/assemble.rs`
- `crates/nirs4all-io-core/tests/assemble_in_memory.rs`
- `src/nirs4all_io/materialize/assemble.py`
- `tests/test_dataset_package.py`

Datasets:

- `tests/test_access.py`

Report:

- `docs/agent_reports/RC_J_FORMATS_IO_DATASETS.md`

Formats:

- No changes.

## Tests / Checks

IO:

- `PYTHONPATH=src pytest -q tests/test_dataset_package.py tests/test_load_e2e.py` → **17 passed, 1 warning**.
- `cargo test -p nirs4all-io-core` → **all tests passed** (`101` unit tests plus integration/doc tests).
- `cargo clippy -p nirs4all-io-core --all-targets -- -D warnings` → **passed**.
- `cargo fmt --all --check` → **passed**.
- `ruff check src/nirs4all_io/materialize/assemble.py tests/test_dataset_package.py` → **passed**.

Datasets:

- `PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-io/src pytest -q tests/test_access.py tests/test_dataset.py` → **27 passed, 1 skipped, 1 warning**.
- `ruff check tests/test_access.py` → **passed**.

Targeted probes before broader checks:

- `cargo test -p nirs4all-io-core row_aligned_multisource_duplicate_headers_remain_separate_blocks -- --nocapture` → **passed**.
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-io/src pytest -q tests/test_access.py::test_get_local_reference_dataset_loads_through_io_package_bridge` → **passed**.

## Decisions

- Fixed the IO assembly bug in both Python and Rust mirrors, preserving the repo's byte-parity discipline.
- Added bounded contract tests rather than broad refactors:
  - IO public API test for row-aligned multi-source reference objects with duplicate wavelength headers.
  - Rust core in-memory assembly test for the same contract.
  - Datasets `get()` policy/bridge test proving a local reference dataset can pass directly into `nirs4all_io.load(..., target="dataset_package")`.
- Made `tests/test_access.py` use a fake `_acquire` module for access-policy tests, so the source-tree test path no longer imports the compiled `_n4ds` extension just to monkeypatch remote fetches. `_acquire` itself remains covered by its dedicated tests.

## Risks / Remaining Gaps

- Full IO workspace gate (`cargo test --workspace`, no-default-features build, binding builds) was not run; only the touched core crate and Python MVP bridge tests were run.
- The native pyo3 binding was not rebuilt with `maturin develop`; the Rust core fix is in the crate it links, and existing binding tests already cover reference-object adapters, but a binding smoke should be run by the integration coordinator if this lane is bundled with binding release artifacts.
- Formats full conformance was not run because no formats code changed. Any final RC should still run the normal `nirs4all-formats` workspace gate and conformance cadence.

## Follow-up Full Parity

No Python reference parity rerun is triggered by this lane. The changed behavior is confined to IO dataset assembly/package headers and multi-source source retention. The final RC gate should still include the broader IO/datasets reference bridge suite and language binding smoke tests.
