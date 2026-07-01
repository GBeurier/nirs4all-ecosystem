# Wave 3AG - Cluster RBAC Boundary Tests

Date: 2026-07-01
Lane: I - cluster client/server scheduler and rights
Scope: `nirs4all-cluster` test-only patch

## Decision

GO for integrating the RBAC boundary tests.

The server implementation already enforced credential-bound rights correctly;
this wave adds missing proof around artifact upload/download and job-scoped
WebSocket streaming. No scheduler behavior, server route implementation, wire
schema, or `nirs4all` runtime path was changed.

## Commit

- `nirs4all-cluster` `fa9f8f2` - `test(cluster): cover rbac artifact and websocket boundaries`

## Agents

- Poincare the 2nd: implemented the test-only patch in `tests/test_rbac.py`.
- Schrodinger the 2nd: reviewed the diff. Initial verdict was NO-GO because
  the first version did not test a valid token lacking `read`, and the
  job-specific WebSocket live event had a possible subscriber race. After fixes,
  final verdict was GO.
- Heisenberg the 2nd: audited the next Lane D `nirs4all-tools` tranche in
  parallel. Recommended a later, bounded `runs/manifest.yaml` to loose
  predictions lowering; no tools files were changed in W3AG.

## Files Modified

`nirs4all-cluster`:

- `tests/test_rbac.py`
  - Adds a `SUBMIT_ONLY` principal with `submit` but no `read`.
  - Proves `/v1/artifacts` input upload requires `submit`: viewer/executor are
    rejected; submit-only, submitter, and admin are accepted.
  - Proves `/v1/artifacts/{id}` download requires `read`: viewer/executor/
    submitter can read; submit-only gets 403; missing/unknown tokens get 401.
  - Proves `/v1/jobs/{job_id}/events/stream` requires `read`, not just an
    authenticated token.
  - Reworks WebSocket receives through a bounded polling helper and waits for
    the TestClient broker subscriber before emitting live events, avoiding the
    prior race.

`nirs4all-ecosystem`:

- `docs/agent_reports/WAVE_3AG_CLUSTER_RBAC_BOUNDARY_TESTS.md`

## Tests Run

`nirs4all-cluster`:

- `PATH=/home/delete/nirs4all/nirs4all-cluster/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 pytest tests/test_rbac.py -q -p no:cacheprovider`
  - Result: 23 passed, 1 existing Starlette/httpx deprecation warning.
- `for i in 1 2 3 4 5; do PATH=/home/delete/nirs4all/nirs4all-cluster/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 pytest tests/test_rbac.py::test_job_specific_ws_stream_requires_read -q -p no:cacheprovider || exit $?; done`
  - Result: 5/5 passed, same existing warning.
- `PATH=/home/delete/nirs4all/nirs4all-cluster/.venv/bin:$PATH ruff check tests/test_rbac.py`
  - Result: passed.
- `PATH=/home/delete/nirs4all/nirs4all-cluster/.venv/bin:$PATH python -m py_compile tests/test_rbac.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.

The system `pytest` outside the repo venv was not usable for this repo because
`httpx` is not installed there; the venv command above is the valid local gate.

## Review Notes

The final review noted one non-blocking maintenance risk: the WebSocket helper
uses TestClient/EventBroker internals (`_send_rx`, `_raise_on_close`,
`_global`, `_subscribers`) to keep synchronous tests bounded and deterministic.
This is acceptable for the current Starlette/AnyIO test stack, but should be
watched during dependency upgrades.

## Risks And Follow-Ups

- No full Python-reference parity was run; this was a cluster API/RBAC proof
  only.
- The wider cluster release/e2e and fine-grained DAG scheduler gates remain
  separate work.
- The old roadmap note that cluster only had a single static token is stale for
  the current local `main`; RBAC is implemented, and this wave adds boundary
  regression coverage around it.
