# W93 IO/Datasets Reference Bridge

## Scope

- IO worktree: `_worktrees/W93-io-datasets-bridge`
  - Branch: `refactor/W93-datasets-bridge`
  - Commit: `ac7809d feat(io): accept reference dataset specs`
- Datasets worktree: `_worktrees/W93-datasets-reference-bridge`
  - Branch: `refactor/W93-reference-bridge`
  - Commit: `20b41824 feat(datasets): bridge reference datasets to io`
- Formats worktree: `_worktrees/W93-formats-io-contract`
  - Branch: `refactor/W93-io-contract`
  - No code change needed.

## Result

Implemented the local reference-dataset path:

1. `nirs4all-datasets.NirsDataset.to_io_spec()` now emits a normal `nirs4all-io` `DatasetSpec` over the verified local canonical Parquet layout.
2. `NirsDataset.to_dataset_package()` delegates package materialization back to `nirs4all_io.to_dataset_package()`.
3. `nirs4all_io.load()` / `to_spec()` now accepts any object exposing `to_io_spec()` without importing `nirs4all-datasets`, so the dependency boundary stays one-way and duck-typed.

Native split labels are exposed as metadata, not applied as train/test partitions. Multi-source datasets are bridged only when sources are uniquely alignable by observation/sample identity; asymmetric repeated sources fail clearly and can be bridged one source at a time.

## Boundaries

- Datasets owns catalog access, canonical path discovery, source/variable role projection, and public docs.
- IO owns loading, joins, target-agnostic `DatasetPackage` assembly, and downstream package summaries.
- Formats remains the parser layer behind IO's optional vendor loader. No parser logic was added to datasets or IO.
- Provider/repository/benchmark write paths were not touched.

## Verification

IO:

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/W93-io-datasets-bridge/src \
  /home/delete/nirs4all/nirs4all-io/.venv/bin/python -m pytest tests/test_dataset_package.py
ruff check src/nirs4all_io/api.py tests/test_dataset_package.py
ruff format --check src/nirs4all_io/api.py tests/test_dataset_package.py
git diff --check
```

Datasets:

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/W93-io-datasets-bridge/src:/home/delete/nirs4all/_worktrees/W93-datasets-reference-bridge/src \
  /home/delete/nirs4all/nirs4all-datasets/.venv/bin/python -m pytest tests/test_dataset.py
ruff check src/nirs4all_datasets/dataset.py tests/test_dataset.py
ruff format --check src/nirs4all_datasets/dataset.py tests/test_dataset.py
git diff --check
```

Formats:

```bash
. "$HOME/.cargo/env" && cargo test -p nirs4all-formats-core --lib
git diff --check
```

All commands passed.
