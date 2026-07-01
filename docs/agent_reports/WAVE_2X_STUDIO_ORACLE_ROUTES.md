# Wave 2X Studio Oracle Routes

Date: 2026-07-01T17:45:00+02:00

## Scope

Follow-up after W2W. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2X targets the remaining Studio-oracle gap identified by Volta:

- Migrate the legacy Studio routes that still call `nirs4all.run()` without
  engine selection or runtime recording:
  - `_worktrees/INT-studio/api/training.py`
  - `_worktrees/INT-studio/api/automl.py`
  - `_worktrees/INT-studio/api/pipelines.py`
- Keep `api/runs.py` unchanged unless tests reveal a direct integration need.
- Do not run `pyref_oracle_full`.

## Starting State

- `nirs4all-ecosystem`: `569cbb6`
- `_worktrees/INT-studio`: `17dfe69`
- `_worktrees/INT-nirs4all`: `122ef5d1`
- W2W passed the installed-`n4m` proof and release surface checks.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| H/Runtime | coordinator | `_worktrees/INT-studio/api/runtime_engine.py`, integration edits as needed | Add or reuse a shared strict/fallback run helper and integrate route changes. |
| H/TrainingAutoML | Einstein | read-only: `training.py`, `automl.py`, related tests | Completed audit. Confirmed route migration shape, requested `fallback_policy` in job config, response runtime fields, and AutoML metrics update even when no prediction loop runs. |
| H/Pipelines | Noether | read-only: `pipelines.py`, frontend contract | Completed audit. Confirmed backend route migration shape, identified missing frontend serialization for `engine`/`allow_fallback`, and asked for failure-path runtime policy reporting. |
| K | Bohr | read-only W2X diffs after implementation | Completed first review with four findings; fixes applied; re-review approved W2X integration. |

## Planned Gates

- Focused Python unit tests for new Studio route/helper coverage.
- Ruff on touched backend files.
- Frontend contract test for legacy pipeline execute payload.

`pyref_oracle_full` is intentionally deferred.

## Integration Notes

- Added shared `run_with_engine_record()` in Studio runtime engine routing.
- Training, AutoML, and Pipeline legacy route workers now:
  - thread `engine` and `allow_fallback`,
  - run `dag-ml` strictly with `allow_fallback=False` and `results_path`,
  - preserve legacy/default `workspace_path` behavior per route:
    Training/AutoML keep sending `workspace_path`; Pipelines intentionally do
    not send it on legacy/default because they did not before W2X,
  - record `fallback_policy` and runtime metadata in results/metrics.
- Pipeline frontend contract now serializes `engine`/`allow_fallback` only when explicitly set, preserving previous payloads by default.
- `AnalysisExecutionRequest` metadata records runtime fallback policy only for
  run-backed or explicitly engine-selected analyses; AutoML opts in, SHAP/default
  analyses stay unpolluted.

## Review Resolution

Bohr first review findings:

- High: pipeline legacy/default path gained `workspace_path`.
  - Fixed with `pass_workspace_path_to_legacy=False` in `api/pipelines.py`.
  - Added tests for `engine=None` and `engine="legacy"` pipeline calls.
- Medium: allowed fallback could drop the original strict `dag-ml` refusal when
  fallback `RtResult` carried its own diagnostics.
  - Fixed by merging explicit diagnostics with `RtResult` diagnostics.
  - Added a regression test for both diagnostics.
- Medium: Training metrics endpoint wrote runtime fields but did not expose them
  in `TrainingMetricsResponse`.
  - Fixed model/endpoint response and added route coverage.
- Low: analysis fallback policy leaked into non-run analyses such as SHAP.
  - Fixed by requiring `include_fallback_policy` unless an engine policy is explicit.
  - AutoML opts in; SHAP/direct metadata test asserts no fallback policy by default.

Bohr re-review verdict: approved for W2X integration. Residual non-blocking
suggestion: add a future route-level test for pipeline `engine="dag-ml"` with
`allow_fallback=True` where dag-ml refuses and legacy fallback preserves both
diagnostics and no `workspace_path`.

## Gates Run

- PASS: `python3.11 -m py_compile api/runtime_engine.py api/training.py api/automl.py api/pipelines.py api/execution_driver.py tests/test_runtime_engine.py tests/test_studio_oracle_routes.py tests/test_automl_durable_results.py tests/test_analysis_execution_metadata.py`
- PASS: `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runtime_engine.py tests/test_studio_oracle_routes.py tests/test_automl_durable_results.py tests/test_analysis_execution_metadata.py tests/test_execution_driver.py -q --tb=short`
  - 44 passed, 5 existing warning-capture warnings.
- PASS: `/home/delete/nirs4all/_worktrees/W95-studio-strict-runtime/.venv/bin/python -m ruff check api/runtime_engine.py api/training.py api/automl.py api/pipelines.py api/execution_driver.py tests/test_runtime_engine.py tests/test_studio_oracle_routes.py tests/test_automl_durable_results.py tests/test_analysis_execution_metadata.py tests/test_execution_driver.py`
- PASS: `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npx vitest run src/lib/__tests__/pipelineExecutionContract.test.ts`
  - 7 passed.

## Deferred Gates

- `pyref_oracle_full` deferred by instruction because it is long and should run only after larger integrated batches.
