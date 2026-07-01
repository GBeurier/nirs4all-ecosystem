# W79 Cluster Scheduler DAG Report

Date: 2026-07-01

## Status

Implemented and verified a bounded RBAC/client-server scheduler improvement in
`nirs4all-cluster`.

## Change

- Bound each registered worker row to the authenticated principal that registered it.
- Added an additive SQLite migration for older `workers` tables missing the `principal` column.
- Enforced worker-principal ownership on heartbeat, lease, start, task events, artifact upload,
  completion, and failure routes.
- Added an end-to-end RBAC regression with two executor principals proving one valid executor
  cannot spoof another registered worker or report on its selected task.

## Validation

- `uv run pytest tests/test_rbac.py tests/test_scheduler.py -q`
- `uv run ruff check .`
- `uv run mypy nirs4all_cluster`
- `uv run pytest -q`

Full suite result: 128 passed, 1 skipped.

## Notes

- Scope stayed inside `/home/delete/nirs4all/_worktrees/W79-cluster-scheduler-dag` except for this
  required report file.
- `nirs4all-ecosystem` was not committed.
