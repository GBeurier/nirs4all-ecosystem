# SW8 — Runtime API + Studio backend extraction: concrete implementation plan (L10/L12)

**Agent:** SW8 (second-wave; Runtime API impl + Studio reassembly) · **Mode:** read-only audit → implementation spec. No code, no sync board, no other report edited. This file is the only write.
**Date:** 2026-06-30 · **Lanes:** `L10` Runtime API (`LOCK-RT` landed, `DEC-RT-001` accepted), `L12` Studio reassembly. **Blockers targeted:** `B-018` (explicit RtError), `B-017` (compute trapped in Studio FastAPI), `B-011`/PYREF-008/`BLK-PYREF-5` (Studio rides the oracle).
**Consumes:** `RT_spec.md`, `A6_A6-studio-ui.md`, `A2_A2-pyref.md`, `A3_A3-dagml.md`, `A4_A4-controllers.md`, `CAP_spec.md`, sync board pass-2.
**Method:** direct `Read`/`Grep` + three read-only sub-audits on the live heads (`nirs4all e41362b4`, `nirs4all-studio 2ccbf68`, `nirs4all-web 745eef8`, `dag-ml f58d7bf`). Every `path:line` below was verified in-tree, not from CodeGraph.

---

## 0. TL;DR

1. **Nothing new needs to be invented; three things need to be *named and wired*.** The result triple (`score_set.json` + `predictions.parquet` + `manifest.json`) is already written by `native_results.py` and already read back by both Studio (`native_results_adapter.py:141`) and the legacy projector (`result.py:590-603`). `RtResult`/`RtRunRequest`/`RtError` are **thin wrappers** over surfaces that already exist on all three runtimes — exactly per `LOCK-RT`.
2. **Home (V1):** wire schema in `nirs4all-ecosystem/docs/contracts/runtime/` (neutral, GOV-deferred); Python dataclasses in a **new `nirs4all/pipeline/dagml/rt.py`** (where all four inputs already live); a non-breaking `RunResult.to_rt_result()` public seam; TS mirror in `nirs4all-web/.../engine/rt.ts` + Studio `api/` Pydantic models. **No change to `RunResult`, `.n4a`, or the native format** (0.9.x stable contract).
3. **Studio routing (V1):** the *run/predict* verbs are routable **now** — thread `engine=` through `runs/training/automl/predict` and **persist which engine ran** (today it is never passed and never recorded — `runs.py:1431`, `training.py:466`, `automl.py:903`, `predict.py:81,89`). The *analysis/metrics* hotspots are **not** routable in V1 because the math has no library home yet; V1 only stops the re-implementations that *do* have a home (`predict.py` metrics → `eval_multi`), and **defines** the later `analysis`/`inspect` verb target. The deep push-down is Wave-4 (`B-017`, couples L5/L16/north-star).
4. **Manifests (V1):** add a public `nirs4all` accessor over the existing 5-dict `controller_manifests()` and a thin Studio `GET /api/operators/manifests`; Studio's `generate_registry.py` catalog becomes the **product-metadata overlay keyed by `controller_id`**. Full per-operator manifests wait on the CTRL-000 adapter (A4 §2).
5. **Fallback (V1):** make the Python warn+fallback (`run.py:606-618`) emit a structured `RtError` diagnostic onto the result, and add an opt-in `allow_fallback=False` that **raises** `RtError` instead of silently degrading. Make the Web silent catch (`dagml-engine.ts:520-534`) surface `RtError`. The **hard** "no implicit fallback" cutover stays `LOCK-DROP`/`L19` (gated on `EXPECTED_FALLBACK==empty`, 11 cases, A3).
6. **Gate (V1):** a Studio dual-engine route-parity test + an engine-recorded assertion + a manifest-no-drift test + RtError contract tests (reusing the 11 `EXPECTED_FALLBACK` fixtures and the parity comparator). Blocked on `BLK-PYREF-1` (`compatibility.md` tolerance ledger) for the *numeric tolerance* and on `B-013` (matplotlib missing in `.venv`) for the suite to collect at all.

---

## 1. Verified ground truth (the surfaces V1 wraps)

| Fact | Evidence (`path:line`) |
|---|---|
| Python `engine="dag-ml"` dispatch + transparent legacy fallback (warn, then `_run_legacy()`); only `DagMlUnavailable`/`DagMlUnsupported`/`NotImplementedError` caught | `nirs4all/nirs4all/api/run.py:570-620` |
| `run_via_dagml(pipeline, dataset, *, name, random_state, refit, project, session, cache, runner_kwargs, dagml_cli, venv_python, workdir, results_path) -> RunResult` — the **de-facto `RtRunRequest` field set** | `nirs4all/nirs4all/pipeline/dagml/run_backend.py:212-226` |
| Error taxonomy: `DagMlUnsupported(NotImplementedError)`, `_OperatorLoweringUnsupported(DagMlUnsupported)`, `DagMlUnavailable(RuntimeError)`; structured `error_kind ∈ {unsupported, error}` adapter protocol | `nirs4all/nirs4all/pipeline/dagml/errors.py:24-149` |
| Native triple writer/reader: `write_native_results(result, score_set, results_path)` → `manifest.json` + `score_set.json` + `predictions.parquet` + `artifacts/`; `read_native_results(run_dir)` → `{manifest, score_set, predictions, artifacts}`, **hash-validated** (`score_set_hash`); manifest `schema_version=2` carries `engine, plan_id, bundle_id, selected_variant, capabilities, files` | `nirs4all/nirs4all/pipeline/dagml/native_results.py` (write ~311-360, read ~363-417, manifest ~255-308) |
| ScoreSet→legacy projection + raw stash: `_scores_to_run_result(...)` stashes `result._dagml_score_set` and `result._dagml_refit_artifacts` | `nirs4all/nirs4all/pipeline/dagml/result.py:293-604` (stash 590-603) |
| **No** `contracts`/`schema`/`envelope`/`runtime` module exists in nirs4all; top-level pkgs = `analysis, api, cli, config, controllers, core, data, operators, optimization, pipeline, sklearn, synthesis, utils, visualization, workspace` | `find` over `nirs4all/nirs4all/` |
| Studio never passes `engine=` and never records which engine ran | `runs.py:1431`, `training.py:466`, `automl.py:903`, `predict.py:81,89` |
| Execution backend (`local-python|cluster|wasm-local`) is the **environment**, not the ML engine; `ExecutionDriverCapability{backend,label,available,mode,supports_progress,supports_cancellation,metadata}`; only `local-python` available | `api/execution_driver.py:13,22-31,223-328`; `api/runs.py:1543-1551` |
| Studio reads the native triple through the library reader only; `NativeResultsAdapter._variant_summaries()` pivots to `ChainSummary`; used as the fallback store when no `store.sqlite` | `api/native_results_adapter.py:141,662-763`; `api/aggregated_predictions.py:587-594` |
| `controller_manifests()` returns **5 JSON-ready kind-level dicts** (`transform, y_transform, model, merge_concat→prediction_join, meta_model`), each already shaped to `controller_manifest.v1.schema.json` | `nirs4all/nirs4all/pipeline/dagml_bridge.py:1008-1127` |
| Studio catalog is `pkgutil` introspection of `nirs4all.operators.*` + `_webapp_meta`, merged in `node_registry_loader.py:160-175`; **zero** `ControllerManifest`/`operator_kind`/`/api/operators/manifests` references | `scripts/generate_registry.py`; `api/node_registry_loader.py:160-175` |
| Web fallback is **silent**: unsupported generator throws (`dagml-engine.ts:187-189`), but the campaign-phase catch silently calls `runChainOverFolds()` (`dagml-engine.ts:520-534`); split swallow + `console.warn` (`orchestrate.ts:316-322`); AOM/POP cost guard throws (`guard.ts:24-56`) | as cited |
| Web result shapes: `RunResult` (`types.ts:235-259`), `ScoreNode` (`215-223`), `PredRow` (`202-209`), `Engine.run/predict` (`284-293`) | `nirs4all-web/studio-lite/src/engine/types.ts` |
| Studio compute hotspots: `analysis.py` 100% trapped (PCA/t-SNE/UMAP/correlation/permutation+MI+F importance); `metrics_computer.py` ~80% trapped descriptors; `evaluation.py` mixed (`eval_multi`+`detect_task_type` delegated, skew/kurtosis/Shapiro/KFold hand-rolled); `predict.py:114-122` re-rolls RMSE/R²/MAE/RPD via `sklearn.metrics` | A2 §5 + sub-audit, file:line per §4 below |

---

## 2. Decision 1 — where `RtResult` / `RtRunRequest` / `RtError` live

### 2.1 Constraints that fix the answer
- `DEC-DESIGN-001`: **core = inspect/validate/capability only; execution lives in runtimes** → the envelope is a *runtime* surface, not a dag-ml core contract.
- `RT_spec` point 1 + `LOCK-RT`: the envelopes add **zero new dag-ml fields**; they wrap `score_set` + `predictions` + `manifest` + `selection_decision`. So the wire schema must **reference** dag-ml contracts, not fork them.
- 0.9.x stability: `RunResult`/`PredictResult`/`.n4a`/workspace are frozen contracts (nirs4all CLAUDE.md). **`RtResult` must be a separate projection** — never a mutation of `RunResult`.
- GOV (`DEC-GOV-002`) unresolved on the *published-package* home (lite→`nirs4all-core`, facade `n4a.*`). `RT_spec` Q1 explicitly defers the package home to GOV.

### 2.2 V1 placement (concrete)

| Artifact | V1 home | Why |
|---|---|---|
| **Wire schema** (single source of truth) | `nirs4all-ecosystem/docs/contracts/runtime/{rt_result,rt_run_request,rt_error}.v1.schema.json` | Ecosystem is the cross-repo spec home; watchlist binds "Runtime request/response schemas → L10". Neutral ground that sidesteps the GOV package decision. Each schema `$ref`s dag-ml `score_set`/`selection_decision`/`coordinator_data_plan_envelope` and the CAP-004 cause set — references only. |
| **Python dataclasses + adapters** | **new `nirs4all/pipeline/dagml/rt.py`** | All four inputs already live in `pipeline/dagml/`: `native_results.py` (triple), `result.py` (`_dagml_score_set`), `errors.py` (`DagMl*`), `run_backend.py` (`run_via_dagml` field set). Putting `rt.py` beside them keeps the wrapper next to its data and out of the frozen `api/result.py`. |
| **Public seam** | additive method `RunResult.to_rt_result() -> RtResult` in `nirs4all/nirs4all/api/result.py` + a public `nirs4all.runtime.from_native_dir(path)` re-export | So Studio/Web/CLI get `RtResult` without importing the private `pipeline.dagml` package (Studio already does this at `native_results_adapter.py:141`, but the seam makes it contractual). Additive → 0.9.x-safe. |
| **TS types + adapters** | `nirs4all-web/studio-lite/src/engine/rt.ts` (+ reconcile with `engine/types.ts`/`contracts.ts`, the UI-004 negotiating table per A6 §6) | Web `RunResult` becomes the *nest* view of `RtResult`. |
| **Studio models** | `nirs4all-studio/api/` Pydantic models mirroring the schema; `NativeResultsAdapter` emits `RtResult`, `ChainSummary` = *pivot* view | Studio `ChainSummary` and Web `RunResult` are both lossless projections (RT_spec §RT-002). |

### 2.3 The three envelope shapes (V1, wrappers only)

```
RtResult v1   = { schema_version, run_id, plan_id,
                  selection,            # ← dag-ml selection_decision (winner + ranked); manifest also has selected_variant
                  reports[],            # ← VERBATIM score_set.reports[]  (the join key: partition/level/fold_id/variant_id/target)
                  predictions[],        # ← predictions.parquet rows
                  manifest{ engine, fingerprints, capabilities, portable_level, files },  # ← manifest.json (schema_version=2)
                  artifacts?[],         # ← artifacts/ refs
                  diagnostics?[] }      # ← list[RtError]  (e.g. "ran legacy because <cause>"; see Decision 4)
RtRunRequest v1 = { pipeline_dsl, dataset_ref, cv{folds,seed}, execution_backend, options{ name, refit, project, session, cache, allow_fallback } }
                  # == run_via_dagml field set (run_backend.py:212) + execution_backend (execution_driver) + allow_fallback (new)
RtError v1    = { verb, cause, message, mitigation, unsupported_capability?, portable_level? }
                  # cause/mitigation/unsupported_capability VOCAB owned by CAP-004; RtError only carries it
```

`RtResult` constructors: `RtResult.from_native_dir(run_dir)` (wraps `read_native_results`) and `RtResult.from_run_result(rr)` (reads `rr._dagml_score_set` + the stashed predictions). Both are pure projections — no recompute.

### 2.4 Deferred to later (not V1)
- The **published contracts package** (a real importable module others depend on) and a top-level `nirs4all/runtime/` consolidation namespace → **GOV / `LOCK-REL`**. V1 ships the schema in ecosystem + per-runtime mirrors; this is exactly `RT_spec` Q1's "ship spec, defer package home".

---

## 3. Decision 3 — expose operator manifests to Studio (do this before the hotspots; it is the cheapest win)

*(Ordering note: manifests first because the existing 5-dict producer makes it a near-zero-risk endpoint, and the node-registry reconciliation unblocks the capability-aware UI that L11 wants.)*

### 3.1 V1 steps
1. **Library accessor:** add a public `nirs4all` function (e.g. `nirs4all.runtime.list_controller_manifests() -> list[dict]`) that returns `dagml_bridge.controller_manifests()` verbatim (already JSON-ready, `dagml_bridge.py:1008`). Studio must not import the private bridge module.
2. **Studio endpoint:** `GET /api/operators/manifests` (thin route, `api/` not `src/`) returning `{ runtime: {nirs4all_version, dag_ml_version}, manifests: [...] }`. This is the `inspect` verb surface (`RT_spec` RT-001) — its envelope is `LOCK-RT`-bound.
3. **Reconcile the catalog (A4 §4.2/§4.3):** keep `generate_registry.py` output as the **product-metadata overlay keyed by `controller_id`** (category/tier/tags/icons/widget params). Make Studio's 8-value `NodeType` a **view over** dag-ml `NodeKind` instead of a parallel enum. Point `NodeRegistryContext` at the manifest endpoint for identity/kind/phase/ports; keep the overlay for UI copy.
4. **No-drift gate** (test): `/api/operators/manifests` output `==` `list_controller_manifests()` by construction, and **validates against** `dag-ml/docs/contracts/controller_manifest.v1.schema.json`.

### 3.2 Honest scope limit (state it in the endpoint docs)
The runtime registers only **5 kind-level manifests** today (`transform/y_transform/model/prediction_join/meta_model`); the `OperatorController → ControllerManifest` B1 adapter does **not** exist (A4 §1.3, sync board `B-CTRL-1`). So the V1 endpoint surfaces the **static kind-level set**, not one manifest per operator. That is enough for "show which controller-kind will own this node + unsupported diagnostics", but the per-operator capability ledger waits on CTRL-000.

### 3.3 Later
- Replace the static set with the CTRL-000 two-layer adapter (A4 §2: keyword→lowering kind, class→`operator_selectors`) → full per-operator manifests endpoint, capability-aware palette (`LOCK-CAP`), controller-ownership panel (greenfield, A6 §2.3).

---

## 4. Decision 2 — route Studio through runtime APIs instead of backend compute hotspots (L12)

Two **distinct** problems hide under "route through runtime APIs". Separate them or the plan over-promises.

### 4.A The *run/predict* verbs — routable **now** (V1). Closes the bypass / `B-011` / PYREF-008.
Studio already calls `nirs4all.run/predict`; it just never selects or records the engine.

| V1 step | Change | File |
|---|---|---|
| Thread engine into the request | add `engine` to `CreateRunRequest`/`QuickRunRequest`/predict request → pass `nirs4all.run(..., engine=...)` / `predict(..., engine=...)` | `runs.py:1431`, `training.py:466`, `automl.py:903`, `predict.py:81,89` |
| **Persist which engine ran** | record the resolved engine on the run record (the engine that actually produced the result, incl. fallback) | run-record write path + `execution_job_records.py` |
| Surface it | expose engine + any `RtResult.diagnostics` on the run/aggregated-predictions read models | `native_results_adapter.py`, `aggregated_predictions.py` |
| Keep `execution_backend` orthogonal | `execution_backend` (`local-python|cluster|wasm-local`) stays the *environment* selector; do **not** overload it with engine | `execution_driver.py` |

This is the concrete meaning of "Studio routes through the RT `run` verb": `RtRunRequest.options.engine` + the engine recorded on the result.

### 4.B The *analysis/metrics* hotspots — **not** routable in V1 (the math has no library home). Two-step.

**Step 1 (V1): stop the re-implementations that already have a home.** Minimal, high-value:
- `predict.py:114-122` re-rolls RMSE/R²/MAE/RPD via `sklearn.metrics` → route through `nirs4all.core.metrics.eval_multi` (already used by `evaluation.py:229`). Kills the worst of the four A2 §5 re-implementations and makes Studio metrics oracle-checkable.

**Step 2 (later, Wave-4 — `B-017`, couples L5/L16/north-star): migrate trapped math *down*, then expose as a runtime verb.** A component becomes WASM-portable only after its compute lives in the library (A6 §7-8). Target table:

| Studio hotspot | Trapped compute (verified) | Target library home | Runtime verb | Phase |
|---|---|---|---|---|
| `api/analysis.py` (100% trapped) | PCA/t-SNE/UMAP (`sklearn.decomposition`/`manifold`, `umap`), correlation (`scipy.stats`), permutation/MI/F importance | `nirs4all.analysis` (PCA partly there: `compute_pca_projection` already called from `playground/charts.py`) | `analysis`/`inspect` (RtResult-shaped) | **later** |
| `api/shared/metrics_computer.py` (~80%) | amplitude/energy/noise/quality + distance descriptors (`numpy`/`scipy.signal`/`LedoitWolf`/`PCA`) | new `nirs4all` descriptors module (chemometric leverage/Hotelling/LOF already delegate to `operators.filters`) | `inspect` | **later** |
| `api/playground/charts.py` (mixed) | per-wavelength stats, Mahalanobis/repetition distances (`scipy.spatial`), `umap` | `nirs4all.analysis` / `nirs4all.data.repetition_detection` (PCA + rep-detection already delegate) | `inspect` | **later** |
| `api/playground/executor.py` | "mini step-runner" (delegates compute to `_steps`/`_charts`, but is a parallel pipeline path outside `StepRunner`) | converge onto the real runtime `run`/`plan` once it can drive a single-step preview | `plan`/`run` | **later** |
| `api/evaluation.py` (mixed) | confusion (`sklearn`), skew/kurtosis/Shapiro (`scipy.stats`), KFold cross_val | `nirs4all.core` evaluation (`eval_multi`/`detect_task_type` already delegate) | `inspect`/`run` | later |
| `api/spectra.py`, `datasets.py`, `preprocessing.py` | DELEGATES-OK (loading + minor UI stats + `fit_transform` via library operators) | — | — | leave |

**V1 must not claim the deep push-down.** It only (a) routes run/predict, (b) kills `predict.py` metric re-roll, and (c) **defines** the `analysis`/`inspect` verb contract (RtResult-shaped) so Wave-4 has a target. Whether `analysis`/`inspect` become first-class RT verbs beyond the 8 or stay assembled wrappers is `RT_spec` Q4.

---

## 5. Decision 4 — make fallback/unsupported explicit (`B-018`)

Three divergent shapes today (RT_spec §RT-003): Python warn+fallback (`run.py:606-618`), Studio preflight `issues[]` + driver `metadata.reason`, Web **silent** catch (`dagml-engine.ts:520-534`). Converge them onto `RtError`, whose vocabulary is owned by **CAP-004** (`CAP_spec.md` §5 cause table).

### 5.1 Migration map (cause vocab = CAP-004, do not invent)
| Source signal | `RtError.cause` | `path:line` |
|---|---|---|
| `DagMlUnsupported` / `NotImplementedError` | `unsupported_shape` | `errors.py:30,44`; `run.py:612` |
| `DagMlUnavailable` | `unavailable_backend` | `errors.py:56`; `run.py:606` |
| preflight `missing_module` | `unsupported_capability` | `runs.py` preflight `issues[]` |
| driver `metadata.reason=driver_unavailable` | `unavailable_backend` | `execution_driver.py:304-335` |
| Web `hasUnsupportedGenerator` throw | `unsupported_shape` | `dagml-engine.ts:187-189` |
| Web campaign-phase silent catch | `runtime_error`/`unsupported_shape` | `dagml-engine.ts:520-534` |
| `guard.ts` oversized AOM/POP | `unsupported_capability` (+ `mitigation`) | `guard.ts:44-49` |

### 5.2 V1 (do not force the hard cutover)
- **Python:** at `run.py:606-618`, keep the transparent fallback as the default (`LOCK-DROP`: legacy stays default until cutover), **but** build an `RtError` from the caught exception and **attach it** to the returned result (`RunResult.to_rt_result().diagnostics` / a `rt_diagnostics` field) so every caller can see *"ran legacy because `<cause>`"*. Add `allow_fallback: bool = True` to `run_via_dagml`/`run` and `RtRunRequest.options`; **`allow_fallback=False` re-raises `RtError`** instead of degrading. This is the opt-in "no silent fallback" `B-018` asks for, without the L19 flip.
- **Web:** convert the `dagml-engine.ts:520-534` silent `runChainOverFolds()` into: emit `RtError` (surfaced to the UI) and only fall back behind an explicit opt-in mirroring `allow_fallback`. Wrap `guard.ts`/`orchestrate.ts:316-322` swallows in `RtError` diagnostics.
- **Studio:** map preflight `issues[]` + driver `metadata.reason` to `RtError.cause`; surface the recorded engine + diagnostics on the run read model.

### 5.3 Later
- **Hard "no implicit fallback"** (`allow_fallback=False` as the default, or removal of `_run_legacy`) = `LOCK-DROP`/`L19`, gated on `EXPECTED_FALLBACK==empty` (11 cases — 4 `branch_dup_*`, 4 `multi_source_*`, 3 `preprocessing_*`; A3 §"Current Expected Legacy Fallbacks", `B-010`, owned by L5/A3) + native `.n4a` export (DML-008).

---

## 6. Decision 5 — PYREF / Studio-bypass tests that gate this

Source: A2 §7 (G1-G9), §3c, PYREF-008, `BLK-PYREF-5`; CAP-004; RT_spec §RT-003. **Reuse the existing oracle, never a weaker parallel suite** (A2 output guarantee).

### 6.1 V1 gates (new, but built on existing harness)
1. **Studio dual-engine route parity (PYREF-008 / G9, closes `BLK-PYREF-5`):** run the *same* pipeline through Studio's run path with `engine=legacy` then `engine=dag-ml`; assert `RtResult` parity using the parity oracle's `dual_engine_runner`/comparator and tolerances (`tests/integration/parity/_conformance_helpers.py`). Studio is currently invisible to the oracle because it never passes `engine=`.
2. **Engine-recorded assertion:** assert the Studio run record persists which engine produced the result (incl. fallback) — directly closes the "Studio never records which engine ran" finding.
3. **Studio re-implementation parity (A2 §5):** assert Studio `predict.py` metrics `==` `nirs4all.core.metrics.eval_multi` after the V1 reroute (the other three — `transfer.py`, `analysis.py` importances — get a parity check or move down in Wave-4).
4. **Manifest no-drift:** `/api/operators/manifests` `==` `list_controller_manifests()` and validates against `controller_manifest.v1.schema.json` (§3.1.4).
5. **RtError contract:**
   - Python: feed each of the 11 `EXPECTED_FALLBACK` shapes with `allow_fallback=False` → assert `RtError(cause=unsupported_shape)`; with `allow_fallback=True` → assert the result carries the diagnostic with the correct `cause`. Fixtures = the existing `EXPECTED_FALLBACK` allowlist.
   - Web: extend `dagml.test.ts`/`engine.test.ts` so an unsupported generator surfaces `RtError` (not a silent `runChainOverFolds`).
6. **RtResult view round-trip (anchors LOCK-RT point 2):** on a shared fixture, assert Studio `ChainSummary == pivot(RtResult)` and Web `RunResult == nest(RtResult)` (both views are lossless projections of the same `reports[]`).
7. **Keep the boundary invariant:** `test_native_fallback_boundary` stays green; `EXPECTED_FALLBACK` cannot silently widen; strict-xfail XPASS = RED (A2 §2).

### 6.2 Blocking pre-conditions (not solvable inside L10/L12)
- **`BLK-PYREF-1` (high):** `nirs4all/docs/compatibility.md` tolerance ledger is **absent**; `1e-9` contract vs `1e-3` enforced is unreconciled. The parity tests above have **no fixed tolerance to assert** until L17 authors it.
- **`B-013`:** the integration suite does **not collect** (`tests/conftest.py` imports `matplotlib`, absent from `.venv`). Fix the venv before any of these can run on `main`.
- **Later cross-engine gaps (A2 G5/G6):** `.n4a`/workspace cross-engine read/predict (PYREF-009) and error-parity (same invalid pipeline → same `RtError` both engines) are post-V1 additions tied to native export (DML-008).

---

## 7. Sequencing — V1 vs later cleanup

### V1 (immediate; unblocked or only lightly gated)
1. **Envelopes:** schema in `ecosystem/docs/contracts/runtime/` + `nirs4all/pipeline/dagml/rt.py` (`RtResult`/`RtRunRequest`/`RtError` + `from_native_dir`/`from_run_result` + `from_dagml_error` classifier) + additive `RunResult.to_rt_result()`. **No `RunResult`/native-format change.**
2. **Explicit fallback (Python):** attach `RtError` diagnostics at `run.py:606-618`; add `allow_fallback=False` strict mode that raises `RtError`; map `DagMl*` → CAP-004 cause vocab.
3. **Studio run routing:** thread `engine` through `runs/training/automl/predict`; persist + surface the engine that ran; reroute `predict.py` metrics through `eval_multi`.
4. **Manifests:** public `nirs4all` accessor + thin Studio `GET /api/operators/manifests`; node-registry overlay keyed by `controller_id`.
5. **Web:** surface `RtError` on the `dagml-engine.ts` silent catch + `guard.ts`; fallback behind explicit opt-in.
6. **Gates:** §6.1 tests (Studio dual-engine parity, engine-recorded, manifest-no-drift, RtError contract, view round-trip); fix `.venv` matplotlib so the suite collects.

### Later cleanup (gated by north-star / locks)
- **Compute push-down (Wave-4, `B-017`):** migrate `analysis.py`/`metrics_computer.py`/`playground.charts`/mini-step-runner math into `nirs4all`(/`dag-ml`/`io`), then expose as `analysis`/`inspect` RT verbs returning RtResult-shaped payloads → unblocks WASM portability. Move the remaining 3 Studio re-implementations down.
- **Native `.n4a` export (DML-008):** so the RT `export` verb is native; enables PYREF-009 cross-engine `.n4a`/workspace + error-parity tests; criterion for `LOCK-DROP` D2.
- **CTRL-000 adapter:** replace the static 5-manifest set with the two-layer `OperatorController→ControllerManifest` projection (A4 §2) → full per-operator manifest endpoint + capability-aware UI (`LOCK-CAP`).
- **Hard cutover (`LOCK-DROP`/`L19`):** make `allow_fallback=False` the default / remove implicit legacy fallback once `EXPECTED_FALLBACK==empty` (`B-010`, L5/A3) + oracle green on `main` (`B-013`) + tolerance ledger (`BLK-PYREF-1`).
- **Package home:** published contracts module + `nirs4all/runtime/` namespace → GOV / `LOCK-REL`.

---

## 8. Dependencies, blockers, open questions

**Depends on / coupled to:**
- `CAP-004` (cause/mitigation/`portable_level` vocabulary — RtError *carries*, never redefines) · `CAP_spec.md` §5.
- `DEC-CTRL-001` / CTRL-000 B1 adapter (manifest completeness) · A4.
- L5/A3 for `EXPECTED_FALLBACK==empty` (`B-010`) and native export (DML-008) · A3.
- L17 for the tolerance ledger (`BLK-PYREF-1`) and the dual-engine comparator · A2.
- GOV / `LOCK-REL` for the published envelope package home.
- `LOCK-IO` for dataset read models (out of the L10/L12 run/predict path; do not block V1 on it).

**Open questions for A0 / maintainer:**
1. Envelope package home: ecosystem-spec-only for V1 (recommended) vs a published contracts package now (GOV)?
2. Does `allow_fallback=False` ever become the Studio default before `L19`, or stay strictly opt-in with the diagnostic surfaced? (Recommend opt-in.)
3. Manifest endpoint: library accessor + Studio proxy (recommended) vs Studio computing it?
4. Do `analysis`/`inspect` earn first-class RT verbs (beyond the 8) or stay assembled wrappers? (`RT_spec` Q4.)

---

## 9. Sync board handoff (for A0 to integrate — NOT applied here; I did not edit the board)

**Proposed `L10` lane row:**
> `L10` Runtime API · `review` · SW8 · spec+impl · **Next:** implement V1 envelopes (`rt.py` + ecosystem schema + `RunResult.to_rt_result()`), explicit `RtError`/`allow_fallback`, per-runtime adapters per `SW8_RT_STUDIO_IMPL_spec.md`. · Blockers: `B-018`, `CAP-004` vocab, GOV (package home).

**Proposed `L12` lane row:**
> `L12` Studio reassembly · `review` · SW8 · `nirs4all-studio` · **Next:** V1 = thread+record `engine=` (close bypass `runs.py:1431`/`training.py:466`/`automl.py:903`/`predict.py:81,89`), `predict.py` metrics→`eval_multi`, `GET /api/operators/manifests`, Web `RtError`. Wave-4 = push `analysis`/`metrics_computer`/`playground` compute down. · Blockers: `B-017`, `B-011`/PYREF-008, `BLK-PYREF-1`, `B-013`.

**Proposed worklog entry:**
> 2026-06-30 | SW8 (L10+L12) | review | Implementation plan for RtResult/RtRunRequest/RtError (home = ecosystem schema + `pipeline/dagml/rt.py` + additive `RunResult.to_rt_result()`, zero native-format change), Studio run/predict routing (thread+record engine, close the never-passed-`engine=` bypass), `/api/operators/manifests` over the existing 5-dict `controller_manifests()`, explicit `RtError`+`allow_fallback` (Python diagnostic + opt-in raise; Web silent-catch→RtError), and the PYREF/Studio-bypass gate set (dual-engine route parity, engine-recorded, manifest-no-drift, RtError contract, view round-trip). V1 vs Wave-4 split; deep compute push-down kept gated on B-017/L5/L16. | read-only; 3 sub-audits + direct Read/Grep on live heads; no code/sync/board edits; report `docs/agent_reports/SW8_RT_STUDIO_IMPL_spec.md`. | Gating: `BLK-PYREF-1` (tolerance ledger), `B-013` (matplotlib venv), `B-010` (EXPECTED_FALLBACK) for hard cutover, GOV for package home.

**Blockers recorded (not resolved):** `B-018` (lane core), `B-017` (compute push-down, Wave-4), `B-011`/PYREF-008/`BLK-PYREF-5` (Studio on oracle), `BLK-PYREF-1` (tolerance ledger), `B-013` (suite collection), `B-010` (EXPECTED_FALLBACK==empty for L19), CTRL-000 (manifest completeness), GOV/`LOCK-REL` (package home).

---

### Evidence (read-only; only this file written)
`nirs4all/nirs4all/api/run.py`, `pipeline/dagml/{errors,run_backend,native_results,result}.py`, `pipeline/dagml_bridge.py`, `api/result.py`, `nirs4all/__init__.py`; `nirs4all-studio/api/{runs,training,automl,predict,execution_driver,native_results_adapter,aggregated_predictions,node_registry_loader,analysis,evaluation,spectra,datasets,preprocessing}.py`, `api/shared/metrics_computer.py`, `api/playground/{executor,charts}.py`, `scripts/generate_registry.py`; `nirs4all-web/studio-lite/src/engine/{dagml-engine,dagml,guard,orchestrate,types}.ts`; `dag-ml/docs/contracts/{score_set,controller_manifest,selection_decision}.schema.json`. Reports: `RT_spec.md`, `A6_A6-studio-ui.md`, `A2_A2-pyref.md`, `A3_A3-dagml.md`, `A4_A4-controllers.md`, `CAP_spec.md`, `PARALLEL_REFACTORING_SYNC.md`.
