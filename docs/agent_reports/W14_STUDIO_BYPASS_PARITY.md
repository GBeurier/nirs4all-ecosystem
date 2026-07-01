# W14 - Studio Bypass Parity

Status: salvaged and validated after Claude reached max-turns.

## Scope

W14 covered the Studio side of B-011: make the run route prove that a requested
runtime engine is threaded through Studio instead of being silently bypassed.

## Changes

- Added focused backend tests in `tests/test_runs_engine_routing.py`.
- Verified `POST /runs` -> `Run.engine` -> `_execute_run_job` ->
  `_execute_pipeline_training` -> `nirs4all.run(engine=...)`.
- Verified default requests omit the `engine` kwarg so the Python library default
  remains the source of truth.
- Verified transparent `dag-ml` -> `legacy` fallback diagnostics are recorded.
- Persisted `PipelineRun.engine_requested` before training starts so hard failures
  still record the engine the user requested.

## Verification

From `_worktrees/W14-studio-parity`:

```bash
ruff check api/runs.py tests/test_runs_engine_routing.py
/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest \
  -p no:cacheprovider -q -o addopts="" \
  tests/test_runs_engine_routing.py \
  tests/test_runtime_engine.py \
  tests/test_runs_execution_backend.py
```

Result: `59 passed, 6 warnings`. The warnings are expected fallback-warning test
fixtures.

## Commit

`83b0580 test(studio): prove requested engine run routing`
