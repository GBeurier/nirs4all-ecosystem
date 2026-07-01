# W95 Studio Strict Runtime Fallback Default

## Status

Completed the Studio strict fallback-default slice.

## Scope

- Worktree: `/home/delete/nirs4all/_worktrees/W95-studio-strict-runtime`
- Branch: `refactor/W95-studio-strict-runtime`
- Commit: `88fbd99` (`fix(runtime): require explicit fallback opt-in`)

## Changed Files

- `api/runs.py`
  - Changed `Run`, `ExperimentConfig`, `QuickRunRequest`, and `_execute_pipeline_training()` fallback defaults to `False`.
  - Updated request descriptions so fallback is described as an explicit opt-in.
  - Preserved structured `RtError` diagnostics, runtime envelopes, and `fallback_policy` records.
- `api/execution_driver.py`
  - Changed internal `ExecutionRequest.allow_fallback` default to `False` so job metadata cannot silently opt in.
- `tests/test_runs_engine_routing.py`
  - Added coverage for ExperimentConfig and QuickRunRequest default refusal.
  - Added explicit `allow_fallback=True` opt-in coverage.
  - Added structured RtError refusal coverage for the default path.
  - Asserted route-created QuickRun/runtime records persist `refuse_fallback`.
- `tests/test_runs_execution_backend.py`
  - Updated job metadata and store-run `fallback_policy` expectations to strict defaults.
  - Made legacy store lifecycle tests explicitly request `engine="legacy"` after the core default moved to `dag-ml`.
- `tests/test_execution_driver.py`
  - Updated execution-driver serialized request metadata expectations to `refuse_fallback`.

No frontend files were changed. Current frontend launch payloads omit `allow_fallback`, so they now use the backend strict default; explicit API clients can still opt in by sending `allow_fallback: true`.

## Verification

- `rtk .venv/bin/python -m pytest tests/test_runs_engine_routing.py tests/test_runs_execution_backend.py tests/test_execution_driver.py -q`
  - Passed: 67 tests.
- `rtk .venv/bin/ruff check api/runs.py api/execution_driver.py tests/test_runs_engine_routing.py tests/test_runs_execution_backend.py tests/test_execution_driver.py`
  - Passed.
- `rtk git diff --check`
  - Passed before commit.

## Failures / Setup Notes

- Initial system-python pytest collection failed because `fastapi` was not installed. Resolved by creating a local Python 3.11 venv and installing `requirements-cpu.txt`, `pytest`, and `ruff`.
- Editable `nirs4all` install with dependencies failed because `dag-ml` is local and not available from the configured registry. Resolved for Studio tests by installing the clean `_worktrees/INT-nirs4all` package editable with `--no-deps` plus the non-`dag-ml` import dependencies needed by the existing monkeypatched tests.
- A stale test expected `engine=None` to resolve to `legacy`; updated it to the current integration default, `dag-ml`.
- Legacy store lifecycle tests were relying on `engine=None` behaving like legacy; updated those tests to request `engine="legacy"` explicitly.

## Blockers

None.

## Follow-Up

Coordinator integration is needed to merge `refactor/W95-studio-strict-runtime` into the Studio integration branch. No additional W95 backend follow-up is required.
