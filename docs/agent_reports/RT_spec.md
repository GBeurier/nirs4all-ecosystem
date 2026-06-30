# RT-SPEC report — lane L10 (Runtime API commune) — LOCK-RT

**Agent:** RT-SPEC (read-only, manual multi-CLI mode)
**Decision:** `DEC-RT-001` (accepted) — the runtime API is a **surface over the EXISTING dag-ml
contracts**, not a re-specification. Every dag-ml field below is **referenced**; anything genuinely
new is flagged **`NET-NEW`**.
**Date:** 2026-06-30
**Method:** CodeGraph + direct `rg`/`sed`/`Read` (local code is authoritative). All citations are
`path:line` verified against working-tree heads (`nirs4all e41362b4`, `dag-ml f58d7bf`,
`nirs4all-studio 2ccbf68`, `nirs4all-web 745eef8`).

**One-line thesis:** there is no missing engine — three runtimes already drive the SAME dag-ml
NodeTask/NodeResult + ScoreSet contracts; LOCK-RT only has to (a) name the 8 verbs over those
contracts and (b) collapse the **two divergent result projections** (Studio REST aggregated-predictions
vs Web WASM `RunResult`) into one envelope whose anchor is the dag-ml **ScoreSet**.

---

## RT-001 — the 8 verbs mapped onto existing dag-ml contracts

The 8 RT verbs are the **runtime/product** surface (`CAP-001`, roadmap:189). They are **not** the
dag-ml controller *phases* (`COMPILE, PLAN, FIT_CV, SELECT, REFIT, PREDICT, EXPLAIN` —
`dag-ml/docs/contracts/controller_manifest.schema.json:116`); a single RT verb drives several phases.
Each verb maps to one or more **existing** contracts (no new contracts are proposed).

| RT verb | dag-ml contract(s) it rides on (file:line) | dag-ml C-ABI / CLI entry (existing) | Python / Studio / Web consumer | Status |
|---|---|---|---|---|
| **inspect** | `execution_plan.schema.json:7` + `score_set.schema.json:7` + `controller_manifest.schema.json:7` (caps `:149`) + `coordinator_data_plan_envelope.schema.json:6` | *(no dedicated verb)* — read-only projection of the above | Studio `GET /aggregated-predictions` (`aggregated_predictions.py:656`), `native_results_adapter.py:1`; Web lineage block (`dagml-engine.ts:228`) | **`NET-NEW`** surface (assembled from existing contracts; no single dag-ml verb) |
| **validate** | `pipeline_dsl.schema.json:6`, `graph_spec.schema.json:7`, `campaign_spec.schema.json:7`, `execution_plan.schema.json:7`, `controller_manifest.schema.json:7` | ABI `dagml_pipeline_dsl_validate_json` (`dag_ml.h:319`), `dagml_graph_validate_json:296`, `dagml_campaign_validate_json:298`, `dagml_execution_plan_validate_json:351`, `dagml_controller_manifest_validate_json:305`; CLI `validate-graph` (`main.rs:864`), `validate-execution-plan:986`, `validate-bundle:1821` | Studio `POST /runs/preflight` (`runs.py:1659`); Web `compileWithDagMl` (`dagml.ts`) | existing |
| **plan** | `pipeline_dsl.schema.json:6` → `execution_plan.schema.json:7` (+ `campaign_spec`, `graph_spec`) | ABI `dagml_pipeline_dsl_execution_plan_build_json` (`dag_ml.h:322`), `dagml_execution_plan_build_json:335`, `dagml_execution_plan_schedule_json:345`; CLI `compile-pipeline-dsl` (`main.rs:898`), `build-pipeline-dsl-plan:925`, `print-execution-schedule:1004` | Python `dagml_bridge.build_dagml_plan` (`dagml_bridge.py:1130`), `compile_with_dagml:1159`; Web `compile_pipeline_dsl_artifact_json` (`dagml-engine.ts:336`) | existing |
| **run** | `execution_plan` + `campaign_spec` + `node_task.schema.json:7` / `node_result.schema.json:7` + `coordinator_data_plan_envelope.schema.json:6` → **`score_set.schema.json:7`** | CLI `run-mock-campaign` (`main.rs:1042`), `run-process-cv-refit-bundle:1378`, `run-process-campaign:1143`; ABI schedule+node task/result | Python `run_via_dagml` (`run_backend.py:212`); Web `execute_campaign_phase_json` (`dagml-engine.ts:182`); Studio `POST /runs` (`runs.py:1749`) | existing |
| **predict** | `node_task`/`node_result` PREDICT phase (`node_runner.py:42` REFIT/PREDICT→`final`) + prediction-cache | ABI `dagml_prediction_cache_payload_f64_tensor_json` (`dag_ml.h:372`), `dagml_prediction_cache_payload_validate_for_bundle_json:371`, `dagml_score_regression_prediction_block_json:361`; **no single CLI `predict` verb** | Python `nirs4all.predict` (`api/predict.py:57`); Studio `api/predict.py`; Web `Engine.predict` (`types.ts:287`) | **`NET-NEW`** as a *unified* verb (assembled; no single dag-ml `predict` entry) |
| **replay** | execution-bundle replay + `parity_oracle.v1.json:2` | ABI `dagml_replay_request_validate_for_bundle_json` (`dag_ml.h:370`), `dagml_replay_execute_json:380`, `dagml_execution_bundle_validate_replay_envelopes_json:369`; CLI `run-mock-replay` (`main.rs:2080`), `run-process-replay:2158`, `run-process-cv-refit-replay:1467` | *(no Studio/Web consumer today)* | dag-ml side existing; **`NET-NEW`** Studio/Web surface |
| **explain** | EXPLAIN is a **phase enum only** (`execution_plan.schema.json:105`, `controller_manifest.schema.json:116`) — **no C-ABI / CLI entry exists** | none (confirmed: zero `dagml_*explain*` symbols in `dag_ml.h`) | Python-only `nirs4all.explain` (`api/explain.py:46`) + SHAP; Studio `api/shap.py:337` | stays **Python-exclusive** (North Star); **`NET-NEW`** runtime wrapper around `nirs4all.explain` |
| **export** | `data_output_provenance.schema.json:7` + `research_provenance_package_profile.v1.json` | ABI `dagml_research_provenance_export_json` (`dag_ml.h:377`); CLI `export-research-provenance` (`main.rs:1994`), `export-open-lineage:2065`, `export-artifact-manifest:1944`, `export-prediction-cache-store:1916` | Python `RunResult.export(".n4a")` (re-fit bridge, `run_backend.py:336`); Studio `.n4a` model export (`runs.py:1498`); Web `.n4a` round-trip | existing — **two targets**: `.n4a` bundle (nirs4all) vs research-provenance/RO-Crate/OpenLineage (dag-ml native) |

**Verb-vs-phase note (for A0):** the RT verb set and the manifest phase set overlap by name but are
different axes. RT `run` internally drives `FIT_CV → SELECT → REFIT`; RT `predict` = `PREDICT`; RT
`explain` = `EXPLAIN`; RT `plan` = `COMPILE/PLAN`. `inspect`, `validate`, `replay`, `export` have **no
phase** — they are coordinator/IO verbs. This separation must be stated once so `CAP` and `RT` do not
collide on the word "phase".

**Generators / synthesis:** `nirs4all.generate` (`api/generate.py`) is a Python-exclusive verb outside
the 8 (synthesis); listed here only so A0 does not expect it in the portable surface.

---

## RT-002 — shared request/response schema (the core of LOCK-RT)

### The reconciliation problem (Studio REST vs Web WASM)

Today the **request** side is already near-aligned (both submit a pipeline DSL + dataset ref + cv/seed),
but the **result** side has **two divergent projections of the same underlying dag-ml output**:

**Form A — Studio REST `aggregated-predictions`** (`nirs4all-studio/api/aggregated_predictions.py`):
a **flat, columnar, store-shaped** model — one row per *chain* (= run × variant), metrics spread into
**named scalar columns**, predictions fetched **separately** as parallel arrays. Multi-source /
multi-target / aggregation aware.
- `ChainSummary` (`:97`): `run_id, pipeline_id, chain_id, model_class, preprocessings, branch_path,
  source_index, model_step_idx, metric, task_type, dataset_name, **cv_val_score, cv_test_score,
  cv_train_score, cv_fold_count, cv_scores**, **final_test_score, final_train_score, final_scores**,
  **final_agg_test_score** (repetition aggregation), `synthetic_refit`, `is_refit_only`, `fold_artifacts`.
- `PartitionPrediction` (`:150`): drill-down row `prediction_id, chain_id, fold_id, partition,
  val_score/test_score/train_score, source_index, target_index, target_name, …`.
- `PredictionArraysResponse` (`:222`): `y_true, y_pred, y_proba, sample_indices, weights, n_samples,
  source/target index`.

**Form B — Web WASM `RunResult`** (`nirs4all-web/studio-lite/src/engine/types.ts:235`): a **nested,
per-run object**, metrics grouped by **ScoreNode**, predictions **inline**, carries the **fitted model**.
Single-target.
- `RunResult` (`:235`): `id, pipelineName, taskType, targetName, **refit: ScoreNode**, **cv?:
  ScoreNode**, **folds: ScoreNode[]**, seed, engine, scoreMetric, variants[], lineage, **model:
  FittedPipeline**`.
- `ScoreNode` (`:215`): `{ id, name, kind: 'refit'|'cv'|'fold', metrics: Metrics, predictions:
  PredRow[], confusion?, status }`.
- `PredRow` (`:202`): `{ sampleId, actual, predicted, residual, actualLabel?, predictedLabel? }`.

Divergence in one sentence: **Studio is a flat multi-target/aggregation-aware pivot pulled from the
SQLite/Parquet store; Web is a nested single-target object that inlines predictions and the fitted
model — both are lossy projections of the same dag-ml ScoreSet.**

### The anchor already exists: dag-ml `ScoreSet`

`dag-ml/docs/contracts/score_set.schema.json:7` — `{ schema_version, plan_id, selection_metric?,
reports[] }`, where each **report** (`:18`) is the common atomic unit carrying every dimension both
forms need:

```
report = { prediction_id?, variant_id?, variant_label?, producer_node,
           partition ∈ {train, validation, test, final},   # :27
           fold_id?, level ∈ {observation, sample, target, group},  # :29
           row_count, target_width, target_names[], metrics: {name: number} }  # :33
```

Both forms are deterministic group-bys of `reports[]`:

| ScoreSet report selector | → Studio `ChainSummary` column | → Web `ScoreNode` |
|---|---|---|
| `partition=validation, fold_id=null` (OOF concat) | `cv_val_score` | `cv.metrics` |
| `partition=validation, fold_id=k` | `cv_scores[k]` | `folds[k].metrics` |
| `partition=test` (at CV) | `cv_test_score` | *(dropped — Web has none)* |
| `partition=final, level=observation/sample` | `final_test_score` / `final_train_score` | `refit.metrics` |
| `partition=final, level=sample/group` (repetition agg) | `final_agg_test_score` | *(dropped — Web single-level)* |

**Existence proof:** `native_results_adapter.py` ALREADY performs the `ScoreSet → ChainSummary`
projection (`native_results_adapter.py:1-55`; surrogate ids `chain_id = "{run_id}::{config_name}"` `:34`,
`pipeline_id = run_id` `:40`), reading the native triple `manifest.json + score_set.json +
predictions.parquet` (`:26-28`) through the library reader only. The Web `invoke()` controller builds
the same `ScoreSet`-equivalent `NodeResult` in-WASM (`dagml-engine.ts:436-482`) and nests it into
`RunResult`. So **both projections are already written; they were just never unified.**

### Proposed unified envelope — `RtResult` (`NET-NEW` wrapper, zero new dag-ml fields)

Anchor the shared result on the dag-ml **native triple** and define Form A and Form B as **views**:

```
RtResult v1 {                                   # NET-NEW envelope; all fields below already exist
  schema_version, run_id, plan_id,              # ← score_set.plan_id (score_set.schema.json:10)
  selection,                                    # ← selection_decision.schema.json:7 (winner + ranked)
  reports[],                                    # ← VERBATIM score_set.reports[] (the join key)
  predictions[] { level, partition, fold_id, variant_id, sample_id, target_index,
                  y_true, y_pred, y_proba? },   # ← predictions.parquet rows / NodeResult predictions
  manifest {                                    # ← native_results manifest.json
     engine,                                    # 'local-python' | 'wasm-local' | 'cluster' (see RT-002 req)
     fingerprints,                              # ← coordinator_data_plan_envelope {schema,plan,relation}
     lineage, capabilities, portable_level },   # capabilities/portable_level = LOCK-CAP (referenced)
  artifacts?[]                                  # ← fitted_adapter_ref / .n4a handle
}
```

- **Studio `ChainSummary`** = `RtResult` pivoted `group_by(run_id, variant_id)` with `partition×metric`
  flattened — i.e. exactly today's `native_results_adapter` mapping, generalized.
- **Web `RunResult`** = `RtResult` nested `group_by(kind)` with `predictions[]` joined by `sample_id`
  and the `model` handle attached — i.e. today's `dagml-engine` assembly, generalized.

No dag-ml contract changes are required: `RtResult` is a thin envelope binding `score_set` +
`predictions` + `manifest` + `selection_decision` that **already travel together** in the native
results dir. The `NET-NEW` work is the wrapper schema + the two (lossless-superset) view adapters.

### Request side (already converging)

- Studio: `CreateRunRequest{config: ExperimentConfig}` (`runs.py:249`/`212`) — `dataset_ids,
  pipeline_ids|inline_pipeline(s), execution_backend, cv_folds, cv_strategy, test_size, random_state`;
  `QuickRunRequest` (`:230`).
- Web: `Engine.run(ds: MaterializedDataset, dsl: PipelineDSL, opts)` (`types.ts:286`).
- Both reduce to: **`{ pipeline_dsl (pipeline_dsl.schema.json:6), dataset_ref, cv{folds,seed},
  execution_backend, options }`**. Proposed unified `RtRunRequest` = that tuple (the DSL is the
  *existing* `pipeline_dsl` compat contract; only the envelope is `NET-NEW`).
- **Execution-backend advertisement already exists** and should back the RT `inspect`/capabilities
  surface: `GET /runs/execution-backends` → `ExecutionDriverCapabilitiesResponse{default_backend,
  backends[]}` (`runs.py:1543`/`:317`), where each `ExecutionDriverCapability` =
  `{backend ∈ local-python|cluster|wasm-local, label, available, mode, supports_progress,
  supports_cancellation, metadata}` (`execution_driver.py:13,21`). `wasm-local` and `cluster` are
  **typed but unavailable** today (`execution_driver.py:317,304`) — the RT contract is what makes
  `wasm-local` (Web) and `local-python` (Studio) emit the **same** `RtResult`.

---

## RT-003 — error model + unsupported diagnostics (links `CAP-004`)

Three **disjoint** error shapes exist today and must converge into one wire envelope:

1. **Python (dag-ml backend)** — `errors.py`: `DagMlUnsupported(NotImplementedError)` (`:30`, shape not
   covered → cause), `_OperatorLoweringUnsupported(DagMlUnsupported)` (`:44`),
   `DagMlUnavailable(RuntimeError)` (`:56`, neither mechanism installed); kind constants
   `ERROR_KIND_UNSUPPORTED`/`ERROR_KIND_GENERIC` (`:26-27`). These are the catchable signals that drive
   the legacy fallback (`api/run.py:606-618`). `_reject_unsupported_run_options` (`run_backend.py:126`)
   raises `DagMlUnsupported` for `refit≠True / session / cache / project / workspace runner_kwargs`.
2. **Studio REST** — preflight `{ ready: bool, issues: [{ type, message, details }] }` with
   `type ∈ {env_mismatch, not_found, no_workspace, load_error, missing_module}` (`runs.py:1659`); and
   driver refusal `ExecutionDriverCapability{available:false, metadata{reason:'driver_unavailable',
   message}}` (`execution_driver.py:304-335`).
3. **Web WASM** — `guard.ts` refuses an oversized AOM/POP screen; `hasUnsupportedGenerator`
   (`dagml-engine.ts:8`); `DagMlEngine` silently **falls back** to direct `runPipeline` on any error.

**Proposed unified `RtError` (`NET-NEW`):**
`{ verb, code, cause ∈ {unsupported_shape, unsupported_capability, unavailable_backend,
   invalid_request, runtime_error}, message, mitigation, unsupported_capability?, portable_level? }`.
- `cause`/`unsupported_capability`/`portable_level`/`mitigation` **vocabulary is owned by `CAP-004`**
  (normalized `unsupported` diagnostics with cause + mitigation, roadmap:195) and `CAP-002` (portability
  levels). RT-003 only standardizes the **envelope** that carries them across REST/WASM/CLI; it does
  **not** invent the vocabulary (`DEC-RT-001`). The mapping `DagMlUnsupported → cause:unsupported_shape`,
  `DagMlUnavailable → cause:unavailable_backend`, preflight `missing_module → cause:unsupported_capability`
  is the migration table.
- **Decision needed (gates `CAP-004`):** the Web "silent fallback" and the Python "warn+fallback" must
  become an **explicit `RtError` with `mitigation`** at the RT boundary, or the unified contract leaks
  divergent UX. Flagged, not blocking.

---

## Binding points

### RT-PY-001 — the in-tree Python runtime is the de-facto binding (it already exists)

`nirs4all/nirs4all/pipeline/dagml/` IS today's Python runtime over dag-ml. Dispatch from
`api/run.py:570` (`engine=="dag-ml" → run_via_dagml`).
- **Entry:** `run_via_dagml(pipeline, dataset, *, name, random_state, refit, project, session, cache,
  runner_kwargs, results_path) → RunResult` (`run_backend.py:212`).
- **Two mechanisms** (router cascade `in_process_runner.run_cv_refit_bundle_router:266`):
  **Mechanism B (default, in-process)** = PyO3 ext **`dag_ml._dag_ml`**; **Mechanism A (fallback,
  subprocess)** = **`dag-ml-cli`** at `_DEFAULT_CLI` (`run_backend.py:74`) driven through the **process
  adapter** (`process_adapter.py:97` `run_jsonl_loop`). Preflight `preflight_dagml_backend`
  (`run_backend.py:182`) → `DagMlUnavailable` iff both missing.
- **NodeTask/NodeResult host callback:** `run_node(task, …) → dict` (`node_runner.py:672`) consumes a
  `NodeTask` dict, returns a schema-complete `NodeResult` dict (`_build_result:264`); phase→partition
  `_PREDICTION_PARTITION` (`:42`). The JSONL frame loop the CLI drives = `process_adapter.run_jsonl_loop`.
- **Data envelope:** `envelope.build_envelope(...) → coordinator_data_plan_envelope`
  (`envelope.py:297`, delegates `dag_ml_data.build_coordinator_data_plan_envelope:352`) + `build_fold_set`
  (`:373`) + `sample_relations` (`:215`).
- **Native results / RtResult anchor:** `native_results.write_native_results(...)`
  (`native_results.py:311`) writes `score_set.json` (`:335`) + `predictions.parquet` (`:350`) +
  `manifest.json` (`:358`); `read_native_results` (`:363`) is the only decoder.
  `result._scores_to_run_result` (`result.py:293`) projects ScoreSet → `RunResult` and stashes the raw
  ScoreSet on `result._dagml_score_set` (`:596`).
- **Hardening note (L5):** `run_paths.py` is 81 KB of **per-shape** `_run_*` scorers
  (`_run_native_generation:76`, `_run_repetition:363`, `_run_rep_fusion:462`, `_run_augmentation:780`,
  `_run_separation_branch:872`, `_run_by_source_branch:1037`, `_run_duplication_branch:1119`,
  `_run_stacking_branch:1198`). These are the Python-shim generator/variant/branch expansions the North
  Star wants migrated **down into dag-ml/nirs4all-methods** — RT must not freeze them as the contract;
  it targets the **ScoreSet/NodeResult** boundary, which is stable regardless of where expansion runs.

### RT-WASM-001 — the Web engine is the second binding (already drives dag-ml in-WASM)

`nirs4all-web/studio-lite/src/engine/`. `Engine` contract = `types.ts:284` (`run:286`, `predict:287`).
- `DagMlEngine.run` (`dagml-engine.ts:182`): compile DSL → artifact via
  **`compile_pipeline_dsl_artifact_json`** (`:336`), build `FoldSet`, run **`execute_campaign_phase_json`**
  (FIT_CV) with a synchronous JS controller `invoke()` (`:409`) that consumes `NodeTask` JSON and returns
  `NodeResult` JSON (`predictions / observation_predictions / aggregated_predictions / lineage`,
  `:436-482`). The model controller manifest (`modelManifest():28`) advertises
  `supported_phases:['FIT_CV']` (`:34`) and the `capabilities[...]` array (`:38`) — **the same enum
  LOCK-CAP owns**.
- Data layer: `dag-ml-data` WASM `WasmInMemoryProvider` → coordinator-data-plan fingerprints
  `{schema, plan, relation}` recorded on lineage `dataProvider` (`dagml-engine.ts:228-239`).
- WASM exports live in `dag-ml/crates/dag-ml-wasm` (`execute_campaign_phase_json`,
  `compile_pipeline_dsl_artifact_json`). RT-WASM-001 = this engine emitting `RtResult` instead of the
  bespoke `RunResult`.

### RT-CLI-001 — already present as `dag-ml-cli` + the nirs4all process adapter

`dag-ml-cli` exposes **36 subcommands** (`crates/dag-ml-cli/src/main.rs:219` enum, dispatch `:863`),
kebab-case. RT verbs map to families: validate→`validate-*` (`:864…`), plan→`compile-pipeline-dsl:898`
/`build-pipeline-dsl-plan:925`/`print-execution-schedule:1004`, run→`run-mock-*`/`run-process-*`
(`:1042…`), replay→`run-mock-replay:2080`/`run-process-replay:2158`, export→`export-research-provenance:1994`
/`export-open-lineage:2065`. nirs4all already uses it as Mechanism A through
`process_adapter_description.schema.json:7` (handshake) + `process_adapter_frame.schema.json:6`
(`init|task|close|ack|result|error`). RT-CLI-001 is therefore **smoke/automation packaging** over an
existing surface, not a new binding. **`inspect` / `explain` / `predict` have no dedicated CLI verb**
(see RT-001) — RT-CLI exposes them as `NET-NEW` thin wrappers (read-plan/score-regression/cache, and
explain stays Python-only).

---

## Dependencies (note, do not block — `DEC-RT-001`)

- **`LOCK-CAP` (CAP-SPEC, in_progress).** RT **references** the capability vocabulary; it does not
  define it. Source of truth = `controller_manifest.schema.json`: `capabilities` enum (`:149-171`:
  `deterministic, thread_safe, process_safe, needs_python_gil, emits_predictions,
  consumes_oof_predictions, emits_artifacts, stateful, emits_relation, uses_core_rng, shape_changing,
  generates_data, generates_model, expands_variants, aggregates_predictions, supports_sample_weights,
  supports_row_resampling, supports_backend_loss_weights, supports_missing_masks`), `fit_scope` (`:212`),
  `rng_policy` (`:215`), `artifact_policy` (`:223`), `supported_phases` (`:116`). RT consumes these in
  `RtResult.manifest.capabilities`, the `inspect` verb, and `RtError.unsupported_capability`. **Open
  fields `portable_level` (CAP-002) and the `unsupported` cause/mitigation vocab (CAP-004) are owned by
  CAP** — RT carries them as opaque referenced fields. RT can proceed against the live Web manifest
  (`dagml-engine.ts:38`) and the schema enum as the interim vocabulary.
- **`DEC-CTRL-001` (accepted).** `ControllerManifest` is canonical, and the **`OperatorController →
  ControllerManifest` adapter (B1) does not exist yet**: today `dagml_bridge.controller_manifests()`
  **hand-builds 5 static manifests** (`transform / y_transform / model / merge_concat / meta_model`,
  `dagml_bridge.py:1008`, "control-plane declarations only" `:1013`). *(The sync-board reference
  "`dagml_bridge.py:1070` OperatorController→manifest comment" is imprecise — that exact comment does
  not exist; `:1069-1071` is an `emits_predictions` port-validation note. The architectural fact stands:
  manifests are static, no live-registry adapter.)* RT's `inspect`/`validate` verbs surface controller
  manifests/capabilities, so a complete capability ledger depends on B1 landing; until then RT reads the
  static set. **Not blocking** — RT targets the NodeResult/ScoreSet boundary, which is stable whether
  manifests are static or registry-derived.

---

## Proposed `LOCK-RT` content (for A0 to sign)

> **`LOCK-RT` — Runtime API commune.** Decision source `DEC-RT-001` (accepted). Owner RT-SPEC.
>
> 1. **Eight verbs** `inspect, validate, plan, run, predict, replay, explain, export` are the runtime
>    product surface, **distinct from** dag-ml controller phases. Each verb is a **surface over existing
>    dag-ml contracts** per the RT-001 table; **no new dag-ml contract is created**. Verbs without a
>    native dag-ml entry (`inspect`, `predict`-as-verb, `replay` for Studio/Web, `explain`) are
>    **`NET-NEW` thin wrappers**, not new engines.
> 2. **One result envelope `RtResult v1` (`NET-NEW`)** anchored on the dag-ml **ScoreSet**
>    (`score_set.schema.json:7`) + `predictions` + `manifest` + `selection_decision` (the native triple
>    already co-emitted by `native_results.write_native_results`). **Studio `aggregated-predictions` and
>    Web `RunResult` become deterministic VIEWS** of `RtResult` (pivot vs nest); neither is the contract.
>    `RtResult.reports[]` is verbatim `ScoreSet.reports[]` (the `partition/level/fold_id/variant_id/target`
>    join key).
> 3. **One request envelope `RtRunRequest v1` (`NET-NEW`)** = `{ pipeline_dsl (existing
>    pipeline_dsl.schema.json), dataset_ref, cv, execution_backend, options }`; `execution_backend`
>    drawn from the existing `ExecutionDriverCapability` taxonomy (`local-python | wasm-local | cluster`).
> 4. **One error envelope `RtError v1` (`NET-NEW`)** carrying `cause/mitigation/unsupported_capability/
>    portable_level` whose **vocabulary is owned by `CAP-004`/`CAP-002`** (referenced, not redefined).
>    Silent fallbacks (Web, Python-warn) surface as explicit `RtError`.
> 5. **Capability/portability fields are referenced from `LOCK-CAP`**, controller manifests from
>    `DEC-CTRL-001`. RT freezes only the **envelopes**, not those vocabularies.
> 6. **Watchlist surface** `Runtime request/response schemas` (sync board) is bound to this lock.
> 7. **Interim authority:** RT-PY-001 = `nirs4all/pipeline/dagml` (`run_via_dagml`), RT-WASM-001 =
>    `studio-lite/src/engine` (`DagMlEngine`), RT-CLI-001 = `dag-ml-cli` + process adapter — all three
>    already speak NodeTask/NodeResult + ScoreSet; LOCK-RT makes them emit the same `RtResult`.

---

## Open questions + gates

1. **`RtResult` home repo** — does the envelope schema live in `nirs4all-ecosystem` (spec only) with
   adapters per runtime, or as a new shared contract? `DEC-DESIGN-001`/`ARB-013` topology
   (lite→core) is unresolved; RT can ship the spec in ecosystem and defer the package home. **Gate: GOV.**
2. **Multi-target / aggregation parity** — Web `RunResult` is single-target and drops `level=group`/CV
   `test` partition; Studio keeps them. `RtResult` must be the **superset** (full `reports[]`); confirm
   Web may render a subset without the contract claiming Web is "complete". **Gate: CAP-002 portable_level.**
3. **Silent-fallback policy** — must Web/Python convert fallback into an explicit `RtError`? Affects UX
   contract and the `unsupported` ledger. **Gate: CAP-004.**
4. **`predict`/`replay`/`inspect` native verbs** — accept them as `NET-NEW` assembled wrappers for V1
   (no new dag-ml CLI/ABI), or request dag-ml add first-class `predict`/`inspect` entries later? RT
   recommends assembled-wrappers for V1. **Gate: L5 dag-ml hardening.**
5. **Controller capability ledger** — `inspect` completeness depends on the `OperatorController →
   ControllerManifest` B1 adapter (`DEC-CTRL-001`), absent today (static 5-manifest set). RT reads the
   static set interim. **Gate: CTRL B1.**
6. **`.n4a` vs research-provenance export** — `export` has two targets; RT must declare whether `RtResult`
   export defaults to `.n4a` (Python re-fit bridge) or research-provenance (dag-ml native). **Gate:
   LOCK-DROP** (native `.n4a` export is a cutover criterion).

---

### Evidence (heads, read-only; no code/tests/sync-board modified)
dag-ml contracts `dag-ml/docs/contracts/*.schema.json`; `dag-ml/crates/dag-ml-cli/src/main.rs`;
`dag-ml/crates/dag-ml-capi/include/dag_ml.h`; `nirs4all/nirs4all/api/run.py` +
`nirs4all/nirs4all/pipeline/dagml/{run_backend,detect,envelope,node_runner,process_adapter,errors,
native_results,result,run_paths}.py` + `nirs4all/nirs4all/pipeline/dagml_bridge.py`;
`nirs4all-studio/api/{runs,execution_driver,aggregated_predictions,native_results_adapter}.py`;
`nirs4all-web/studio-lite/src/engine/{types,dagml-engine}.ts`. Only this file was written.
