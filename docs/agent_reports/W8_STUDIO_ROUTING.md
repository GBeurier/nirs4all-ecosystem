# W8 — Studio engine routing + manifests + metric reroute (B-017 V1 / B-018) — IMPLEMENTED

**Agent:** W8 (Studio routing, Wave-2B) · **Date:** 2026-07-01 · **Mode:** implementation (minimal shippable slice).
**Repo / branch:** `nirs4all-studio`, worktree `_worktrees/W8-studio`, branch `refactor/W8-studio-routing` (off committed `refactor/L12-runtime-routes`, tip `155678b`).
**Blockers:** `B-017` (V1 routable half only) + `B-018` (record runtime engine/fallback/RtError). **Specs consumed:** `SW8_RT_STUDIO_IMPL_spec.md` §3/§4.A/§5/§6, `RV10_NEXT_WAVE_PLAN.md` W8 prompt, `RT_spec.md` §RT-003 (cause vocab via L12's `RtError`).
**Scope guard honored:** worktree-only; no sibling-repo edits; **did NOT edit** `PARALLEL_REFACTORING_SYNC.md` / `AGENT_RUN_SUPERVISION.md`; no deep `analysis.py` / `metrics_computer.py` push-down (Wave-4); `execution_backend` kept orthogonal to `engine`. This report lives in the `nirs4all-ecosystem` repo and is **left untracked** for the supervisor; only the `nirs4all-studio` code branch is committed.

---

## 0. TL;DR

A focused, low-risk Studio slice that **consumes and records** the runtime ML engine, its transparent fallback, and `RtError` diagnostics — without broad UI/backend refactors. Five pieces, all additive and backward-compatible, gated green:

1. **`api/runtime_engine.py`** (new) — the engine seam: `resolve_engine()` (delegates to nirs4all's own resolver), `engine_run_kwargs()`, and `observe_engine()` — a non-suppressing warning observer that records **which engine actually ran** (incl. the transparent `dag-ml`→`legacy` fallback) and emits L12 `RtError` envelopes classified onto the CAP-004 cause vocab. Forward-compatible with W7's `RunResult.to_rt_result()` when it lands.
2. **`api/runs.py`** — thread `engine` through `ExperimentConfig` / `QuickRunRequest` → `Run.engine` → `_execute_pipeline_training(..., engine=...)` → `nirs4all.run(engine=...)`; **persist** the actual engine + requested engine + diagnostics on `PipelineRun` (serialized into the run manifest, so it round-trips and surfaces on the `GET /runs` read model).
3. **`api/predict.py`** — replace the Studio-side sklearn RMSE/R²/MAE/RPD re-roll with `nirs4all.core.metrics.eval_multi` (the same impl behind `evaluation.py`), making predict metrics oracle-checkable.
4. **`api/operators.py`** (new) + `main.py` — thin guarded `GET /api/operators/manifests` over the **public** `nirs4all.runtime.list_controller_manifests()` accessor (never the private bridge); degrades to `available:false` + `[]` when W7 has not landed.
5. **Tests** — 3 new backend test files (`test_runtime_engine.py`, `test_operators_manifests.py`, `test_predict_metrics.py`) + a 1-line sync of 3 existing mock signatures in `test_runs_execution_backend.py`.

---

## 1. What was implemented (file-by-file)

### 1.1 `api/runtime_engine.py` (new, ~210 LOC)
Dependency-light, Phase-1-safe (imports only stdlib + `pydantic` via L12's `runtime_errors`). Public surface:
- **`resolve_engine(requested) -> str`** — delegates to `nirs4all.api.run.resolve_engine` (single source of truth; `None`→`"legacy"`); degrades to the same default if the library is absent.
- **`engine_run_kwargs(requested) -> dict`** — returns `{"engine": requested}` only when a non-blank engine was selected, else `{}`. This is **behaviour-preserving**: runs that don't pick an engine call `nirs4all.run` exactly as before (library default).
- **`observe_engine(requested)`** (context manager) → **`EngineObservation`**. Wraps the `nirs4all.run` call in a scoped `warnings.catch_warnings()` + `simplefilter("always")` + a **non-suppressing** `showwarning` hook (forwards to the original handler), so the transparent-fallback warning (`run.py:413-421`, fragment `"falling back to the legacy engine"`) is captured for the record *and still printed*. `EngineObservation.finalize(result)` returns `{engine, engine_requested, engine_diagnostics}`:
  - prefers W7's `result.to_rt_result().manifest.engine` + `.diagnostics` when that accessor exists (forward-compatible; tested with a fake);
  - else classifies the captured fallback warning onto CAP-004 (`"is not available"`→`unavailable_backend`, `"does not support this pipeline shape"`→`unsupported_shape`, else `runtime_error`) and emits an `RtError(verb="run", cause=…, message=<verbatim warning>, mitigation=…).to_envelope()`.

### 1.2 `api/runs.py` (engine thread + record)
- `PipelineRun` gains `engine` (actual, incl. fallback), `engine_requested`, `engine_diagnostics: list[dict] | None` — additive optional fields (the model already carries ~30). Serialized by `_save_run_manifest` and re-read via `Run(**data)`, so the engine round-trips and appears on `GET /runs` with **no read-model code change**.
- `Run` gains `engine` (requested, experiment-level); `ExperimentConfig` and `QuickRunRequest` gain `engine` (the request input). The 3 config→`Run` constructors (`_create_quick_run`, `_create_run_from_config`, `_create_run_group_from_payload`) set it.
- `_execute_pipeline_training(..., engine=None)`: `run_kwargs.update(engine_run_kwargs(engine))`; the `nirs4all.run(**run_kwargs)` call is wrapped in `observe_engine(engine)`; the finalized record is returned and applied to `PipelineRun` in the job loop. `engine_record` is bound inside the `try` only on a successful run, before the `return` — no unbound-reference path (a raising run propagates out before the return).

### 1.3 `api/predict.py` (metric reroute, B-017 V1 Step-1)
`_run_prediction` no longer imports `sklearn.metrics`; it calls `get_cached("eval_multi")(y_true, y_pred, "regression")` and sanitises the returned dict. Net: metrics now match the library's single implementation (superset of the old 4 keys). Non-breaking — the frontend reads specific keys; extra keys are ignored. `task_type` is fixed to `"regression"` to match the endpoint's prior behaviour exactly (it always computed regression metrics); task-type-aware predict metrics are a later refinement.

### 1.4 `api/operators.py` (new) + `main.py`
`GET /api/operators/manifests` → `OperatorManifestsResponse{available, runtime:{nirs4all_version, dag_ml_version}, manifests:[...]}`. `list_controller_manifests()` imports **only** `nirs4all.runtime` (the W7 public seam) and returns `None` if the module/accessor is missing or raises. Registered in `main.py` with `prefix="/api"`. The route path is unique, so `test_route_registry.py` stays green.

---

## 2. Gates run (from `_worktrees/W8-studio`, studio `.venv` = Python 3.13.11, fastapi 0.128.0, `SENTRY_DSN=""`)

| Gate | Command | Result |
|---|---|---|
| Engine seam unit tests | `pytest tests/test_runtime_engine.py` | **11 passed** (resolve, run-kwargs, no-fallback, both fallback causes, unrelated-warning ignore, non-suppression, W7 forward-compat, broken-rt-result) |
| Manifest endpoint | `pytest tests/test_operators_manifests.py` | **4 passed, 1 skipped** (skip = schema validation, needs W7 accessor + dag-ml schema) |
| Predict == eval_multi | `pytest tests/test_predict_metrics.py` | **2 passed** |
| Route registry (new router) | `pytest tests/test_route_registry.py` | **2 passed** |
| L12 RtError (my dependency) | `pytest tests/test_runtime_errors.py` | **12 passed** |
| Runs API regression | `pytest tests/test_runs_execution_backend.py` | **37 passed** (after syncing 3 mock signatures) |
| Run-manifest round-trip | `pytest tests/test_store_integration.py tests/test_store_adapter_enriched_runs.py` | **52 passed** |
| Runs estimation | `pytest tests/test_runs_estimation.py` | **3 passed** |
| **Combined** | the 9 files above | **123 passed, 1 skipped** |
| Lint | `ruff check` (all 8 touched/new files) | **All checks passed** |
| `py_compile` | all 5 touched modules | OK |

**Frontend gate (`validate:nodes` / `tsc` / `eslint` / `vitest` / `lint:deps`):** **not run** — the worktree has no `node_modules` (git worktrees don't share it) and this slice changes **zero** TS / node-registry JSON / dependency files, so these gates are unaffected by construction. No frontend code was added (see §4).

---

## 3. Soft-dependency handling (W7 not yet landed)

The sibling `../nirs4all` is on `refactor/L17-pyref` (0.10.3): `engine=` is already a real `nirs4all.run` kwarg and `resolve_engine` exists, but **`nirs4all.runtime` and `RunResult.to_rt_result()` do not** (they are W7's `refactor/W7-rt-envelopes`). Per the W8 prompt ("until W7 lands, stub the accessor import behind a feature guard"), both consumers degrade safely:
- `operators.list_controller_manifests()` returns `None` → endpoint reports `available:false`, `manifests:[]`. The no-drift **passthrough** assertion still runs today via a fake accessor; the **schema-validation** assertion auto-skips until W7 + the dag-ml `controller_manifest.schema.json` are present.
- `EngineObservation.finalize()` uses the warning-based detection today and will automatically prefer `to_rt_result()` once present (covered by `test_finalize_prefers_w7_rt_result_when_present`).

No private `nirs4all.pipeline.dagml_bridge` import anywhere (SW8 §3.1 constraint).

---

## 4. Deferred (explicitly out of this minimal slice)

- **Engine threading for `training.py` (quick/refit) and `automl.py`.** These are separate run chokepoints from the `runs.py` job loop and do not share `PipelineRun`'s persisted storage path; recording there needs new response/job-record surface. The primary multi-pipeline run path (both `create_run` and `quick_run` funnel through `_execute_run_job` → `_execute_pipeline_training`) **is** covered. Wiring the other two is a small, isolated follow-up.
- **Frontend consumption (typed fields + engine/RtError badge).** The backend now carries `engine` / `engine_requested` / `engine_diagnostics` on the `GET /runs` read model, but no `src/` TS type or component was changed (supervisor directive: minimal, don't touch unrelated UI; the worktree also can't typecheck/test TS without `node_modules`). Adding the optional fields to the run TS types + a small badge is the natural next step.
- **Studio dual-engine route-parity test (PYREF-008 / SW8 §6.1.1).** Requires a real run through both engines + the nirs4all parity oracle/comparator (gated on `BLK-PYREF-1` tolerance ledger and `B-013` suite collection). The engine-recorded assertion is covered here at the unit level (`observe_engine` + `finalize`); full oracle parity is a nirs4all-side gate.
- **Node-registry overlay keyed by `controller_id`** (SW8 §3.1.3) — a palette refactor; deferred as "broad UI" per the slice constraints. The manifest endpoint that would feed it is shipped.
- **Deep B-017 compute push-down** (`analysis.py` / `metrics_computer.py` / `playground`) — Wave-4 by design (RV10 §10).

---

## 5. Coordination notes

- **No shared-file contention.** All edits are in Studio-owned files (`api/{runs,predict,operators,runtime_engine}.py`, `main.py`, tests). `api/runtime_engine.py` builds on L12's committed `api/runtime_errors.py` (`RtError`/`RtErrorCause`) — reused, not duplicated.
- **Backward compatibility.** Every model field is optional with a default; old run manifests deserialize unchanged. Runs that don't select an engine call `nirs4all.run` byte-identically to before (no `engine` kwarg) and record the resolved default (`legacy`).
- **Feeds:** the engine-recorded surface feeds `B-011` §6d (Studio visible to the engine question) and L19 (Studio on the runtime route). The manifest endpoint is the V1 `inspect` surface for L11's capability-aware palette.

### Evidence (files written, all under `_worktrees/W8-studio`)
New: `api/runtime_engine.py`, `api/operators.py`, `tests/test_runtime_engine.py`, `tests/test_operators_manifests.py`, `tests/test_predict_metrics.py`.
Modified: `api/runs.py`, `api/predict.py`, `main.py`, `tests/test_runs_execution_backend.py` (3 mock signatures).
Ecosystem: this report (untracked, for the supervisor).
