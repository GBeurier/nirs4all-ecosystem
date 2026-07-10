# W105 — Python/Studio transition legacy backend

Date: 2026-07-10

## Scope

Transition-release hardening for the two held production projects:

- `nirs4all` Python library: keep both `legacy` and `dag-ml` backends selectable, detect old workspace/save formats, warn with a concrete conversion command, and prevent accidental blank-store creation in old filesystem workspaces.
- `nirs4all-studio`: expose the same transition diagnosis in the workspace UI/API and provide a conversion action backed by `nirs4all-tools`.
- `nirs4all-studio`: expose runtime backend selection in both pipeline execution and new experiment review flows, with explicit `legacy` / `dag-ml` / library-default selection and a guarded fallback-to-legacy option.

## Decisions

- `nirs4all-tools` remains the canonical legacy reader/converter. The runtime does not duplicate full legacy readers.
- `nirs4all` gets an optional `transition` extra (`nirs4all-tools>=0.0.5`) and a CLI wrapper: `nirs4all workspace convert <input> --output <dir> --verify`.
- Existing DuckDB/SQLite legacy-array compatibility is preserved, but now emits a transition warning.
- Legacy filesystem `runs/*/*/manifest.yaml` workspaces are refused in-place by `WorkspaceStore` with a conversion command, because opening them as a new SQLite workspace would risk hiding old data behind a blank store.
- Studio conversion runs through a maintenance job and calls `python -m nirs4all_tools legacy migrate ... --target nirs4all-workspace-v2`.
- Studio's direct pipeline execute endpoint now threads the selected ML engine through the same `runtime_engine` helper used by `/runs`, and records the resulting runtime envelope in the job result.

## Files Modified

`nirs4all`:

- `nirs4all/workspace/compat.py`
- `nirs4all/pipeline/storage/workspace_store.py`
- `nirs4all/cli/commands/workspace.py`
- `pyproject.toml`
- `tests/unit/workspace/test_workspace_compat.py`
- `tests/unit/cli/test_main.py`

`nirs4all-studio`:

- `api/workspace/models.py`
- `api/workspace/services.py`
- `api/workspace/router_maintenance.py`
- `src/api/workspace.ts`
- `src/types/storage.ts`
- `src/components/settings/WorkspaceStats.tsx`
- `src/components/settings/WorkspaceStatsData.ts`
- `src/components/runtime/RuntimeBackendSelector.tsx`
- `src/components/runtime/index.ts`
- `src/components/pipeline-editor/PipelineExecutionDialog.tsx`
- `src/components/experiments/NewExperimentReviewStep.tsx`
- `src/components/experiments/NewExperimentStepContent.tsx`
- `src/components/experiments/NewExperimentStepContentPanels.tsx`
- `src/lib/pipelineExecutionContract.ts`
- `src/lib/__tests__/pipelineExecutionContract.test.ts`
- `src/pages/NewExperiment.tsx`
- `api/pipelines.py`
- `requirements.txt`
- `requirements-cpu.txt`
- `tests/test_workspace_transition.py`
- `tests/test_pipeline_execute_runtime_request.py`

## Tests Run

`nirs4all`:

- `.venv/bin/python -m ruff check nirs4all/workspace/compat.py nirs4all/cli/commands/workspace.py nirs4all/pipeline/storage/workspace_store.py tests/unit/workspace/test_workspace_compat.py tests/unit/cli/test_main.py`
- `.venv/bin/python -m pytest tests/unit/workspace/test_workspace_compat.py tests/unit/cli/test_main.py tests/unit/pipeline/test_engine_selector.py`
- Result: 39 passed.

`nirs4all-studio`:

- `ruff check api/workspace/models.py api/workspace/services.py api/workspace/router_maintenance.py tests/test_workspace_transition.py`
- `.venv/bin/python -m pytest tests/test_workspace_transition.py tests/test_runtime_engine.py tests/test_runs_engine_routing.py`
- Result: 37 passed, 7 expected warning-capture warnings from engine fallback tests.
- `python3 -m ruff check api/pipelines.py tests/test_runtime_engine.py tests/test_runs_engine_routing.py tests/test_workspace_transition.py tests/test_pipeline_execute_runtime_request.py`
- `.venv/bin/python -m pytest tests/test_runtime_engine.py tests/test_runs_engine_routing.py tests/test_workspace_transition.py tests/test_pipeline_execute_runtime_request.py`
- `source ~/.nvm/nvm.sh && nvm use 24 && npm run lint:tsc`
- `source ~/.nvm/nvm.sh && nvm use 24 && npx vitest run src/lib/__tests__/pipelineExecutionContract.test.ts src/lib/__tests__/experimentLaunchConfig.test.ts src/lib/__tests__/experimentLaunchPayload.test.ts`
- `source ~/.nvm/nvm.sh && nvm use 24 && npx vitest run src/components/experiments/NewExperimentReviewStep.test.tsx src/components/experiments/NewExperimentStepContent.test.tsx`
- Result: backend 39 passed, 7 expected warning-capture warnings; frontend tsc passed; frontend Vitest 26 passed.

## Risks / Follow-up

- Node 24 must be loaded through nvm in this WSL shell; otherwise `npm` resolves to the Windows shim and fails before TypeScript starts.
- Full parity is intentionally deferred until a larger batch, per project instruction.
- Studio UI conversion action is wired locally in Studio, not in shared `nirs4all-ui`, to avoid interfering with the concurrent quality work.
