# W88 Cluster V1 DAG Report

Date: 2026-07-01

## Summary

Advanced the `nirs4all-cluster` V1 trusted-LAN scheduler slice on branch
`refactor/W88-cluster-v1-dag`. The server now resolves dead-worker tasks through
the same deterministic lost-task state path as lease expiry, instead of leaving
them in-flight after a worker is classified dead. Cancellation-window success
and failure reports are now accepted only from the assigned worker and emit
`task_cancelled`, not misleading completed/failed events. Added RBAC and
capability tests for DAG-shaped whole-run jobs.

## Changed Files

- `nirs4all_cluster/server/db.py`
- `nirs4all_cluster/server/app.py`
- `tests/test_scheduler.py`
- `tests/test_rbac.py`
- `tests/test_server_api.py`

## Commit

- `260c753` - `fix(cluster): make DAG worker loss deterministic`

## Tests Run

- `uv run --extra dev pytest tests/test_scheduler.py tests/test_rbac.py tests/test_server_api.py -q` -> 62 passed.
- `uv run --extra dev mypy nirs4all_cluster` -> passed.
- `uv run --extra dev ruff check .` -> passed after fixing an unused loop variable.
- `uv run --extra dev pytest -q` -> 133 passed, 1 skipped, 3 warnings.

## Failures

- `uv run pytest tests/test_scheduler.py tests/test_rbac.py tests/test_server_api.py -q` failed before validation because the fresh uv environment lacked project dependencies (`ModuleNotFoundError: No module named 'httpx'`). Reran with `--extra dev`.
- First `uv run --extra dev ruff check .` failed with `B007` for an unused loop variable in the new reaper finalization loop. Fixed and reran successfully.

## Blockers

None.
