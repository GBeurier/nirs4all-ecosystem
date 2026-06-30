# A3 - dag-ml runtime and native coverage report

Date: 2026-06-30
Agent/lane: A3, L5 dag-ml runtime
Repos inspected: `nirs4all`, `dag-ml`
Mode: multi-CLI report mode. No implementation code or `PARALLEL_REFACTORING_SYNC.md` edits.

## Executive Summary

`run(engine="dag-ml")` is present, opt-in, and intentionally behind the legacy
default. The public selector defaults to `legacy`; explicit `dag-ml` enters
`run_via_dagml`, and only catchable capability errors fall back to legacy
(`DagMlUnavailable`, `DagMlUnsupported`, `NotImplementedError`). Runtime bugs and
operator failures are not blanket-swallowed.

The Rust `dag-ml-core` runtime already owns the high-value generic mechanics:
fold validation, scheduler phases, prediction stores, OOF input delivery, branch
merge reassembly, prediction aggregation, scoring, `ScoreSet`, and candidate
selection. The Python side still owns most legacy-shape detection/lowering,
several reshape/materialization orchestration paths, legacy `RunResult`
projection, and the `.n4a` export bridge.

Current conformance has an explicit `EXPECTED_FALLBACK` allowlist of 11 cases.
That count is the immediate blocker for `EXPECTED_FALLBACK == empty`. A second
class of blockers remains after that: several shapes run through dag-ml but are
still Python-expanded or Python-orchestrated before entering the Rust runtime.

Native results are additive and off by default. They write native score sets and
parquet projections, and can persist in-process refit artifacts, but `export()`
still delegates `.n4a` to a legacy refit bridge. `export_model()` only uses native
artifacts for the narrow case of an existing native results directory plus exactly
one captured artifact.

## Runtime Flow Diagram

1. Public API:
   - `nirs4all.api.run.run(...)` accepts `engine` and `results_path`.
   - `nirs4all.pipeline.engine.resolve_engine()` uses explicit arg, then
     `N4A_ENGINE`, then `DEFAULT_ENGINE = "legacy"`.
   - For explicit `engine="dag-ml"`, `api.run` calls `run_via_dagml`; catchable
     unsupported/unavailable errors warn and rerun `_run_legacy`.

2. Python dag-ml bridge:
   - `run_via_dagml()` rejects unsupported non-default run options (`refit is not
     True`, project/session/cache, runner kwargs, persistence-style kwargs).
   - `preflight_dagml_backend()` accepts either the in-process extension or the
     sibling `dag-ml-cli`.
   - The bridge materializes the dataset, chooses a scratch directory, attaches a
     future export spec, and optionally writes native results.

3. Shape routing:
   - `_dispatch_run()` uses `detect.py` predicates and path helpers in
     `run_paths.py`.
   - Concrete pipelines, selected generator forms, repetition, rep-fusion,
     augmentation, separation branches, by-source branches, duplication fusion,
     and a narrow stacking form can enter dag-ml.
   - Unsupported explicit shapes raise catchable `DagMlUnsupported` or
     `NotImplementedError`; operator-lowering misses may demote to Python
     expansion before another dag-ml run.

4. DSL/envelope/fold preparation:
   - Python builds the executable DSL, controller registry, graph artifact,
     materialization envelope, fold set, and model-node data bindings.
   - Fold sets are passed into dag-ml; dag-ml validates their leakage and
     completeness invariants.

5. Runtime adapter:
   - The in-process path calls `dag_ml._dag_ml.run_cv_refit_in_process`; the
     subprocess path shells through `dag-ml-cli run-process-dsl-cv-refit-bundle`.
   - Both paths use Python `node_runner.run_node` as the host operator callback.
     This boundary is expected: model/preprocessing/augmentation operators remain
     host-owned.

6. Rust runtime:
   - Scheduler executes phases and variants, invokes host controllers through
     `NodeTask`, validates `NodeResult`, appends predictions/aggregates, captures
     refit artifacts, scores blocks, and delivers OOF/off-fold prediction inputs.
   - Merge handlers reassemble separation concat, fusion, and off-fold
     REFIT/PREDICT predictions under the merge producer.
   - Aggregation reducers and scoring create `ScoreSet`; selection chooses the
     winning candidate deterministically from native candidate scores.

7. Compatibility projection:
   - Python `result.py` projects native `ScoreSet` and optional captured results
     into legacy `Predictions`/`RunResult` rows (`avg`, `w_avg`, `final`, etc.).
   - Optional `native_results.py` writes `score_set.json`, `predictions.parquet`,
     `manifest.json`, and in-process model artifacts.

8. Export:
   - `RunResult.export()` for dag-ml delegates to a frozen legacy rerun.
   - `RunResult.export_model()` tries native joblib only for exactly one captured
     native artifact and otherwise uses the same legacy bridge.

## Coverage / Fallback Matrix

| Surface | Current route | Native ownership | Python-owned / fallback residue |
| --- | --- | --- | --- |
| Engine selection | Python public selector | None; default remains `legacy` | Backend absence and unsupported shapes fall back to legacy by design. LOCK-DROP must decide whether this becomes hard error. |
| Concrete single model / preprocessing | dag-ml DSL plus host operator callback | Scheduler, folds, OOF, scoring, selection/refit phases | Lowering and operator routing remain Python bridge code; host operators are expected boundary. |
| Fold semantics | Python builds fold set, Rust validates | `FoldSet::validate()` enforces train/validation disjointness, group boundary, and partition-mode OOF completeness | Split construction is still host-side for nirs4all cases. |
| Prediction store | Rust runtime | `InMemoryPredictionStore` and aggregated store validate and index blocks | Python only projects results for compatibility. |
| Scoring and selection | Rust runtime | `apply_result_scoring`, metrics, `ScoreSet`, `select_candidate`, grouped selection | Python chooses metric string (`rmse`/`balanced_accuracy`) and projects selected result. |
| OOF and stacking inputs | Rust scheduler | `requires_oof` input delivery and REFIT/PREDICT off-fold prediction inputs | Python detector only accepts a narrow stacking syntax. |
| Separation concat branch | dag-ml for exact shape | Native fan-out and concat merge reassembly, fold coverage checks, native scores | Richer branch syntax and merge options can fall back. |
| Duplication / by-source fusion | dag-ml for exact mean/avg shapes | Native cross-branch reduction and fusion merge scoring | `proba_mean`, source concat, feature merge, "merge all", and named/metamodel variants are not fully covered. |
| Stacking | dag-ml for exact duplication + predictions merge + meta model | Native OOF/off-fold transport; Python host fits meta model from prediction inputs | Richer stacking options fall back. |
| Param-level model sweep | Native generation path | Native variants, selection, refit winner | Python derives legacy config names and params for compatibility. |
| Operator generators | Native for recognized `_or_`, constrained, and unconstrained forms | Native variant execution and SELECT where lowered | Other generator shapes are Python-expanded, then each concrete route is run through dag-ml; some PYREF generator cases are divergent/xfailed. |
| Repetition | dag-ml path for group-aware repetition | Native resampled/partition scoring and selection | Some combinations are rejected; rep-fusion is separate and still host-reshaped. |
| Rep-fusion (`rep_to_sources`, `rep_to_pp`) | dag-ml after host reshape | CV/refit/scoring once reshaped dataset is supplied | `run_paths.py` performs production reshape in Python; conformance currently xfails semantic divergence. |
| Sample augmentation | dag-ml after host materialization | CV/refit/scoring on augmented dataset/folds | Augmentation controller and fold-local child construction are Python-orchestrated; several augmentation cases xfail. |
| Native results | Python writer over native ScoreSet | ScoreSet is native and hash-validated on read | Persistence/projection/artifact packaging is Python-side and off by default. |
| `.n4a` / export | Legacy bridge | None for `.n4a` today | Native `export_model` only for one artifact with results enabled; multi-artifact and `.n4a` still legacy-refit. |

## Current Expected Legacy Fallbacks

The PYREF conformance boundary currently allows 11 expected fallbacks:

- Branch duplication / merge:
  - `branch_dup_three_way_merge_predictions`
  - `branch_dup_two_way_merge_features`
  - `branch_dup_named_with_metamodel`
  - `branch_dup_merge_all`
- Multi-source / by-source / source concat:
  - `multi_source_by_source_branch_shared_preproc`
  - `multi_source_by_source_branch_distinct_preproc`
  - `multi_source_per_source_models_stacking`
  - `multi_source_sources_concat_then_rf`
- Preprocessing keyword / fit-on-all / force-layout:
  - `preprocessing_explicit_keyword`
  - `preprocessing_fit_on_all`
  - `preprocessing_force_layout_2d`

The list above is the concrete `EXPECTED_FALLBACK` blocker for the DML-003
`EXPECTED_FALLBACK == empty` objective.

## Blockers For `EXPECTED_FALLBACK == empty`

1. The 11 allowlisted conformance cases above still require legacy fallback.
2. Python `detect.py` accepts only exact branch, merge, by-source, duplication,
   and stacking shapes. Richer but valid legacy graph forms are rejected before
   the Rust runtime can reason about them.
3. Preprocessing keyword forms (`preprocessing=...`), `fit_on_all`, and
   `force_layout_2d` are not lowered to dag-ml.
4. Classification probability fusion (`proba_mean`) exists in Rust reducers but
   is not wired through the nirs4all duplication/by-source bridge as a supported
   route.
5. Top-level run features remain rejected for dag-ml: project/session/cache,
   non-default `refit`, unsupported runner kwargs, and legacy workspace/store
   persistence knobs.
6. Backend availability still means transparent legacy fallback. LOCK-DROP needs
   a product decision: required dag-ml dependency or explicit hard failure.
7. `.n4a` export is not native. The existing export bridge reruns legacy and can
   warn for stochastic runs; that is incompatible with a full native handoff.
8. Several native routes still have conformance xfails rather than expected
   fallback. These are not blockers for "fallback count equals zero", but they
   are blockers for declaring dag-ml behavior fully authoritative without a
   fix-or-accept decision: augmentation RNG/order, feature augmentation replace,
   concat transform, finetune/Optuna generator behavior, unseeded sample
   generator behavior, and rep-fusion semantics.
9. Some paths count as "dag-ml native" from the public API but still perform
   generic orchestration in Python first: operator generator expansion fallback,
   rep-fusion reshape, augmentation materialization, legacy-name projection, and
   legacy `RunResult` row synthesis.

## DML Work Breakdown

### DML-002 - Move Generic Runtime Slices Down Into dag-ml

1. Move shape grammar out of `nirs4all/pipeline/dagml/detect.py` and into a
   native dag-ml lowering/planning layer, or expose an explicit lowering contract
   that returns structured unsupported reasons instead of Python exact-shape
   gates.
2. Branch/fusion/stacking slice:
   - Cover duplication, by-source, separation, source concat, merge-all,
     prediction merge, feature merge, named branches, and metamodel branches as
     native graph constructs.
   - Keep actual operators/controllers host-owned; move the generic scheduling,
     OOF, merge, and selection orchestration down.
3. Generator slice:
   - Nativeize remaining finite/random/sampled generator forms, including count,
     seed, distribution metadata, and deterministic variant labels.
   - Treat Python expansion as a temporary compatibility path with an explicit
     measurement bucket.
4. Rep-fusion slice:
   - Move repetition relation/reshape planning to dag-ml.
   - Python should provide data views/materialized handles, not decide generic
     repetition-to-source/preprocessing orchestration.
5. Augmentation slice:
   - Move parent/child sample relation semantics, fold-local inclusion/exclusion,
     and selection/scoring rules to dag-ml.
   - Keep augmentation operator execution in the host; do not materialize feature
     buffers inside core.
6. Fold/split slice:
   - Decide whether split construction remains host-owned permanently or whether
     dag-ml should own generic KFold/group/repeated split specs for PYREF parity.

### DML-003 - Native-vs-Fallback Measurement

1. Add a PYREF inventory runner that records, per case:
   - native dag-ml route
   - native but Python-expanded
   - native but Python-orchestrated pre-materialization
   - legacy fallback
   - xfail/known divergence
   - skip reason
2. Publish both machine-readable JSON and a small markdown summary under
   ecosystem reports or generated artifacts. Include total cases, runnable cases,
   fallback count, expected fallback count, unexpected fallback count, and native
   divergence count.
3. Keep `test_native_fallback_boundary` as the hard guard, but make the summary
   explicit enough that shrinking `EXPECTED_FALLBACK` is visible in review.
4. Add a lock-drop gate: `EXPECTED_FALLBACK` must be empty, and the coverage
   report must show zero unexpected fallbacks.

### DML-008 - Native Export

1. Replace the dag-ml `.n4a` legacy-refit bridge with native bundle export based
   on `ScoreSet`, selected variant, graph/DSL, fold set, manifest, prediction
   cache, and captured artifact refs.
2. Support multi-artifact native exports for branches/stacking, not just exactly
   one model artifact.
3. Make model artifact persistence independent of the optional compatibility
   results writer, or make native results mandatory for native export.
4. Add replay/read validation that checks content fingerprints and refuses
   missing or stale artifacts.
5. Keep legacy export available only as an explicit compatibility mode until it
   can be removed.

## Tests And Gates To Run

No full test gates were executed during this audit. Work performed: CodeGraph
lookup plus direct `rg`/`nl` source reads.

Recommended gates before changing status:

```bash
cd nirs4all
pytest tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary -q
pytest tests/integration/parity/test_conformance_dual_engine.py -q
pytest tests/integration/parity/test_dagml_cli_runner.py \
  tests/integration/parity/test_dagml_operator_generation_phase7.py \
  tests/integration/parity/test_dagml_native_results.py \
  tests/integration/parity/test_dagml_native_export_model.py -q
pytest tests/integration/parity/test_conformance_export_roundtrip.py -q
ruff check nirs4all tests/integration/parity
```

```bash
cd dag-ml
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo run -p dag-ml-cli -- validate-graph examples/minimal_graph.json
python3 scripts/check_so_freshness.py
python3 scripts/validate_contracts.py
```

## A0 Sync Board Handoff

Do not apply this directly in multi-CLI mode; A0 owns
`PARALLEL_REFACTORING_SYNC.md`.

Suggested lane/worklog update:

- L5 dag-ml runtime: A3 audit complete. Report:
  `docs/agent_reports/A3_A3-dagml.md`.
- Current state: `run(engine="dag-ml")` is opt-in and mostly native for runtime
  scoring/scheduling, but Python still owns shape detection/lowering,
  rep-fusion/augmentation orchestration, compatibility projection, and legacy
  export bridge.
- Native fallback blocker: `EXPECTED_FALLBACK` currently has 11 cases.
- Next work: DML-003 coverage meter, DML-002 branch/generator/rep-fusion/
  augmentation migration slices, DML-008 native export.
- Tests executed by A3: none; source audit only.
- Blockers: DEC/contract decisions needed before moving cross-repo schema/export
  contracts or changing fallback policy.

## Source References

- `nirs4all/nirs4all/api/run.py`: public engine selector, fallback boundary, and
  legacy rerun behavior.
- `nirs4all/nirs4all/pipeline/engine.py`: `DEFAULT_ENGINE = "legacy"` and
  `N4A_ENGINE` resolution.
- `nirs4all/nirs4all/pipeline/dagml/run_backend.py`: option rejection,
  preflight, `run_via_dagml`, `_dispatch_run`, export spec attachment.
- `nirs4all/nirs4all/pipeline/dagml/detect.py`: Python exact-shape routing
  predicates for generators, branches, rep-fusion, duplication, and stacking.
- `nirs4all/nirs4all/pipeline/dagml/run_paths.py`: concrete, generator,
  repetition, rep-fusion, augmentation, branch, by-source, duplication, and
  stacking run paths.
- `nirs4all/nirs4all/pipeline/dagml/cli_runner.py`: process DSL bundle assembly,
  data bindings, fold invocation, CLI adapter.
- `nirs4all/nirs4all/pipeline/dagml/in_process_runner.py`: in-process extension
  routing and refit artifact capture.
- `nirs4all/nirs4all/pipeline/dagml/node_runner.py`: host operator execution,
  transform chains, y transforms, model/meta-model prediction emission.
- `nirs4all/nirs4all/pipeline/dagml/result.py`: native `ScoreSet` to legacy
  `Predictions`/`RunResult` projection.
- `nirs4all/nirs4all/pipeline/dagml/native_results.py`: additive native results
  writer/reader and joblib artifact loader.
- `nirs4all/nirs4all/api/result.py`: dag-ml export/export_model legacy bridge and
  narrow native model-artifact path.
- `nirs4all/tests/integration/parity/test_conformance_dual_engine.py`:
  `EXPECTED_FALLBACK`, known divergences, and native/fallback boundary tests.
- `dag-ml/crates/dag-ml-core/src/fold.rs`: fold leakage/completeness validation.
- `dag-ml/crates/dag-ml-core/src/runtime/scheduler.rs`: phase execution, merge
  interception, OOF/off-fold prediction delivery, scoring hooks.
- `dag-ml/crates/dag-ml-core/src/runtime/merge.rs`: separation/fusion/off-fold
  branch merge reassembly.
- `dag-ml/crates/dag-ml-core/src/runtime/task.rs`: `NodeResult` contract and
  validation.
- `dag-ml/crates/dag-ml-core/src/runtime/scoring.rs`: native scoring and
  aggregation hooks.
- `dag-ml/crates/dag-ml-core/src/runtime/prediction_store.rs`: prediction and
  aggregated prediction stores.
- `dag-ml/crates/dag-ml-core/src/aggregation.rs`: observation/sample aggregation
  and cross-fold/cross-branch reducers.
- `dag-ml/crates/dag-ml-core/src/metrics.rs`: `ScoreSet` and cross-fold
  validation scoring.
- `dag-ml/crates/dag-ml-core/src/selection.rs`: native candidate and grouped
  selection.
