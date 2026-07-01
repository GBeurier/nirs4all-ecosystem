# W57 report - Providers real-service read adapter bridge

Summary:
Implemented a narrow real backing bridge for `BenchmarkProvider.get_pipeline()`: by-hash lookup now uses the local Arena store read API (`store.query_one`) when available, preserving a list-scan fallback for older/faked `Queries` shapes. No run, ingest, upload, or ecosystem write-back path was added.

Code changed:
- Added a SQL-backed benchmark pipeline lookup for `pipeline_dag_hash` against the local Arena `pipeline_dags` table, returning the same projected row shape as `Queries.pipelines()`.
- Kept the existing fallback over `Queries.pipelines()` for hermetic fakes and older backing versions.
- Added hermetic tests that make `pipelines()` fail if the direct store lookup is bypassed.
- Added real-API conformance coverage for `ArenaStore.query_one`.
- Documented the benchmark by-hash lookup behavior in the provider README.

Files touched:
- `README.md`
- `src/nirs4all_providers/benchmarks.py`
- `tests/test_benchmarks_provider.py`
- `tests/test_conformance.py`

Commits:
- `441d3b7eaf850bacea300857d3be5bbb7da1659c` (`feat(benchmarks): bridge provider get by hash`)

Tests run:
- `PYTHONPATH=src pytest -q` (58 passed, 3 skipped)
- `ruff check .`
- `/home/delete/miniconda3/bin/python -m mypy src`
- `git diff --check`

Tests not run and why:
- None for the provider scope. Plain `pytest -q` failed before collection because this worktree was not installed in the active environment; it was rerun successfully with `PYTHONPATH=src`. The `mypy` executable was not on `PATH`, so mypy was run through the Miniconda Python module entrypoint.

Blockers:
- None.

Impact on blockers/locks:
- Advances DEC-PROV-001 by bridging the benchmarks provider to a real local Arena read API for get-by-hash without adding benchmark execution or ecosystem write-back.

Next action:
- Consider upstreaming a first-class `Queries.pipeline(dag_hash)` method in `nirs4all-benchmarks` later to remove the provider-side SQL projection, if the query facade becomes the only supported read boundary.

Sync doc updated: no
