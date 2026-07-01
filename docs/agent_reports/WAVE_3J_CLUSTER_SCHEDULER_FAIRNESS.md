# Wave 3J - Cluster Scheduler Fairness

Date: 2026-07-01

## Scope

Lane I follow-up from W3I audit. No core/runtime parity run.

Goal: improve cluster worker-pull fairness for same-priority DAG/matrix jobs
without changing the wire contract, RBAC vocabulary, runner boundary, or
`nirs4all` import boundary.

## Commit

Repository: `nirs4all-cluster`

- `4605f9b fix(scheduler): balance same-priority leases`

Files changed:

- `nirs4all_cluster/server/db.py`
- `tests/test_scheduler.py`

## Behavior

- `lease_next_task` now orders queued candidates by:
  `priority DESC`, `job_in_flight ASC`, `created_at ASC`, `id ASC`.
- `job_in_flight` counts currently leased/running tasks for that task's job.
- Priority remains strict: fairness only applies within the same priority.
- The extra SQL column is used only during candidate ordering; `_set_task_status`
  still reloads the task row with `SELECT *` before returning the payload.

## Review

- Nash reviewed the diff read-only.
- Initial note: the high-priority test needed a real competing second
  high-priority task.
- The test was strengthened so a high-priority matrix job with one in-flight
  task still leases its second task before a lower-priority job with zero
  in-flight tasks.
- Final decision: go.

## Tests

From `nirs4all-cluster` using `.venv/bin/python`:

- `.venv/bin/python -m pytest -q tests/test_scheduler.py tests/test_rbac.py`
  - PASS: 36 passed.
- `.venv/bin/python -m pytest -q`
  - PASS: 135 passed, 1 skipped.
- `.venv/bin/python -m ruff check .`
  - PASS.
- `.venv/bin/python -m mypy nirs4all_cluster`
  - PASS.
- `git diff --check`
  - PASS.

## Risks

- This is queue fairness, not a full DAG node-level scheduler. Fold/DAG-native
  scheduling remains gated by core/dag-ml runtime contracts.
- Trusted-LAN artifact read semantics are unchanged.
