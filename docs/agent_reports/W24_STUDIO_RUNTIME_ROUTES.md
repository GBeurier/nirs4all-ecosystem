# W24 report - Studio runtime routes

Summary:
Continued W24 after `455e1f3`. The broader slice now preserves the requested
ML engine through Studio execution-driver route metadata and durable execution
job snapshots, and exposes unavailable execution-backend refusals as the neutral
`RtError` envelope instead of collapsing them to plain strings.

Code changed:
- `ExecutionRequest` now carries `requested_engine` and includes it in
  `execution_request` metadata when a non-default engine is requested.
- `_start_run_job` passes `Run.engine` into the execution request, covering
  create, quick, retry, and native run-group submissions.
- Workspace execution job records now persist `request.requested_engine` when
  present.
- Shared store-run config now preserves `requested_engine` for runs launched
  with an explicit ML engine.
- Create-run, retry, and native run-group unavailable-backend responses now use
  `RtError` detail shape: `verb`, `cause`, `message`, and `mitigation`.
- Unavailable driver cancel refusals keep the same success/message behavior and
  now include `metadata.rt_error` for callers that understand the runtime
  envelope.

Files touched:
- `api/execution_driver.py`
- `api/runs.py`
- `tests/test_runs_execution_backend.py`

Commits:
- `455e1f3` `fix(runs): preserve requested engine on retry`
- `69f576a` `fix(runs): preserve runtime engine route metadata`

Tests run:
- `PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runs_execution_backend.py tests/test_runs_engine_routing.py tests/test_runtime_engine.py tests/test_operators_manifests.py -q`
  - `66 passed, 1 skipped, 6 warnings`
- `PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runtime_errors.py -q`
  - `12 passed`
- `PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m compileall -q api/execution_driver.py api/runs.py tests/test_runs_execution_backend.py`
  - passed
- `ruff check api/execution_driver.py api/runs.py tests/test_runs_execution_backend.py`
  - passed

Tests not run and why:
Full Studio backend/frontend suites were not run; W24 touched only backend route
runtime metadata/refusal wiring, so targeted backend route, runtime-engine,
operator-manifest, runtime-error, compile, and Ruff gates were run.

Blockers:
None for this W24 slice.

Impact on blockers/locks:
Advances `B-017`/`B-018`: Studio routes now retain requested ML-engine context
for future/local execution drivers and durable job records, preserve the prior
retry engine fix, and expose execution-backend refusals in the shared runtime
error shape.

Sync doc updated: no
