# W85 Studio Runtime V1

## Summary

Finalized the Studio backend runtime/run routing contract around structured runtime envelopes. Studio now treats `RtResult` / `RtError` data as the source of truth for engine outcome, diagnostics, fallback/refusal policy, runtime manifest data, and native result references. Warning-string fallback classification remains only as a compatibility quarantine for older results without structured runtime data.

## Changed Files

- `api/runtime_engine.py`
- `api/runs.py`
- `api/execution_driver.py`
- `tests/test_runtime_engine.py`
- `tests/test_runs_engine_routing.py`
- `tests/test_execution_driver.py`
- `tests/test_runs_execution_backend.py`

## Commit

- `b7a90f9319414b6446da06f86b9b94a2183dc0c8` (`fix(runtime): persist structured Studio runtime outcomes`)

## Verification

- `rtk /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runtime_engine.py tests/test_runs_engine_routing.py tests/test_execution_driver.py tests/test_runs_execution_backend.py tests/test_runtime_errors.py tests/test_execution_job_records.py` — 95 passed.
- `rtk /home/delete/.local/bin/ruff check api/runtime_engine.py api/runs.py api/execution_driver.py tests/test_runtime_engine.py tests/test_runs_engine_routing.py tests/test_execution_driver.py tests/test_runs_execution_backend.py` — passed.

## Failures / Notes

- Initial system-Python pytest collection failed because the global interpreter lacked Studio backend dependencies (`pydantic`, `fastapi`). Re-ran successfully with the existing Studio venv at `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python`.
- The Studio venv did not have `ruff` installed as a Python module, so Ruff was run with the available `/home/delete/.local/bin/ruff` binary matching the repo `lint:ruff` command.

## Blockers

- None.
