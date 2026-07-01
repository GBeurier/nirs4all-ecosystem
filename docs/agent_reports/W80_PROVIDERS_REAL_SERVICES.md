# W80 Providers Real Services

## Status

Implemented a bounded provider-side service contract improvement in `nirs4all-providers`.

## Scope

Worktree: `/home/delete/nirs4all/_worktrees/W80-providers-real-services`

Only the providers worktree was edited for code/docs/tests. Repository, benchmarks, datasets, and papers repos were not edited. This report is written in `nirs4all-ecosystem` as required and must remain uncommitted there.

## Change

- Added `BenchmarkProvider.queue_pipeline_test(...)`, a thin local adapter over `nirs4all_benchmarks.ingestion.upload`.
- The new method opens the local Arena store, forwards the payload and target dataset tokens to the backing service, returns the backing `UploadResult.to_json()` shape, and closes the store.
- Added validation for non-empty target dataset tokens before opening the backing store.
- Added `WriteAccess.LOCAL_STORE` and updated benchmark capabilities to reflect local `planned_runs` writes, while keeping `executes=False`.
- Updated README service-surface documentation to clarify that benchmark planning writes only to the local Arena store and never executes pipelines or writes back to repository/datasets/papers.
- Added hermetic fake-backed tests for delegation, local store closing, validation, and real-API conformance for the `upload` signature.
- Modernized `WriteAccess` to `StrEnum` because the package targets Python 3.11+ and the current ruff gate flags `str, Enum`.

## Design Notes

- Drafts/lab remain out of scope.
- Repository provider remains read-only.
- Benchmark provider now supports local queue/test planning via the Arena upload state machine, but remains write-disconnected from the ecosystem and does not run compute.
- Papers provider was not changed; it remains the local-output reproducible export surface.

## Gates

- `PYTHONPATH=src python3.11 -m pytest -q` -> passed (`59 passed, 4 skipped`)
- `python3.11 -m ruff check .` -> passed
- `PYTHONPATH=src python3.11 -m mypy src` -> passed

## Notes

- `python3` points to Python 3.10 in this environment; gates were run with `python3.11` to match the package's `requires-python >=3.11`.
- `python3.11 -m pip install -e '.[dev]'` was not used because the current setuptools build backend in this environment lacks editable-install support; dev tools were installed directly and tests were run with `PYTHONPATH=src`.

## Commit

`bc4736e` (`feat(providers): add benchmark local planning adapter`)
