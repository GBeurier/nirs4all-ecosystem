# Wave 3A - Studio Predict Oracle Routes

Date: 2026-07-01

## Scope

Studio prediction endpoints that still call `nirs4all.predict` directly:

- `api/predictions.py` (`/predictions/batch`, `/predictions/dataset`)
- `api/models.py` (`/models/compare`)

No full parity run in this batch. Per user instruction, full parity gates are deferred until larger integrated batches.

## Roadmap Coverage Note

The release/topology roadmap must keep all `nirs4all` aggregate surfaces in scope:

- `nirs4all.python.oracle`
- `nirs4all.r.aggregate`
- `nirs4all.browser_wasm.aggregate`

Wave 2Y already validated those surfaces in the selected-root release matrix. W3A does not alter release topology.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Erdos | `api/predictions.py` and prediction route tests | done | Read-only. Recommended a strict `prediction_runtime` adapter: default/legacy uses Python oracle, explicit `dag-ml` refuses unless fallback is requested. |
| Kant | `api/models.py::compare_models` and tests | done | Read-only. Recommended not forwarding `engine` to `nirs4all.predict`; attach deterministic runtime trace per successful model result. |
| McClintock | Python `nirs4all.predict` oracle contract | done | Read-only. Confirmed `PredictResult` exposes `y_pred`/`to_numpy`, not `.predictions`; `engine`/`allow_fallback` are not valid `predict` kwargs. |

## Decisions

- Do not pass `engine`, `allow_fallback`, `results_path`, or runtime-only kwargs into `nirs4all.predict`.
- Preserve Python `nirs4all.predict` as the oracle for Studio prediction routes.
- Add a Studio-only runtime trace for prediction calls so the route is explicit about running the Python oracle.
- Refuse `engine="dag-ml"` for `predict` unless `allow_fallback=true`; with fallback, run the Python oracle and record the structured refusal diagnostic.
- Fix `api/predictions.py` to read `PredictResult.y_pred`/`to_numpy()` instead of stale `.predictions`.

## Gates

- `python -m py_compile api/prediction_runtime.py api/predictions.py api/models.py tests/test_prediction_runtime.py` - passed.
- `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_prediction_runtime.py tests/test_predict_metrics.py tests/test_models_api.py tests/test_runtime_engine.py -q --tb=short` - 33 passed, 5 expected warning-emission tests.
- `/home/delete/.local/bin/ruff check api/prediction_runtime.py api/predictions.py api/models.py tests/test_prediction_runtime.py` - passed.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node_modules/.bin/vitest run src/components/runs/__tests__/PredictDialogData.test.ts` - 11 passed.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node_modules/.bin/eslint src/components/runs/PredictDialogData.ts src/components/runs/__tests__/PredictDialogData.test.ts` - passed.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node_modules/.bin/tsc --noEmit --project tsconfig.app.json` - failed on pre-existing errors outside W3A files: `src/api/inspector.test.ts`, `src/components/predictions/viewer/fetchPartitionData.ts`.
- Full parity not run in W3A; deferred until a larger integrated batch.

## Integration Notes

- Worktree target: `_worktrees/INT-studio` on `refactor/integration-studio`.
- Existing older Studio runtime-bypass worktrees were audited but not merged wholesale; several are superseded by W95/W2X integration.
- Reviewer: Hooke found two issues; both were fixed before commit:
  - strict `engine="dag-ml"` prediction refusal no longer resolves the Python oracle first;
  - `PredictDialogData` now handles multi-output prediction and actual arrays for preview/export.
- Final Hooke follow-up: no blocking finding remaining.
