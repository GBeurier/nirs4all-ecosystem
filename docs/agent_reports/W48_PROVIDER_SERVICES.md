# W48_PROVIDER_SERVICES

Date: 2026-07-01

Repo: `/home/delete/nirs4all/_worktrees/W48-providers-services`
Branch: `refactor/W48-provider-services`
Commit: `074d07dfc24349c5a11293857ab1bba14f1502d3` (`feat(providers): harden read lookup adapters`)

## Summary

Hardened the read-only provider adapter boundary for dataset and pipeline lookup flows.

- Added a shared lookup-id guard in `_BaseProvider` so adapter methods reject blank or non-string
  identifiers before touching optional backing packages.
- Applied the guard to dataset `card` / `get_dataset` / `retrieve_dataset`, repository `card` /
  `get_pipeline` / `get_bundle`, and benchmark `get_pipeline` / `get_results` / `residuals`.
- Added `DatasetProvider.retrieve_dataset()` as a transparent delegate to `nirs4all_datasets.retrieve`.
  It forwards root/cache/options to the backing package and remains local-cache scoped.
- Updated README and conformance tests to document the identifier contract: repository
  `get_pipeline()` takes repository pipeline ids, while benchmark `get_pipeline()` takes
  `pipeline_dag_hash` values.

No upload, publish, benchmark runner, ecosystem write-back, or dataset assembly logic was added.

## Files Changed

- `README.md`
- `src/nirs4all_providers/_adapter.py`
- `src/nirs4all_providers/datasets.py`
- `src/nirs4all_providers/repository.py`
- `src/nirs4all_providers/benchmarks.py`
- `tests/test_datasets_provider.py`
- `tests/test_repository_provider.py`
- `tests/test_benchmarks_provider.py`
- `tests/test_conformance.py`

This report is written in `nirs4all-ecosystem` as requested and is outside the provider branch commit.

## Tests Run

From `/home/delete/nirs4all/_worktrees/W48-providers-services`:

- `ruff check src/nirs4all_providers tests` -> passed.
- `UV_CACHE_DIR=/tmp/nirs4all-w48-uv-cache PYTHONPATH=src uv run --no-project --python 3.11 --with pytest python -m pytest -q tests/test_datasets_provider.py tests/test_repository_provider.py tests/test_benchmarks_provider.py tests/test_conformance.py` -> 36 passed, 4 skipped.
- `UV_CACHE_DIR=/tmp/nirs4all-w48-uv-cache PYTHONPATH=src uv run --no-project --python 3.11 --with mypy mypy src/nirs4all_providers` -> passed.
- `UV_CACHE_DIR=/tmp/nirs4all-w48-uv-cache PYTHONPATH=src uv run --no-project --python 3.11 --with pytest python -m pytest -q` -> 56 passed, 4 skipped.

Note: `/bin/python` is not installed in this environment, so tests/type checks were run through `uv`
with Python 3.11.

## Blockers

None.
