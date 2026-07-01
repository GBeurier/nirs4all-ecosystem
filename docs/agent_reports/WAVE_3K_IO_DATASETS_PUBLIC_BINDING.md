# Wave 3K - IO/Datasets Public Binding Bridge

Date: 2026-07-01

## Scope

Lane G tranche focused on the public bridge between `nirs4all-datasets` reference objects and `nirs4all-io`, without running full parity suites.

## Commits

- `_worktrees/INT-io` `569ed68` - `feat(bindings): accept io spec adapters`
- `nirs4all-datasets` `44662562` - `fix(io): guard dataset package bridge`

## Files Modified

`_worktrees/INT-io`:

- `bindings/python/Cargo.lock`
- `bindings/python/python/nirs4all_io/__init__.py`
- `bindings/python/tests/test_idiomatic.py`

`nirs4all-datasets`:

- `src/nirs4all_datasets/dataset.py`
- `tests/test_dataset.py`

## Decisions

- The pyo3 `nirs4all_io` wrapper now accepts duck-typed objects exposing `to_io_spec()`, including `(spec, base_dir)` tuples.
- `(spec, base_dir)` adaptation absolutizes every filesystem ref consumed by the current native materializer: `source.input`, `source.variations[*].input`, `partitions.{train,test,predict}_file`, and `folds.file`.
- Canonical Parquet/DatasetPackage support remains a Python MVP `nirs4all-io` responsibility. The pyo3 binding now raises a clear Parquet error instead of letting binary Parquet bytes fall through to text loaders.
- `NirsDataset.to_dataset_package()` now fails explicitly when the installed `nirs4all_io` surface lacks `to_dataset_package`.
- DatasetPackage-positive tests now feature-detect the package-capable IO surface; they remain active with the MVP IO package and skip with the pyo3-only surface.

## Review

Reviewer: Socrates (`019f1ed7-9a22-7a01-81fe-63126a52a985`)

- Initial review: NO-GO.
  - DatasetPackage tests would fail with only the pyo3 binding installed.
  - `(spec, base_dir)` path adaptation covered only `source.input`.
- Follow-up review: GO.
  - Low finding: Parquet guard did not cover list inputs.
  - Fix applied before commit: list inputs containing `.parquet` now get the same actionable Parquet error, with test coverage.

## Tests Run

`_worktrees/INT-io`:

- `cd bindings/python && maturin develop && python -m pytest tests/test_idiomatic.py tests/test_smoke.py tests/test_parity.py -q` -> 16 passed.
- `PYTHONPATH=src pytest tests/test_dataset_package.py::test_reference_dataset_adapter_uses_to_io_spec -q` -> 1 passed.
- `ruff check bindings/python/python/nirs4all_io/__init__.py bindings/python/tests/test_idiomatic.py`
- `python3.11 -m py_compile bindings/python/python/nirs4all_io/__init__.py bindings/python/tests/test_idiomatic.py`
- `cargo check --locked`
- `git diff --check`

`nirs4all-datasets`:

- `PYTHONPATH=src pytest tests/test_dataset.py tests/test_access.py -q` -> 24 passed, 3 skipped.
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-io/src:/home/delete/nirs4all/nirs4all-datasets/src pytest tests/test_dataset.py::test_to_dataset_package_delegates_to_nirs4all_io tests/test_dataset.py::test_to_dataset_package_rejects_io_without_package_helper tests/test_dataset.py::test_nirs4all_io_load_accepts_real_reference_dataset -q` -> 3 passed.
- With pyo3 binding venv installed: `PYTHONPATH=/home/delete/nirs4all/nirs4all-datasets/src python -m pytest tests/test_dataset.py::test_to_dataset_package_delegates_to_nirs4all_io tests/test_dataset.py::test_to_dataset_package_rejects_io_without_package_helper tests/test_dataset.py::test_nirs4all_io_load_accepts_real_reference_dataset -q` -> 1 passed, 2 skipped.
- `PYTHONPATH=src ruff check src/nirs4all_datasets/dataset.py tests/test_dataset.py`
- `PYTHONPATH=src mypy --config-file pyproject.toml src/nirs4all_datasets/dataset.py`
- `git diff --check`

## Risks / Follow-Ups

- pyo3/native IO still does not read canonical Parquet; this is now explicit but remains a future native-format bridge decision.
- Full IO/datasets parity and release-lock validation were intentionally deferred to larger batch gates.
- `nirs4all-datasets` remains ahead of origin and behind one remote commit from the pre-existing state; no remote merge/push was performed.
