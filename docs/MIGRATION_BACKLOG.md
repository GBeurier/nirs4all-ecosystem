# nirs4all → Rust ecosystem (dag-ml / dag-ml-data / nirs4all-methods / nirs4all-io / nirs4all-formats) — Backend Replacement Backlog

**Date:** 2026-06-14
**Status:** DRAFT v2 — Codex xhigh review incorporated
**Audience:** nirs4all maintainer + reviewing model (Codex)
**Companion:** [`MIGRATION_BACKLOG_CODEX_REVIEW.md`](MIGRATION_BACKLOG_CODEX_REVIEW.md) — the full Codex xhigh review (verdict, findings, evidence). Its corrections are folded into this document; see **§0.1** and **§16**.

---

## 0. Front matter

### 0.1 Revision note — what the Codex xhigh review changed (read this first)

A Codex review (`gpt-5.5`, `model_reasoning_effort=xhigh`) read all five Rust repos read-only and verified this document's load-bearing claims against source. **One claim was a keystone error and is corrected throughout; several others were sharpened.** Independently re-verified, then folded in:

| # | What the draft said | What the source actually says (verified) | Fixed in |
|---|---|---|---|
| **1 (CRITICAL)** | The `dag-ml-py` **pyo3 in-process controller vtable** is the default transport and "the only path" for sklearn-shaped operators + zero-copy buffers. | **`dag-ml-py` is JSON-contracts-only** — *"validates, compiles and plans serialized JSON contracts, but does not execute host controllers or own data buffers"* (`dag-ml/crates/dag-ml-py/src/lib.rs:1-5`; exports are validate/compile/plan only, `:56-202`). The C-ABI controller vtable **"is not the path for Python/R hosts"**; the **JSONL process adapter is the only stable cross-language transport**, and **native PyO3/C-ABI controller wrappers are explicitly OUT OF SCOPE** today (`dag-ml/docs/HOST_ADAPTER_BACKLOG.md:12-17, 85-90`). | §3.3 (rewritten), §3.7, TL;DR, §4.1, §6, §8 (R1/R2/R10/R14), §10, §13, §15 |
| 2 | `.n4a` round-trip "blocked-unknown" on n4m model pickleability. | **The pattern already ships:** `_Pls4allModelEstimator` persists the `.n4a` `_bundle_` bytes and drops `_model_handle_`/`_model_ctx_` from `__getstate__` (`nirs4all-methods/bindings/python_pls4all/src/pls4all/sklearn/_base.py:158-176`). Risk **downgraded**; E10 is a known wrapper contract, not a spike. | §8/R4, §13/S3, §16, A8 |
| 3 | "Every dag-ml production execution path is smoke/mock." | **Stale** — sklearn-production + prospectr + mdatools JSONL adapters are *shipped* (`dag-ml/docs/STATUS.md:650-685`); tuner execution and adaptive-search lowering are what's still smoke/missing. | §4.1 |
| 4 | nirs4all-io "routes only vendor extensions". | **Conflated surfaces** — the **Python** MVP reads numpy/parquet/Excel/CSV/vendor (`loaders.py:201-276`); only the **Rust facade** is CSV-only (`loaders.rs:57-64`). | §4.1, §10/E3 |
| 5 | "57 import sites across ~28 files"; "188 catalog methods"; symbol `n4m_domain_adaptation_di_pls`; kennard symbol. | Studio count needs a reproducible definition (Codex: 28 API files / 112 occurrences). "**188 ABI-mapped** catalog methods" (209 YAML files exist). Exact names: `..._di_pls_fit`; `n4m_model_selection_kennard_stone_*`. | §5, §7.1 |

**New scope the review surfaced** (added to risk register, epics, and detailed in **§16**): an **FFI/ABI safety contract** epic (ownership/lifetimes/panic-propagation/thread-safety/ABI-skew/GIL policy) **before** the integration epics; a **Studio run-lifecycle** parity contract (JobManager WebSocket jobs, cooperative cancel, retry, progress); an explicit **rollback strategy** (keep `legacy` runnable ≥1 release — deleting it while the studio reads private SQL removes the rollback path); a **Phase-0 licensing gate** (libn4m is dual CeCILL/AGPL **+ commercial**; dag-ml/data CeCILL/AGPL); an **`n_jobs`→dag-ml scheduler** compatibility map; a **dtype/tolerance ledger**; and a **process-adapter security model**.

**Net effect:** the *data* and *contract* analysis stands, but the **controller-execution transport is re-grounded on the JSONL process adapter** (or a net-new in-process Python controller runtime *proposed to and built by the dag-ml owners* — not a capability that exists today, and one that contradicts dag-ml's stated design). This raises the effort and **moves the linchpin earlier** — from M2 (first native run) to **M0: decide and prove the controller-execution transport at all**.

### Executive summary

This document is the complete migration backlog for replacing the entire `nirs4all` Python backend with the Rust ecosystem — `dag-ml` (the reproducible/OOF-leakage-safe ML coordinator), `dag-ml-data` (typed sample-aligned data contracts), `nirs4all-methods`/`libn4m` (the portable C++17/C-ABI PLS+NIRS numerical engine and its `n4m` Python binding), `nirs4all-io` (dataset assembly), and `nirs4all-formats` (Rust vendor-format readers). The finding, grounded in a full read of all five Rust libraries and the `nirs4all` package, is that **the numerical core is not the bottleneck** — `libn4m` already has parity-fixture-gated coverage for ~85–90% of nirs4all's classical operator surface (every PLS variant, all preprocessing/baselines/wavelets, splitters, filters, feature selection, AOM-PLS/POP-PLS, augmentation, regression metrics). The cutover lives or dies instead on three things the Rust stack cannot yet do end-to-end: (1) getting a real wide-NIRS feature matrix into a host controller per fold on a *runnable* path; (2) running the KEEP-listed NN backends (torch/TF/JAX) and `shap` through dag-ml as host controllers; and (3) preserving the **STABLE 0.9.x contracts** (`run/predict/explain/retrain/session/generate`, `RunResult`/`PredictResult`/`ExplainResult`, the SQLite+Parquet workspace, the `.n4a` bundle) that the `nirs4all-studio` webapp consumes — including via raw SQL against `store.sqlite`. The new `nirs4all` becomes a **thin Python host shell** over the Rust engines: it owns the public API + Result objects, the NN/AutoML operators, the optuna outer driver, the shap explainer, the operator shims, and the storage/bundle compatibility facades — and nothing else. Everything numerical, every orchestration phase, all data assembly, and all file parsing moves to Rust.

### TL;DR — effort & verdict

> **Total estimate (revised after review):** **~110–150 person-weeks**, central estimate **~125 pw**. (Bottom-up: ~81 pw host migration + ~20–28 pw net-new lib-side gap work + the review-surfaced scope: FFI/ABI safety, the controller-transport build-or-adopt, Studio run-lifecycle parity, packaging/CI, licensing, rollback ≈ **+15–25 pw**.) The earlier ~105 pw figure held **only** if an in-process pyo3 controller path existed — it does not (§0.1/§3.3), so the realistic floor moved up. **~80 pw is achievable only** if the team adopts the existing **JSONL process adapter** as-is and accepts its serialization envelope; **~150 pw** if a net-new in-process Python controller runtime must be built in dag-ml. Calendar **~26–30 weeks** wall-clock, 5 parallel tracks (≈5–7 engineers).
>
> **Single biggest risk (R1, re-grounded):** **There is no runnable cross-language path that gets a wide NIRS feature matrix into a *Python* host controller per fold.** `dag-ml-py` is JSON-contract-only and **does not execute host controllers or own buffers**; dag-ml's own design declares the **JSONL process adapter the only stable cross-language transport** and **out-of-scopes native PyO3/C-ABI controller wrappers** (`HOST_ADAPTER_BACKLOG.md:12-17, 85-90`). So before *anything real runs*, the team must **decide the transport**: (a) adopt JSONL + engineer around per-fold serialization (task batching via `accepts_task_batch`, keep wide X host-side, persistent workers), or (b) sponsor a net-new in-process Python controller runtime *in dag-ml* (contradicts its stated scope — needs dag-ml-owner buy-in). Tied with it: the **`.n4a` + SQLite/Parquet workspace contract** is read by the studio with **raw SQL**, and "remove pyarrow" *contradicts* preserving the Parquet workspace (resolved: keep pyarrow storage-only, §1.3).
>
> **Recommended go/no-go gates (M0 — before committing the full cutover):**
> - **S0 (NEW, gate-zero) — controller-transport ADR + proof.** Decide JSONL-adapter-as-is vs build in-process Python runtime in dag-ml. Then prove the chosen path runs *one real* FIT_CV node on a real NIRS X. *(retires R1/R2; supersedes the old "S1 via dag-ml-py")*
> - **S1 — borrowed-view provider.** Wire `dagmldata_inmemory_provider_new_with_f64_feature_views` into the ctypes shim (today JSON-only, `_provider.py:151-158`; the C funcs exist unused at `dag_ml_data.h:273-275`) and pass a NumPy f64 buffer with **zero `_json` calls**. *(prerequisite for any low-latency transport)*
> - **S2 — one torch model trains+predicts through the chosen transport**, identical loss curve, warm REFIT→PREDICT stickiness. *(retires R2)*
> - **S3 — `.n4a` round-trip over a dag-ml bundle** using the **already-shipped** bundle-byte wrapper pattern (`pls4all/sklearn/_base.py:158-176`): persist `_bundle_`, drop handles from `__getstate__`. Confirm v1 stays non-breaking. *(retires R4 — now low risk)*
> - **S4 — RNG-kind audit** (PCG64 vs NUMPY_MT) + the four missing PLS parity fixtures green before deleting `trendfitter`/`ikpls`/`pyopls`. *(retires R5/R6)*
> - **S-FFI — FFI/ABI safety contract** (ownership/lifetimes/panic-propagation across pyo3+ctypes+C-ABI, `Send+Sync` scheduler requirement, three independent ABI versions) **before** the integration epics.
>
> **Verdict (revised):** dag-ml's *control* core is production-architecture-grade and a genuine *superset* of nirs4all's orchestration, and **shipped JSONL adapters (sklearn/prospectr/mdatools) prove the host-controller path works** — but **no path executes a Python NN/feature-heavy controller end-to-end today**, and the workspace/`.n4a` shim is net-new. Proceed via **strangler migration with an always-green parity gate**, not big-bang. **The linchpin is M0 — decide and prove the controller-execution transport** — *not* M2; until M0 is green, dag-ml can only *validate* nirs4all pipelines as conformance tests, not *run* them.

---

## 1. Goal & non-goals

### 1.1 The decree (precise keep/cut/replace)

The objective is to replace the **entire** `nirs4all` Python backend with the Rust ecosystem. The disposition of every third-party dependency is fixed as follows.

**KEEP (do NOT remove) — genuinely have no Rust home:**

| Dependency | Why retained |
|---|---|
| `torch`, `tensorflow`, `jax`/`flax` | The NN model backends. `libn4m` is a PLS/NIRS engine, not a deep-learning runtime. |
| `optuna` | Hyperparameter search. dag-ml has no adaptive-sweep machinery (FACT, Inventory B/F). |
| `shap` | Explainability. dag-ml's EXPLAIN phase has no execution path (FACT, Inventory B). |

**KEEP ONLY A FEW FUNCTIONS — shrink to the named survivors:**

| Dependency | Survivors (everything else CUT) |
|---|---|
| `scikit-learn` | `sklearn.base` (BaseEstimator/TransformerMixin/RegressorMixin/ClassifierMixin/clone — the operator *protocol*); `sklearn.metrics` **classification only**; `sklearn.preprocessing` **LabelEncoder/OneHotEncoder/FunctionTransformer** (target/metadata encoding); `sklearn.ensemble` **RandomForest/GradientBoosting/Stacking/Voting** (user host models); `sklearn.utils.check_random_state`. |
| `scipy` | `scipy.stats` (pearsonr/spearmanr/ks_2samp/wasserstein/chi2/entropy/median_abs_deviation); `scipy.special` (voigt_profile/gammaln); and `scipy.signal`/`ndimage`/`optimize`/`interpolate`/`integrate` **used only inside `synthesis/`** (offline data generation). |

**REMOVE / REPLACE entirely (now provided by the Rust libs):**

| Dependency (file count) | Replaced by |
|---|---|
| `ikpls` (4), `pyopls` (2), `trendfitter` (1) | `libn4m` PLS variants |
| `PyWavelets`/pywt (3), `pybaselines` (3), `kennard-stone` (3) | `libn4m` signal/baseline/splitting |
| `polars` (22), `pyarrow` (4), `h5py` (3) | `dag-ml` + `dag-ml-data` + `nirs4all-io` + `nirs4all-formats` |
| `joblib` (23) | dag-ml orchestration (parallel) + handle lifecycle (serialization) |

### 1.2 Non-goals

- **No reimplementation of Rust-owned logic in Python.** Per dag-ml's `CLAUDE.md` and the cross-cutting ecosystem rules, boundaries are sacred: the host never re-derives OOF joins, fold identity, leakage enforcement, fusion/collation, or vendor parsing. Where a capability is missing in a lib, it is added in that lib, not shimmed in Python.
- **No new numerical algorithms in the Python host.** The host glue marshals; it does not compute (except the explicitly KEEP-listed scipy.stats/special and classification metrics, and the self-contained `synthesis/` subsystem).
- **No silent contract breaks.** Any change to the 0.9.x public API, the Result-object shapes, the workspace SQLite+Parquet schema, or the `.n4a` bundle format is a **major-version event** and must be called out explicitly (see §7, §8, §14).
- **No big-bang cutover.** The migration is strangler-style with per-operator parity gating (§9).

### 1.3 One documented exception to the removal decree

**`pyarrow` is retained as a storage-only dependency.** It is the only way to write the **frozen workspace Parquet layout** (`arrays/<ds>.parquet`, `*.meta.parquet`) that the studio reads directly via `pd.read_parquet`. The storage layer is polars+pyarrow-coupled (`pipeline/storage/array_store.py:35-37`, `workspace_store.py:42`); **`polars` is removed** by rewriting array-store frames to pyarrow/numpy, but dropping `pyarrow` too would require dag-ml-data to emit byte-identical Parquet through the facade, which it does not. This contradiction between "remove pyarrow" and "preserve the Parquet workspace contract" is resolved in favor of the contract (see §3.4, §7, §8/R3).

---

## 2. Current state: nirs4all backend inventory & dependency footprint

### 2.1 Measured removable-dependency footprint (FACT)

| Dependency | Import sites | Disposition |
|---|---|---|
| `sklearn` (total) | 147 files | Shrink to survivors (§1.1) |
| — `sklearn.base` | 75 | KEEP (operator protocol), shrink subclasses |
| — `sklearn.utils.validation` | 27 | CUT with their estimators |
| — `sklearn.preprocessing` | 26 | Mostly CUT; keep label/onehot/function encoders |
| — `sklearn.model_selection` | 23 | CUT (splitters→libn4m); keep one protocol boundary |
| — `sklearn.cross_decomposition` | 16 | CUT (→libn4m PLS) |
| — `sklearn.decomposition` | 15 | CUT (→libn4m PCA/SVD) |
| — `sklearn.metrics` | 14 | SPLIT: regression→libn4m, classification KEEP |
| — `sklearn.linear_model` | 7 | CUT (numeric); keep bare logistic head if needed |
| — `sklearn.ensemble` | 7 | KEEP (trees/forests/boosting are user models) |
| — `sklearn.neighbors` | 5 | CUT (LWPLS); keep diagnostics |
| — `sklearn.pipeline` | 3 | KEEP (thin) |
| `scipy` (total) | 45 files | Shrink to stats/special + synthesis-only |
| `polars` | 22 | REMOVE (→pyarrow/numpy + dag-ml-data) |
| `joblib` | 23 | NARROW to blob-only; remove parallelism |
| `pyarrow` | 4 | RETAIN storage-only (the documented exception) |
| `ikpls` | 4 | REMOVE (→libn4m) |
| `pywt` | 3 | REMOVE (→libn4m wavelet) |
| `pybaselines` | 3 | REMOVE (→libn4m baseline) |
| `h5py` | 3 | REMOVE (→nirs4all-formats) |
| `pyopls` | 2 | REMOVE (→libn4m OPLS) |
| `trendfitter` | 1 | REMOVE (→libn4m DiPLS, after parity pin) |

### 2.2 Subpackage inventory & disposition (condensed from Inventory A)

Disposition codes: **→lib** = moves to the named Rust lib · **KEEP-thin-host** = stays Python as glue/contract · **KEEP-NN/shap/optuna** = explicitly retained backend · **SPLIT** = parts move, parts stay · **DELETE** = removed entirely.

| Subpackage | Key files (size) | Removable-dep footprint | Disposition |
|---|---|---|---|
| `api/` | `run.py`, `predict.py`, `explain.py`, `retrain.py`, `session.py`, `generate.py`, `result.py` (59 KB) | sklearn in docstrings + `_looks_like_step` duck-typing (`run.py:118-135`) | **KEEP-thin-host** — the stable 0.9.x contract; thin facade over dag-ml. |
| `pipeline/execution` | `orchestrator.py` (119 KB), `executor.py` (78 KB), `refit/*`, `step_cache.py` | joblib (parallel), polars (config_extractor) | **→dag-ml** — COMPILE→PLAN→FIT_CV→SELECT→REFIT is dag-ml's runtime. Highest-risk cutover. |
| `pipeline/storage` | `workspace_store.py` (135 KB), `array_store.py`, `store_schema.py`, `artifacts/*` (`artifact_registry.py` 51 KB, `artifact_loader.py` 39 KB) | polars, pyarrow, joblib | **SPLIT: KEEP-thin-host (schema) + →dag-ml (handle lifecycle).** SQLite+Parquet is a **STABLE on-disk contract**; artifact-handle lifecycle is dag-ml's, but dag-ml never serializes models — the blob store stays host-side. |
| `pipeline/steps` | `parser.py` (StepParser), `router.py` (ControllerRouter), `step_runner.py` | none | **→dag-ml (compile) + KEEP-thin-host (operator deserialize).** |
| `pipeline/bundle` | `generator.py` (39 KB), `loader.py` (58 KB) | joblib | **KEEP-thin-host wrapping →dag-ml.** `.n4a` is a **STABLE contract**; dag-ml owns bundle validation, host keeps the envelope + model blobs. |
| `pipeline/config` | `_generator/` (`keywords.py` 16 KB, `strategies/`), `context.py` (52 KB), `pipeline_config.py`, `component_serialization.py` | none | **→dag-ml (generator expansion) + KEEP-thin-host (component (de)serialization).** |
| `pipeline/trace` | `execution_trace.py`, `extractor.py` (32 KB), `recorder.py` | none | **→dag-ml** — lineage/replay/fingerprints are core. |
| `pipeline/{resolver,runner,predictor,retrainer,explainer}` | `resolver.py` (64 KB), `retrainer.py` (30 KB), `runner.py`, `minimal_predictor.py`, `explain_lineage.py` | joblib (indirect) | **KEEP-thin-host over →dag-ml** — adapters that build a campaign and translate results back to RunResult. |
| `controllers/transforms` | `transformer.py` (prio 10), `y_transformer.py` | `sklearn.base.TransformerMixin/clone` (`transformer.py:3,19`) | **→dag-ml controller ABI (dispatch) + KEEP-thin-host (fit_transform shim).** |
| `controllers/models` | `base_model.py` (joblib.Parallel), `sklearn_model.py` (prio 6), `torch_model.py`, `tensorflow_model.py`, `jax_model.py`, `factory.py`, `residual_model.py`, `stacking/` | sklearn.base, joblib | **→dag-ml controller ABI + KEEP-NN.** Fit/CV/stacking/OOF → dag-ml; NN controllers become host process/in-proc adapters. |
| `controllers/data` | `branch.py`, `feature_augmentation.py`, `sample_augmentation.py`, `concat_transform.py`, `exclude.py`, `tag.py`, `resampler.py`, `auto_transfer_preproc.py`, `merge.py` (`operators/data/merge.py` 57 KB) | joblib, polars (`data/_indexer`) | **→dag-ml** — first-class graph nodes (verified in `pipeline_dsl.schema.json`). |
| `controllers/flow` | `flow/dummy.py` | none | **→dag-ml (flow semantics) or DELETE (dummy).** |
| `controllers/shared` | ModelSelector, PredictionAggregator | none | **→dag-ml** — SELECT phase + aggregation contracts. |
| `controllers/splitters` | `splitters/split.py` (`CrossValidatorController`) | none directly | **→dag-ml (fold identity) + →libn4m (algorithms).** |
| `controllers/charts` | `spectra.py`, `folds.py`, `targets.py`, `augmentation.py`, `spectral_distribution.py` | polars (augmentation chart) | **KEEP-thin-host** — presentation. |
| `data/{_dataset,_features,_targets,_indexer,_predictions}` | `dataset.py` (86 KB), `indexer.py` (53 KB), `predictions.py` (128 KB), `relations.py` (60 KB), `raw_multisource.py` (82 KB) | polars (densest coupling, 22 files concentrated here) | **→dag-ml-data (contracts) + →dag-ml (pred/OOF store) + KEEP-thin-host (SpectroDataset surface).** The XL rewrite. |
| `data/loaders` | `csv_loader_new.py`, `parquet_loader.py`, `excel_loader.py`, `matlab_loader.py`, `numpy_loader.py`, `archive_loader.py`, `loader.py` (26 KB) | pyarrow (parquet), h5py (matlab) | **→nirs4all-io (assembly) + →nirs4all-formats (byte-decode).** |
| `data/parsers` | `folder_parser.py`, `files_parser.py` (32 KB), `normalizer.py` (19 KB), `schema/` | none | **→nirs4all-io** — parity copied verbatim. |
| `data/{signal_type, detection}` | `signal_type.py` (16 KB), `detection/` | none | **SPLIT: →nirs4all-io (detect/infer) + →libn4m (conversion) + KEEP (enum/API on SpectroDataset).** |
| `data/{config, config_parser}` | `config.py` (26 KB), `config_parser.py` | none | **→nirs4all-io + KEEP-thin-host re-export.** |
| `operators/transforms` | `nirs.py` (72 KB), `scalers.py`, `orthogonalization.py`, `feature_selection.py` (41 KB), `wavelet_denoise.py`, `norris_williams.py`, `signal_conversion.py`, `resampler.py` | pywt, pybaselines, scipy.ndimage/signal/interpolate | **→libn4m** — removes pywt/pybaselines + scipy signal paths. |
| `operators/models/sklearn` | 24 PLS variant files (~400 KB), `_aom_nirs/` | ikpls, pyopls, trendfitter, sklearn.cross_decomposition, scipy.linalg/optimize | **→libn4m** (PLS/AOM/POP) **+ KEEP-NN** (tabpfn). |
| `operators/models/{pytorch,tensorflow,jax}` | `models/pytorch/*`, `tensorflow/*`, `jax/*`, `meta.py`, `selection.py` | torch/TF/JAX (KEEP) | **KEEP-NN.** |
| `operators/splitters` | `splitters.py` (47 KB), `grouped_wrapper.py` | kennard algo, scipy.cdist, sklearn KMeans/PCA/model_selection | **→libn4m (algorithms) + →dag-ml (fold identity).** |
| `operators/filters` | `x_outlier.py` (19 KB), `y_outlier.py`, `high_leverage.py`, `spectral_quality.py`, `metadata.py` | scipy, sklearn.decomposition, polars (report) | **→libn4m** (MetadataFilter → KEEP-thin-host). |
| `operators/augmentation` | `spectral.py` (31 KB), `edge_artifacts.py` (31 KB), `scattering.py`, `splines.py`, `environmental.py`, `synthesis.py`, `random.py` | scipy (4 files) | **→libn4m** (all families; corrected from "UNKNOWN" by Inventory D). |
| `operators/data` | `merge.py` (57 KB), `repetition.py`, `rep_fusion.py` | none | **→dag-ml-data (fusion/collation) + →dag-ml (merge legality).** |
| `operators/base` | `base/spectra_mixin.py` | sklearn (TransformerMixin parent) | **KEEP-thin-host** — host operator base. |
| `config/` | `cache_config.py`, `validator.py` (21 KB) | none | **KEEP-thin-host (cache) + →dag-ml (graph validation).** |
| `sklearn/` | `pipeline.py` (20 KB), `classifier.py` | sklearn.base/pipeline | **KEEP-shap / KEEP-thin-host** — SHAP-consumable wrapper. |
| `visualization/` | `predictions.py` (84 KB), `pipeline_diagram.py` (85 KB), `reports.py` (58 KB), `charts/*` | polars | **KEEP-thin-host** — presentation; depolars to numpy. |
| `synthesis/` | `generator.py` (70 KB), `fitter.py` (196 KB), `_constants` (158 KB), `builder.py`, `products.py`, `_bands.py`, `instruments.py` | joblib, scipy.special (voigt) | **KEEP-thin-host** — `generate()` contract; lowest priority. |
| `analysis/` | `selector.py` (53 KB), `transfer_metrics.py`, `projections.py`, `presets.py`, `results.py` | scipy, sklearn | **→libn4m (numerics) + →dag-ml (orchestration) + KEEP (diagnostics).** |
| `core/` | `metrics.py` (26 KB), `task_type.py`, `task_detection.py`, `exceptions.py`, `logging/` | sklearn.metrics, scipy.stats | **→libn4m (regression metrics) + KEEP (classification + task/logging).** |
| `utils/` | `backend.py` (14 KB), `hashing.py`, `memory.py`, `lazy.py`, `header_units.py` | none | **KEEP-thin-host.** |
| `optimization/` | `optuna.py` (68 KB, `OptunaManager`) | sklearn.model_selection.train_test_split | **KEEP-optuna** — outer driver; dag-ml owns tuner-node phase control. |
| `cli/` | `main.py`, `commands/`, `installation_test.py` | none | **KEEP-thin-host.** |
| `workspace/` | `__init__.py` (1.7 KB) | none | **KEEP-thin-host** — on-disk contract. |

### 2.3 The architectural crux (sklearn protocol + controller registry)

**How dispatch works today (FACT):** a step → `StepParser.parse()` (`pipeline/steps/parser.py:69`) → `ParsedStep{operator, keyword, step_type}` with operators deserialized to **live Python objects** (`_deserialize_operator`, `parser.py:225`). `ControllerRouter.route()` (`steps/router.py:29`) iterates the global `CONTROLLER_REGISTRY` (`controllers/registry.py:13`), calls `cls.matches(step, operator, keyword)` on every controller, and sorts matches by `(priority, class_name)` (`router.py:71`); lowest priority number wins. The chosen controller's `execute(...)` runs (`controllers/controller.py:54`).

The **sklearn coupling** is the meaning of `sklearn.base ×75`: `matches()` is overwhelmingly an `isinstance` against sklearn protocol types. `TransformerMixinController` (prio 10) matches `TransformerMixin` and calls `clone()`+`fit_transform`; `SklearnModelController` (prio 6, wins over transformers) matches `BaseEstimator` and branches on `is_classifier/is_regressor`. **`BaseEstimator`/`TransformerMixin`/`RegressorMixin` are simultaneously how the host identifies an operator (routing) and invokes it (fit/transform/predict/clone).** The load-bearing precedence — *SklearnModel prio 6 beats Transformer prio 10, so a PLS is a model not a transform* — must be reproduced by the new dispatch. This decision is resolved in §3.2.

---

## 3. Target architecture: thin nirs4all over the Rust stack

### 3.1 The thesis

The new `nirs4all` is a **Python host shell** owning exactly four things the Rust stack cannot or must not own — the **public API + Result objects** (stable contract), the **NN/AutoML/TabPFN operators** (torch/TF/JAX backends), the **optuna ask-tell driver**, and the **shap explainer** — plus the **thin operator shims and storage/bundle facades** that translate between dag-ml's portable contracts and the frozen 0.9.x on-disk shapes. Everything numerical, every orchestration phase, all data assembly, and all file parsing moves to the Rust engines.

### 3.2 Layered architecture (control path + live data path)

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ PYTHON HOST  (the new "thin" nirs4all package — pip install nirs4all)                       │
│                                                                                              │
│  api/         run() predict() explain() retrain() session() generate()   ← STABLE 0.9.x     │
│               RunResult / PredictResult / ExplainResult  (shape-frozen dataclasses)          │
│                    │ build campaign           ▲ repopulate from dag-ml prediction tables     │
│  ───────────────── │ ──────────────────────── │ ─────────────────────────────────────────── │
│  HOST GLUE         ▼                           │                                              │
│   • dsl_frontend   live Python objs → pipeline_dsl JSON  (operator (de)serialization)        │
│   • store_facade   WorkspaceStore (SQLite DDL + Parquet layout FROZEN) ── dag-ml writes thru │
│   • bundle_facade  .n4a v1 envelope (joblib model blobs packed host-side)                    │
│   • operator shims thin BaseEstimator/TransformerMixin classes → get_params/signature only   │
│                                                                                              │
│  HOST CONTROLLERS (operators that STAY Python — registered via controller_manifest)          │
│   • NN: PyTorch / TensorFlow / JAX   • AutoGluon   • TabPFN / residual_tabpfn                 │
│   • composites: Residual, Meta/stacking ESTIMATOR head (OOF assembly is dag-ml's)            │
│   • optuna outer ask-tell driver (samplers, BinarySearchSampler, pruning)                    │
│   • shap explainer (capture_model seam → predict-fn closure)                                 │
│   • classification metrics, scipy.stats/special, label encoders, synthesis/ (offline)        │
└───────────┬──────────────────────────┬───────────────────────────┬────────────────────────┘
            │ ctypes (in-proc, native)   │ pyo3: compile/plan ONLY    │ ctypes provider
            ▼ no Python on hot path      ▼ (NOT controller exec)      ▼ (wire f64 views: S1)
┌───────────────────────┐   ┌──────────────────────────┐   ┌────────────────────────────────┐
│ BINDINGS              │   │ BINDINGS                  │   │ BINDINGS                        │
│  n4m (libn4m ctypes)  │   │  dag-ml-py (pyo3)         │   │  dag-ml-data provider (ctypes)  │
│  ~150 sklearn classes │   │  validate/compile/plan    │   │  host-owned NumPy f64 buffers   │
│  row-major f64        │   │  JSON contracts ONLY*     │   │  → borrowed f64 views (no JSON) │
└──────────┬────────────┘   └────────────┬─────────────┘   └───────────────┬────────────────┘
   (* dag-ml-py does NOT execute host controllers or own buffers — src/lib.rs:1-5)
           ▼                             ▼                                 ▼
┌───────────────────────┐   ┌──────────────────────────┐   ┌────────────────────────────────┐
│ RUST ENGINE: libn4m   │   │ RUST ENGINE: dag-ml       │◄──┤ RUST ENGINE: dag-ml-data        │
│ C++17 numerical core  │   │ COMPILE→PLAN→FIT_CV→       │   │ schemas/axes/representations    │
│ PLS variants, prep,   │   │ SELECT→REFIT→PREDICT→      │   │ alignment/fusion/collation      │
│ splitters, filters,   │   │ EXPLAIN; OOF/leakage/folds │   │ fingerprints; provider vtable   │
│ AOM/POP, augment,     │   │ bundles/replay/lineage/    │   │ (validates folds, never owns)   │
│ metrics, transfer     │   │ fingerprints; ArtifactRef  │   │                                 │
└───────────────────────┘   └────────────┬─────────────┘   └────────────────────────────────┘
                                          │ controller invoke — TRANSPORT IS THE M0 DECISION:
                                          │   • native op  → in-process Rust/C-ABI controller (no Python)
                                          │   • host-Python op → JSONL process adapter (the only shipped
                                          │     cross-lang path) OR a net-new in-proc Py runtime (Opt B)
                                          ▼
                              calls BACK into Python host controllers (NN/optuna/shap)
                              and DIRECTLY into libn4m for native operators (no Python hop)

LIVE DATA PATH (ingest):
  files ─► nirs4all-formats (Rust, ~58 vendor + .mat/parquet/npy/xlsx) ─► nirs4all-io
        (RESOLVE→INFER→CONFIGURE→MATERIALIZE) ─► SpectroDataset (class stays in nirs4all)
        ─► dag-ml-data envelope + host-buffer provider ─► dag-ml FIT_CV

CONTROL PATH:
  api.run() ─► dsl_frontend (Py objs→JSON) ─► dag-ml-py.compile/plan ─► dag-ml PLAN
        ─► dag-ml schedules phases ─► invokes controllers:
              • native op  → libn4m directly (Rust→C++, Python uninvolved)
              • host-Python op (NN/optuna/shap) → JSONL process adapter worker (Opt A)
                                                  [or in-proc Py runtime if Opt B is built]
        ─► dag-ml SELECT/REFIT/PREDICT ─► prediction tables + ArtifactRefs
        ─► store_facade + bundle_facade re-materialize SQLite/Parquet/.n4a
        ─► api repopulates RunResult ─► studio
```

**Who calls whom (decisive):** dag-ml is the **conductor**, not a library the host calls per-step. The host *compiles+plans* a campaign through `dag-ml-py` (JSON contracts) and hands execution to the dag-ml runtime **once**; dag-ml then drives host controllers (Python operators, **via the JSONL process adapter** — Option A) and dispatches native operators **sideways** into libn4m in-process. This inverts today's model (the Python orchestrator calls operators) and is the whole point — it makes OOF/leakage enforcement structural rather than conventional. **Note:** dag-ml-py compiles/plans but does not itself *run* host controllers — execution rides the host-adapter transport (§3.3).

### 3.3 The controller-boundary decision

> **⚠️ Corrected after the Codex xhigh review (§0.1, finding #1).** The DRAFT v1 recommended an *in-process pyo3 controller vtable via `dag-ml-py`* as the default transport. **That path does not exist and is explicitly out of scope in dag-ml today.** This section is rewritten to the verified reality. Treat the controller transport as an **open decision (M0)**, not a settled one.

**The verified ground truth.** `dag-ml-py` *"validates, compiles and plans serialized JSON contracts, but **does not execute host controllers or own data buffers**"* (`dag-ml/crates/dag-ml-py/src/lib.rs:1-5`; every export is validate/compile/plan, `:56-202`). dag-ml's host-adapter design is explicit: the C-ABI controller vtable *"is an in-process abstraction for Rust controllers compiled into the same binary … **It is not the path for Python/R hosts**"*, and *"the only stable wire protocol for cross-language host controllers is the **process adapter JSONL contract**"* — with **native PyO3 / C-ABI controller wrappers listed under "Out of scope (explicitly)"** (`dag-ml/docs/HOST_ADAPTER_BACKLOG.md:12-17, 85-90`). Shipped proof the JSONL path works: `sklearn_production` + `prospectr` + `mdatools` controllers (`STATUS.md:650-685`).

**What is still settled (unchanged):** operators keep the sklearn `BaseEstimator`/`TransformerMixin` **shape** for authoring + studio introspection; `OperatorController.matches()`/priority is retired as the *runtime* router in favor of a declarative `controller_manifest` (`operator_kind` + `class_prefixes`) resolved by dag-ml at PLAN time; and **libn4m-backed operators (~85–90%) bypass Python entirely** — dag-ml dispatches them to in-process Rust controllers over the C-ABI, no host callback, no JSON. The per-fold transport cost therefore applies **only to the host-Python nodes: NN models, optuna-driven fits, shap, and any not-yet-native operator.**

**The open decision (M0) — two real options, neither free:**

| Option | What it is | Pros | Cons / cost |
|---|---|---|---|
| **A. Adopt the JSONL process adapter as-is** (dag-ml's intended path) | Host-Python controllers run as JSONL subprocess workers; dag-ml streams `NodeTask`/`NodeResult`. | Exists, shipped, stable, sandboxable; matches dag-ml's design; no dag-ml core change. | **Per-fold/per-trial JSON serialization of feature matrices is `O(variants×folds×n×p)`** — the original CRITICAL concern. Mitigations: **task batching** (`accepts_task_batch`), keep wide X **host-side** and pass sample-id selections + a data handle rather than raw matrices (dag-ml-data already keys by identity), **persistent workers** for warm NN/GPU state. Latency must be **measured** on a real sweep (S0). |
| **B. Sponsor an in-process Python controller runtime in dag-ml** | A net-new dag-ml capability: a pyo3 host-controller execution surface with borrowed f64 views (`dag_ml_data.h:273-275` exist, unwired). | Lowest per-fold latency; zero-copy buffers; no IPC. | **Does not exist; contradicts dag-ml's stated scope.** Requires **dag-ml-owner buy-in + net-new design/tests/ABI** (FFI-safety epic, §16). Adds **~+8–15 pw** to dag-ml itself and pulls the FFI-safety contract onto the critical path. Not a nirs4all-host-only decision. |

**Recommendation:** **default to Option A and engineer the serialization envelope down** (batching + host-side data + persistent workers), because it is the only path that exists and matches dag-ml's design; **pursue Option B only if S0's latency benchmark on a representative sweep fails the agreed budget** — and then as a *jointly owned dag-ml feature*, not a nirs4all shim. Either way, **the borrowed-view provider wiring (S1) is needed** for Option A's host-side data handles too. Native libn4m operators are unaffected (they were never on the Python boundary).

**Per-axis notes (re-grounded):**

| Axis | Verdict |
|---|---|
| **Per-fold latency** | Real and the dominant risk under Option A. **Measure first** (S0) on `variants×folds×preprocessing` at NIRS width before committing. Reduce by batching + handle-passing, not by assuming a zero-copy path that isn't built. |
| **GIL** | Manifests carry `thread_safe`/`process_safe`/`needs_python_gil` (`COORDINATOR_SPEC.md:112-117`); the scheduler requires `Send+Sync` controllers (`STATUS.md:498-504`). Native libn4m ops → parallel Rust threads, Python never entered. Host-Python controllers → process-isolated workers (Option A) sidestep the GIL entirely; torch/TF/JAX release the GIL in their own kernels regardless. |
| **Buffer handoff** | Under either option, wire `dagmldata_inmemory_provider_new_with_f64_feature_views` into the ctypes shim (today JSON-only, `_provider.py:151-158`) so host NumPy f64 reaches dag-ml-data without `_json`. **Mandatory prerequisite (S1, ~1–2 pw).** |
| **libn4m bypass** | Unchanged and load-bearing: ~85–90% of operators are native Rust controllers, dispatched in-process over the C-ABI with no Python hop. The `BaseEstimator` shim exists only at compile time for `get_params()`/signature. |

**Consequence for the sklearn `BaseEstimator` protocol (the ×75 surface):** unchanged from v1 — it **survives, demoted from dispatch key to authoring/declaration shape**. `sklearn.base` stays the operator-authoring protocol; `@register_controller` becomes a **manifest-emitting shim**; the **precedence-equivalence** test (manifest ≡ old `(priority, class_name)` sort, esp. *SklearnModel prio 6 > Transformer prio 10*) remains the gate for this layer (story S6, epic E5) — **UNVERIFIED until tested.**

### 3.4 The data boundary (SpectroDataset → envelope + provider)

**Where the SpectroDataset class lives: in `nirs4all`, full-weight. Settled by source (Inventory E §E.2), not inference.** Three independent confirmations:
1. nirs4all-io Load-bearing rule #1 (`nirs4all-io/CLAUDE.md:141`): *"`import nirs4all_io` must never import `nirs4all`; only `to_spectrodataset` may lazily import it"* — enforced by `tests/test_import_boundary.py` in a subprocess.
2. `materialize/spectrodataset.py:38` — `from nirs4all.data import SpectroDataset` is **lazy, inside the function**, "the sole nirs4all touch-point."
3. COPY_PROVENANCE #15: the build orchestration is `COPY-LOGIC + EMIT(lazy)`.

`SpectroDataset` (`data/dataset.py`, 86 KB) owns multi-source X, folds, repetition, aggregation, the named-processings axis — it is the pipeline's working structure, not a loader output. It **cannot** move to io (cycle) or to dag-ml-data (which excludes predictions/OOF).

The boundary end to end:

```
files ─► nirs4all-formats (.mat v5+v7.3, parquet, npy, xlsx, ~58 vendor — golden-tested)
      ─► nirs4all-io  RESOLVE→INFER→CONFIGURE→MATERIALIZE
      ─► SpectroDataset  (nirs4all class, built by io via lazy import — single canonical builder)
      ─► [host adapter]  SpectroDataset → DatasetSchema + SampleRelationTable + host-buffer provider
      ─► dag-ml-data  validates schema/relations/folds, fingerprints, exposes f64 views
      ─► dag-ml  FIT_CV consumes provider handles by identity (sample_id), never by row position
```

Key facts and prerequisites:
1. **Ingest is a wiring job, not a capability gap (Inventory E's key correction).** The Rust readers exist and are golden-tested, but **io does not yet route tabular files through formats** (Python MVP routes only vendor extensions; Rust facade is CSV-only, `loaders.rs:60`). The `.mat` reader is the highest-confidence single removal — it kills `scipy.io.loadmat` AND the `h5py` v7.3 path at once.
2. **The host adapter (net-new) translates SpectroDataset → coordinator envelope:** sources → `DatasetSchema.sources[]`; wavelength headers/units → `CoordinateSpec`; the `Indexer` (identity, repetitions, augmentation origins, `excluded`) → `SampleRelationTable`; `y` → `CoordinatorTargetTable`; X buffers → host-owned NumPy f64 → borrowed views.
3. **Two gaps to flag as prerequisites:**
   - **Named-processings axis (`n_pp`) not modeled end-to-end** in dag-ml-data (`AxisKind::Processing` is a dead variant — zero usages). Until collation/fusion reason over the processing axis, the host adapter must flatten processings into namespaced columns (losing named-processing provenance the studio shows) or carry processings as separate sources. **A dag-ml-data backlog item, not host wiring.**
   - **Folds and predictions are owned by dag-ml, not dag-ml-data** (validated vs owned). The host supplies fold *assignments* from libn4m splitters; dag-ml-data validates; dag-ml owns the OOF/prediction store.
4. **Provider is host-owned buffers, not the in-memory fixture.** The only provider today is the in-memory C-conformance fixture; a production host-owned-buffer provider "is not written" (Inventory C). The nirs4all host builds this over its SpectroDataset NumPy buffers — the same wiring as the §3.3 buffer handoff.

### 3.5 The final dependency set (pyproject sketch)

```toml
[project.dependencies]
# ---- core runtime (always) ----
numpy
pandas                  # RunResult/Predictions DataFrame surface, studio reads
pyyaml                  # run manifest (YAML contract)
# ---- Rust ecosystem bindings (the new backend) ----
n4m                     # libn4m: all PLS/preprocessing/splitters/filters/AOM/metrics
dag-ml                  # pyo3 binding: validate/compile/plan contracts (engine drives
                        #   COMPILE→…→PREDICT, OOF/leakage/bundles/lineage; controllers run
                        #   via the JSONL process adapter — §3.3, not in-proc today)
dag-ml-data             # ctypes/pyo3: typed data contracts + host-buffer provider
nirs4all-io             # dataset assembly (RESOLVE→INFER→CONFIGURE→MATERIALIZE)
nirs4all-formats        # ~58 vendor + .mat/parquet/npy/xlsx readers (Rust)
# ---- KEPT compute (no Rust home) ----
scikit-learn            # SHRUNK: sklearn.base protocol; classification metrics;
                        #   LabelEncoder/OneHotEncoder/FunctionTransformer (target/metadata);
                        #   tree/ensemble models (RF/GBM) as user host operators
scipy                   # SHRUNK: stats (pearsonr/spearmanr/ks_2samp/wasserstein/chi2/MAD),
                        #   special (voigt/gammaln), and the synthesis/ offline kernels
                        #   (signal/optimize/interpolate USED ONLY inside synthesis/)
shap                    # explain() — KEEP
optuna                  # HPO outer driver — KEEP
pyarrow                 # STORAGE-ONLY: writes the frozen workspace Parquet layout
joblib                  # NARROWED: .n4a / artifact model-blob (de)serialization ONLY
                        #   (parallelism removed — dag-ml owns scheduling)

[project.optional-dependencies]
torch = ["torch", "tabpfn>=2.0.0"]
tensorflow = ["tensorflow"]
jax = ["jax", "flax"]
autogluon = ["autogluon.tabular"]

# ---- REMOVED ENTIRELY ----
# ikpls, pyopls, trendfitter        → libn4m PLS variants (PARITY-gated)
# PyWavelets, pybaselines           → libn4m transform/wavelet + transform/baseline (PARITY)
# kennard-stone                     → libn4m model_selection.kennard_stone (PARITY)
# polars                            → pyarrow/numpy (storage) + dag-ml-data (compute)
# h5py                              → nirs4all-formats hdf5/matlab v7.3 readers
```

### 3.6 The sklearn / scipy cut-line table (from Inventory F)

Legend: **CUT** = capability now provided by libn4m/dag-ml/io, delete from Python. **KEEP** = needed, no Rust equivalent or host glue. Counts are import-occurrence counts.

#### sklearn submodules

| Import | Used for | Verdict | Replacement / justification |
|---|---|---|---|
| `sklearn.base` (BaseEstimator ×56, TransformerMixin ×32, RegressorMixin ×32, ClassifierMixin ×5, clone ×10; 71 files) | The operator/controller protocol; `is_classifier/is_regressor` (`sklearn_model.py:19`); `clone` for fresh fold models | **KEEP (protocol) — but shrink** | Host-operator interface; dag-ml host controllers expose fit/transform/predict in sklearn shape. **CUT every BaseEstimator subclass that only wraps a PLS/PCA/scaler now in libn4m.** RISK: dropping it entirely orphans controller-matching — keep until the registry is fully manifest-driven. |
| `sklearn.cross_decomposition.PLSRegression` (×16) | Base PLS + inner engine of OPLS/iPLS/AOM/feature-selection/synthesis | **CUT** | libn4m `n4m_estimators_pls_fit` (FACT: `estimators/regression.h`); also SIMPLS via `sparse_simpls_fit`. |
| `sklearn.decomposition.PCA`/`TruncatedSVD` (×15) | PCA in splitters, filters, `nirs.py`, charts, transfer, PCR, SPXY | **CUT** | libn4m `n4m_decomposition_flexible_pca_*` / `flexible_svd_*` (FACT: `decomposition.h`). |
| `sklearn.preprocessing` (StandardScaler, MinMaxScaler, FunctionTransformer, LabelEncoder, OneHotEncoder, KBinsDiscretizer; ×26) | Scaling, target encoding, stratification binning | **MOSTLY CUT** | StandardScaler→`baseline_center`/`scaling` (FACT `transform/scaling.h:76` maps to StandardScaler); MinMax/normalize→`normalize`/`simple_scale`; KBinsDiscretizer→`kbins_discretizer_*`. **KEEP narrowly:** LabelEncoder/OneHotEncoder/FunctionTransformer for target/metadata; UNKNOWN whether dag-ml-data owns categorical target encoding. |
| `sklearn.model_selection` (BaseCrossValidator, StratifiedGroupKFold, StratifiedShuffleSplit, KFold, GroupKFold, train_test_split, cross_val_score; ×23) | CV splitters + base class; `cross_val_score` in iPLS/selector; `train_test_split` in optuna no-folds path | **CUT (splitters) / KEEP (one boundary)** | Stratified/group/kbins/kennard/kmeans/SPXY all in libn4m `n4m_model_selection_*`. Plain KFold/ShuffleSplit/train_test_split owned by dag-ml. `BaseCrossValidator` as protocol KEPT only if user-supplied sklearn CV objects are still accepted — RISK: public-API affordance. |
| `sklearn.cluster.KMeans` (×1, `splitters.py:8`) | KMeans split | **CUT** | libn4m `n4m_model_selection_kmeans_*`. |
| `sklearn.metrics` (×14) | Regression + classification scoring (`core/metrics.eval`) | **SPLIT** | Regression (r2/rmse/mae/bias/mape/max_error/explained_variance) → libn4m `metrics.h` → **CUT**. **KEEP** classification (accuracy/balanced_accuracy/f1/precision/recall/roc_auc/average_precision/cohen_kappa/matthews_corrcoef/log_loss/confusion_matrix/classification_report/hamming_loss/jaccard/top_k_accuracy) — no libn4m symbol. |
| `sklearn.linear_model` (Ridge, RidgeCV, LinearRegression, LogisticRegression; ×7) | Meta/residual final estimators, PCR, AOM heads, selector | **CUT (numeric) / KEEP (head)** | Ridge→`ridge_fit`, LinearRegression→PLS/PCR, PLS-logistic→`pls_logistic_fit`. KEEP plain LogisticRegression as a stacking/AOM head **only if** no bare libn4m logistic exists — RISK: verify before cutting. |
| `sklearn.ensemble` (RandomForest, GradientBoosting, IsolationForest, Stacking/Voting; ×7) | Tree models users pass; factory Stacking/Voting; IsolationForest outliers | **KEEP** | Trees/forests/boosting not in libn4m. IsolationForest outlier path → prefer libn4m `x_outlier_*`, but RF/GBM-as-model stays. |
| `sklearn.neighbors` (NearestNeighbors, LocalOutlierFactor; ×5) | LWPLS neighbor search, transfer metrics, augmentation, LOF | **CUT (LWPLS) / KEEP (diagnostics)** | LWPLS→`lw_pls_fit`. KEEP NearestNeighbors in transfer/augmentation viz; LOF unless mapped to libn4m outlier. |
| `sklearn.covariance` (EmpiricalCovariance, MinCovDet; ×1) | Mahalanobis outlier in `x_outlier.py` | **CUT** | libn4m `outlier_detection.h` (`x_outlier_*`/`high_leverage`/`q_residuals`). |
| `sklearn.pipeline.Pipeline` (×3) | `presets.py`, SHAP wrapper docstrings | **KEEP (thin)** | Host-side compose convenience; dag-ml owns the real graph. |
| `sklearn.utils` / `sklearn.utils.validation` (×27) | Input validation inside to-be-CUT estimators | **CUT with their estimators** | Disappears with the PLS/scaler bodies. KEEP `check_random_state` (`pipeline/runner.py`). `_num_samples` dies with the splitter. |
| `sklearn.exceptions` (×3, all `_aom_nirs`) | AOM vendored code | **CUT** | Vanishes with `_aom_nirs/`. |

#### scipy submodules

| Import | Used for | Verdict | Replacement / justification |
|---|---|---|---|
| `scipy.signal` (savgol_filter, find_peaks, fftconvolve; ×~6) | SG, peak finding, conv | **CUT (SG) / KEEP (synthesis)** | SG→libn4m `savitzky_golay_*`+derivatives+norris_williams. KEEP find_peaks/fftconvolve inside `synthesis/`. |
| `scipy.ndimage.gaussian_filter1d`/`convolve1d` (×8) | Gaussian smoothing | **CUT (signal) / KEEP (synthesis)** | →libn4m `gaussian_*`. KEEP in `synthesis/`. |
| `scipy.spatial.distance.cdist` / `procrustes` (×5) | KS/SPXY/LWPLS distance; procrustes in transfer | **CUT (KS/SPXY/LWPLS) / KEEP (procrustes)** | Distances computed internally by libn4m splitters/lw_pls. KEEP procrustes/subspace_angles in `analysis/transfer_metrics.py`. |
| `scipy.optimize` (nnls ×4, minimize ×5, lsq_linear) | AOM-Ridge weights, synthesis fitting | **CUT (AOM) / KEEP (synthesis)** | →libn4m AOM/ridge/blender. KEEP minimize/nnls inside `synthesis/`. |
| `scipy.linalg` (cho_factor/solve ×3, solve_banded, subspace_angles) | Cholesky in AOM-Ridge; banded baselines | **CUT** | →libn4m ridge/cholesky + baseline banded solvers. |
| `scipy.stats` (×9: pearsonr, spearmanr, ks_2samp, wasserstein, chi2, entropy, MAD) | Correlation metrics; distribution tests; chi2 threshold; MAD | **KEEP (mostly)** | Not in libn4m's regression-metrics set; tiny. CUT only `median_abs_deviation` if robust_pls→libn4m. |
| `scipy.interpolate.interp1d` (×3) | Resampling | **CUT (resampler) / KEEP (synthesis)** | →libn4m `resampler_*`. KEEP in `synthesis/detectors.py`. |
| `scipy.integrate.trapezoid` / `scipy.special` (voigt_profile, gammaln) | Band integration; line shapes | **KEEP** | No libn4m equivalent; synthesis/feature extraction. |
| `scipy.io.loadmat` (×2) | Reading `.mat` | **CUT** | →nirs4all-formats MATLAB reader (v5 + v7.3 golden-tested). |
| `scipy.sparse` (×2) | OSC/orthogonalization | **CUT** | →libn4m `osc_*`. |

**The cut-line in one sentence:** *everything in `sklearn.cross_decomposition / decomposition / cluster / covariance`, the numerical half of `preprocessing` + `model_selection` + `linear_model` + `neighbors` + regression `metrics`, and the scipy `signal`/`ndimage`/`optimize`/`linalg`/`interpolate` paths that feed the live spectral pipeline → CUT to libn4m; keep `sklearn.base` (host-operator protocol), tree/ensemble models, classification metrics, label encoders, and scipy `stats`/`special` — those genuinely have no Rust home.*

**The `_aom_nirs/` special case:** `operators/models/_aom_nirs/` is vendored AOM paper code already carved out of ruff+mypy gates ("pending replacement — debt audit 2026-06-04", `pyproject.toml:188,235-240`). It accounts for the bulk of the `scipy.optimize`/`scipy.linalg`/`sklearn.exceptions` hits. **Verdict: CUT the entire tree** — its numerics are libn4m's AOM/POP surface — and do not migrate its imports individually; they vanish with the directory.

### 3.7 Where each capability lands (authoritative, reconciling all inventories)

Owner codes: **PY** = Python host · **N4M** = libn4m · **DML** = dag-ml · **DMD** = dag-ml-data · **IO** = nirs4all-io · **FMT** = nirs4all-formats.

| nirs4all subsystem | New owner | Note |
|---|---|---|
| `api/` public surface | **PY** | Stable contract; thin facade over `dag-ml-py`. |
| RunResult / PredictResult / ExplainResult | **PY** | Repopulated from DML tables; shape frozen. |
| `pipeline/execution` orchestrator+executor+refit | **DML** | The engine being replaced. |
| `pipeline/steps` parser/router | **DML** (compile) + **PY** (deserialize) | `matches()` retired; manifest-driven. |
| `pipeline/config` generator (`_or_/_range_/_grid_/_cartesian_/_zip_/_chain_/_sample_`) | **DML** | All verified in `pipeline_dsl.schema.json`; changes fingerprints/seeds. |
| `pipeline/config` component (de)serialization | **PY** | The dsl_frontend. |
| `pipeline/trace` lineage/replay | **DML** | Core DML. |
| `pipeline/bundle` `.n4a` | **PY facade** over **DML** ArtifactRefs | Envelope + joblib blobs host-side. |
| `pipeline/storage` SQLite + Parquet | **PY facade** | **Frozen on-disk contract**; DML writes through it. |
| `pipeline/storage` artifact handle lifecycle | **DML** (refs) + **PY** (blob store) | DML holds opaque refs; host writes joblib/torch.save. |
| controllers/transforms dispatch | **DML** vtable + **PY/N4M** op | Native transforms → N4M direct. |
| controllers/models (CV/OOF/stacking schedule) | **DML** | Phase ordering, fold scheduling, OOF joins. |
| controllers/models NN (torch/TF/JAX/AutoGluon/TabPFN) | **PY** | Host controllers via the M0 transport (JSONL process adapter default; §3.3). |
| controllers/models Meta/stacking **OOF assembly** | **DML** | Leakage-safe join by sample_id. **Must move, not reimplement.** |
| controllers/models Meta/stacking **estimator head** | **PY** or **N4M** | Ridge→N4M, bare logistic→PY (verify). |
| controllers/data branch/merge/exclude/tag/concat/aug | **DML** (nodes) + **DMD** (alignment/collation/fusion) | All keys in `pipeline_dsl.schema.json`. |
| controllers/splitters dispatch | **DML** (identity) | Algorithms → N4M. |
| controllers/charts | **PY** | Presentation. |
| controllers/shared ModelSelector/PredictionAggregator | **DML** SELECT + aggregation | Classification metrics gap (below). |
| data/dataset (SpectroDataset class) | **PY** (class) + **DMD** (contract) | Class stays full-weight (Inventory E settled). |
| data/predictions, indexer, relations, raw_multisource | **DMD** + **DML** (pred/OOF) + **PY** (surface) | The XL rewrite (22 polars files). |
| data/loaders | **IO** + **FMT** | Removes scipy.io/h5py/pyarrow once io routes tabular through FMT. |
| data/parsers | **IO** | Parity copied verbatim. |
| data/signal_type | **IO** (detect) + **N4M** (convert) + **PY** (enum/API) | Split. |
| data/config DatasetConfigs | **IO** + **PY** re-export | Parity oracle = `nirs4all.DatasetConfigs`. |
| data reduction/ensemble/fit_influence/repetition | **DML** / **DMD** | OOF/leakage/repetition invariants. |
| operators/transforms | **N4M** | Cuts pywt, pybaselines, scipy.signal/ndimage. |
| operators/models PLS variants (24 files) | **N4M** | Cuts ikpls/pyopls/trendfitter/sklearn.cross_decomposition. |
| operators/models KOPLS/OKLMPLS/FCKPLS-model/NLPLS-multikernel/TabPFN | **PY** (torch/jax) | **MISSING in N4M**; keep on NN backends. |
| operators/models `_aom_nirs/pls/` | **N4M** (delete tree) | Covered. |
| operators/models `_aom_nirs/ridge/` MKL/kernelizer/local-ridge | **N4M** (port) or **PY** (orchestrate over N4M ridge+moments) | The real porting debt. |
| operators/models `_aom_nirs/fast/` generators | **PY** feeding **N4M** sweep kernels | Generators stay Python. |
| operators/splitters | **N4M** | All PARITY; cuts kennard-stone, scipy.cdist, sklearn KMeans/PCA. |
| operators/filters | **N4M** | MetadataFilter → **PY**. |
| operators/augmentation (incl. spline/edge/environmental) | **N4M** | All 50 fixtures present. RNG-kind pinning is load-bearing. |
| operators/data merge/repetition/fusion | **DMD** + **DML** | |
| operators/base SpectraTransformerMixin | **PY** | Host operator protocol. |
| config/ cache + validator | **PY** + **DML** | |
| sklearn/ NIRSPipeline (SHAP wrapper) | **PY** | KEEP-shap. |
| visualization/ | **PY** | Presentation; depolars to numpy. |
| synthesis/ | **PY** | `generate()` contract; keeps scipy offline. |
| analysis/ transfer selection | **N4M** + **DML** + **PY** (diagnostics) | |
| core/ metrics | **N4M** (regression) + **PY** (classification) | Classification stays Python. |
| core/ task_type/logging/exceptions | **PY** | Host infra. |
| optimization/ optuna | **PY** | Outer ask-tell; fold-training stripped, joblib removed. |
| utils/ cli/ workspace/ | **PY** | Host infra + on-disk contracts. |

**Conflicts reconciled:** (1) Inventory A flagged feature-selection/splitters/augmentation as UNKNOWN; **Inventory D's fixture audit closes these as PARITY** — they go to N4M. (2) Inventory A vs F disagreed on the controller transport. **DRAFT v1 resolved this to "pyo3 in-process"; the Codex review proved that path does not exist (§0.1/§3.3).** Re-resolved: the controller transport is an **open M0 decision** — default to the shipped **JSONL process adapter** (Option A) with serialization mitigated by batching + host-side data, and consider a net-new in-process Python runtime (Option B) only if S0's benchmark fails. (3) The polars/pyarrow-vs-Parquet contradiction (Inventories F+G) is resolved in §3.4/§7 — keep pyarrow storage-only, drop polars.

---

## 4. Capability readiness of the Rust stack

### 4.1 Per-library maturity verdicts

**dag-ml — control core production-grade; host-execution layer pre-production (Inventory B).** Compile/plan/OOF/leakage/bundle/replay/lineage/fingerprint is IMPLEMENTED and a genuine *superset* of nirs4all's orchestration, turning controller-side conventions into enforced invariants. The immutable compiled plan (`ExecutionPlan`, STATUS.md:274-277) structurally **exceeds** nirs4all's mutable-context reconstruction (COORDINATOR_SPEC.md:780). FIT_CV/SELECT/REFIT/PREDICT all IMPLEMENTED with byte-equal sequential and parallel schedulers (STATUS.md:498-504). **It ships *real* JSONL process-adapter controllers — `sklearn_production`, `prospectr`, `mdatools` (pls/pca/plsda)** (STATUS.md:650-685) — so the host-controller path is proven, not mock; what remains smoke/missing is **tuner execution** and **adaptive-search lowering** (STATUS.md:639-646). The gaps that matter for nirs4all: **no torch/tf/jax controller**; **`dag-ml-py` is JSON-contract-only and does not execute controllers or own buffers** (`src/lib.rs:1-5`), and **native PyO3/C-ABI controller wrappers are explicitly out of scope** (`HOST_ADAPTER_BACKLOG.md:85-90`) — so the only shipped cross-language transport is the **JSONL process adapter**, whose per-fold serialization of wide-NIRS matrices is unmeasured at sweep scale; and **no EXPLAIN execution**. It can *validate and coordinate* every nirs4all use-case as a conformance test today, and *run* classical-operator pipelines through JSONL adapters; it cannot yet *run* a real NN/feature-heavy nirs4all pipeline end-to-end without the transport decision (M0) being made.

Phase-by-phase parity (FACT from STATUS.md / COORDINATOR_SPEC.md):

| dag-ml phase | Status | Covers nirs4all? |
|---|---|---|
| **COMPILE** | IMPLEMENTED; serialized-nirs4all importer accepts `pipeline/preprocessing/model/branch/merge/_or_/_cartesian_/_chain_/_grid_/_range_/_log_range_/_zip_/_sample_/split/sources` (STATUS.md:185-253) | **PARTIAL** — needs a Python-object→JSON frontend ("direct Python/YAML DSL frontends … remaining work", STATUS.md:640-642). |
| **PLAN** | IMPLEMENTED, first-class published `ExecutionPlan` schema | **EXCEEDS** — upgrade, no gap. |
| **FIT_CV** | IMPLEMENTED (core); separate fold-train/validation views, OOF aggregation, `requires_oof` edges | **PARTIAL** — coordinated but cannot execute a real model (only smoke/sklearn-production adapters). |
| **SELECT** | IMPLEMENTED; deterministic ranking, identity-aligned `mse/rmse/mae/r2` | **MOSTLY COVERED (regression).** GAP: classification + custom scorers ride as `custom_controller` (contract exists, reducers don't). |
| **REFIT** | IMPLEMENTED; requires full CV OOF coverage before refit | **COVERED, stronger** than nirs4all. |
| **PREDICT** | IMPLEMENTED (mock + stateful sklearn smoke) | **PARTIAL** — gated on host adapters; dag-ml never deserializes a model. |
| **EXPLAIN** | **WEAKEST** — phase slot + replay-request validation only (STATUS.md:359); no SHAP path, no explanation payload contract | **NOT-YET / major gap** — `explain()`→`ExplainResult` is a STABLE contract with no dag-ml execution path. |

**dag-ml-data — contract + planning + in-memory-conformance, NOT a production data engine (Inventory C).** Self-described "foundation scaffold plus coordinator data-plan envelope, materialized data/view handle smokes" (STATUS.md:3). 12,073 LOC, 183 unit tests. Multi-source X, alignment (inner/left/outer), fusion (namespacing), collation (f64/f32 + masks), multi-target, sample/group/origin identity, repetitions, and the frozen provider vtable with a **no-JSON f64 C path** are all genuinely present and tested. The load-bearing gaps: **production provider arenas, signal-type enforcement wiring, the named-processings axis (`AxisKind::Processing` is a dead variant), and the nirs4all connector itself** (descoped to nirs4all-io, ADR-0001). The Python provider shim is real (733 LOC ctypes) but **JSON-only on the numeric hot path** (`_provider.py:152` wires only `..._features_json`; the borrowed-view constructors are declared-unused).

**libn4m — the numerical core is ready; coverage ~85–90% with parity fixtures (Inventory D).** 669 `n4m_*` symbols (548 method + 121 infra, `ABI_RECONCILE_GAP.md:5-7`) → **188 ABI-mapped catalog methods** (the split catalog has 209 method YAMLs; 188 are ABI-reconciled, reconciliation GREEN). 204 JSON parity fixtures incl. manifest (1e-8 to 1e-12 vs sklearn 1.4 / R pls / NumPy). The `n4m` Python binding ships ~150 sklearn-compatible classes loading `libn4m.so.2.0.0` via ctypes (GIL released in native calls). The one structural caveat: the C-ABI input contract is **row-major contiguous F64 only** (`n4m.h:322-324`) — a copy/cast cost, not a correctness blocker, since nirs4all passes f64. Full coverage map in §5.

**nirs4all-io + nirs4all-formats — capabilities exist and are golden-tested; the cutover is a wiring job (Inventory E; surface-split corrected per Codex review).** nirs4all-formats has golden-tested Rust readers for MATLAB v5/v7.3 (incl. eigenvector corn, NIR shootout 2002), numpy npy/npz, parquet, excel (calamine), and CSV. **The two io surfaces differ and must not be conflated:** the **Python MVP already reads numpy/parquet/Excel/CSV + vendor files** (`nirs4all-io/src/nirs4all_io/.../loaders.py:201-223, 241-276`) — it is *not* vendor-only; the **Rust facade is CSV-family only** today (`loaders.rs:57-64`). The removal target is to route **all** tabular ingest **through nirs4all-formats in both surfaces**, so that scipy.io/h5py/pyarrow/polars leave `nirs4all/data/loaders`. Until the Rust facade is rewired (S1.7), the Rust path can't replace the Python loaders one-for-one. `SpectroDataset` stays full-weight in nirs4all (settled, §3.4).

### 4.2 Consolidated capability-gap matrix (from Inventory I)

Readiness reflects the owning library's STATUS. **READY** = implemented + parity/conformance-gated. **PARTIAL** = mechanism exists but unwired/unfixtured/smoke-only. **MISSING** = no implementation. Sorted high→low risk (remaining effort × contract-criticality × parity uncertainty).

| # | Capability (must survive) | Owner | Readiness (cite) | The gap | Effort |
|---|---|---|---|---|---|
| 1 | **Controller-execution transport for host-Python ops (feature matrix per fold)** | DML + DMD | **DECISION OPEN; no zero-copy path exists** (`dag-ml-py/src/lib.rs:1-5` JSON-only; `HOST_ADAPTER_BACKLOG.md:85-90` PyO3 out-of-scope; `_provider.py:151-158` JSON-only) | The keystone (re-grounded). The shipped path is the **JSONL process adapter**; its per-fold serialization is unmeasured at sweep scale. Either adopt+mitigate (batching, host-side data, S1 borrowed views) or build an in-proc Py runtime in dag-ml (Option B). | **L–XL (~4–10 pw, option-dependent)** |
| 2 | **NN model fit/predict (torch/TF/JAX/AutoGluon/TabPFN)** | PY host controller via the M0 transport | **MISSING** (Inv B §2; ROADMAP:119-120) | No NN controller exists; the 6-method `BaseModelController` protocol is the template but unbuilt. Rides whichever transport M0 picks. | **XL (~6-8 pw)** |
| 3 | **`.n4a` + SQLite/Parquet workspace** (STABLE; studio raw SQL) | PY facade over DML refs | **PARTIAL/format-mismatch** (Inv B §4, G; STATUS.md:168-169,417) | Net-new shim re-materializing refs/predictions into SQLite DDL + Parquet + `.n4a` v1. **Blocked-unknown:** n4m model pickleability. | **L-XL (~6-10 pw)** |
| 4 | **OOF stacking / meta-model assembly** | DML (join) + PY (head) | **PARTIAL — behavioral break** (Inv B §3; COORDINATOR_SPEC.md:705-711 vs meta_model.py:907) | `stacking/` OOF logic must **move to DML, not be reimplemented**. Partial-fold pipelines correctly rejected. | **L (~3-4 pw)** |
| 5 | **EXPLAIN / SHAP** (STABLE `explain()`→ExplainResult) | PY (shap) + DML phase | **MISSING execution** (Inv B §1,§6; COORDINATOR_SPEC.md:601) | Net-new EXPLAIN host adapter: `capture_model` → DML handle + host predict-fn closure. | **M (~2 pw)** |
| 6 | **AOM-Ridge MKL/kernelizer/local-ridge/multi-branch/auto-selector** (`_aom_nirs/ridge/`, 23 files) | N4M (port) or PY (orchestrate) | **PARTIAL** (Inv D §D.2/D.4) | Decide port-to-C++ vs Python-orchestration over N4M ridge+moments. The real porting debt. | **L (~3-4 pw)** |
| 7 | **Optuna HPO** (TPE/CMA-ES/BinarySearchSampler/pruning) | PY outer driver | **PARTIAL/by-design** (Inv B §5, F §F.2; STATUS.md:643-644) | No adaptive-sweep hook in DML; optuna stays outer driver, strip in-process fold-training. | **S-M (~1-2 pw)** |
| 8 | **Tabular ingest removing scipy.io/h5py/pyarrow/polars** | IO + FMT | **PARTIAL — wiring gap** (Inv E; `loaders.rs:60`) | Route CSV/Excel/Parquet/NumPy/MATLAB through FMT in both io facades + re-freeze goldens. | **L-XL (~6-9 pw)** |
| 9 | **Named-processings axis** (`n_pp`) | DMD | **MISSING end-to-end** (Inv C §4; dead `AxisKind::Processing`) | DMD collation/fusion must reason over the processing axis. A DMD backlog item. | **M-L (~2-4 pw)** |
| 10 | **SpectroDataset/Predictions core** (~409 KB; 22 polars files) | PY (class) + DMD (contract) + DML (pred store) | **PARTIAL** (Inv A §A.4; Inv C ARCHITECTURE:53-58) | The single largest rewrite. **Unknown:** can DML `PredictionStore` host the 0.9.x SQLite+Parquet prediction contract. | **XL (~8-12 pw)** |
| 11 | **Variant orchestration** (orchestrator 119 KB + executor 78 KB) | DML | **READY (core)** (Inv B §1) — **EXCEEDS** structurally | Engine is there; risk is behavioral OOF/refit/leakage parity. Gated on #1+#2 to execute. | **XL (~6-10 pw integration)** |
| 12 | **Python-object → DSL JSON serializer** | PY (dsl_frontend) | **PARTIAL** (Inv B §1; STATUS.md:640-642) | Faithful object→canonical-JSON. Byte-parity vs `pipeline_dsl_nirs4all_compat.json` is the gate, UNVERIFIED. | **M-L (~2-3 pw)** |
| 13 | **Controller dispatch precedence** (prio 6 > prio 10) | DML manifest | **PARTIAL** (Inv A §A.2; precedence-equivalence UNVERIFIED) | `@register_controller` → manifest shim. Equivalence is the gate for the operator layer. | **M (~2 pw)** |
| 14 | **IntervalPLS regressor** (ipls.py 50 KB) | N4M (selectors) + PY (regressor) | **PARTIAL** (Inv D §D.1) | Selection kernels PARITY; rebuild forward/backward/synergy regressor over `interval/bipls/sipls_select`. | **M (~2 pw)** |
| 15 | **DiPLS / SparsePLS / RobustPLS / RecursivePLS** | N4M | **PARTIAL — PRESENT-no-parity** (Inv D §D.4) | Write 4 parity fixtures (legacy toggles + window semantics differ). Removes trendfitter after pinning. | **M (~2-3 pw)** |
| 16 | **RNG-kind parity for stochastic ops** | N4M | **PARTIAL** (Inv D §D.4; n4m.h:362-366) | Audit current RNG; pin each op to `N4M_RNG_PCG64`/`NUMPY_MT`. Mismatch = silent value drift. | **M (~2 pw, schedule-critical)** |
| 17 | **Operator/node registry for studio palette** | PY shims | **PARTIAL** (Inv G §G.2-6) | Thin `BaseEstimator` shims exposing `get_params()`/signature, delegating to libn4m. ~35 KB presets reference class names. | **M-L (~3-4 pw)** |
| 18 | **Classical PLS variants** (SIMPLS/IKPLS/PCR/PLSDA/OPLS/LWPLS/MBPLS) | N4M | **READY** (Inv D §D.1) | Re-point. Removes ikpls/pyopls/sklearn.cross_decomposition. Verify `mbpls` symbol. | **M (~2 pw)** |
| 19 | **AOM-PLS / POP-PLS + strict-operator bank** | N4M | **READY** (Inv D §D.1/D.2) | Delete `_aom_nirs/pls/`, replace with n4m calls. (AOM is live upstream dev — coordinate.) | **M (~2 pw)** |
| 20 | **Preprocessing** (SNV/MSC/EMSC/SG/derivatives/NW/Gaussian/detrend/baselines×9/wavelets×6/OSC/EPO) | N4M | **READY** (Inv D §D.1) | Re-point. Removes pywt, pybaselines, scipy.signal.savgol, scipy.ndimage.gaussian. | **M (~2 pw)** |
| 21 | **Splitters** (Kennard/SPXY/KMeans/KBins/SystematicCircular/SPlit) | N4M (algo) + DML (identity) | **READY** (Inv D §D.1 — corrects Inv A "UNKNOWN") | Re-point. Removes kennard-stone, scipy.cdist, sklearn KMeans/PCA. | **S-M (~1-2 pw)** |
| 22 | **Filters** (X/Y-outlier/high-leverage/quality/composite) | N4M | **READY** (Inv D §D.1) | Re-point. Removes sklearn IsolationForest/LOF/covariance for filtering. | **S (~1 pw)** |
| 23 | **Augmentation** (incl. spline/edge/environmental) | N4M | **READY** (Inv D §D.1 — corrects Inv A "UNKNOWN") | Re-point; gated by RNG-kind audit (#16). | **S-M (~1-2 pw)** |
| 24 | **Feature selection** (CARS/MCUVE/SPA/GA/PSO/VISSA + iPLS-family) | N4M | **READY** (Inv D §D.1 — corrects Inv A "UNKNOWN") | Re-point selectors (iPLS regressor is separate, #14). | **S-M (~1-2 pw)** |
| 25 | **Regression metrics** (RMSE/R²/MAE/bias/RPD/RPIQ/SEP/MAPE) | N4M | **READY** (Inv D/F) | Re-point `core/metrics.eval`. | **S (~1 pw)** |
| 26 | **Classification metrics** | PY (KEEP) | **READY (stays)** (Inv D/F) | Keep in Python; SELECT classification rides as `custom_controller`. | **S (~1 pw)** |
| 27 | **DatasetConfigs / FolderParser / ConfigNormalizer / signal-type detection** | IO | **READY** (Inv E §E.1; parity verbatim) | Delete parsers, re-export DatasetConfigs. `files_parser.py` (32 KB) needs line-diff before deletion. | **S-M (~1-2 pw)** |
| 28 | **Signal-type enforcement** (train-tolerant/predict-strict) | DMD + N4M (convert) | **PARTIAL** (Inv C §3; inert `require_signal_type_match`, model.rs:331-333) | Wire the guard; conversion → libn4m. | **S-M (~1-2 pw)** |
| 29 | **Sample weights** (if surfaced to models) | DMD | **MISSING** (Inv C §4; spectrodataset.py:28 shim) | If models consume weights, no transport contract. Confirm usage. | **S-M (~1-2 pw)** |
| 30 | **KOPLS / OKLMPLS / FCKPLS-model / NLPLS-multikernel** | PY (torch/jax) — KEEP | **MISSING in libn4m** (Inv D §D.4) | **Keep on NN backends, do NOT port.** Route linear/RBF NLPLS to `kernel_pls_fit`. | **S (decision)** |
| 31 | **Synthesis / `generate()`** | PY — KEEP | **READY (stays)** (Inv A/F) | Lowest priority; leave last. | **M (KEEP)** |
| 32 | **Transfer / calibration-transfer selection** (PDS/DS) | N4M + DML + PY (diagnostics) | **PARTIAL** (Inv D §D.1, F §F.4) | Numerics→N4M, orchestration→DML, procrustes/subspace KEEP scipy. | **M (~2 pw)** |
| 33 | **Multi-source X / fusion / collation / repetition** | DMD | **READY** (Inv C §2) | Strong fit; reconcile aggregation-reducer drift (Inv C §6). | **S-M (~1-2 pw)** |
| 34 | **Metadata/headers/units export back to studio** | DMD | **PARTIAL** (Inv C §5; no metadata-export vtable hook) | Add a metadata-export hook if the studio needs columns back. | **S-M (~1-2 pw)** |
| 35 | **Branch-view materialization** (`by_metadata`/`by_tag`/`by_filter`/`by_source`) | DMD provider | **PARTIAL** (Inv B §6; only `by_source` pinned) | Production provider backends for the others. | **M (~2 pw)** |
| 36 | **Workspace metadata/lineage persistence into legacy SQLite** | PY facade | **PARTIAL/UNKNOWN** (Inv G) | DML persists through the facade or the facade dual-writes from DML's lineage DB. | **L (folded into #3)** |

---

## 5. The libn4m numerical-parity coverage map

This is the largest work item. Legend: **PARITY** = present + JSON fixture (1e-8…1e-12) · **PRESENT** = C-ABI symbol + Python wrapper, no dedicated fixture · **PARTIAL** = sub-capability covered, not a 1:1 op · **MISSING** = no equivalent.

### 5.1 PLS / regression models

| nirs4all operator (file) | libn4m id / header | STATUS | Notes |
|---|---|---|---|
| `SIMPLS` (simpls.py, wraps **ikpls**) | `N4M_SOLVER_SIMPLS` / regression.h | **PARITY** | fixtures `pls4all-numpy-simpls`, `synthetic_simpls_*`. ikpls fully replaceable. |
| `IKPLS` (ikpls.py, wraps **ikpls**) | `n4m_estimators_pls_fit`, 6 solvers | **PARITY** | **The ikpls dep (4 files) is fully covered.** |
| `PCR` (pcr.py) | `n4m_estimators_pcr_fit` | **PARITY** | `pls4all-numpy-pcr`, `synthetic_pcr_*` |
| `PLSDA` (plsda.py) | `N4M_ALGO_PLS_DA` / classification.h | **PARITY** | `synthetic_pls_da_{binary,multiclass}` |
| `OPLS` (opls.py, wraps **pyopls**) | `N4M_ALGO_OPLS` | **PARITY** | **pyopls fully covered.** |
| `OPLSDA` (oplsda.py, wraps **pyopls**) | `N4M_ALGO_OPLS_DA` | **PARITY** | `synthetic_opls_da_{binary,multiclass}` |
| `DiPLS` (dipls.py, wraps **trendfitter**) | `n4m_domain_adaptation_di_pls_fit` | **PRESENT** | No dedicated fixture. **trendfitter replaceable but verify parity.** RISK-M. |
| `SparsePLS` (sparsepls.py) | `n4m_estimators_sparse_simpls_fit` | **PRESENT** | `legacy` toggle (Chun-Keles 2010 vs legacy); needs pinning. RISK-M. |
| `LWPLS` (lwpls.py) | `n4m_estimators_lw_pls_fit` | **PARITY** | `synthetic_lw_pls_local_window`; ~7e-16, mirrors `lwpls.py::_lwpls_predict`. Strong. |
| `MBPLS` (mbpls.py) | `n4m_estimators_mb_pls_fit` | **PARITY** | `synthetic_mb_pls_block_weighted`. **Verify symbol in `estimators/multiblock.h` before deleting.** |
| `RobustPLS` (robust_pls.py) | `n4m_estimators_robust_pls_fit` | **PRESENT** | legacy toggle (PRM vs Huber-IRLS); nirs4all variant is JAX/NumPy — parity unverified. RISK-M. |
| `RecursivePLS` (recursive_pls.py) | `n4m_estimators_recursive_pls_run` | **PRESENT** | Window semantics differ (warmup-then-predict). RISK-M. |
| `IntervalPLS` (ipls.py, 50 KB) | `n4m_feature_selection_{interval,bipls,sipls}_select` | **PARTIAL** | Selection kernels PARITY; the forward/backward/synergy **regressor wrapper** must be rebuilt. RISK-M. |
| `KOPLS` (kopls.py, 31 KB, kernel+JAX) | — | **MISSING** | Kernel Orthogonal PLS. No equivalent. |
| `NLPLS`/`KPLS` (nlpls.py, 36 KB, JAX) | `n4m_estimators_kernel_pls_fit` | **PARTIAL** | libn4m has a single-kernel PLS; nirs4all's is a JAX multi-kernel family. Not drop-in. RISK-L/M. |
| `OKLMPLS` (oklmpls.py, 32 KB, JAX) | — | **MISSING** | No equivalent. |
| `FCKPLS` (fckpls.py, 28 KB, JAX) | FCK as *preprocessing* (`N4M_OP_FCK`) | **PARTIAL** | Static featurizer covered; the **learned** FCK-PLS model is NOT (NN). |
| `TabPFNNIRSRegressor` (tabpfn_nirs.py) | — | **MISSING** | TabPFN (NN; KEEP torch). |

### 5.2 AOM / POP family (the headline capability)

| nirs4all operator | libn4m id | STATUS | Notes |
|---|---|---|---|
| `AOMPLSRegressor` / `POPPLSRegressor` (aom_pls.py) | `n4m_model_selection_aom_pls_select`, `pop_pls_select`, sweep/chain-sweep | **PARITY** | `synthetic_aom_global_simpls_cv`, `synthetic_aom_pop_simpls_covariance_cv`. **Strongest-covered advanced capability.** |
| AOM operators (Identity/Detrend/SavGol/FiniteDiff/NorrisWilliams/Whittaker/FCK) | strict-operator bank in `model_selection.h` | **PARITY** | `bench-AOM_v0-aom-operators` (1e-10), `synthetic_aom_{strict,extended_strict}_operators` |
| `AOMRidgeRegressor`/`AOMRidgePLS`/`AOMRidgePLSCV` (aom_ridge.py) | `n4m_estimators_ridge_fit` + superblock funcs | **PRESENT** | Wrappers in `_impl/native_sweeps.py`. No fixture. RISK-M. |
| `AOMRidgeBlender` (aom_ridge.py) | `n4m_ensemble_aom_ridge_blender_fit` | **PRESENT** | `NativeAOMRidgeBlenderRegressor`. No fixture. |
| `AOMMultiKernelRidge`/`AOMKernelizer`/`AOMMultiBranchMKL`/`AOMLocalRidge`/`AOMRidgeAutoSelector` | partial (`aom_ridge_mkl_superblock`, `aom_ridge_active_superblock`) | **PARTIAL/MISSING** | kernelizer/local_ridge/multi_branch_mkl/auto_selector/residual_tabpfn in `_aom_nirs/ridge/` (23 files) NOT 1:1. RISK-L. |
| `FastAOMPLSRidge`/`Single/Hard/Soft ChainPLSRidge`/`SparseMultiKernelRidge` (aom_fast.py) | `aom_chain_{sweep,fixed_fit}`, `aom_chain_ridge_pls` | **PARTIAL** | Chain kernels PARITY (`synthetic_aom_{soft,hard}_preprocessing`); `_aom_nirs/fast/` generators stay Python. RISK-L. |

### 5.3 Preprocessing transforms

| nirs4all op | libn4m id | STATUS |
|---|---|---|
| `StandardNormalVariate`/`Local`/`Robust` | `snv`/`lsnv`/`rnv` (scatter.h) | **PARITY** |
| `MSC`/`EMSC` | `n4m_transform_{msc,emsc}_*` | **PARITY** |
| `SavitzkyGolay` (uses **scipy.savgol**) | `n4m_transform_savitzky_golay_*` | **PARITY** — cuts scipy.signal.savgol_filter |
| `First/SecondDerivative`/`Derivate` | `first/second_derivative`, `derivate` | **PARITY** |
| `NorrisWilliams` | `n4m_transform_norris_williams_*` | **PARITY** |
| `Gaussian` (uses **scipy.ndimage**) | `n4m_transform_gaussian_*` | **PARITY** — cuts scipy.ndimage |
| `Detrend`/`Baseline` | `detrend`, `baseline_center` | **PARITY** |
| `AreaNormalization`/`Normalize`/`SimpleScale`/`LogTransform` | `area_norm`/`normalize`/`simple_scale`/`log_transform` | **PARITY** |
| `Wavelet`/`Haar`/`WaveletDenoise/Features/PCA/SVD` (use **pywt**) | `n4m_transform_wavelet*`, `haar`, `wavelet_{denoise,features,pca,svd}` | **PARITY** — fully cuts pywt (3 files) |
| `AirPLS/ArPLS/IModPoly/ModPoly/SNIP/RollingBall/IASLS/BEADS/ASLSBaseline` (use **pybaselines**) | `n4m_transform_{airpls,arpls,imodpoly,modpoly,snip,rolling_ball,iasls,beads,asls}_*` | **PARITY** (all 9) — fully cuts pybaselines (3 files) |
| `OSC`/`EPO` | `n4m_transform_osc_*`, `domain_adaptation_epo_*` | **PARITY** |
| `CARS`/`MCUVE` | `cars_select`, `uve_select`/`emcuve_select` | **PARITY** |
| `FlexiblePCA`/`FlexibleSVD` | `flexible_pca`/`flexible_svd` (decomposition.h) | **PARITY** — cuts sklearn.decomposition |
| `Resampler`/`Crop`/`ResampleTransformer` (use **scipy.interp1d**) | `resampler`/`crop`/`resample` | **PARTIAL** — verify interp parity. RISK-M. |
| `ToAbsorbance`/`FromAbsorbance`/`Pct↔Frac`/`KubelkaMunk`/`SignalTypeConverter` | `to_absorbance`/`from_absorbance`/`pct_to_frac`/`frac_to_pct`/`kubelka_munk` + `signal_type_detector` | **PARITY** |
| `IntegerKBinsDiscretizer`/`RangeDiscretizer` | `kbins_discretizer`/`range_discretizer` | **PARITY** — cuts sklearn.preprocessing.KBinsDiscretizer |
| `FCKStaticTransformer` (uses **scipy**) | `n4m_transform_fck_static_*` | **PARITY** |
| `FlattenPreprocessing` | — | **N/A** (pure reshape) |

### 5.4 Splitters

| nirs4all op | libn4m id | STATUS |
|---|---|---|
| `KennardStoneSplitter` (uses **kennard-stone**) | `n4m_model_selection_kennard_stone_*` | **PARITY** — cuts kennard-stone |
| `SPXYSplitter`/`SPXYFold`/`SPXYGFold` | `spxy`/`spxy_fold`/`spxy_g_fold` | **PARITY** |
| `KMeansSplitter` | `kmeans` split | **PARITY** — cuts sklearn KMeans for splitting |
| `KBinsStratifiedSplitter` | `kbins_stratified` | **PARITY** |
| `BinnedStratifiedGroupKFold` | `binned_strat_group_kfold` | **PARITY** |
| `SystematicCircularSplitter` | `systematic_circular` | **PARITY** |
| `SPlitSplitter` | `data_twinning`/`split_splitter` | **PARITY** |
| `CustomSplitter`/`GroupedSplitterWrapper` | — | **N/A** (Python orchestration) |

### 5.5 Filters (outlier / quality)

| nirs4all op | libn4m id | STATUS |
|---|---|---|
| `XOutlierFilter` (Mahalanobis/IsolationForest/LOF/PCA-residual/leverage) | `x_outlier_*`, `high_leverage_*`, `hotelling_t2`, `q_residuals` | **PARITY** — cuts sklearn IsolationForest + LOF for filtering |
| `YOutlierFilter` (IQR/MAD/zscore/percentile) | `y_outlier_*` | **PARITY** (all 4) |
| `HighLeverageFilter` | `high_leverage_filter` | **PARITY** |
| `SpectralQualityFilter` | `spectral_quality_filter` | **PARITY** |
| `CompositeFilter` | `composite_filter` | **PARITY** |
| `MetadataFilter` | — | **N/A** (keep in nirs4all) |

### 5.6 Augmentation (all 50 fixtures verified present)

| Family | libn4m | STATUS |
|---|---|---|
| spectral.py (18: Gaussian/Spike/Hetero-Noise, Baseline-Drift, Wavelength-Shift/Stretch/Warp, MagnitudeWarp, BandPerturbation, Jitter, UnsharpMask, BandMasking, ChannelDropout, LocalClip, Mixup, LocalMixup, ScatterSimMSC) | `n4m_augmentation_*` | **PARITY** — every one has `aug_*_v1.json` |
| scattering.py (ParticleSize, EMSCDistortion) | `particle_size`, `emsc_distort` | **PARITY** |
| synthesis.py (PathLength, BatchEffect, InstrumentalBroadening, HeteroNoise, DeadBand) | `path_length`,`batch_effect`,`instrument_broaden`,`hetero_noise`,`dead_band` | **PARITY** |
| environmental.py (Temperature, Moisture) | `temperature`,`moisture` | **PRESENT** (`aug_phase17` covers env block) |
| edge_artifacts.py (DetectorRollOff, StrayLight, EdgeCurvature, TruncatedPeak, EdgeArtifacts) | `detector_rolloff`,`stray_light`,`edge_curvature`,`truncated_peak`,`edge_artifacts` | **PARITY** |
| splines.py (Smoothing, X/Y Perturb, Simplification) | `spline_*` | **PARITY** (5 fixtures) |
| random.py (Rotate_Translate, Random_X_Operation) | `rotate_translate`, `random_x_op` | **PARITY** |

**RNG parity note (load-bearing):** libn4m ships a PCG64 **bit-exact vs `numpy.random.default_rng`** (`n4m.h:362-366`, fixture `_rng_pcg64_stream_v1`). If nirs4all's augmenters use `RandomState` (MT19937) instead, there is a **stream-mismatch risk** — libn4m also exposes `N4M_RNG_NUMPY_MT`, but each op must be pinned to the right kind (story S0.4).

### 5.7 The vendored `_aom_nirs` debt (59 files)

**Verdict: SPLIT.** The PLS/strict-operator AOM core is in libn4m and parity-tested; the ridge and "fast" research families are NOT 1:1.

- **`_aom_nirs/pls/` (18 files)** — **Covered.** AOM-PLS / POP-PLS global+per-component CV selection is `aom_pls_select`/`pop_pls_select`/sweep/chain-sweep, gated by `bench-AOM_v0-*` (1e-8/1e-10) + `synthetic_aom_*`. **Deletable now**, replaced by `n4m` calls. The AOM moment-route is the live upstream work (memory `studio-lite-methods-hold` — do not push nirs4all-methods).
- **`_aom_nirs/ridge/` (23 files)** — **Partially covered.** libn4m has Ridge (`ridge_fit`), ridge-PLS, the blender (`aom_ridge_blender_fit`), and superblock designs. **NOT in libn4m:** kernelizer + MKL learning, `local_ridge`, `auto_selector`, `residual_tabpfn`/`tabpfn_candidate` (TabPFN stays torch). The MKL/kernel-ridge numerics need porting OR re-expression over `ridge_fit` + `moments`.
- **`_aom_nirs/fast/` (15 files)** — **Partially covered.** Chain sweep/fixed-fit/ridge-PLS kernels are in libn4m + fixture'd. **grammar-driven chain generation, xcorr fast-screening, low-rank approximation** are research scaffolding that the sweep kernels assume as input — those stay Python (they produce candidate specs; libn4m scores them).

**Effort to retire `_aom_nirs`:** `pls/` deletable now (**M**); `ridge/` MKL+kernelizer port is the real debt (**L**); `fast/` generators mostly keepable Python (**S–M**).

### 5.8 libn4m gaps to reach parity (drives §10 epics E2/E14)

**MISSING — port or keep on NN backend:** KOPLS (**L**, keep JAX), OKLMPLS (**L**, keep in nirs4all-lab), FCK-PLS learned model (**L**, KEEP torch/jax), TabPFN (**N/A**, KEEP torch).

**PARTIAL — wrapper/orchestration work:** IntervalPLS regressor (**M**), AOM-Ridge MKL/kernelizer/local-ridge (**L**), AOM-fast generators (**S–M**, keep Python), NLPLS/KPLS multi-kernel (**M**, keep JAX, route linear/RBF to `kernel_pls_fit`).

**PRESENT-NO-PARITY — pin before cutover:** DiPLS vs trendfitter (**S**), SparsePLS/RobustPLS/RecursivePLS (**M**), AOM-Ridge superblock/blender (**S**), environmental augmenters (**S**).

**Cross-cutting:** RNG-kind pinning (**M, RISK-HIGH** if not audited first), resampling/interpolation parity (**S**), stride/dtype copy cost (**S**, perf footnote).

**Total libn4m-side parity backlog: ~10–14 person-weeks**, of which the RNG-kind audit and the controller/preset re-pointing (~35 KB of presets) are schedule-critical despite low numerical risk.

**Single biggest verdict:** the numerical core is **not** the bottleneck. The bottleneck is (a) deciding which kernel/NN models stay on torch/jax, (b) porting/orchestrating the AOM-Ridge MKL family, and (c) the RNG-kind audit + controller/preset re-pointing.

---

## 6. Retained Python surface: NN controllers, optuna, shap re-attachment

The Rust cutover does not remove Python. The retained surface is exactly: the operator implementations that are not numerical-core (NN/AutoML/TabPFN), the search driver (optuna), the explainer (shap), and the thin glue marshalling these to/from dag-ml as host controllers through the **host-controller transport** — the shipped **JSONL process adapter** (the `sklearn_production_controller.py` pattern is the reference, `HOST_ADAPTER_BACKLOG.md`), pending the M0 decision (§3.3).

### 6.1 NN controller inventory and re-attach

All NN controllers subclass `BaseModelController` (`controllers/models/base_model.py:52`) and implement a **6-method protocol** (`base_model.py:100-197`): `_get_model_instance`, `_train_model(model, X_train, y_train, X_val, y_val, **train_params)`, `_predict_model`, `_prepare_data`, `_clone_model`, `_evaluate_model`, plus optional `_predict_proba_model`. **This protocol IS the host-controller contract** — it cleanly separates build/fit/predict/prep/clone/score and maps directly onto a dag-ml `ControllerManifest` + a **JSONL process-adapter worker** (the shipped transport; §3.3).

| Controller | File | Wraps | Re-attach |
|---|---|---|---|
| `PyTorchModelController` | `torch_model.py:67` | `torch.nn.Module`; custom loop, device mgmt, `state_dict` warm-start (`:437`) | KEEP. `operator_kind=model`, **persistent JSONL process-adapter worker** (warm GPU model survives across phases) + `stateful_refit_artifacts`. Artifact = `torch.save(state_dict)`. |
| `TensorFlowModelController` | `tensorflow_model.py` | `keras.Model`; `compile/fit` (`:251`), `clone_model` (`:561`) | KEEP. Artifact = `.keras`. |
| `JAXModelController` | `jax_model.py` | `flax.linen` + jax train step (`:173`) | KEEP. Artifact = orbax/msgpack. |
| `AutoGluonModelController` | `autogluon_model.py:50` | `TabularPredictor` | KEEP. Owns its own internal CV — single opaque fit/predict node. |
| `tabpfn_nirs` / `residual_tabpfn` | `tabpfn_nirs.py`, `_aom_nirs/ridge/residual_tabpfn.py` | TabPFN (torch-backed) | KEEP (rides the torch extra). NN engine → host controller. |
| `ResidualModelController` | `residual_model.py` | base+residual composition | KEEP as Python composite (or a 2-node dag-ml graph; simplest to keep intact). |
| `MetaModelController` | `meta_model.py` + `stacking/` | stacking meta-learner over branch OOF | **RISK/boundary:** stacking-over-OOF is dag-ml's (leakage-safe sample_id join). Meta **estimator** stays Python/N4M, but **OOF assembly in `stacking/` must move to dag-ml**. Largest re-attach risk in the model layer. |

**train_params / finetune_params flow (FACT):** `execute()` reads `model_config['train_params']`/`['finetune_params']` (`base_model.py:547,691`); `_dispatch_execution` (`:662`) routes to finetune when present and not REFIT. `train_params` pass verbatim as `**kwargs` into `_train_model`. On the dag-ml side these become the per-node operator payload + a train-config blob the host controller consumes; dag-ml never interprets them (only fingerprints them).

### 6.2 optuna re-attach to SELECT/campaign

**Today (FACT):** `OptunaManager.optimize` (`optimization/optuna.py:485+`) owns the entire search loop. The objective **trains the model in-process** by calling the controller's own `_get_model_instance`/`_prepare_data`/`_train_model`/`_evaluate_model` across folds (`:610-733`). Strategies: grouped/individual/single/multiphase. Samplers: TPE/Random/CMA-ES/Grid + a custom `BinarySearchSampler` for unimodal ints like PLS `n_components` (`:52`). Pruning (Median/SH/Hyperband) reports per-fold intermediate scores. The search lives **under one pipeline step** (`finetune_params`) — inner CV inside one FIT node, not a campaign-level sweep.

**The fork (COORDINATOR_SPEC.md:290-291: "compile-time generation of variants/search spaces belongs to dag-ml"):**
- **(A) dag-ml owns the sweep** — any *enumerated* search (`_grid_`/`_or_`/`_range_`/`_log_range_`) becomes a CampaignPlan search space; dag-ml runs FIT_CV per variant, joins OOF, ranks via SELECT. Optuna not in the loop. Leakage-safe, fingerprinted.
- **(B) Python keeps the *adaptive* sweep** — TPE/CMA-ES/binary/pruning are sequential-adaptive; **dag-ml has no ask-tell/candidate-feedback hook** (STATUS.md:643-644 confirms). So adaptive HPO must stay a Python **outer driver**: optuna proposes a candidate → emits it as a single-variant dag-ml campaign → reads back the CV/OOF score → tells optuna → repeats.

**Recommendation:** KEEP `optimization/optuna.py` as the model-(B) outer driver but **strip its in-process fold-training** — the objective stops calling `controller._train_model` directly and instead submits a one-variant dag-ml campaign and reads its score. `BinarySearchSampler` and param-spec sampling stay (no Rust equivalent). `n_jobs` parallel trials and the `joblib.Parallel` fold parallelism (`base_model.py:1036`) are **CUT** (dag-ml owns parallel execution).

### 6.3 shap re-attach to EXPLAIN

**Today (FACT):** `nirs4all.explain()` → `PipelineRunner.explain` → `pipeline/explainer.py:60`. The runner re-runs in `explain` mode with `_capture_model=True`; the model controller calls `runtime_context.explainer.capture_model(model, self)` (`base_model.py:1338`). `explainer.py:170` unpacks `(model, controller)`, pulls `X_test`/`y_test` via `controller.get_preferred_layout()`, hands them to `ShapAnalyzer.explain_model` (`visualization/analysis/shap.py:65`). `_create_explainer` (`shap.py:259`) auto-selects Tree/Linear/Deep/Kernel by class name; the kernel fallback wraps `model.predict`/`predict_proba` (`shap.py:371-375`). Keras is rejected on the kernel path (`shap.py:347-368`) — SHAP today effectively works on sklearn-API and tree models.

**Re-attach (grounded INFERENCE):** dag-ml's EXPLAIN consumes "bundle, new data provider handle, target node/method → explanation payload refs" (COORDINATOR_SPEC.md:223). The fitted model crosses the ABI as an **opaque handle** (`dag-ml/CLAUDE.md:156-157`). So EXPLAIN cannot run SHAP itself — it **calls back into the host controller** to materialize the model behind the handle and expose a `predict(X)->y` (and `predict_proba`) closure, which is exactly what `shap.KernelExplainer`/`TreeExplainer` need. Therefore:
- KEEP `ShapAnalyzer` and `capture_model`, re-targeted to receive the **dag-ml handle + a host predict callback** instead of the Python controller. The "predict fn" abstraction (`shap.py:373`) is already the right seam.
- The `sklearn/NIRSPipeline` SHAP wrapper stays as a convenience for the same predict-fn contract.
- shap dependency, matplotlib rendering, binning/spectral viz are all retained Python.

### 6.4 Summary of the retained surface

- The 6 NN/composite controllers + AutoGluon + TabPFN (`controllers/models/{torch,tensorflow,jax,autogluon,residual,meta}*`, `stacking/`); the optuna outer ask-tell driver (minus in-process fold training + joblib); the shap explainer (`visualization/analysis/shap.py`, `sklearn/` NIRSPipeline, `capture_model` seam); the classification-metric scorers + a handful of scipy.stats/special statistics; `synthesis/` (offline); target/metadata label encoders. Plus the thin dag-ml host-controller marshalling glue.

---

## 7. Downstream contracts & studio blast radius + contract-preservation plan

### 7.1 Blast radius: the studio is the entire surface

Of the five named consumers, **only `nirs4all-studio` imports the Python `nirs4all` package** — and it reaches deep into *private* internals (`WorkspaceStore._fetch_pl`, raw `store.sqlite` SQL, `pipeline.analysis.*`, `operators.*` by introspection). **Count (use a reproducible definition — flagged by the Codex review):** `grep -rl 'import nirs4all\|from nirs4all' nirs4all-studio/api` → **~28 backend API files**; ~112 import occurrences in `api/`, ~133 across all studio Python (37 files). The migration checklist must **freeze the exact file list** from a checked-in command, not a prose number. The other four consumers are **not at risk** (FACT):
- `nirs4all-aom` (`pyproject.toml:63`): nirs4all is only an "Instrumentation context" link; the dependency runs the other way.
- `nirs4all-datasets` (`reproduce.py:85`): imports `nirs4all_io`, never the main lib.
- `nirs4all-lite`: references `nirs4all.operators.*` only as class-name **strings** in a parity oracle; it already *is* the Rust path.
- `nirs4all-web`: pure TS/WASM over `nirs4all-lite`; no Python `nirs4all`.

The studio already guards the import (`try: import nirs4all … except ImportError`, e.g. `system.py:85-88`, `lazy_imports.py`), so it boots without the lib — the swap can lean on that.

### 7.2 Consumer/contract table

| Consumer surface | Path | Break risk | Mitigation |
|---|---|---|---|
| **public API** (run/predict/explain/retrain) | subprocess `nirs4all_adapter.py:492`; `from nirs4all.sklearn import NIRSPipeline` (analysis.py:533/573) | **Medium** — signatures stable, behavior changes if numerics move | Keep facade identical; parity oracle (§7.4). |
| **Result objects** | `.best_score`, `.top(n)`, `.export()`, `per_dataset` (api/result.py:281,1180,1376) | **Medium** | Re-emit same dataclasses from dag-ml tables. |
| **WorkspaceStore (SQLite)** | 11 files; `store_adapter.py`+`workspace_scanner.py` call private `_fetch_pl`, `query_predictions`, `top_predictions`, raw SQL (`store_adapter.py:1071`) | **HIGH** — deepest coupling; private API + on-disk schema (`SCHEMA_VERSION=2`, tables runs/pipelines/chains/predictions/artifacts/logs/projects) | Preserve `WorkspaceStore` facade with **identical method set + SQL DDL + `PRAGMA user_version`**; dag-ml writes through it. Load-bearing item. |
| **Parquet arrays** | `*.meta.parquet` via `pd.read_parquet` (workspace_scanner.py:268); `arrays/<ds>.parquet` | **HIGH** — direct file-format dependency | Keep Parquet layout byte-stable. |
| **.n4a bundle** | `BundleLoader`/`NIRSBundle` (runs.py:780, lazy_imports.py:236); `RunResult.export()` | **HIGH (semantic)** — `.n4a` stores `.joblib`-pickled Python operator objects (generator.py:250,649); dag-ml stores opaque refs, NOT model bytes | See §7.3 — Python adapter wrapping dag-ml refit artifacts into the joblib-in-zip layout, OR `.n4a` v2 (breaking). |
| **operators registry** | `models.py`/`preprocessing.py`/`automl.py` introspect operator `__init__` signatures + docstrings; `CONTROLLER_REGISTRY` | **HIGH (UI-driving)** — palette generated by `inspect`; libn4m operators are C-ABI | Keep thin Python operator shims exposing `get_params()`/signature; or ship a static node-registry JSON. |
| **SpectroDataset / DatasetConfigs** | 5 files each (lazy_imports.py:157-163, spectra.py:183, router_datasets.py) | **Medium** — moves to io | Facade over io's materialize path. |
| **analysis/diagnostics** | `pipeline.analysis.{model_diagnostics,topology,shape_inference,splitter_config}`, `compute_pca_projection`, `visualization.analysis.{shap,transfer}` | **Medium** | Python compute on predictions; repoint inputs to dag-ml tables. |
| **metrics** | `core.metrics.eval_multi/get_available_metrics`, `get_metric_info` (4 files) | **Low** | Thin Python passthrough keeps names stable. |

### 7.3 Contract-by-contract: PRESERVE-behind-facade vs BREAKING

1. **Public API → PRESERVE.** Pure Python facade; signatures + dataclasses decoupled from compute. The studio calls via subprocess, so `import nirs4all; nirs4all.run(...)` returning `.best_score/.top()/.export()/.per_dataset` satisfies it. **explain stays Python** (shap KEEP). **generate stays Python** (synthesis).
2. **Result objects → PRESERVE.** Thin wrappers over a Predictions facade + `per_dataset`. Repopulate from dag-ml's store. Risk only in *values* (numerics), caught by the oracle.
3. **Workspace SQLite → PRESERVE-behind-facade (hardest item).** `SCHEMA_VERSION=2`, 7 tables, `PRAGMA user_version`. Studio reads via `WorkspaceStore` AND raw SQL. **Verdict:** keep `WorkspaceStore` as a Python class with the exact public + de-facto-private (`_fetch_pl`) method set and the same DDL; dag-ml persists through this facade (or mirror its lineage DB into the legacy schema on write). **Do NOT change table/column names without a major bump** — the studio's hand-written SQL silently breaks.
4. **Parquet array layout → PRESERVE.** `arrays/<dataset>.parquet` + `*.meta.parquet`, read by `pd.read_parquet`. **RISK/contradiction:** removing polars+pyarrow conflicts with this; the workspace store is polars-backed (`workspace_store.py:42`). **Resolution (§3.4):** retain pyarrow storage-only, drop polars. Flag explicitly.
5. **`.n4a` bundle → BREAKING unless adapted (sharpest conflict).** FACT: `.n4a` = ZIP + `manifest.json` (`bundle_format_version="1.0"`) + `artifacts/step_*_*.joblib`, each a `joblib.dump` of the live operator object (generator.py:250,649; loader.py:337). dag-ml stores portable `ArtifactRef` handles + fingerprints and is operator-external — it never holds model bytes. Two outcomes:
   - **(a) Preserve `.n4a` v1.0 behind facade:** host pulls host-owned fitted operators and re-pickles them. **Blocker:** a libn4m PLS model is a C-ABI handle, not joblib-able. Needs a pickleable Python wrapper per libn4m model presenting `predict()`.
   - **(b) `.n4a` v2 (BREAKING, major bump):** embeds dag-ml's `ArtifactRef` + libn4m serialized state. Studio `BundleLoader` and saved `.n4a` files break.
   - **Recommend (a) for the cutover window, (b) as the announced major bump.**
6. **Operator/node registry → BREAKING risk for the UI, not the data.** The palette `inspect`-s Python class `__init__` signatures; libn4m operators have no Python `__init__`. **Mitigation:** thin Python operator shims (subclassing `BaseEstimator`/`TransformerMixin` — the x75 surface) exposing `get_params()`/signatures while delegating to libn4m. Consistent with dag-ml's "operators are external" design — the shims *are* the host operators.
7. **Run manifest (`runs/<ds>/NNNN_xxx/manifest.yaml`) → PRESERVE.** YAML; keep keys stable. Low risk.

### 7.4 Compatibility test harness (parity oracle)

Because the swap is signature-preserving but **numerics- and bytes-changing**, the only safe gate is a **golden-run differential harness** (modeled on `nirs4all-lite/scripts/parity/generate_python_oracle.py`, `nirs4all-aom/tests/.../test_parity_with_production.py`):

1. **Freeze golden runs (pre-swap):** on the current backend, run a matrix of pipelines × datasets covering every controller path the studio exercises. Snapshot: `RunResult.top(n)` rows, `best_score/best_rmse/best_r2`, the full predictions table, the `store.sqlite` (every table dumped), the `*.parquet` arrays, and the `.n4a` (manifest + per-artifact `predict()` on a fixed probe matrix).
2. **Replay post-swap, assert three layers:**
   - **Schema/shape parity (exact, zero tolerance):** SQLite DDL + `user_version`, columns, Parquet schema, `.n4a` manifest keys, Result-object fields.
   - **Numeric parity (tolerance-banded, declared per operator as the new contract):** predictions and scores within agreed atol/rtol (libn4m vs sklearn PLS differ ~1e-6–1e-4). Use `.n4a` round-trip `predict()` on a frozen probe matrix as the bundle oracle — never pickled bytes.
   - **API-call parity:** drive through the studio's own subprocess adapter (`nirs4all_adapter.py`) and `store_adapter`/`workspace_scanner` read paths so the harness exercises the exact private surfaces.
3. **Wire into both gates:** a `pytest` job in nirs4all CI **and** an integration job in `nirs4all-studio` CI (spin FastAPI against a swapped nirs4all, assert byte-identical schemas + tolerance-equal numbers).
4. **Effort:** oracle + matrix = **M (~2–3 pw)**; making the facades pass it = **L–XL (~6–10 pw)**, dominated by the `.n4a` joblib↔handle round-trip and the polars/pyarrow-vs-Parquet contradiction.

### 7.5 Flags (UNKNOWN / RISK)

- **RISK (direct contradiction):** "remove polars+pyarrow" vs "preserve workspace Parquet." Decided in favor of the contract: retain pyarrow storage-only, remove polars.
- **RISK (highest blast radius):** `store_adapter.py` issues raw SQL against `store.sqlite` and calls private `_fetch_pl`. Any column rename silently breaks the studio. (This already violates "studio never reimplements nirs4all" — worth flagging to studio owners regardless.)
- **UNKNOWN:** whether dag-ml can persist *into* the legacy SQLite schema vs insisting on its own lineage DB. If not, the facade must dual-write.
- **UNKNOWN:** whether a libn4m fitted model exposes a Python-pickleable wrapper today. If not, `.n4a` v1.0 preservation is blocked → `.n4a` v2 (breaking).

Key paths: `/home/delete/nirs4all/nirs4all-studio/api/{store_adapter.py,workspace_scanner.py,lazy_imports.py,models.py,preprocessing.py,nirs4all_adapter.py}`; `/home/delete/nirs4all/nirs4all/nirs4all/api/result.py:281,1180,1376`; `/home/delete/nirs4all/nirs4all/nirs4all/pipeline/bundle/generator.py:54,250,649`; `/home/delete/nirs4all/nirs4all/nirs4all/pipeline/storage/store_schema.py:28`; `/home/delete/nirs4all/dag-ml/docs/STATUS.md:158-176`.

---

## 8. Risk register

Likelihood × Impact on 1–5 (5 = near-certain / catastrophic). Sorted by L×I.

| ID | Risk | L | I | L×I | Mitigation | Owner-area |
|---|---|---|---|---|---|---|
| **R3** | **Workspace + `.n4a` contract preservation, with a polars/pyarrow contradiction.** dag-ml is manifest-only / refuses model serialization; nirs4all embeds joblib blobs + a specific Parquet/SQLite schema the studio reads with **raw SQL**. "Remove pyarrow" *contradicts* preserving Parquet. Any column rename silently breaks studio. | 5 | 5 | **25** | Retain pyarrow storage-only (write frozen Parquet), remove polars by rewriting `array_store` to pyarrow/numpy. Keep `WorkspaceStore` facade with identical DDL + `_fetch_pl` + `user_version`; dag-ml writes through it (or dual-writes). Golden-run harness (§7.4) as acceptance gate. | Python facade |
| **R1** | **No decided/runnable controller-execution transport for host-Python ops (CRITICAL, re-grounded).** `dag-ml-py` is JSON-only and does not execute controllers or own buffers; native PyO3/C-ABI wrappers are out of scope; the only shipped cross-language path is the **JSONL process adapter**, whose per-fold serialization of wide NIRS X is unmeasured at sweep scale. The original "pyo3 borrowed-view default" does not exist. *Nothing NN/feature-heavy runs until the transport is decided.* | 4 | 5 | **20** | **M0 first (Spike S0): controller-transport ADR + proof.** Default Option A (adopt JSONL + batching + host-side data); build Option B (in-proc Py runtime in dag-ml) only if S0's latency benchmark fails. Wire borrowed-view provider (S1) regardless. Gate-zero. | M0 decision: dag-ml owners + host |
| **R2** | **NN-controller across the transport: latency + correctness.** No torch/tf/jax adapter exists; per-fold task round-trips + GPU device mgmt + state_dict stickiness unproven; JSON serialization latency for sweeps is the open question. | 4 | 5 | **20** | Build the torch controller on the M0 transport (JSONL persistent worker). Prove identical loss curve (Spike S2); warm-worker REFIT→PREDICT stickiness; process isolation sidesteps the GIL. Measure sweep latency; escalate to Option B if it fails budget. | Python host + dag-ml |
| **R5** | **Numerical parity drift (libn4m vs ikpls/sklearn/scipy goldens).** Even at 1e-6–1e-4, scores/predictions change; studio surfaces exact numbers; golden tests diff. Unfixtured: DiPLS/SparsePLS/Robust/Recursive, resampler interp1d, mbpls/bare-logistic symbols. | 4 | 4 | **16** | Declare a tolerance band as part of the new contract and surface it to studio. Write the 4 missing fixtures before deleting trendfitter etc. Verify mbpls/multiblock.h + bare-logistic head. Use `.n4a` probe-`predict()` as bundle oracle. | libn4m + facade |
| **R6** | **RNG-kind mismatch = silent value drift masquerading as a parity bug.** Every stochastic op must pin PCG64 vs NUMPY_MT. Undetected until augmentation/selection subtly diverge. | 4 | 4 | **16** | Audit nirs4all's current RNG first (`RandomState`/MT19937 vs `default_rng`); pin each op. Per-op RNG-stream fixtures. Do the audit before any stochastic cutover. | libn4m binding |
| **R9** | **Studio webapp breakage — ~28 backend API files import nirs4all (freeze the exact list), deep private coupling.** Signature-stable but behavior/bytes change. | 4 | 4 | **16** | Lean on the existing `try: import nirs4all` guard. Preserve every private surface behind the facade. Wire the parity harness into studio CI through `nirs4all_adapter`/`store_adapter`. Flag the raw-SQL coupling to studio owners. | Python facade + studio |
| **R11** | **Packaging: C++17 (libn4m) + Rust pyo3 (dag-ml/data) + n4m wheels across linux/mac/win × the torch/tf/jax matrix.** Three native toolchains × 3 OSes × NN ABIs. Memory note `methods-cpp-coverage-recipe` records a conda libmvec/sysroot link bug. | 4 | 4 | **16** | Stand up the wheel-build matrix early (manylinux, macOS arm64+x86, win). Clean PATH per the coverage recipe to dodge libmvec/sysroot. NN backends as optional extras (decouples their matrix). Treat wheel-build as a first-class deliverable. | Build/release |
| **R4** | **`.n4a` round-trip (DOWNGRADED after review).** A libn4m fitted model is a C-ABI handle — but the **pickle pattern already ships**: `_Pls4allModelEstimator` persists `_bundle_` bytes and drops `_model_handle_`/`_model_ctx_` from `__getstate__` (`pls4all/sklearn/_base.py:158-176`). So v1 preservation is a **known wrapper contract**, not an unknown. | 2 | 4 | **8** | E10 requires every libn4m host wrapper to implement bundle-byte pickle/deepcopy (the shipped pattern). S3 confirms on a fresh `.n4a` round-trip. `.n4a` v2 only if a non-pls4all model can't carry bundle bytes. | Python bundle facade + n4m |
| **R7** | **OOF/leakage parity is a *correct* behavioral break.** dag-ml refuses positional/NaN-filled OOF joins nirs4all `MetaModelController` tolerates (meta_model.py:907). Incomplete-fold stacking pipelines rejected. | 4 | 3 | **12** | Migrate `stacking/` OOF assembly to dag-ml (don't reimplement). Inventory existing stacking pipelines; provide a migration note + `leakage_acknowledged` escape hatch. Frame as a correctness improvement. | dag-ml |
| **R8** | **optuna ↔ dag-ml SELECT has no native hook.** dag-ml has no ask-tell callback. If the team assumes dag-ml absorbs HPO, it won't. | 3 | 4 | **12** | Confirmed: optuna stays a Python outer driver; strip in-process fold-training. Keep BinarySearchSampler/param-spec machinery. Validate per-trial recompile cost. | Python (optuna) |
| **R10** | **Performance/throughput regression (elevated — the JSONL path is now primary, not a fallback).** Per-fold/per-trial JSON serialization on the process adapter is O(variants×folds×n×p) on wide spectra. | 4 | 4 | **16** | Reduce serialization, not assume it away: **task batching** (`accepts_task_batch`), keep wide X **host-side** and pass sample-id selections + a data handle (dag-ml-data keys by identity), **persistent workers**, native libn4m ops bypass Python entirely. **Measure** (Spike S0) before committing; escalate to Option B if budget fails. | dag-ml + host |
| **R12** | **sklearn-protocol break for third-party operators.** Retiring `matches()`/`@register_controller` as runtime router changes the extension model. Precedence-equivalence (prio 6 > prio 10) UNVERIFIED. | 3 | 4 | **12** | Keep `@register_controller` as a manifest-emitting shim; keep `BaseEstimator`/`TransformerMixin` as authoring protocol. Build the precedence-equivalence integration test (story S6). Document the manifest extension path. | dag-ml + Python shims |
| **R13** | **Two-language debugging & observability.** A failed fold spans Python → pyo3 → Rust → C ABI → C++. Stack traces, panics-across-FFI, lineage of a wrong number become hard. | 4 | 3 | **12** | Invest in cross-boundary error propagation (Rust panic → Python exception with context), structured logging carrying node/variant/fold ids, and dag-ml lineage/replay as the debugging substrate. Add a "single-fold replay in pure Python" debug mode. | All |
| **R16** | **Team/skills: Rust + C++ vs Python.** The cutover demands C++17, Rust+pyo3, Python, and FFI/ABI debugging. A Python-centric team faces a real ramp. | 3 | 4 | **12** | Sequence so Python-side facades/adapters proceed in parallel with a smaller Rust/C++ core group. Use the inventories as the shared map. Pair on the first NN adapter + first provider wiring. Budget ramp explicitly. | Org/planning |
| **R17** | **Multi-source / fold semantics divergence.** dag-ml-data validates folds but doesn't own them; dag-ml owns OOF; libn4m produces assignments; the host stitches all three. Subtle `split_unit` default mismatch (repetition→sample, group dominance) could mis-assign folds. | 3 | 4 | **12** | Conformance-test fold identity end-to-end against nirs4all's current assignments on golden datasets. Verify `split_unit` defaults. | dag-ml + libn4m |
| **R18** | **io↔formats tabular wiring is greenfield-ish in two languages.** Until rewired in both Python and Rust, scipy.io/h5py/pyarrow/polars are *not removable* from ingest. | 4 | 3 | **12** | Route CSV/Excel/Parquet/NumPy/MATLAB through formats in both io facades; re-freeze goldens. Sequence the `.mat` path first. | nirs4all-io + formats |
| **R14** | **Maturity of the dag-ml process-adapter (now the PRIMARY Python transport, elevated).** Worker pool/watchdog/retries/persistent-worker stickiness/back-pressure are smoke/example level; nirs4all runs it at full sweep × fold × NN scale. The whole host-Python path depends on it. | 4 | 4 | **16** | Harden the JSONL adapter to production: pool lifecycle, watchdog/timeout/retry, persistent stateful workers (warm GPU), structured `AdapterTaskError` survival, back-pressure. Conformance-test under realistic fold counts. Jointly owned with dag-ml. | dag-ml |
| **R15** | **Named-processings axis gap forces lossy flattening.** `AxisKind::Processing` is dead; the studio displays named processings. | 3 | 3 | **9** | Either land the processing-axis in dag-ml-data (item #9) or carry processings as namespaced columns + a host-side name→column map. Decide before the SpectroDataset rewrite (E11). | dag-ml-data |
| **R19** | **DSL byte-parity unverified.** Host-emitted `pipeline_dsl` JSON must match `pipeline_dsl_nirs4all_compat.json`. | 3 | 3 | **9** | Build the object→JSON serializer against the compat fixtures as the gate. Start with what the studio emits. | Python (dsl_frontend) |
| **R20** | **EXPLAIN/SHAP keras-path + handle-callback unproven.** shap rejects keras on the kernel path; dag-ml EXPLAIN has no execution; the handle→predict-fn closure is net-new. | 3 | 3 | **9** | Build the EXPLAIN host adapter. Prove SHAP on a libn4m PLS handle + a torch handle. Document the pre-existing keras limitation. | Python (shap) + dag-ml |
| **R21** | **Two `to_spectrodataset` emitters diverge** (io + formats binding both lazily build SpectroDataset). | 2 | 3 | **6** | Pick io as the single canonical builder; make formats' emitter delegate or remove it. | nirs4all-io |
| **R22** | **Categorical target encoding ownership unknown.** Unclear if dag-ml-data owns LabelEncoder/OneHot for targets. | 2 | 2 | **4** | Verify against dag-ml-data schemas; keep encoders in Python until confirmed. Cheap either way. | dag-ml-data / Python |

#### Risks added after the Codex xhigh review (§0.1, §16)

| ID | Risk | L | I | L×I | Mitigation | Owner-area |
|---|---|---|---|---|---|---|
| **R23** | **No explicit FFI/ABI safety contract across pyo3 + ctypes + three C-ABIs.** dag-ml scheduler requires `Send+Sync` controllers (`STATUS.md:498-504`); manifests declare `thread_safe`/`process_safe`/`needs_python_gil` (`COORDINATOR_SPEC.md:112-117`); dag-ml-data has borrowed/Rust-owned alloc rules (`ABI.md:126-132, 239-244`); the three libs version their ABIs independently (`dag_ml.h:120-141`, `dag_ml_data.h:209-216`, `n4m_version.h:20-22`). Lifetime/ownership/panic-propagation bugs across the boundary are silent and catastrophic. | 4 | 4 | **16** | **New FFI-safety epic (E-FFI) before E5/E7:** an ownership/lifetime/release-callback matrix, Rust-panic→Python-exception conversion, thread-safety + GIL policy per operator kind, native-library loading, and an **ABI-skew matrix** (which dag-ml/dag-ml-data/libn4m versions are tested together in one wheel/studio bundle). | All (FFI) |
| **R24** | **Licensing not gated.** `nirs4all-methods` is dual **CeCILL/AGPL + commercial** (`nirs4all-methods/LICENSING.md`); dag-ml + dag-ml-data are CeCILL/AGPL. Bundling these natively into the studio/Electron app and into hosted/SaaS deployments has copyleft + commercial-term implications absent today (pure-Python nirs4all). | 3 | 4 | **12** | **Phase-0 legal review** before defaulting to `rust`: AGPL/CeCILL obligations for the studio (desktop + hosted), libn4m commercial terms for proprietary users, and the wheel/redistribution story. | Org/legal |
| **R25** | **Studio run-lifecycle parity under-modeled.** Studio runs are `JobManager`-backed WebSocket jobs (`runs.py:1-18, 583-607`), submitted to a thread pool (`:1332-1338`), with cooperative cancellation via `job_manager.cancel_job()` + `should_stop` (`:1664-1680`). The backlog covered schema/query parity but not start/progress/cancel/fail/retry/export over the Rust backend. | 3 | 4 | **12** | Add lifecycle acceptance tests: run **start/progress/cancel/fail/retry/export** over `rust`; map dag-ml phase events → studio progress; ensure cooperative cancel reaches dag-ml's scheduler/process workers. | Python facade + studio |
| **R26** | **Deleting legacy removes the rollback path.** E15 deletes legacy controllers while the studio still reads private SQL + `.n4a`/workspace directly. If a post-cutover defect surfaces in production, there is no `legacy` to fall back to. | 3 | 4 | **12** | Keep `NIRS4ALL_BACKEND=legacy` **runnable for ≥1 compatibility release** after default flips to `rust`. Define **abort criteria + rollback ownership** before the flip; delete legacy only in the *following* release. | Release/planning |
| **R27** | **`n_jobs`/scheduler semantics change is not a cleanup detail.** nirs4all uses joblib/loky variant parallelism (`orchestrator.py:89-110, 515-526`) + threads for branches (`branch.py:2165-2193`); dag-ml has deterministic level-order commit (`STATUS.md:498-504`). Naive removal changes parallelism, oversubscription (BLAS×torch×folds), progress cadence, cancellation points, and seed streams. | 3 | 3 | **9** | Author an `n_jobs`→dag-ml **compatibility map**: how `n_jobs` maps to dag-ml concurrency, nested-thread oversubscription control, progress-event mapping, cancellation points, deterministic seed streams. | dag-ml + host |
| **R28** | **Dtype/non-finite policy unspecified.** libn4m C-ABI is row-major contiguous **f64-only** (`n4m.h:322-324`); host data may be f32/views/NaN-bearing. Implicit copies/casts and NaN handling can change numbers or cost. | 2 | 3 | **6** | Keep a **dtype/tolerance ledger**: where f64 copies happen, f32 paths, non-finite handling, row/col-major cost; fold into the per-operator tolerance band. | libn4m + host |
| **R29** | **Process-adapter security model unspecified.** If host-Python controllers run as subprocess workers, artifact confinement, workspace path hardening, and trust boundaries for user-supplied operators need a policy. | 2 | 3 | **6** | Define a security model: trusted in-process vs sandboxed worker, artifact/workspace path confinement, no arbitrary code from untrusted DSL. | dag-ml + host |

---

## 9. Migration strategy: strangler + always-green parity gate

### 9.1 Strangler over big-bang (decided)

**Verdict: strangler/incremental, feature-flagged at the controller-dispatch seam, with operator-by-operator parity gating. Big-bang is rejected.** Three forcing facts:
1. **The blast radius is one consumer with deep private coupling** (§7): the studio reads `store.sqlite` with raw SQL. A big-bang's first failure is undiagnosable across ~10 simultaneously-changed subsystems; strangler bisects each cutover to one operator/one phase.
2. **The new backend is provably NOT end-to-end-runnable today** (§4): no feature transport on a runnable path, no NN adapter, EXPLAIN has no execution, `.n4a`/workspace need a net-new shim. Big-bang has no green intermediate state for ~17–22 pw.
3. **Numerics change even where "covered"** (§5/§7): the cutover is signature-preserving but value-changing, so every operator needs an independent tolerance gate — the literal definition of strangler-with-parity-gates.

### 9.2 The "always-green" invariant (the contract every story must hold)

> At the end of **every** merged story, on `main`: (a) `ruff + mypy + pytest` green in `nirs4all`; (b) the **studio integration job** green — FastAPI boots against the swapped `nirs4all`, and the workspace/predict/bundle/registry endpoints return **schema-identical** SQLite/Parquet/`.n4a`/RunResult shapes; (c) the **parity oracle** green for every operator/phase whose flag is ON. A story that cannot hold this is split until it can.

### 9.3 The backend feature flag

A single dispatch switch — `NIRS4ALL_BACKEND ∈ {legacy, rust, shadow}` resolved at runtime-context construction (`pipeline/runner.py`), with **per-operator-kind and per-controller overrides** (`NIRS4ALL_RUST_OPS="snv,msc,pls,..."`). `legacy` = today's Python orchestrator + operators. `rust` = dag-ml conductor + libn4m operators for the flagged set, legacy for the rest. `shadow` = run both, assert parity, return legacy (the migration's own CI mode). Feasible because the registry already routes by `matches()`/priority — the flag picks which controller-set is registered.

### 9.4 The parity oracle (the gate)

A frozen example corpus → three assertion layers:
- **Layer S (schema/shape) — zero tolerance, exact:** SQLite DDL + `PRAGMA user_version=2` + all 7 table columns; Parquet schema; `.n4a` `manifest.json` keys; Result-object fields; the studio's raw-SQL result columns.
- **Layer N (numeric) — tolerance-banded, declared per operator as the new contract:** predictions, `best_score/rmse/r2`, OOF tables within a per-operator `(atol, rtol)` band frozen at the operator's cutover story. For bundles, compare `.n4a` round-trip `predict()` on a fixed probe matrix — never pickled bytes.
- **Layer A (API-call) — drive through the studio's own adapters:** run the corpus through `nirs4all_adapter.py` (subprocess) and the `store_adapter`/`workspace_scanner` read paths.

**Corpus:** ≥1 pipeline per controller path the studio exercises (a transform chain, each major PLS variant, an AOM/POP run, an augmentation step, each splitter, a branch+merge, a finetune run, a stacking run, an explain run, a `.n4a` export+reload) × 3 small datasets (1 regression, 1 classification, 1 multi-source). Frozen on **legacy** in Phase 0; replayed on **rust** at every story.

---

## 10. Epics & parallel tracks with estimates

Five parallel tracks: **T1** libn4m operator parity · **T2** dag-ml orchestration adoption · **T3** io/formats ingestion · **T4** NN/optuna/shap host re-attach · **T5** contract-preservation + studio.

| # | Epic | Track | Goal / scope | Blocked by | Exit criteria | Size / pw |
|---|---|---|---|---|---|---|
| **E0** | Spikes & oracle harness + **M0 transport ADR** | T5 | Parity oracle + corpus; freeze golden runs on legacy; `NIRS4ALL_BACKEND` flag + `shadow`; **RNG-kind audit** (PCG64 vs NUMPY_MT — schedule-critical, gates ALL stochastic cutovers); **the controller-transport ADR (Option A JSONL vs Option B in-proc runtime) decided + benchmarked**; spikes S0–S4 (transport proof on a real FIT_CV; borrowed-view provider no-JSON; one torch model trains through the transport; `.n4a` bundle-byte round-trip; **Phase-0 licensing review**). | — | Oracle in CI; flag toggles; RNG kinds documented; **transport decided with latency evidence**; spikes green; licensing cleared. | **L, 4** |
| **E-FFI** | FFI / ABI safety contract | T2 | Ownership/lifetime/release-callback matrix across pyo3+ctypes+3 C-ABIs; Rust-panic→Python-exception conversion; `Send+Sync`/GIL policy per `operator_kind`; native-lib loading; **ABI-skew matrix** (which dag-ml/dag-ml-data/libn4m versions ship together). | E0 | An intentional Rust panic surfaces as a contextual Python exception; thread-safety policy documented + enforced; ABI versions pinned + CI-checked together. | **M, 3** |
| **E1** | libn4m operator-shim layer | T1 | Thin `BaseEstimator/TransformerMixin` shims delegating `fit/transform/predict` to `n4m`, exposing `get_params()`/signature. Covers PARITY set: all preprocessing, splitters, filters, regression metrics. Per-operator Layer-N tolerance frozen. | E0 | Every PARITY operator passes shadow oracle; shims introspectable. | **L, 5** |
| **E2** | libn4m PLS-variant cutover | T1 | Re-point 24 PLS files to `n4m`; delete `_aom_nirs/pls/`; write the PRESENT-no-fixture parity fixtures (DiPLS/SparsePLS/Robust/Recursive). | E1; verify `mbpls` symbol, `recursive_pls` semantics | ikpls/pyopls/trendfitter unused; PLS oracle green; fixtures committed. | **L, 5** |
| **E3** | io→formats tabular wiring | T3 | Route CSV/Excel/Parquet/NumPy/MATLAB through formats in **both** io facades (Python MVP + Rust `loaders.rs`); re-freeze parity goldens both langs. | io Rust facade lacks formats dep | All tabular ingest through formats; scipy.io/h5py gone from `data/loaders`; goldens re-blessed. | **XL, 7** |
| **E4** | Host-buffer provider + DSL frontend | T2 | Wire the provider's borrowed-f64-view constructors (close `_provider.py:152`); build `dsl_frontend` (objs → `pipeline_dsl` JSON) + operator (de)serialization. | E0; provider JSON-only shim | Host NumPy → borrowed view, no JSON; DSL frontend byte-matches `pipeline_dsl_nirs4all_compat.json`. | **L, 4** |
| **E5** | dag-ml conductor for native-only pipelines | T2 | First end-to-end `rust` run: COMPILE→…→PREDICT for all-libn4m pipelines (no NN). Splitters as FoldSet controllers; OOF/leakage enforced. **Precedence-equivalence test** (manifest ≡ old sort). | E1, E2, E4, E-FFI | A preprocessing→PLS→CV→refit pipeline runs fully on `rust`, oracle-green incl. OOF; precedence test green. | **XL, 8** |
| **E6** | Storage facade (SQLite + Parquet) | T5 | `WorkspaceStore` facade: exact public + `_fetch_pl` + DDL + `user_version=2`; dag-ml writes through. **Rewrite `array_store` polars→pyarrow/numpy; retain pyarrow, drop polars.** | E5 | Studio raw-SQL + `pd.read_parquet` green; polars gone from storage; pyarrow retained. | **L, 5** |
| **E7** | NN/AutoML host controllers | T4 | torch/TF/JAX/AutoGluon/TabPFN as host controllers on the **M0 transport** (JSONL persistent workers; 6-method protocol → manifest). Artifacts: `torch.save`/`.keras`/orbax (joblib narrows to blob-only). Includes **Studio run-lifecycle parity** (start/progress/cancel/retry over `rust`). | E4, E5, E-FFI | An NN pipeline runs on `rust`; warm-worker REFIT→PREDICT stickiness; cancel/progress reach dag-ml; oracle-green. | **XL, 8** |
| **E8** | optuna outer driver re-attach | T4 | Strip in-process fold-training; objective submits a one-variant campaign and reads its score. Keep samplers + `BinarySearchSampler` + pruning. Remove joblib fold-parallelism. | E5, E7; no adaptive-sweep hook in dag-ml | `finetune_params` pipelines run on `rust`; trials leakage-safe; oracle-green. | **L, 4** |
| **E9** | EXPLAIN / shap host adapter | T4 | dag-ml EXPLAIN calls back to host; `capture_model` → dag-ml handle + host predict-fn closure; shap runs host-side. | E5, E7; EXPLAIN is a phase slot with no execution | `explain()`→`ExplainResult` on `rust`; oracle-green (shape exact). | **M, 2** |
| **E10** | `.n4a` bundle facade | T5 | Host `bundle_facade` packs joblib/torch/keras blobs into the v1 envelope from dag-ml `ArtifactRef`s. **Verify n4m pickleability**; if not → `.n4a` v2 (major bump). | E5, E6, E7; n4m pickleability UNKNOWN | `.n4a` export+reload+`predict()` probe-equal; studio `BundleLoader` green. | **L, 4** |
| **E11** | data-core split (SpectroDataset/Predictions) | T2/T5 | The XL rewrite: `data/{dataset,predictions,indexer,relations,raw_multisource}` (22 polars files) → dag-ml-data contracts + dag-ml prediction store + thin `SpectroDataset` surface. **De-polars** the data layer. | E4, E5, E6; named-processings axis dead in dag-ml-data | `SpectroDataset` surface stable; polars gone from `data/`; oracle-green incl. multi-source + repetition. | **XL, 10** |
| **E12** | Branch/merge/concat/aug graph nodes | T2 | branch/merge/exclude/tag/concat/feature_aug/sample_aug as dag-ml graph nodes + dag-ml-data alignment/fusion/collation. | E5, E11; `by_metadata/by_tag/by_filter` provider views missing | branch+merge run on `rust`; train-only aug gating enforced; oracle-green. | **L, 6** |
| **E13** | Stacking/meta OOF move | T2/T4 | Move OOF **assembly** (`stacking/`) into dag-ml (sample_id join); meta **head** stays Python/n4m. Accept the break: positional/NaN-fill OOF refused. | E5, E11 | Stacking on `rust`; partial-OOF pipelines correctly rejected (documented); oracle-green. | **L, 5** |
| **E14** | analysis/transfer + classification metrics | T1/T4 | Transfer numerics (PDS/DS) → n4m; selection orchestration → dag-ml; keep procrustes/subspace + classification metrics in Python. | E1, E5 | transfer + classification-metric paths oracle-green. | **M, 3** |
| **E15** | Dependency removal + cleanup | T5 | Delete ikpls/pyopls/trendfitter/pywt/pybaselines/kennard-stone/polars/h5py; narrow joblib→blob-only; shrink sklearn/scipy to survivors. Flip default `NIRS4ALL_BACKEND=rust`. **Keep `legacy` runnable for ≥1 compatibility release (rollback path); delete legacy controllers + dead operator bodies only in the FOLLOWING release**, after abort criteria are met. | E1–E14 green on `rust` | pyproject matches §3.5; `import nirs4all` clean; default rust; `legacy` still runnable this release; full + studio CI green. | **M, 3** |

**Parallelism map:**
- **Phase-0:** E0 includes the **M0 transport ADR** (gate-zero). **E-FFI** (FFI/ABI safety) starts as soon as E0's transport is decided and gates E5/E7.
- **Phase-1 parallel:** T1 (E1) ∥ T3 (E3) ∥ T2 (E4) ∥ E-FFI — depend only on E0/M0.
- **Phase-2:** T1 (E2) continues ∥ T2 (E5, first integration; needs E-FFI) ∥ T5 (E6 once E5 lands).
- **Phase-3 parallel:** T4 (E7→E8→E9) ∥ T5 (E10) ∥ T2 (E11) — advance independently once E5/E6 are green.
- **Phase-4:** E12, E13, E14 fan out after E11; E15 is the serializing tail (and keeps `legacy` runnable one release).

---

## 11. Phased roadmap + milestones

```
PHASE 0  SPIKES + ORACLE + M0     E0 (transport ADR, gate-zero) → E-FFI
PHASE 1  FOUNDATIONS (parallel)   E1(T1)  E3(T3)  E4(T2)  E-FFI(T2)
PHASE 2  FIRST INTEGRATION        E2(T1)  E5(T2)  E6(T5)
PHASE 3  HOST RE-ATTACH + DATA    E7→E8→E9(T4)  E10(T5)  E11(T2)
PHASE 4  ADVANCED GRAPH + CUT     E12  E13  E14  →  E15(cleanup, keep legacy 1 rel)

ordering (─ active, · waiting-on-dep, ✓ gate/milestone):

         P0        P1              P2              P3                    P4
E0   ───✓ M0  ← TRANSPORT DECIDED + proven (gate-zero)
EFFI ····───✓ (T2)  ← FFI/ABI safety; gates E5/E7
E1   ····─────────✓                                                         (T1)
E3   ····─────────────────✓                                                 (T3)
E4   ····────────✓                                                          (T2)
E2   ··········──────────────✓                                             (T1)
E5   ·····················──────────✓ M2  ← FIRST native rust E2E run        (T2)
E6   ····························──────✓                                     (T5)
E7   ·································──────✓                                 (T4)
E8   ········································────✓                           (T4)
E9   ········································──✓                             (T4)
E10  ·······························──────✓                                  (T5)
E11  ····························─────────────────✓ M3 ← data-core de-polars (T2)
E12  ················································──────✓                  (T2)
E13  ················································────✓                    (T4)
E14  ·······························──────✓                                  (T1)
E15  ··················································································─✓ M4 (T4/T1)
                                                                                      ↑ DONE
```

**Milestones:**
- **M0 (end P0) — THE GATE-ZERO LINCHPIN:** controller-transport ADR decided **with latency evidence** (Option A JSONL vs Option B in-proc runtime); one real FIT_CV node runs a real NIRS X through the chosen path; borrowed-view provider wired; oracle in CI; flag live; RNG audit done; licensing cleared; FFI-safety contract drafted. **Until M0 is green, no host-Python pipeline can run.**
- **M1 (during P1):** spikes S1–S4 green; FFI-safety epic (E-FFI) landed.
- **M2 (end P2):** first all-native libn4m pipeline runs on the `rust` backend through dag-ml with OOF enforced; studio integration green; storage facade holds. **The integration linchpin for the classical path — everything after it is additive and independently gateable.**
- **M3 (mid P4):** SpectroDataset/Predictions de-polarsed; multi-source + branch/merge run on `rust`.
- **M4 (end P4):** all deps removed, default=rust, `legacy` retained one release as rollback, full + studio CI green.

**Calendar:** with 5 tracks staffed ~1–1.5 engineers each, wall-clock ≈ **P0 1–2 wk · P1 4 wk · P2 5 wk · P3 8 wk · P4 6 wk ≈ 26–30 calendar weeks** despite ~86 pw of host work (parallelism + dependency stalls absorb the rest); the wider range reflects the M0 transport decision (Option B adds dag-ml-side work).

---

## 12. Story-level backlog: Phases 0–1

Format: **ID · title · track · deps · acceptance · est(pw)**.

### Phase 0 — Spikes & Oracle (E0)

- **S0.1 · Backend flag scaffold · T5 · — ·** `NIRS4ALL_BACKEND={legacy,rust,shadow}` in `pipeline/runner.py` runtime-context build; per-op override env (`NIRS4ALL_RUST_OPS`). *Accept:* legacy unchanged with flag unset; `shadow` runs both controller-sets for a flagged op and logs a diff; unit test toggles all three. **0.5**
- **S0.2 · Parity-corpus freeze · T5 · — ·** Assemble the corpus (§9.4); run on legacy; persist golden `RunResult.top(n)`, scores, predictions, full `store.sqlite` dump, Parquet arrays, `.n4a` + probe-`predict()` outputs. *Accept:* `oracle/golden/` committed; re-running legacy reproduces it bit-for-bit (schema) at 0 tol (same backend). **1.0**
- **S0.3 · Oracle 3-layer asserter · T5 · S0.2 ·** Layer S (schema exact), Layer N (per-op `(atol,rtol)`), Layer A (via `nirs4all_adapter`/`store_adapter`). *Accept:* `pytest` job + studio-CI integration job invoke it; green on legacy-vs-legacy; fails loudly on an injected column rename. **1.0**
- **S0.4 · RNG-kind audit · T1 · — ·** Enumerate every stochastic op (augmenters, CARS/UVE/GA/PSO, KMeans/MonteCarlo splits); record `default_rng`(PCG64) vs `RandomState`(MT19937); map each to `N4M_RNG_*`. *Accept:* table committed; one augmenter pinned reproduces legacy stream bit-exact. **0.5** *(schedule-critical — blocks every stochastic cutover)*
- **S0.5 · Controller-transport ADR + proof (M0) · T2 · — ·** Decide Option A (JSONL adapter as-is) vs Option B (build in-proc Py runtime in dag-ml). Drive ONE real FIT_CV node on a real NIRS X through the chosen path; log per-fold + sweep latency vs current. *Accept:* ADR committed with latency evidence; a real X reaches a host controller and predictions come back. **1.0** *(gate-zero; supersedes the old "pyo3 vtable" spike)*
- **S0.6 · Spike borrowed-view provider · T2 · — ·** Declare + call `dagmldata_inmemory_provider_new_with_f64_feature_views` in the ctypes shim (today JSON-only, `_provider.py:151-158`; C funcs unused at `dag_ml_data.h:273-275`) from a NumPy buffer. *Accept:* a wide matrix crosses with zero `..._json` calls (asserted by symbol trace). **0.5**
- **S0.7 · Spike NN through the transport · T4 · S0.5 ·** A trivial torch module trains+predicts through the M0 transport (JSONL persistent worker). *Accept:* `state_dict` persisted host-side; predictions returned; warm worker reused across phases. **0.5**

### Phase 1 — Foundations (E1 ∥ E3 ∥ E4)

- **S1.1 · Shim base + registry-manifest emitter · T1 · S0.1 ·** `OperatorShim(BaseEstimator/TransformerMixin)` delegating to `n4m`; `@register_controller` also emits a `controller_manifest` entry (`operator_kind`+`class_prefixes`). *Accept:* shimmed SNV introspectable (`get_params`, signature) and produces a manifest entry; legacy `matches()` still works. **0.5**
- **S1.2 · Preprocessing parity (scatter/deriv/baseline/wavelet) · T1 · S1.1,S0.4 ·** SNV/LSNV/RNV/MSC/EMSC/SG/derivatives/NorrisWilliams/Gaussian/Detrend + all 9 baselines + wavelet family → `n4m`. *Accept:* each passes shadow oracle at declared band; `pywt`/`pybaselines`/`scipy.ndimage,signal` unused by these ops. **1.5**
- **S1.3 · Splitter parity · T1 · S1.1,S0.4 ·** Kennard/SPXY(+Fold/GFold)/KMeans/KBinsStratified/BinnedStratGroupKFold/SystematicCircular/SPlit → `n4m`. *Accept:* fold assignments match legacy by identity; `kennard-stone`/`scipy.cdist`/sklearn-KMeans unused by splitters. **1.0**
- **S1.4 · Filter + regression-metric parity · T1 · S1.1 ·** X/Y-outlier/HighLeverage/SpectralQuality/Composite → `n4m`; regression metrics (r2/rmse/mae/rpd/rpiq/sep/bias) → `n4m`. *Accept:* oracle-green; sklearn covariance/ensemble(IsoForest)/neighbors(LOF) unused by filters. **1.0**
- **S1.5 · Resampler interp parity · T1 · S1.1 ·** Resampler/Crop → `n4m`; verify interp method vs `scipy.interpolate.interp1d`. *Accept:* resample output within band; document any edge-handling delta. **0.5**
- **S1.6 · io→formats tabular routing (Python MVP) · T3 · — ·** Route CSV/Excel/Parquet/NumPy/MATLAB through `nirs4all_formats.open_path` in io `materialize/loaders.py`. *Accept:* a `.mat` v5 + v7.3, `.parquet`, `.npz`, `.xlsx` ingest via formats; io parity vs `DatasetConfigs` green. **1.5**
- **S1.7 · io→formats tabular routing (Rust facade) · T3 · S1.6 ·** Wire formats reader registry + Frame conversion into io `loaders.rs` (today CSV-only). *Accept:* Rust facade reads npy/parquet/xlsx/mat; goldens re-blessed both langs; scipy.io/h5py removable from `data/loaders` (flagged, not yet deleted). **2.0**
- **S1.8 · archive + .xls gap triage · T3 · S1.6 ·** Decide tar/multi-zip + legacy `.xls` (OLE) — re-implement in io or declare dropped. *Accept:* written decision; if kept, single-entry+tar+multizip pass; if dropped, documented regression note. **1.0**
- **S1.9 · Host-buffer provider wiring · T2 · S0.6 ·** Production: NumPy/Arrow host buffers → borrowed f64 views through the provider vtable; NumPy buffer-protocol path. *Accept:* wide-NIRS X crosses with no JSON; provider passes dag-ml-data C-conformance from Python. **1.5**
- **S1.10 · DSL frontend (objs→JSON) · T2 · S0.1 ·** `dsl_frontend`: live Python pipeline → `pipeline_dsl` JSON via component (de)serialization. *Accept:* emitted DSL byte-matches `pipeline_dsl_nirs4all_compat.json` + `..._generator_parity.json` for the corpus. **1.5**
- **S1.11 · Compile round-trip check · T2 · S1.10 ·** Feed `dsl_frontend` output to `dag-ml-py.compile`; assert GenerationSpec/VariantPlan for `_or_/_grid_/_range_/_log_range_/_cartesian_/_zip_/_chain_/_sample_`. *Accept:* variant ids/seeds/fingerprints deterministic across two runs; matches legacy generator's variant set. **1.0**

*(Phase-1 subtotal ≈ 16 pw across 3 tracks → ~4 calendar weeks at the staffing above.)*

---

## 13. Open questions / unknowns to resolve via spikes

These are ordered: each gates the work behind it. **Do not start the full cutover until S1–S4 are green** — they retire the four highest-L×I risks (R1, R2, R4, R5/R6).

**S0 — Decide the controller-execution transport (M0, gate-zero). [retires R1; the keystone the review surfaced]** `dag-ml-py` is JSON-only and does not execute controllers; native PyO3/C-ABI controller wrappers are out of scope; the only shipped cross-language transport is the **JSONL process adapter** (`HOST_ADAPTER_BACKLOG.md:12-17, 85-90`). So **first decide**: **Option A** — adopt the JSONL adapter and engineer the serialization envelope down (task batching via `accepts_task_batch`, keep wide X host-side and pass sample-id selections + a data handle, persistent workers); or **Option B** — sponsor a net-new in-process Python controller runtime *in dag-ml* (needs owner buy-in + the FFI-safety epic). Then **prove the chosen path** runs one real FIT_CV node on a real NIRS X. Measure per-fold + sweep (`12-trial × 5-fold × 3-preprocessing`) latency vs current joblib. **Pass:** ADR committed with latency evidence; a real X reaches a host controller; wall-clock within the agreed budget (e.g. ≤1.5× today). **Nothing NN/feature-heavy proceeds until this is green.**

**S1 — Borrowed-view provider (prerequisite for both options). [informs R10]** Declare + call `dagmldata_inmemory_provider_new_with_f64_feature_views` in the ctypes shim (today JSON-only, `_provider.py:151-158`; the C funcs exist unused at `dag_ml_data.h:273-275`); build a host-buffer provider over a NumPy f64 array. **Pass:** a wide NIRS X crosses with zero `..._json` calls (symbol-trace asserted). Needed even for Option A's host-side data handles.

**S2 — Prove a torch model trains+predicts through the chosen transport. [retires R2]** Implement one `PyTorchModelController` on the M0 transport (JSONL persistent worker; 6-method protocol). Train a small NN on a NIRS dataset through FIT_CV→REFIT→PREDICT; assert loss curve + predictions match `controllers/models/torch_model.py` within tolerance. Verify state_dict warm-start survives REFIT→PREDICT stickiness on a persistent worker; process isolation sidesteps the GIL against native parallel nodes. **Pass:** identical training trajectory + a warm GPU model reused across phases.

**S3 — Prove `.n4a` round-trips over a dag-ml bundle (LOW RISK — pattern already ships). [retires R4]** Take a fitted libn4m model via the `n4m`/`pls4all` binding; reuse the shipped **bundle-byte** persistence (`_Pls4allModelEstimator` stores `_bundle_`, drops `_model_handle_`/`_model_ctx_` from `__getstate__`, `pls4all/sklearn/_base.py:158-176`). Export a `.n4a` v1 from a dag-ml `ExecutionBundle` (host packs the blob), reload, assert `predict()` on a frozen probe matrix is byte/tolerance-identical. **Pass:** non-breaking `.n4a` v1 works (expected). **`.n4a` v2 only if** a non-pls4all model can't carry bundle bytes.

**S4 — RNG-kind audit + numerical-parity fixture sweep. [retires R5, R6]** Audit nirs4all's current RNG across every stochastic op; pin each to `N4M_RNG_PCG64`/`NUMPY_MT`. Write the 4 missing parity fixtures (DiPLS/SparsePLS/Robust/Recursive); verify resampler interp1d-vs-libn4m. **Pass:** every stochastic op reproduces nirs4all's stream; every PLS variant within declared tolerance. Do this before deleting trendfitter/ikpls/pyopls.

**S5 — Verify the three header-unresolved libn4m symbols. [retires part of R5]** Confirm in `estimators/multiblock.h` that `mbpls` is exported; whether a bare (non-PLS) logistic/softmax head exists for the meta classifier; whether dag-ml-data owns categorical **target** encoding. **Pass:** each confirmed before deleting `mbpls.py`, the meta classifier head, or `data/_targets` encoders respectively.

**S6 — Controller precedence-equivalence harness. [retires R12]** Take every operator nirs4all ships; assert the dag-ml `controller_manifest` routes it to the **same** controller the old `(priority, class_name)` sort did — especially *SklearnModel prio 6 beats Transformer prio 10*. **Pass:** 100% routing match across the operator catalog.

**S7 — DSL byte-parity spike. [retires R19]** Run the host object→`pipeline_dsl` JSON serializer against `pipeline_dsl_nirs4all_compat.json` / `pipeline_dsl_nirs4all_generator_parity.json` for a representative pipeline set. **Pass:** emitted JSON matches the compat fixtures (or deltas are understood and accepted).

**S8 — Studio integration smoke against a swapped backend. [retires R3/R9 early]** Stand up the studio FastAPI backend against an early facade build; exercise the workspace/predict/bundle/registry read paths (`store_adapter` raw SQL, `_fetch_pl`, node-palette introspection, `pd.read_parquet`). **Pass:** schemas byte-identical, numbers tolerance-equal, no ImportError, the node palette renders. This is the real acceptance test, wired into both CIs as the golden-run differential harness (§7.4).

**The single decisive sentence:** the numerical core is *not* the bottleneck (libn4m is ~85–90% parity-covered) — **the cutover lives or dies on M0 (decide the controller-execution transport: adopt the shipped JSONL adapter and beat its serialization budget, or sponsor a net-new in-process Python runtime in dag-ml) and on a torch model actually training through that transport; until those are green, dag-ml can only *validate* nirs4all pipelines as conformance tests, not *run* the NN/feature-heavy ones.**

---

## 14. Definition of done

The migration is DONE when **all** hold simultaneously on `main`:

1. **Deps removed from `nirs4all/pyproject.toml`:** `ikpls`, `pyopls`, `trendfitter`, `PyWavelets`(pywt), `pybaselines`, `kennard-stone`, `polars`, `h5py` — gone (zero import sites, verified by grep in CI).
2. **`pyarrow` retained as storage-only** (writes the frozen workspace Parquet layout in `store_facade`; no compute use) — **the one explicit, documented exception** to the removal goal (forced by `array_store.py:35-37` + studio `pd.read_parquet`).
3. **`joblib` narrowed** to `.n4a`/artifact model-blob (de)serialization only; **all `joblib.Parallel` fold/variant parallelism removed** (dag-ml owns scheduling).
4. **sklearn reduced to survivors:** `sklearn.base` (operator protocol), classification metrics, `LabelEncoder/OneHotEncoder/FunctionTransformer`, tree/ensemble user models, `check_random_state`. Everything in `cross_decomposition/decomposition/cluster/covariance` + the numerical half of `preprocessing/model_selection/linear_model/neighbors` + regression metrics — gone.
5. **scipy reduced to survivors:** `stats` (pearsonr/spearmanr/ks_2samp/wasserstein/chi2/entropy/MAD), `special` (voigt/gammaln), and `signal/ndimage/optimize/interpolate/integrate` **only inside `synthesis/`**. All live-pipeline scipy paths (savgol/gaussian/cdist/nnls/minimize/cho_*/solve_banded/interp1d/loadmat/sparse) — gone.
6. **`_aom_nirs/` tree deleted** (pls→n4m; ridge-MKL ported or orchestrated over n4m; fast-generators kept as Python feeding n4m sweep kernels).
7. **Default `NIRS4ALL_BACKEND=rust`; `legacy` retained as a runnable rollback for ≥1 compatibility release** (deleted only in the *following* release once abort criteria are clear — R26). Dead operator bodies removed once legacy is retired.
8. **All green, studio unbroken:** `ruff+mypy+pytest` green; the **parity oracle** green at every operator's declared band across the full corpus; the **studio integration CI** green (workspace/predict/bundle/registry return schema-identical SQLite/Parquet/`.n4a`/RunResult; **run-lifecycle parity** — start/progress/cancel/retry/export over `rust`). The 0.9.x public API (`run/predict/explain/retrain/session/generate`) and Result-object shapes unchanged.
9. **Three lib-gap verifications closed** (else the corresponding cutover is descoped to KEEP-Python and documented): `mbpls` multiblock symbol; bare logistic/softmax meta head; dag-ml-data categorical-target encoding ownership.
10. **Cross-cutting gates cleared (added after review):** the **controller-transport ADR** decided + benchmarked (M0); the **FFI/ABI safety contract** + **ABI-skew matrix** in CI (E-FFI); the **Phase-0 licensing review** signed off (CeCILL/AGPL/commercial for studio + hosted); the **`n_jobs`→dag-ml scheduler** compatibility map and **dtype/tolerance ledger** documented.
11. **Announced breaking changes documented** (correctness-positive but contract-affecting): partial/NaN-fill OOF stacking now refused (E13); numeric tolerance bands declared as the new contract; **and — only if a non-pls4all model can't carry `.n4a` bundle bytes — `.n4a` v2 as a major-version event** (E10; now low-likelihood given the shipped bundle-byte pattern).

### Total effort

**Bottom-up sum of epics (revised after review):** E0 4 + **E-FFI 3** + E1 5 + E2 5 + E3 7 + E4 4 + E5 8 + E6 5 + E7 8 + E8 4 + E9 2 + E10 4 + E11 10 + E12 6 + E13 5 + E14 3 + E15 3 = **86 pw of nirs4all-host migration work** (was 81; +E-FFI, +E0 transport ADR, +E7 lifecycle).

**Plus net-new lib-side parity/gap work the host work depends on** (from Inventories B & D, not double-counted): dag-ml feature-transport + production provider ~3–4 pw; Python controller runtime + torch/tf/jax adapters ~6–8 pw (partly absorbed by E7); EXPLAIN/shap core ~2 pw (absorbed by E9); libn4m residual parity (KOPLS/OKLMPLS decisions, AOM-Ridge MKL, DiPLS/Sparse/Robust/Recursive fixtures, NLPLS, IntervalPLS) ~10–14 pw; dag-ml-data named-processings axis + signal-type enforcement ~3–4 pw. Net new lib-side work not inside host epics ≈ **20–28 pw**.

**Grand total (revised after review): ~110–150 person-weeks**, central estimate **~125 pw** (86 host + ~20–28 lib-side + the review-surfaced FFI/transport/lifecycle/licensing scope). The earlier ~105 pw assumed an in-process pyo3 path that does not exist (§0.1/§3.3).

- **Range:** **~80 pw (optimistic)** — the team **adopts the JSONL process adapter as-is** and its serialization budget passes S0; the three lib-gap verifications resolve favorably; KOPLS/OKLMPLS/FCKPLS/NLPLS-multikernel kept on NN backends (not ported); `.n4a` v1 preserved via the shipped bundle-byte pattern; dag-ml-data ships the named-processings axis on its own roadmap — to **~150 pw (pessimistic)** — **S0 forces Option B** (a net-new in-process Python controller runtime built in dag-ml, +8–15 pw to dag-ml itself); dag-ml-data's processing-axis + production-provider land inside this effort; the JSONL adapter needs heavy hardening (R14); and the precedence-equivalence / OOF-refusal / studio-lifecycle breaks cascade into studio rework.
- **Confidence: Medium.** High on the *shape* of the plan and on libn4m numerical coverage (the fixtures are real and gating). Dominant uncertainties (all flagged): (1) **the M0 controller-transport decision** — the JSONL adapter is the only shipped path and its sweep-scale serialization budget is unmeasured; Option B (in-proc runtime) is net-new dag-ml work; (2) E11 data-core de-polars is genuinely XL and the named-processings axis is a dag-ml-data gap, not host wiring; (3) the studio's private/raw-SQL coupling + run-lifecycle (job/cancel/WebSocket) means contract preservation has a long tail of "found one more endpoint."
- **Calendar:** ~24 weeks wall-clock with 5 tracks ≈ 5–7 engineers.

**Single most schedule-critical item (re-grounded by the review):** **M0 — decide and prove the controller-execution transport (Spike S0/E0)** — comes *before* the first native run. Until the transport is chosen (JSONL-adopt vs build-in-proc) and a real X reaches a host controller at acceptable latency, *no* host-Python pipeline (NN/optuna/shap) can run, so every NN-dependent epic is speculative. **M2 (first all-native libn4m pipeline + studio still green)** remains the *integration* linchpin for the classical path and should follow immediately. Get to **M0 then M2** fast; everything after is additive and independently gateable.

---

## 15. Appendix

### 15.1 Glossary of cross-repo terms

| Term | Meaning |
|---|---|
| **libn4m / `n4m`** | The portable C++17 numerical core (`nirs4all-methods`) and its Python binding. PLS variants, preprocessing, splitters, filters, AOM/POP, augmentation, metrics, transfer. Row-major contiguous F64 C-ABI. |
| **dag-ml** | The reproducible/traceable/OOF-leakage-safe ML coordinator. Owns COMPILE→PLAN→FIT_CV→SELECT→REFIT→PREDICT→EXPLAIN, bundles, replay, lineage, fingerprints. Operators are external (host-owned). |
| **dag-ml-data** | Typed sample-aligned multi-source data contracts: schemas, axes, representations, alignment, collation, fusion, provider vtable, fingerprints. Validates folds; never owns predictions/OOF. |
| **`dag-ml-py`** | The pyo3 crate (`dag-ml/crates/dag-ml-py/`). **JSON-contracts only** — *validates/compiles/plans* serialized contracts; **does not execute host controllers or own data buffers** (`src/lib.rs:1-5`). It is **not** an in-process controller transport (corrected per Codex review). |
| **JSONL process adapter** | dag-ml's only stable cross-language host-controller transport (`HOST_ADAPTER_BACKLOG.md`): controllers run as subprocess workers exchanging `NodeTask`/`NodeResult` JSONL. Shipped for sklearn/prospectr/mdatools. The default controller transport for the host-Python (NN/optuna/shap) nodes in this plan. |
| **nirs4all-io** | Dataset assembly bridge: RESOLVE→INFER→CONFIGURE→MATERIALIZE → `SpectroDataset` / dag-ml-data emit. Consumes formats; never re-parses. |
| **nirs4all-formats** | Rust readers for ~58 vendor spectroscopy formats + `.mat`/parquet/npy/xlsx, with Python/R/WASM/C bindings. |
| **SpectroDataset** | nirs4all's 86 KB working data structure: multi-source X `(n_samples, n_pp, n_features)`, folds, repetition, aggregation, named processings, targets. **Stays full-weight in nirs4all.** |
| **Controller / `matches()` / `@register_controller`** | nirs4all's operator-dispatch mechanism — priority-sorted registry keyed on sklearn protocol types. Retired as runtime router; replaced by a dag-ml `controller_manifest`. |
| **OOF** | Out-of-fold predictions — the leakage-safe substrate for stacking/meta-models. dag-ml joins by `sample_id` identity, refuses positional joins. |
| **`.n4a`** | nirs4all's portable bundle: ZIP + `manifest.json` (`bundle_format_version="1.0"`) + `joblib`-pickled operator blobs + a portable predict script. **STABLE contract.** |
| **Workspace** | SQLite (`store.sqlite`, `SCHEMA_VERSION=2`, 7 tables) + Parquet (`arrays/<ds>.parquet`, Zstd) + content-addressed `artifacts/<hash>.joblib` + `runs/.../manifest.yaml`. **STABLE contract** consumed by the studio. |
| **ArtifactRef** | dag-ml's portable artifact handle: typed backend/URI (strictly relative)/content-fingerprint/plugin metadata. dag-ml never serializes model binaries. |
| **`FoldSet`** | dag-ml-data's validated (not owned) fold assignment table, fingerprinted, checked against group/origin boundaries. |
| **`AxisKind::Processing`** | The dag-ml-data axis variant for the named-processings (`n_pp`) dimension — currently a **dead variant** (zero usages). |
| **PARITY / PRESENT / PARTIAL / MISSING** | libn4m coverage states (§5): fixture-gated / symbol-only / sub-capability / no equivalent. |
| **Strangler** | Incremental migration replacing one operator/phase at a time behind a feature flag, with each cutover parity-gated. |
| **Parity oracle** | The golden-run differential harness (§7.4/§9.4) asserting schema (exact) + numeric (tolerance) + API-call (through studio adapters) parity. |

### 15.2 Assumptions & confidence

Every assumption below is marked; FACT = read in source/STATUS, INFERENCE = derived, UNKNOWN = unresolved and flagged for a spike.

| # | Assumption | Basis | Confidence |
|---|---|---|---|
| A1 | **CORRECTED.** ~~`dag-ml-py` is the in-process controller transport.~~ The controller transport is the **JSONL process adapter** (the only shipped cross-language path); `dag-ml-py` is JSON-contracts-only. An in-process Python runtime would be a net-new dag-ml feature (Option B). | FACT (`dag-ml-py/src/lib.rs:1-5`; `HOST_ADAPTER_BACKLOG.md:85-90`). Sweep-scale latency of the JSONL path is **UNKNOWN** until S0. | Medium |
| A2 | libn4m has parity-fixtured coverage for ~85–90% of the classical operator surface. | FACT (204 fixtures, 188 ABI-mapped catalog methods of 209 YAMLs, reconciliation GREEN — Inventory D; re-verified by Codex). | High |
| A3 | `SpectroDataset` stays full-weight in nirs4all; io/formats only emit it via lazy import. | FACT (io CLAUDE.md:141, `materialize/spectrodataset.py:38`, COPY_PROVENANCE #15). | High |
| A4 | The 0.9.x SQLite+Parquet+`.n4a` contracts must be preserved behind Python facades; dag-ml will not emit them. | FACT (dag-ml is manifest-only, STATUS.md:168-169,417; studio raw SQL `store_adapter.py:1071`). | High |
| A5 | optuna stays a Python outer ask-tell driver; dag-ml has no adaptive-sweep hook. | FACT (STATUS.md:643-644; no candidate-feedback callback found). | High |
| A6 | dag-ml's EXPLAIN has no execution path; shap runs host-side behind a model handle. | FACT (STATUS.md:359; COORDINATOR_SPEC.md:601). | High |
| A7 | KOPLS/OKLMPLS/FCKPLS-learned/NLPLS-multikernel/TabPFN stay on NN backends (not ported to libn4m). | INFERENCE (Inventory D §D.4; porting cost ≫ value). | Medium-High |
| A8 | **UPGRADED.** A fitted libn4m model is wrapped as a picklable Python object presenting `predict()` via bundle-byte persistence. | FACT — the pattern ships: `_Pls4allModelEstimator` persists `_bundle_`, drops handles from `__getstate__` (`pls4all/sklearn/_base.py:158-176`). `.n4a` v1 expected non-breaking; v2 only if a non-pls4all model can't carry bundle bytes. | Medium-High |
| A9 | dag-ml can persist run/lineage *into* the legacy SQLite schema (or the facade dual-writes). | **UNKNOWN** (Inventory G). | Low-Medium |
| A10 | The named-processings axis lands in dag-ml-data on its own roadmap (else host-side namespacing flattening). | **UNKNOWN** — `AxisKind::Processing` is a dead variant (Inventory C §4). | Low-Medium |
| A11 | The dag-ml `controller_manifest` (`operator_kind`+`class_prefixes`) can reproduce the `(priority, class_name)` precedence. | **UNKNOWN** — UNVERIFIED, top integration-test target (spike S6). | Medium |
| A12 | `mbpls` (multiblock) and a bare logistic/softmax head are (or aren't) in libn4m; dag-ml-data does (or doesn't) own categorical target encoding. | **UNKNOWN** — three header-unresolved symbols (spike S5). | Low |
| A13 | nirs4all's stochastic ops can be RNG-pinned to bit-exact reproduce current streams (PCG64 vs NUMPY_MT). | FACT that libn4m offers both kinds (n4m.h:362-366); which each op needs is **UNKNOWN** until S0.4/S4. | Medium |
| A14 | The studio is the entire Python blast radius (the other 4 consumers don't import the lib). | FACT (Inventory G §G.0). | High |
| A15 | Effort estimates are order-of-magnitude (T-shirt → pw), not committed schedules. | INFERENCE — the dominant uncertainties (E11 de-polars, E5/E7 latency, studio long tail) are flagged. | Medium |

**Reconciliation note:** where the input inventories conflicted, this document resolves them as follows — (1) Inventory A's "UNKNOWN" coverage for feature-selection / splitters / augmentation is **superseded by Inventory D's fixture audit (PARITY)**; (2) the Inventory A vs F dispute over controller transport was **resolved in DRAFT v1 to the pyo3 in-process vtable — the Codex xhigh review proved that path does not exist** (`dag-ml-py` is JSON-only; native controller wrappers are out of scope), so it is **re-resolved to an open M0 decision** defaulting to the shipped **JSONL process adapter** (§3.3, §0.1); (3) the Inventory F vs G polars/pyarrow-vs-Parquet contradiction is **resolved in favor of the contract** — pyarrow retained storage-only, polars removed (§3.4, §7, R3).

---

## 16. Codex xhigh review — findings & incorporated corrections

The full review is the companion file [`MIGRATION_BACKLOG_CODEX_REVIEW.md`](MIGRATION_BACKLOG_CODEX_REVIEW.md) (model `gpt-5.5`, `model_reasoning_effort=xhigh`, run from the ecosystem root with read-only access to all sibling repos). Every load-bearing finding was **independently re-verified against source** before incorporation. This section records the disposition of each finding so the review trail is auditable.

### 16.1 Reviewer verdict (verbatim summary)

> *"Not sign-off ready [as DRAFT v1]. The backlog is strongest where it inventories existing coupling and data contracts, but its keystone decision is contradicted by the source: `dag-ml-py` exists, but it is not an in-process Python controller vtable today. Safe next step is spikes/oracle work only, especially controller transport, feature-buffer transport, `.n4a`, and Studio contract preservation."*

DRAFT v2 (this document) folds in every correction below; the keystone is rewritten (§3.3) and the verdict's "safe next step" *is* the plan (M0 → spikes → oracle).

### 16.2 Finding disposition table

Severity/type as assigned by the reviewer. **Disposition:** how DRAFT v2 responds.

| # | Sev/Type | Finding (one line) | Re-verified? | Disposition in v2 |
|---|---|---|---|---|
| 1 | CRITICAL / ERROR | pyo3 in-process controller path is not real; `dag-ml-py` is JSON-only; PyO3 controller wrappers out of scope. | **YES** (`dag-ml-py/src/lib.rs:1-5`; `HOST_ADAPTER_BACKLOG.md:85-90`) | **§3.3 fully rewritten** to JSONL-as-shipped + M0 build-or-adopt decision; cascaded to TL;DR, §3.2/3.7, §4.1, §6, §8 (R1/R2/R10/R14), §10 (E-FFI/E0/E7), §13 (S0), §15 (glossary, A1). |
| 2 | CRITICAL / SEQUENCING | Gate-zero S1 ("drive FIT_CV through dag-ml-py") cannot pass as written. | **YES** (`_provider.py:151-158`; `_abi.py` borrowed views undeclared) | **Split into S0 (transport decision+proof) + S1 (borrowed-view provider) + S2 (NN through transport)** in §13/§12. |
| 3 | HIGH / GAP | No explicit FFI ownership/threading/error/ABI matrix. | **YES** (`STATUS.md:498-504`; `COORDINATOR_SPEC.md:112-117`; three ABI headers) | **New epic E-FFI** before E5/E7; **R23**; ABI-skew matrix in DoD §14.10. |
| 4 | HIGH / GAP | Studio run-lifecycle (JobManager/WebSocket/cancel) under-modeled. | **YES** (`runs.py` job/cancel paths) | **R25**; lifecycle acceptance tests folded into E7 + DoD §14.8. |
| 5 | HIGH / GAP | Deleting legacy removes the rollback path. | n/a (design) | **R26**; E15 keeps `legacy` runnable ≥1 release; DoD §14.7. |
| 6 | HIGH / GAP | Licensing (CeCILL/AGPL + libn4m commercial) not gated. | **YES** (`nirs4all-methods/LICENSING.md`) | **R24**; Phase-0 licensing review in E0 + DoD §14.10. |
| 7 | MEDIUM / ERROR | libn4m count/symbol precision (188 ABI-mapped; `_di_pls_fit`; `kennard_stone_*`). | **YES** (`ABI_RECONCILE_GAP.md:5-7`; `domain_adaptation.h:130`; `model_selection.h:35-42`) | Fixed in §4.1, §5.1, §5.4. |
| 8 | MEDIUM / UNDERSTATEMENT | `.n4a` pickleability is **not unknown** — bundle-byte wrapper already ships. | **YES** (`pls4all/sklearn/_base.py:158-176`) | **R4 downgraded** (15→8); E10/S3/A8 reframed as a known contract. |
| 9 | MEDIUM / OVERSTATEMENT | dag-ml host-adapter maturity misstated ("all smoke/mock"). | **YES** (`STATUS.md:650-685`) | §4.1 corrected: sklearn/prospectr/mdatools JSONL adapters *shipped*; tuner/adaptive-search still smoke/missing. |
| 10 | MEDIUM / ERROR | Studio import count ambiguous ("57/28"). | **YES** (Codex: 28 API files / 112 occ.) | §7.1 + R9 now require a reproducible `grep` count and a frozen file list. |
| 11 | MEDIUM / GAP | `n_jobs` semantics not a cleanup detail. | **YES** (`orchestrator.py`, `branch.py`, `STATUS.md:498-504`) | **R27**; `n_jobs`→scheduler compatibility map in DoD §14.10. |
| 12 | MEDIUM / ERROR | nirs4all-io Python vs Rust loader surfaces conflated. | **YES** (`loaders.py:201-276` vs `loaders.rs:57-64`) | §4.1 split by surface; E3 unchanged (target = both surfaces through formats). |

### 16.3 Missing items the review added (now in scope)

All are reflected above; consolidated here as a checklist:

- **Controller-transport ADR** (JSONL now vs PyO3/in-proc future) with security + performance gates — *E0/S0, §3.3.*
- **FFI memory model** (ownership, borrowed buffers, release callbacks, panic/error conversion, handle invalidation) — *E-FFI, R23.*
- **ABI-skew matrix** (dag-ml × dag-ml-data × libn4m versions tested together in wheels + studio bundles) — *E-FFI, DoD §14.10.*
- **Studio lifecycle contract** (WebSocket events, progress, cancel, retry, persisted run manifests) — *R25, E7, DoD §14.8.*
- **Workspace rollback plan** (legacy retention, dual-write/compare, abort criteria, major-version policy) — *R26, E15, DoD §14.7.*
- **`n_jobs` compatibility** (scheduling semantics, CPU/GPU oversubscription, deterministic RNG, cancellation points) — *R27.*
- **`.n4a` v1/v2 decision** (wrapper serialization contract + saved-bundle compatibility tests) — *R4, S3, E10.*
- **Dtype policy** (f64/f32 copies, non-finite handling, row/col-major costs, tolerance ledger) — *R28, DoD §14.10.*
- **Security model** (process-adapter artifact confinement, trusted in-process Python, workspace path hardening) — *R29.*
- **Licensing gate** (CeCILL/AGPL/commercial for studio + proprietary/SaaS) — *R24, E0.*

### 16.4 Reviewer's independent effort & critical-path read (incorporated)

> The reviewer judged the original ~105 pw **optimistic if PyO3 in-process remains the default**, and would *"budget closer to 120–150 pw unless the team explicitly chooses the existing JSONL process path and accepts its performance envelope,"* and that *"M2/E5 is not the linchpin — the linchpin is M0: prove or reject controller transport with real feature buffers and one real FIT_CV pipeline."*

DRAFT v2 adopts both: the estimate is revised to **~110–150 pw (central ~125 pw)** with the ~80 pw floor explicitly conditioned on adopting JSONL as-is (§14), and **M0 is now the gate-zero linchpin** ahead of M2 (§0.1, §11, §13). The reviewer's recommended re-ordering — *oracle/flag/rollback → controller-transport decision → borrowed-f64 provider → workspace+`.n4a` → libn4m low-risk cuts → NN/optuna/studio breadth* — matches the revised phase order (P0 E0/E-FFI → P1 E1/E3/E4 → P2 E2/E5/E6 → P3 E7/E8/E9/E10/E11 → P4 E12–E15).

### 16.5 What the review did **not** overturn (still load-bearing)

The review explicitly confirmed: libn4m's ~85–90% parity coverage is **real and fixture-gated** (`ABI_RECONCILE_GAP.md`, 204 fixtures); `AxisKind::Processing` **is** a dead variant (`model.rs:11-15`); `SpectroDataset` **stays** in nirs4all behind the lazy import boundary (`test_import_boundary.py`); the workspace/`.n4a`/raw-SQL coupling **is** as deep as described; and the data-contract / dependency-cut analysis stands. The numerical core remains **not** the bottleneck — the transport and contract-preservation layers are.
