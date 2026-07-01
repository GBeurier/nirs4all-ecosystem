# W47 Cluster Real DAG Parity

Date: 2026-07-01
Worktree: `/home/delete/nirs4all/_worktrees/W47-cluster-real-dag`
Branch: `refactor/W47-real-dag-parity`
Commit: `e2a99c2`

## Summary

Strengthened `nirs4all-cluster` real-DAG parity coverage without changing scheduler policy. The new dependency-free parity path uses the existing live client/server/worker fixture, an inline `nirs4all.run` pipeline payload that carries a DAG-like `dagml.nodes` plan, two shared-path datasets, worker materialization, subprocess execution, task completion, server finalization, aggregate ranking, and best-model selection.

## Changes

- Added `test_inline_dag_matrix_preserves_local_result_semantics` in `tests/test_distributed_parity.py`.
- Extended the fake subprocess-only `nirs4all` test module to evaluate a deterministic DAG trace from pipeline nodes and dataset manifests, producing dataset-sensitive metrics and `extra.dag_trace`.
- Verified inline pipeline content fingerprints are preserved from submitter to worker materialization via `fingerprint_obj`.
- Verified distributed task outputs match local executor outputs per dataset, including metrics, counts, DAG trace metadata, uploaded artifacts, server aggregate ranking, `best_task_id`, and `best_model_artifact_id`.
- Updated `nirs4all_cluster/runners/nirs4all_run.py` to preserve JSON-safe `result.extra` metadata in `TaskResult.extra`, while keeping the fixed `best_model`, `task_type`, and `metric` summary fields.

## Tests

- `uv pip install -e ".[dev]"`
- `uv run pytest tests/test_distributed_parity.py -q` -> `2 passed`
- `uv run ruff check .` -> passed
- `uv run ruff format --check nirs4all_cluster/runners/nirs4all_run.py tests/test_distributed_parity.py` -> passed
- `uv run mypy nirs4all_cluster` -> passed
- `uv run pytest -q` -> `126 passed, 1 skipped`

## Blockers

None. The suite reports existing dependency deprecation warnings from Starlette/httpx and websockets/uvicorn, but no W47 blocker.
