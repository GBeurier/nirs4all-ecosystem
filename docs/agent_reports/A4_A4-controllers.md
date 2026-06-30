# A4 — Controllers & bindings (lane L16) report

**Agent:** A4 (L16 controllers/bindings) · **Mode:** multi-CLI report, read-only
**Date:** 2026-06-30 · **Engine:** Claude Opus, effort max
**Target decision:** `ARB-004` → `DEC-CTRL-001` (+ proposed `DEC-CTRL-002..007`)
**Roadmap tasks:** `CTRL-000..007`
**Status:** analysis complete; this report is a handoff for A0 to integrate into
`PARALLEL_REFACTORING_SYNC.md` (I do not edit the sync board in multi-CLI mode).

> Scope note: I did **not** modify any code or any shared contract. No manifest,
> no schema, no `OperatorController` was changed. Sub-agents used were read-only
> (inventory, node-registry, bindings).

## 0. Evidence base (heads + files actually read)

Read directly:

- dag-ml manifest contract: `dag-ml/docs/contracts/controller_manifest.schema.json`,
  `dag-ml/crates/dag-ml-core/src/controller.rs` (struct + `validate()` +
  `ControllerRegistry::resolve_for_node` / `infer_operator_kind`).
- nirs4all controller surface: `nirs4all/nirs4all/controllers/controller.py`
  (the `OperatorController` ABC), `controllers/registry.py` (the
  `CONTROLLER_REGISTRY` + `@register_controller`).
- the **de-facto current adapter**:
  `nirs4all/nirs4all/pipeline/dagml_bridge.py::controller_manifests()`
  (5 hand-authored manifests) + `_step_to_dsl`/`_to_canonical_step`
  (keyword→kind lowering) + `pipeline/dagml/operator_routing.py`
  (node→operator instantiation) + `pipeline/dagml/detect.py` (coverage gate).
- design + governance: `MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md` §4ter,
  `PARALLEL_REFACTORING_ROADMAP.md` §L16/CTRL, `REFACTORING_DECISIONS_TO_ARBITRATE.md`
  §ARB-004, `PARALLEL_REFACTORING_SYNC.md` (L16 row, `DEC-CTRL-001`).

Predecessor note: `A3_A3-dagml.md` is **empty** (the Codex run failed on
`gpt-5-codex` model availability), so L5's runtime flow/coverage matrix does not
yet exist. Where this report touches native-vs-fallback coverage it is from my
own reading of `detect.py`/`dagml_bridge.py`, and should be reconciled with L5
when A3 re-runs.

---

## 1. The three current "controller" surfaces (cartography)

The word *controller* names **three distinct objects** in the live code. The
design doc (§4ter) asserts this; I confirmed it against the code and add the
de-facto adapter that already exists.

| # | Object | Repo / file | Nature | Role |
|---|---|---|---|---|
| 1 | `ControllerManifest` | `dag-ml` `controller.rs` + `controller_manifest.schema.json` | **declarative** JSON contract, validated, cross-language | the canonical surface bindings should target |
| 2 | `OperatorController` | `nirs4all` `controllers/controller.py` (+ ~2 dozen subclasses) | **imperative** stateful Python ABC | executes legacy operators against `SpectroDataset` |
| 3 | `operator_routing.py` + `controller_manifests()` | `nirs4all/pipeline/dagml*` | **bridge glue** | lowers DSL → node kind, hand-authors 5 manifests, instantiates the concrete operator |

### 1.1 `ControllerManifest` (dag-ml) — the target contract

Required: `controller_id`, `controller_version`, `operator_kind`,
`supported_phases`, `fit_scope`, `rng_policy`, `artifact_policy`.
Optional: `priority`, `input_ports`, `output_ports`, `data_requirements`
(a `ModelInputSpec`), `capabilities`, `operator_selectors`.

Closed vocabularies (from the schema/enum):

- `operator_kind` (NodeKind): `transform, y_transform, split, model, fork, map,
  feature_join, prediction_join, mixed_join, source_join, tag, exclude,
  augmentation, adapter, aggregator, generator, restructure, tuner, subgraph,
  chart`.
- `supported_phases` (Phase): `COMPILE, PLAN, FIT_CV, SELECT, REFIT, PREDICT, EXPLAIN`.
- `capabilities`: `deterministic, thread_safe, process_safe, needs_python_gil,
  emits_predictions, consumes_oof_predictions, emits_artifacts, stateful,
  emits_relation, uses_core_rng, shape_changing, generates_data, generates_model,
  expands_variants, aggregates_predictions, supports_sample_weights,
  supports_row_resampling, supports_backend_loss_weights, supports_missing_masks`.
- `fit_scope`: `stateless, fold_train, full_train, inference_only`.
- `rng_policy`: `uses_core_seed, ignores_seed, externally_deterministic, nondeterministic`.
- `artifact_policy`: `serializable, host_only, content_addressed, replay_required`.
- `operator_selector`: any of `aliases | classes | class_prefixes | functions |
  refs | types` (each a non-empty string set; selector matching is
  case/whitespace-normalized, and a class FQN also matches by its basename).

**Cross-field invariants enforced by `validate()`** (these constrain the adapter
— a generated manifest that violates them is rejected at `register`):

- `supported_phases` non-empty; `controller_version` non-empty.
- `Nondeterministic` rng ✗ with `deterministic` capability.
- `inference_only` ✗ with `FIT_CV`/`REFIT` phases.
- `FIT_CV` ⇒ `fit_scope ∈ {stateless, fold_train}` (not `full_train`/`inference_only`).
- a `prediction` output port ⇒ `emits_predictions`; an `artifact` output port ⇒ `emits_artifacts`.
- `data_requirements`, if present, must be a valid `ModelInputSpec`.

**Registry resolution** (`ControllerRegistry::resolve_for_node`):

1. if `node.metadata.controller_id` is set → bind that exact controller (kind must match), else
2. candidates = manifests with `operator_kind == node.kind`; rank
   `OperatorSelector` match **above** `GenericKind` (empty-selector) match; then
   lower `priority`; then `controller_id`.
3. a tie at equal rank **and** priority is a **hard error** demanding an explicit
   `metadata.controller_id`. `infer_operator_kind` can derive a NodeKind from a
   bare alias via selectors, refusing cross-kind ambiguity.

### 1.2 `OperatorController` (nirs4all) — the imperative ABC (31 registered)

```
class OperatorController(ABC):
    priority: int = 100                       # lower = matched first
    matches(cls, step, operator, keyword)->bool   # abstract, IMPERATIVE predicate
    use_multi_source(cls)->bool                   # abstract
    supports_prediction_mode(cls)->bool = False   # charts → False
    supports_step_cache(cls)->bool = False        # only stateless preproc → True
    execute(self, step_info, dataset, context, runtime_context,
            source=-1, mode="train", loaded_binaries=None, prediction_store=None)
```

Registry (`registry.py`): a single shared list `CONTROLLER_REGISTRY`, mutated in
place, **sorted `(priority, classname)`**, and `StepRouter` picks the **first**
controller whose `matches()` returns true (silent first-match-wins, no ambiguity
error).

The controller declares almost nothing statically: everything the manifest needs
(`operator_kind`, phases, fit scope, rng, artifact policy, ports, capabilities)
is **implicit in `execute()`** behavior. That asymmetry is the whole adapter
problem (§2).

### 1.3 The de-facto current adapter (already in the tree)

`dagml_bridge.py::controller_manifests()` already hand-authors **5 manifests**.
This is the current ground truth and it dictates the *shape* of the real adapter:

| controller_id | operator_kind | selectors | key capabilities | notes |
|---|---|---|---|---|
| `controller:nirs4all.transform` | `transform` | **empty (kind catch-all)** | deterministic, thread/process_safe, uses_core_rng | x→x_out tabular_numeric |
| `controller:nirs4all.y_transform` | `y_transform` | **empty** | same | y→y_out; bound by DSL **position**, not class |
| `controller:nirs4all.model` | `model` | **empty** | + emits_predictions, emits_artifacts, stateful | y_hat + model ports |
| `controller:nirs4all.merge_concat` | `prediction_join` | **empty** | consumes_oof_predictions, emits_predictions | **executed natively** by dag-ml; manifest is PLAN-time only |
| `controller:nirs4all.meta_model` | `model` | `refs:[nirs4all.meta_model]` | + consumes_oof_predictions | bound via `metadata.controller_id`; non-empty selector keeps it out of the generic model catch-all |

All five share `controller_version=nirs4all.__version__`, `priority=20`,
`supported_phases=[FIT_CV,REFIT,PREDICT]`, `fit_scope=fold_train`,
`rng_policy=uses_core_seed`, `artifact_policy=serializable`.

**Two structural facts this proves** (load-bearing for §2):

1. **The current adapter is kind-level, not class-level.** Selectors are
   deliberately empty. The inline comment is explicit: a generic scaler
   (`MinMaxScaler`) is an X-transform or a y-transform purely by **DSL position**
   (`bare` vs `{"y_processing": …}`), *not* by its class — so a class selector
   would mis-type it. The keyword/position decision happens earlier, in
   `_step_to_dsl`, which assigns the node kind (`{"model":…}`→`model`,
   `{"y_processing":…}`→`y_transform`, bare→`transform`, generators→`generator`).
2. **Coverage is a thin slice.** `detect.py` demotes to the legacy Python path
   any pipeline that contains `branch`, `exclude`, `sample_augmentation`,
   rep-fusion, multi-reshape, or non-trivial generator shapes. The natively
   bridged shape today is essentially `transform* → y_processing → splitter →
   model` + native generators + separation-branch concat-merge + stacking meta.

---

## 2. Adapter spec draft — `OperatorController` → `ControllerManifest`

### 2.1 The core insight: the adapter is a **two-layer projection**, not a 1:1 reflection

`OperatorController.matches(step, operator, keyword)` mixes two independent
routing dimensions. They must project to **different** places in the dag-ml model:

| `matches()` dimension | Example | Projects to | Phase |
|---|---|---|---|
| **keyword / DSL position** | `keyword=="model"`, `{"y_processing":…}` wrapper | `operator_kind` decided by a **lowering rule** | COMPILE (DSL→graph) |
| **operator class / type** | `isinstance(op, TransformerMixin)`, a methods-PLS type | `operator_selectors` on a manifest | PLAN (registry resolution) |

Consequence: **there is not one manifest per Python controller class.** The
canonical projection is:

- **N generic kind-level host controllers** (one per supported `operator_kind`),
  with **empty** selectors — exactly the pattern `controller_manifests()` already
  uses. The Python runtime controller behind each is the existing
  `TransformerMixinController` / `YTransformerMixinController` /
  `SklearnModelController` / …
- **plus selector-bearing specialization manifests** only where a specific
  operator must bind to a specific (often native) controller — e.g.
  `meta_model` today, and tomorrow a `controller:methods.pls`
  (`aliases:["PLSRegression","PLS"]`, lower priority) that out-ranks the generic
  Python model controller and routes PLS to `libn4m`.

This is also what lets a binding add idiomatic methods **without forking dag-ml**
(roadmap §L16 output): ship a selector-bearing manifest + a host controller.

### 2.2 Field-by-field mapping

Legend — **Mapped** (mechanical), **Inferable** (derivable with a per-kind rule
or behavioral probe), **Authored** (no signal in code; must be declared),
**Blocked** (needs another lane).

| Manifest field | Req | Source today | Adapter rule | Verdict |
|---|---|---|---|---|
| `controller_id` | ✓ | class identity / role | `controller:nirs4all.<role>` (kind-level) or `…py.<ClassName>` (specialization) | **Mapped** |
| `controller_version` | ✓ | — | `nirs4all.__version__` (as bridge does) | **Mapped** |
| `operator_kind` | ✓ | keyword arm of `matches()` + DSL position | **Layer-1 lowering map** keyword→NodeKind (see §2.3) | **Inferable** (lowering) |
| `priority` | – | `OperatorController.priority` (default 100) | copy; semantics align (lower=preferred); **rebase scale** (dag-ml default 0; bridge uses 20) | **Mapped** (+rebase) |
| `supported_phases` | ✓ | `supports_prediction_mode()`; stateful train | model/transform→`[FIT_CV,REFIT,PREDICT]`; output-only chart→ no PREDICT | **Inferable** |
| `input_ports`/`output_ports` | – | none (no port concept) | author per kind (bridge: `x`/`x_out`/`y_hat`/`model`) | **Authored** (representation `Blocked` on L6/L7) |
| `data_requirements` (`ModelInputSpec`) | – | `use_multi_source()`→`multi_source` flag only | partial; representation IDs/types absent | **Blocked** (dag-ml-data reps) |
| `capabilities` | – | behavioral: `stateful` (uses `loaded_binaries`/joblib), `emits_predictions` (writes `prediction_store`), `needs_python_gil` (always, Python host) | infer behavioral set; `thread_safe`/`process_safe`/`deterministic` need author confirmation | **Inferable + Authored** |
| `operator_selectors` | – | class/type arm of `matches()` | reducible **only** for `isinstance(class)` / class-family / keyword-alias predicates; arbitrary predicates are not reducible | **Partial / Impossible** |
| `fit_scope` | ✓ | stateful? model vs transform vs chart | model→`fold_train`(+`full_train` on refit); transform→`fold_train`; output-only→`stateless`/`inference_only` | **Inferable** |
| `rng_policy` | ✓ | none in code | **author-declared**, default `uses_core_seed` | **Authored** |
| `artifact_policy` | ✓ | stateful + joblib | sklearn→`serializable`; DL (TF/torch/jax)→likely `replay_required`/`host_only` | **Inferable + Authored** |

### 2.3 Layer-1 lowering map (keyword/position → `operator_kind`) — proposed

This is the part of `matches()` that becomes a **compile-time rule**, not a
manifest field. Proposed mapping (cross-checked against the NodeKind enum;
✗ = no clean target / native-or-legacy):

| nirs4all keyword / position | `operator_kind` | Note |
|---|---|---|
| bare transformer step | `transform` | already lowered |
| `{"y_processing": …}` | `y_transform` | already lowered |
| `{"model": …}` | `model` | already lowered |
| cross-validator / splitter | `split` | runs as campaign-plan controller, not a data node |
| `{"branch": …}` (duplication) | `fork` | not yet bridged |
| `{"branch": …}` (separation) | `fork` + per-partition `restructure`? | needs DEC |
| `{"merge": "predictions"}` (stacking) | `prediction_join` | concat subset native today |
| `{"merge": "features"}` | `feature_join` | not bridged |
| `{"merge": "all"/"concat"}` | `mixed_join` / `restructure` | needs DEC |
| `{"exclude": …}` | `exclude` | native candidate (handled in `dagml/exclude.py`) |
| `{"tag": …}` | `tag` | native candidate |
| `{"sample_augmentation": …}` / `{"feature_augmentation": …}` | `augmentation` | native candidate; train-scope only |
| `{"concat_transform": …}` | `feature_join` / `transform` | needs DEC |
| `{"rep_to_sources"}` / `{"rep_to_pp"}` | `restructure` / `source_join` | native candidate |
| `{"finetune_params": …}` | `tuner` | Python-only (Optuna) initially |
| generator (`_or_`/`_range_`/`_grid_`/`_cartesian_`/…) | `generator` | native generator subset exists; `expands_variants` |
| chart steps | `chart` | output-only; Python/Studio plugin |

### 2.4 Sidecar fields (NOT current schema — per design §4ter.4 / roadmap CTRL-001)

These are needed by the binding story but are **not** in the v1 manifest. Carry
them as a versioned **sidecar** keyed by `controller_id`, not as new required
schema fields (avoids a breaking schema bump and keeps `validate()` stable):

- `transport`: how the host code is invoked — `runtime_python_internal` (today),
  `jsonl_process_adapter`, `c_abi_vtable`, `wasm_direct`, `cluster_worker`.
- `runtime_requirements`: import/availability gates — **critical for nirs4all**
  because DL backends are lazy-loaded (e.g. `requires: tensorflow|torch|jax`,
  `requires: nirs4all-methods`). A node is "unsupported" in a runtime that lacks
  these.
- `conformance_fixtures`: pointers to the parity/round-trip/leakage fixtures that
  make the controller "supported" (roadmap CTRL-007 / design §4ter.10).

### 2.5 Legacy-only & impossible cases (what the adapter cannot project cleanly)

- **Output-only chart controllers** — `chart` kind exists, but they execute no
  portable ML and `supports_prediction_mode()==False`. Keep as Python/Studio
  plugins; emit a minimal `chart` manifest only if Studio needs them in the graph.
- **`matches()` predicates that inspect step structure or dataset state** (not
  just keyword/isinstance) — selectors cannot be auto-derived; these stay
  Python-runtime-routed (`transport=runtime_python_internal`) or need an authored
  selector.
- **Representation-typed ports / `data_requirements`** — blocked on dag-ml-data
  representation IDs (L6/L7). Until then ports stay coarse (`tabular_numeric` /
  `None`) as the bridge does.
- **Native-execution-but-manifest-for-planning** (e.g. `merge_concat`): the
  manifest exists only so PLAN validates; execution is intercepted natively.
  This is the template for every "replace-by-runtime-controller" case.

### 2.6 Registry-resolution reconciliation (nirs4all ↔ dag-ml)

| Aspect | nirs4all `CONTROLLER_REGISTRY` | dag-ml `ControllerRegistry` | Reconciliation |
|---|---|---|---|
| match mechanism | imperative `matches()`, first-true wins | `kind` filter + declarative selectors | split per §2.1: keyword→lowering, class→selectors |
| ordering | `(priority, classname)` ascending | rank(selector ▷ generic) → priority → id | priority direction matches (lower preferred) |
| ambiguity | **silent** first-match | **hard error** at equal rank+priority | dag-ml is stricter → set `metadata.controller_id` to disambiguate |
| explicit override | none (order only) | `metadata.controller_id` (requested) | new capability; already used by `meta_model` |
| default priority | `100` | `0` (bridge uses `20`) | rebase when porting; keep generic host controllers above specializations |
| kind inference | n/a (keyword decides) | `infer_operator_kind` via selectors | only relevant for minimal bare-alias DSL |

### 2.7 Worked examples (validate the model)

1. `MinMaxScaler()` (bare) → lowering: `transform` → binds
   `controller:nirs4all.transform` (empty-selector catch-all). nirs4all side:
   `TransformerMixinController.matches`.
2. `{"y_processing": MinMaxScaler()}` → lowering: `y_transform` → binds
   `controller:nirs4all.y_transform`. **Same class, different kind** — proof that
   a class selector would be wrong and position must decide.
3. `{"model": PLSRegression()}` → `model` → `controller:nirs4all.model`. Adding a
   native `controller:methods.pls` (`aliases:["PLSRegression","PLS"]`,
   `priority<20`) makes PLS resolve to `libn4m` and out-rank the generic Python
   model controller — the binding-extension path, no dag-ml fork.
4. stacking meta → `model` + `metadata.controller_id=controller:nirs4all.meta_model`
   → bypasses selectors; the `refs` selector exists only to keep it out of the
   generic model catch-all.

---

## 3. Controller inventory & classification (CTRL-000)

**31 registered controllers** (decorated `@register_controller`; sorted
`(priority, classname)`, lower = matched first). Buckets:

- **manifestable** — clean `operator_kind` + `matches()` reducible to declarative
  selectors/keyword; behavioral fields inferable.
- **legacy-only** — bound to Python/`SpectroDataset` semantics or output-only;
  not a portable cross-language manifest in V1 (stays a Python runtime controller).
- **replace-by-runtime-controller** — capability should migrate **down** into
  native dag-ml/methods coordination. Manifest may exist for PLAN only; execution native.
- **unknown** — needs a maintainer decision.

**Counts: 10 manifestable · 10 replace-by-runtime (native candidates) · 11
legacy-only · 0 unknown.**

#### Manifestable (10) — the V1 adapter targets

| Controller | file (under `controllers/`) | prio | match basis | `operator_kind` | note |
|---|---|---|---|---|---|
| TransformerMixinController | `transforms/transformer.py` | 10 | `isinstance(sklearn TransformerMixin)` (X) | `transform` | only one with `supports_step_cache=True`; serializable |
| YTransformerMixinController | `transforms/y_transformer.py` | 5 | `keyword=="y_processing"` + transformer-like | `y_transform` | keyword + isinstance |
| SklearnModelController | `models/sklearn_model.py` | 6 | framework∈sklearn/xgb/lgbm/catboost, else duck `fit&predict` | `model` | broad duck fallback needs a defined "supervised-estimator" selector (flag) |
| TensorFlowModelController | `models/tensorflow_model.py` | 4 | keras class / `@framework('tensorflow')`; gated `TENSORFLOW_AVAILABLE` | `model` | `needs_python_gil`; runtime_requirements=tensorflow |
| PyTorchModelController | `models/torch_model.py` | 4 | `isinstance(nn.Module)` / `framework=='pytorch'`; gated | `model` | runtime_requirements=torch |
| JaxModelController | `models/jax_model.py` | 4 | flax module / `framework=='jax'`; gated | `model` | runtime_requirements=jax |
| AutoGluonModelController | `models/autogluon_model.py` | 5 | `framework=='autogluon'`/`TabularPredictor`; gated | `model` | `artifact_policy=host_only`; embeds own CV/tuning |
| ResamplerController | `data/resampler.py` | 5 | `isinstance(Resampler)` | `transform` (`shape_changing`) | rewrites wl-grid + headers |
| FeatureSelectionController | `data/feature_selection.py` | 5 | `isinstance(CARS, MCUVE)` | `transform` (`shape_changing`) | serializable selector |
| ConcatAugmentationController | `data/concat_transform.py` | 10 | `keyword=="concat_transform"` | `transform`/`feature_join` | persists N sklearn transformers |

#### Replace-by-runtime-controller (10) — native dag-ml/methods candidates

These are the "north-star" coordination/algorithmic features. A thin manifest may
exist for PLAN-time validation (as `merge_concat`/`meta_model` already do), but
execution should be native, not a Python controller.

| Controller | file | prio | keyword/match | `operator_kind` | why native |
|---|---|---|---|---|---|
| BranchController | `data/branch.py` | 5 | `keyword=="branch"` (dup / by_*) | `fork` | sub-pipeline orchestration + CoW snapshots |
| MergeController | `data/merge.py` | 5 | `merge`/`merge_sources`/`merge_predictions` | `feature_join`/`prediction_join`/`mixed_join`/`source_join` | OOF reconstruction + stacking |
| MetaModelController | `models/meta_model.py` | 5 | `isinstance(MetaModel)` | `model`+`aggregator` (`consumes_oof`) | stacking; matches() *is* declarative |
| ExcludeController | `data/exclude.py` | 5 | `keyword=="exclude"` | `exclude` | train-only sample removal (`dagml/exclude.py` exists) |
| TagController | `data/tag.py` | 5 | `keyword=="tag"` | `tag` | tag columns |
| SampleAugmentationController | `data/sample_augmentation.py` | 10 | `keyword=="sample_augmentation"` | `augmentation` (`generates_data`,`expands_variants`) | train-only; class-aware planning |
| FeatureAugmentationController | `data/feature_augmentation.py` | 10 | `keyword=="feature_augmentation"` | `augmentation`/`restructure` | sub-step orchestration over processing lists |
| CrossValidatorController | `splitters/split.py` | 10 | `keyword=="split"` / duck `op.split(X,…)` | `split` | campaign-plan controller; match() partly reflective (flag) |
| RepToSourcesController | `data/repetition.py` | 3 | `keyword=="rep_to_sources"` | `restructure` | reshape reps→sources |
| RepToPPController | `data/repetition.py` | 3 | `keyword=="rep_to_pp"` | `restructure` | reshape reps→preprocessings |

#### Legacy-only (11) — stay Python runtime controllers

| Controller | file | prio | basis | why legacy-only |
|---|---|---|---|---|
| SpectraChartController | `charts/spectra.py` | 10 | `keyword∈{chart_2d,chart_3d,…}` | output-only viz; `chart` kind but no portable ML |
| AugmentationChartController | `charts/augmentation.py` | 10 | augment-chart keywords | viz |
| ExclusionChartController | `charts/exclusion.py` | 10 | exclusion-chart keywords | viz |
| FoldChartController | `charts/folds.py` | 10 | `fold_chart`/`fold_*` | viz |
| SpectralDistributionController | `charts/spectral_distribution.py` | 10 | spectra-dist keywords | viz |
| YChartController | `charts/targets.py` | 10 | `y_chart`/`chart_y` | viz |
| ResidualModelController | `models/residual_model.py` | 5 | `isinstance(ResidualModel)`/`keyword=="residual"` | re-routes sub-models through Python router; composes `base+λ·gate·learner` |
| AutoTransferPreprocessingController | `data/auto_transfer_preproc.py` | 9 | `keyword=="auto_transfer_preproc"` | imperative distributional-distance preproc search |
| RepFusionController | `data/rep_fusion.py` | 3 | `keyword=="rep_fusion"` | bound to `RawMultiSourceDataset` staging + `dataset_override` |
| DummyController | `flow/dummy.py` | 1000 | `return True` (catch-all) | not a selector; becomes the manifest no-match/default path |
| FoldFileLoaderController | `splitters/fold_file_loader.py` | 9 | `keyword=="split"` + str path `.csv/.json/.yaml/…` | declarative match but reads arbitrary **host filesystem** → `host_only` |

#### `matches()` predicates NOT reducible to declarative selectors

These force a sidecar/authored selector or stay Python-routed (`transport=
runtime_python_internal`):

1. **CrossValidatorController** — accepts any object via `inspect.signature(op.split)`
   (first param named `X`): reflective duck-typing; needs a declared splitter
   selector (`BaseCrossValidator` family + `functions`/`refs`).
2. **DummyController** — `matches()==True` always (priority-1000 catch-all) → maps
   to the registry's default/no-match path, not a selector.
3. **SklearnModelController** — `ModelFactory.detect_framework` + broad duck
   `hasattr(fit) and hasattr(predict)` with explicit tf/torch/jax rejection.
4. **TensorFlow/PyTorch/Jax/AutoGluon ModelController** — gated on `*_AVAILABLE`
   (host capability → `runtime_requirements` sidecar) + module-name string sniffing.
   Reducible to a framework-tag/class-registry selector, but not as written.

Plus two **declarative-in-match but non-portable-in-execution** (host-bound, stay
legacy): **FoldFileLoaderController** (arbitrary host file) and **RepFusionController**
(`RawMultiSourceDataset` Python staging object).

---

## 4. Studio node-registry reconciliation plan (CTRL-002b)

### 4.1 Where the Studio catalog comes from today (confirmed)

The catalog is **build-time introspection of the installed `nirs4all` package**,
not the dag-ml manifest. `src/` / `api/` / `scripts/` contain **zero** references
to `ControllerManifest`, `operator_kind`, `supported_phases`, `data_requirements`,
or `operator_selectors`. The generator `scripts/generate_registry.py` walks
`nirs4all.operators.{transforms,filters,augmentation,splitters,models.sklearn,
models.meta}`, derives each node's `type` from the **Python module path** via
`_determine_node_type()` (into Studio's private **8-value `NodeType`**), pulls
`parameters` from `inspect.signature()`, and reads a `_webapp_meta` attribute
(category/tier/tags) **authored on the operator classes inside the nirs4all
library**. Output: `src/data/nodes/generated/canonical-registry.json` (319 nodes,
`nirs4allVersion 0.10.0`) + curated `definitions/<category>/*.json` + a
`ui-overlays.json` overlay. The backend `api/node_registry_loader.py` merges
curated + canonical; `api/pipeline_canonical.py` and `api/system.py` consume it.

**This is the "divergent product node-registry" §4ter (lines 884–886) warns
against**: keyed on Python `classPath` + a Studio-private taxonomy ("consolidated
16→8 functional types"), it does not line up with dag-ml's **20-variant
`NodeKind`**, carries no `controller_id`, no port/phase data, and reflects
"whatever operators are importable" rather than "what controllers the runtime
registers". A second wrinkle: product metadata (`category`/`tier`/`tags`)
currently lives **inside the library** as `_webapp_meta` — reconciliation should
move it into Studio's overlay so the portable manifest stays UI-free.

### 4.2 Field classification (grouped; full per-field audit available)

| Group (Studio `NodeDefinition` fields) | Classification | Maps to |
|---|---|---|
| `type`, `subType`, `isGenerator`, `isContainer`, `containerType`, `generatorKind/Type`, `childTypes`, `isVisualization`, `trainOnlyContainer` | **from-manifest** | `operator_kind` (`NodeKind`) — make Studio's 8-value `NodeType` a **view over** `NodeKind`, not a parallel enum |
| `classPath`, `aliases`, `functionPath`, `legacyClassPaths`, `implementationRefs`, `capabilities.{implementationRefs,requiredPackages}` | **from-manifest** | `controller_id` + `operator_selectors` (classes/aliases/functions/refs/prefixes/types) |
| `validAfter`, `validBefore`, `requiresSplitter`, `childTypes`, `_webapp_split.{groupRequired,groupHandling,runtimeOnlyParams}` | **from-manifest** | `supported_phases` + `input_ports`/`output_ports` + `data_requirements` + `fit_scope` — **replaces hardcoded heuristics** in `registryIntegration.ts` and `validation/engine.ts` |
| `version`, `maxVersion`, `RegistryConfig.nirs4allVersion` | **from-manifest** | `controller_version` / runtime manifest-set version |
| `parameters[].{name,required,default}` + type-hint half of `type`/`options` | **hybrid** | operator signature (manifest/selector surface) |
| `isDeepLearning`, `supportsParameterSweeps`, `supportsFinetuning`, `supportsStepGenerator`, `source` | **hybrid** | `capabilities` + `Tuner`/`Generator` kinds (fact) ⊕ UI affordance |
| `name`, `id` | **hybrid** | operator identity (manifest) ⊕ slug/label convention (Studio) |
| `description`, `longDescription`, `category`, `icon`, `color`, `tags`, `tier`, `isAdvanced`, `isExperimental`, `isDeprecated`, `deprecationMessage` | **product-metadata** | UI copy / palette / search / visibility |
| `layout`, `defaultBranches`, `maxInstances`, `isComment`, `_webapp_meta` | **product-metadata** | editor canvas / curation |
| `parameters[].{min,max,step,minLength,maxLength,pattern,placeholder,unit,group,order,isAdvanced,isExpert,isHidden,validator,sweepPresets,finetuneRange,option labels}` | **product-metadata** | widget/UX layer of the param editor |
| `ColorScheme`, `CategoryConfig`, `FeatureFlags`, `RegistryConfig` plumbing | **product-metadata** | registry config |

### 4.3 Reconciliation plan (CTRL-002b)

- **New runtime endpoint** (the keystone): `GET /api/operators/manifests` that
  enumerates the `ControllerManifest`s **registered by the installed runtime**
  (not a `pkgutil` walk of importable classes). Replace `generate_registry.py`
  introspection + `node_registry_loader.load_editor_registry_nodes()` so the
  catalog **== the controller registry by construction** — this is what kills the
  divergence. Point the frontend `extended.json` fetch in `NodeRegistryContext.tsx`
  at this output. (Depends on `LOCK-RT` for the route shape; design §4ter.11 lists
  exactly this surface: "list installed controller manifests", "inspect which
  controller would own each node".)
- **Switch to manifest-fed:** the identity/kind/sequencing/version/param-core rows
  above. Drop the path-substring type inference (`registryIntegration.ts`) and the
  `SavitzkyGolay`/`n_components`/`test_size` hardcodes (`validation/engine.ts`) in
  favor of port/phase compatibility derived from the manifest.
- **Stays Studio-owned**, as a thin overlay keyed by `controller_id`
  (`ui-overlays.json` + `categories/*.json`): all product-metadata rows above +
  the widget half of `parameters[]`. Move library `_webapp_meta` into this overlay.
- **Studio payoff** (§4ter goal): the UI can show *"this node will run via
  controller X in runtime Y"* before Run, and surface unsupported-node diagnostics
  (CTRL-006) from manifest absence / phase / representation mismatch.

---

## 5. Per-binding deliverables & transport policy (CTRL-004/005)

### 5.1 Transport policy (design §4ter.7) — confirmed against the contract

| Transport | Target | Default for | Status |
|---|---|---|---|
| Runtime-internal Python calls | `nirs4all` first-party | the existing Python controllers | **in use** (`transport=runtime_python_internal`) |
| JSONL process adapter | R / MATLAB / other host langs | the stable cross-language path | example adapters exist in `dag-ml/examples/adapters/` |
| C ABI controller vtable | in-process native / Rust | advanced native embedding | ABI exists (`dag-ml-capi`); not the default Python/R path |
| WASM direct calls | browser portable subset | operators compiled into core/WASM | for `nirs4all-web` |
| Cluster task execution | remote worker | controller runs on the worker runtime | `nirs4all-cluster` |

Policy: process adapters are the default stable path for non-native hosts; a
manifest that names executable code is **trusted code** → the runtime must
enforce allowlists/timeouts/tempdir/env/artifact confinement.

### 5.2 Per-binding deliverables matrix

**Critical caveat (do not conflate the two transports — `docs/HOST_ADAPTER_BACKLOG.md`):**
the **C-ABI controller vtable** (`DagMlControllerVTable`) is for **in-process
Rust controllers compiled into the scheduler binary only**; **Python / R /
external hosts use the process-adapter JSONL contract.** Native PyO3/JNI vtable
wrappers are an explicit **anti-goal**. The browser is a third case: it can spawn
no process, so it needs a synchronous **in-process JS controller** (calling
`libn4m` via WASM).

Each binding must supply the five deliverables (design §4ter.6): (1) manifest
registry, (2) transport/process adapter, (3) data bridge (views→matrices/tensors,
**identities only over the wire, no row-position joins**), (4) artifact
serialization/replay policy, (5) conformance fixtures + unsupported diagnostics.

#### Transport inventory (existing reference adapters)

| Adapter | Lang | Transport | Emits | fit/predict | artifact |
|---|---|---|---|---|---|
| `python_process_controller.py` | Python | process-JSONL (`--describe`, one_shot, `--jsonl`) | description (not full manifest) | phase-routed, mock | mock, backend `json` |
| `sklearn_process_controller.py` | Python | process-JSONL | description | real `Ridge`/`Pipeline`, OOF+refit | `joblib` |
| `sklearn_production_controller.py` | Python | process-JSONL + declarative `*.controller.json` manifest | manifest file (validated) | 24-class resolver, SIGALRM fit-timeout | real `joblib`, confined to `$DAG_ML_PROCESS_ARTIFACT_DIR` |
| `flaky_process_controller.py` | Python | process-JSONL | inherits | delegates after one hang/error | delegates — the timeout/retry fixture |
| `prospectr_process_controller.R` | R | process-JSONL (jsonlite) | description + `*.controller.json` | transform-only (real `prospectr`) | none (stateless) |
| `mdatools_process_controller.R` | R | process-JSONL | description + `*.controller.json` | model fit/predict | `RData`, path-confined |
| `DagMlControllerVTable` | Rust/C-ABI | **in-process vtable** (`invoke` over NodeTask/NodeResult JSON) | manifest validated separately | behind `invoke` (phase-typed) | via `DagMlArtifactStoreVTable` |
| PyO3 `dag_ml` wheel | Python in-proc | in-process FFI — **compile/plan/validate only** | **validates** manifests; **no register/run** today | **none exposed** | none |

#### Process-adapter envelope (the contract a host must implement)

- **Handshake** (`process_adapter_description.schema.json`, on `--describe`):
  `schema_version=1`, `protocol="dag-ml-process-adapter"`, `adapter_id`,
  `supported_modes ⊆ {one_shot, jsonl}`, `capabilities` (must include
  `node_task_json_v1` + `node_result_json_v1`).
- **Frames** (`process_adapter_frame.schema.json`, JSONL): coordinator→host
  `init{controller_id,worker_index,worker_count}` / `task{NodeTask}` / `close`;
  host→coordinator `ack` / `result{NodeResult}` / `error{code,message,retryable}`.
  One-shot mode = bare NodeTask in → bare NodeResult out.
- **NodeTask** (req): `run_id, node_plan, phase, variant_id, fold_id, seed`;
  `node_plan` carries `controller_id/version, kind, supported_phases, fit_scope,
  rng_policy, artifact_policy, input/output_nodes, params_fingerprint`. Host
  consumes `data_views` (**`partition, sample_ids, columns, source_ids` — no
  matrices**), `prediction_inputs` (OOF meta-features), `artifact_inputs` (replay
  refs on PREDICT), `variant.choices[].param_overrides`, `fit_influence`.
- **NodeResult** (req): `node_id` + `lineage` (`record_id, run_id, node_id, phase,
  controller_id/version, variant_id, fold_id, params_fingerprint,
  data_model_shape_fingerprint, aggregation_policy_fingerprint, seed`). Optional:
  `outputs`, `predictions[]` (`partition, fold_id, sample_ids, values`),
  `artifacts[]`+`artifact_handles`, `explanations`.
- **Leakage invariants the host must honor:** FIT_CV fit-view must be `fold_train`
  with a separate `fold_validation` view; PREDICT views must be `predict`; OOF
  prediction inputs must be `validation` partition.
- **artifact vocab to map:** `artifact_policy ∈ {serializable, host_only,
  content_addressed, replay_required}`; `artifact_backend ∈ {joblib, torch,
  tensorflow, onnx, safetensors, json, raw}`.

#### Per-binding deliverables matrix

| Binding | manifest registry | data bridge | artifact policy | transport | conformance fixtures |
|---|---|---|---|---|---|
| **Python in-process (PyO3)** | ✅ validate only; ❌ no register+invoke runtime | ❌ none in wheel | validates bundle; no store binding | in-proc FFI (compile/plan/validate) | drift via `validate_contracts.py` |
| **Python process-adapter** | ✅ declarative `*.controller.json` | host synthesizes X from `sample_id` | ✅ `joblib`, confined dir | ✅ JSONL one_shot + persistent | ✅ `examples/adapters/*` + runtime fixtures; flaky = timeout fixture |
| **R process-adapter** | ✅ `{prospectr,mdatools}.controller.json` | host responsibility; ids only | mdatools `RData` confined; prospectr stateless | ✅ JSONL | ✅ both shipped |
| **nirs4all-methods native (C-ABI)** | ❌ none (kernels only) | would map `n4m_matrix_view_t`; **no view→n4m bridge exists** | n/a (kernels don't serialize) | ❌ no vtable impl — needs a host wrapper repo | ❌ none for dag-ml |
| **WASM (browser)** | ❌ gap: `planning_failed: no controller registered` | needs `dag-ml-data` `WasmInMemoryProvider` | REFIT/PREDICT→JS wiring pending | **in-process JS controller** (no subprocess) | ❌ no WASM example |
| **CLI process host** | consumes declarative manifests; spawn+retry | `--envelope KEY=PATH` + `CoordinatorDataPlanEnvelope` | validates bundle/replay | ✅ **reference host** for JSONL | ✅ `run-process-replay`/`run-mock-campaign` are the drivers |

**Unsupported diagnostics** every binding must surface (CTRL-006): frame
`error{code,message,retryable}` + ADR-11 `DagMlError` descriptor
(`category,code,severity,message,remediation_hint,context`); reference codes
`unsupported_frame_schema`, `invalid_task_frame`, retryable `fit_timeout`.

### 5.3 Methods ownership note (CTRL-003)

**`nirs4all-methods` owns kernels, not controllers.** A grep across its
`cpp/include/`, `bindings/`, `cpp/` for dag-ml/node_task/node_result/
controller_manifest returns **zero** integration hits; `NAMESPACE_MIGRATION_LOG.md`
explicitly lists dag-ml as *not* a methods consumer. The public surface is
`extern "C"` numeric calls (`n4m_*` over stride-aware `n4m_matrix_view_t`), and
`bindings/SPEC.md`'s "manifest" is an unrelated FFI codegen catalog, not a
`ControllerManifest`. **Therefore a PLS/SNV/MSC model controller must NOT live in
nirs4all-methods** — it belongs in a separate controller-host (nirs4all core/io,
a dedicated `nirs4all-controllers` package, or the WASM JS controller), which owns
the manifest + NodeTask→NodeResult handling + the view→`n4m_matrix_view_t` data
bridge, while `libn4m` stays a pure numeric dependency called inside `invoke`.
This is the concrete instance of the §2.7-ex.3 specialization manifest and the
`ARB-003` coupling.

---

## 6. Open decisions for `ARB-004` (→ `DEC-CTRL-001` + sub-decisions)

**`ARB-004`** asks: *does `ControllerManifest` become the canonical binding
surface, with an adapter from `OperatorController`?* Options A/B/C; current
recommendation **A**.

**A4 position: A, with the explicit caveat that "adapter" means the §2.1
two-layer projection, not a 1:1 class reflection.** Option B (keep
`OperatorController` canonical for Python) would let every language binding
reinvent a divergent idiomatic surface — the exact failure §4ter is written to
prevent. The existing `controller_manifests()` already proves A is viable for the
supported slice.

A4 recommends decomposing the umbrella `DEC-CTRL-001` into these ratifiable
sub-decisions (all `proposed`):

| ID | Question | A4 recommendation |
|---|---|---|
| `DEC-CTRL-002` | controller_id **granularity**: one manifest per Python class, or kind-level generic host controllers + selector specializations? | **kind-level generics + selector specializations** (matches current bridge; avoids class/position mis-typing) |
| `DEC-CTRL-003` | where does the **keyword→operator_kind** decision live? | **DSL lowering (COMPILE), authoritative**; `matches()`'s keyword arm becomes a lowering rule, not a selector |
| `DEC-CTRL-004` | `transport` / `runtime_requirements` / `conformance_fixtures`: schema fields or **sidecar**? | **sidecar v1** keyed by controller_id; fold into a manifest **v2** later (keeps `validate()`/JSON stable) |
| `DEC-CTRL-005` | ambiguity policy | adopt dag-ml's **hard-error + explicit `metadata.controller_id`** (drop nirs4all silent first-match) |
| `DEC-CTRL-006` | `rng_policy` / `artifact_policy` authoring | **author-declared with defaults** (`uses_core_seed` / `serializable`); never silently auto-derived |
| `DEC-CTRL-007` | Studio consumes manifests (CTRL-002b) | Studio node = **manifest (runtime/behavioral) + product-metadata overlay**, fed by a runtime "list controller manifests" endpoint |

**Cross-arbitration couplings to flag for A0:**

- `ARB-003` (n4m/methods in the V1 dag-ml path) decides whether a
  `controller:methods.pls` specialization manifest is in V1 scope (§2.7 ex. 3).
- `ARB-005` (core = inspect/validate/capability only) implies **core exposes
  manifest listing/validation/resolution but does not execute** — consistent with
  treating the manifest as the visible surface and runtimes as the executors.
- `LOCK-CAP` owns the capability vocabulary the manifest `capabilities` enum
  feeds; `LOCK-RT` owns the runtime API the §6 Studio endpoint needs. L16 stays
  blocked on both for *implementation*; this report is audit/spec only.

---

## 7. Sync-board handoff (for A0 to integrate — I did not edit the board)

**Proposed L16 lane row update:**

> `L16` Controllers/bindings · `review` · A4 · repos `dag-ml, nirs4all,
> nirs4all-studio, nirs4all-methods` · **Next action:** ratify `ARB-004`→A and
> `DEC-CTRL-002..007`; then implement CTRL-000 adapter as the §2 two-layer
> projection extending `dagml_bridge.controller_manifests()`, and CTRL-002b
> Studio manifest endpoint. · Blockers: `LOCK-CAP`, `LOCK-RT` (impl only).

**Proposed worklog entry:**

> 2026-06-30 | Claude-Opus/L16 (A4) | review | Mapped the 3 controller surfaces +
> the de-facto adapter (`dagml_bridge.controller_manifests`, 5 kind-level
> manifests); produced the `OperatorController→ControllerManifest` adapter spec
> as a two-layer projection (keyword→lowering, class→selectors), field-by-field
> mapping with impossible/sidecar cases, registry-resolution reconciliation,
> Studio node-registry reconciliation frame, per-binding deliverables, and
> ARB-004 sub-decisions DEC-CTRL-002..007. | Read-only; no code/contract changed;
> no tests run (audit). | Maintainer to rule ARB-004 + DEC-CTRL-*; reconcile
> native-vs-fallback coverage with L5 once A3 re-runs (A3 report empty).

**Blockers I am recording (not resolving):**

- `B-CTRL-1` — A3/L5 runtime report is empty (Codex model failure); the
  native-vs-fallback coverage matrix L16 needs for "manifestable vs replace"
  classification is not yet authoritative.
- `B-CTRL-2` — representation IDs absent (L6/L7) block `data_requirements` ports
  beyond `tabular_numeric`.

**Tests/gates run:** none (read-only audit). Implementation lane, when unblocked,
must run dag-ml `cargo test -p dag-ml-core` (controller resolution),
`python3 scripts/validate_contracts.py`, and the nirs4all dual-engine parity
suite for any manifest/selector change.
