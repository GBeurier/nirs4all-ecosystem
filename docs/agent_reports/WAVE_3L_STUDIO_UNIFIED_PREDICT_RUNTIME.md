# Wave 3L - Studio Unified Predict Runtime Route

Date: 2026-07-01

## Scope

Lane H tranche focused on Studio's unified prediction route in `_worktrees/INT-studio`, without running full parity suites.

The earlier W2W finding against `training.py`, `automl.py`, and `pipelines.py` is stale for `refactor/integration-studio`: those routes already use `run_with_engine_record`. The remaining Studio prediction bypass was `/api/predict` and `/api/predict/file`.

## Commit

- `_worktrees/INT-studio` `1fef97c` - `fix(studio): route unified predict through runtime oracle`

## Files Modified

`_worktrees/INT-studio`:

- `api/predict.py`
- `tests/test_predict_metrics.py`
- `src/api/predict.ts`
- `src/types/predict.ts`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Descartes | Read-only audit of Studio oracle/runtime routes | done | Confirmed `training.py`, `automl.py`, and `pipelines.py` are already migrated in `INT-studio`; found `/api/predict` still called `nirs4all.predict` directly. |
| Lagrange | Read-only audit of core/runtime contract consumed by Studio | done | Reconfirmed strict-first `dag-ml` run semantics and runtime record fields; noted some findings against `nirs4all-studio/main` are stale for `INT-studio`. |
| Anscombe | Review of initial `/api/predict` patch | GO | Requested TS contract coverage and real HTTP/TestClient coverage for JSON and multipart routes. |
| Hilbert | Final four-file diff review | GO | No blocking findings; residual risks were direct fetch error formatting and implicit bundle coverage. Both were fixed before commit. |

## Decisions

- Preserve `nirs4all.predict` as the Python oracle for `/api/predict` and `/api/predict/file`.
- Route both unified predict entry points through `api.prediction_runtime.predict_with_runtime_record`.
- Do not forward `engine`, `allow_fallback`, `results_path`, or any runtime-only kwarg into `nirs4all.predict`.
- Default/legacy requests run the Python oracle and return a `runtime` record with `runtime_source="python_oracle"`.
- Explicit `engine="dag-ml"` refuses with structured `RtError`/HTTP 501 unless `allow_fallback=true`.
- Explicit fallback runs the Python oracle and records `runtime_source="python_oracle_fallback"` plus the `dagml_predict` diagnostic.
- Add optional TS contract fields for `engine`, `allow_fallback`, and prediction `runtime`.
- Improve multipart upload client error formatting so structured `detail.message` does not surface as `[object Object]`.

## Review

- Initial Descartes audit: found the only live bypass in `api/predict.py`.
- Anscombe review: GO with two non-blocking requirements.
  - Added `src/types/predict.ts` runtime/policy fields and `src/api/predict.ts` multipart options.
  - Added TestClient coverage for JSON success/refusal and multipart fallback.
- Hilbert review: GO with two residual risks.
  - Added structured error-message extraction in `src/api/predict.ts`.
  - Added explicit bundle branch HTTP coverage in `tests/test_predict_metrics.py`.

## Tests Run

`_worktrees/INT-studio`:

- `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_predict_metrics.py -q --tb=short` -> 12 passed.
- `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_studio_oracle_routes.py tests/test_runtime_engine.py tests/test_prediction_runtime.py tests/test_automl_durable_results.py tests/test_predict_metrics.py -q --tb=short` -> 47 passed, 5 expected warning-emission tests.
- `/home/delete/.local/bin/ruff check api/predict.py tests/test_predict_metrics.py` -> passed.
- `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m py_compile api/predict.py tests/test_predict_metrics.py` -> passed.
- `PATH=/home/delete/.vscode-server/bin/1b50d58d73426c9171299ec4037d01365d995b78:$PATH ./node_modules/.bin/tsc --noEmit` -> passed.
- `PATH=/home/delete/.vscode-server/bin/1b50d58d73426c9171299ec4037d01365d995b78:$PATH ./node_modules/.bin/eslint src/types/predict.ts src/api/predict.ts` -> passed.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- Full Python-reference parity, dag-ml/native parity, and Studio/Web runtime contract suites were intentionally deferred to the next larger integrated batch.
- The Predict page UI does not yet expose a runtime-engine selector for this route; the backend and TS client now support the contract.
- Release-lock/topology validation is unchanged by this Studio-only tranche. The roadmap still keeps `nirs4all.python.oracle`, `nirs4all.r.aggregate`, and `nirs4all.browser_wasm.aggregate` in scope.
