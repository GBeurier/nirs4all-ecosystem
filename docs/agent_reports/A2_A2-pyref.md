# A2 — L17 PYREF oracle & parity — report

**Agent:** A2 (L17 PYREF) · **Mode:** multi-CLI report (read-only; no edits to `PARALLEL_REFACTORING_SYNC.md` or implementation code) · **Date:** 2026-06-30
**Lane:** `L17` Oracle de parité Python · **Lock:** `LOCK-PYREF` (review) · **Decisions:** `DEC-PYREF-001`, `DEC-PYREF-002` · **Cross-lane:** `LOCK-DROP`/`L19`, `L5`/A3 runtime, `L9` methods, `L12` Studio.

**Repos read:** `nirs4all` (e41362b4 main), `dag-ml` (f58d7bf), `dag-ml-data` (347c15f), `nirs4all-methods` (7602eb08), `nirs4all-studio` (2ccbf68).

---

## 0. TL;DR for A0

1. **The oracle already exists and is far more complete than the sync board implies — adopt, do not rebuild.** `nirs4all/tests/integration/parity/` is a working dual-engine (legacy ↔ dag-ml) conformance harness: **95 registered `PipelineCase`s**, a captured legacy gold baseline, enforced tolerances, and a never-xfailed native/fallback boundary. ADR-17 reports it green at **273/0 dual-engine + 11 documented strict-xfails** on `core/dagml`.
2. **The "3-tier registry" the mission asks me to extract is real but SCATTERED** across five structures in two files. `PYREF-000` below consolidates it into one authority table. This is the load-bearing prerequisite for signing `LOCK-PYREF` (`DEC-PYREF-002`).
3. **One hard blocker to signing `LOCK-PYREF`: the tolerance ledger does not exist.** The dag-ml `parity_oracle.v1` contract declares `consumer_ledger → nirs4all/docs/compatibility.md` with `required_before_bridge: true` and tolerance `1e-9`, but **that file is MISSING** and the *actual* enforced tolerance is `1e-3`. Tolerances are split across three inconsistent sources. `LOCK-PYREF` cannot "fix tolerances" until this is authored.
4. **Five cross-engine surfaces the mission flagged are GAPs:** `.n4a` cross-engine read/predict, workspace cross-engine, error-parity, Studio-on-the-oracle, and methods-installed/`.so`-freshness CI. Each is itemised in §4 with EXISTS/GAP + evidence.
5. **`LOCK-DROP` is blocked downstream of me:** `EXPECTED_FALLBACK` is non-empty (11 shapes still fall back to legacy). The oracle already *measures and gates* this; closing it is **L5/A3 runtime work**, not L17. My oracle is ready; the cutover criterion is not met.

---

## 1. Adopt-don't-rebuild — what already exists

`nirs4all/tests/integration/parity/` (markers `parity`/`slow` registered in `nirs4all/pyproject.toml:223-227`):

| File | Markers | What it proves (the single load-bearing thing) |
|---|---|---|
| `_oracle.py` | — | Layer 0–2: `observe()` extracts a JSON observation from `RunResult`; `compare()` enforces exact structure (`num_predictions`/`models`/`datasets`) + per-metric abs tolerance; `save/load_baseline` persist gold under `baselines/`. Legacy = oracle of record (ADR-01). |
| `_registry.py` | — | `PipelineCase` frozen contract + import-time validation (`keywords ⊆ CANONICAL_KEYWORDS`, `capabilities ⊆ COMMON_CAPABILITIES`, dataset key resolves). `skip_kind ∈ {"",fixture,unknown_semantics,legacy_bug}` (`:37`). `keyword_coverage()`/`capability_coverage()`. |
| `_conformance_helpers.py` | — | The dual-run engine: `dual_engine_runner` runs the SAME case on `engine="legacy"` then `engine="dag-ml"` (explicit, load-bearing vs `$N4A_ENGINE`), detects fallback via **two** signals (warning fragment `:54` AND `RunResult._is_dagml_engine`), and asserts score / num_predictions / RunResult-contract / per-sample y_pred parity. Default tols `1e-3` (`:60`,`:65`). |
| `test_conformance_dual_engine.py` | parity, slow | **The contract reference.** ~95 params: native cases assert full parity; fallback cases assert the boundary; `KNOWN_DIVERGENCES`/`legacy_bug` are `xfail(strict=True)`. |
| `test_native_fallback_boundary` (same file `:372`) | parity | **Never xfailed.** Single source of truth for native-vs-fallback: a fallback off the allowlist = native-coverage REGRESSION → FAIL; a native case ON the allowlist = STALE entry → FAIL. The boundary can never silently widen. |
| `test_parity_compiles.py` | parity | Fast/every-commit: every case builds a valid `PipelineConfigs` + every canonical DSL keyword has ≥1 case (allowlist `auto_transfer_preproc`/`na_policy`/`fill_value`). |
| `test_parity_baseline.py` | parity, slow | Layer 1–2: capture/enforce the committed legacy gold (`--parity-capture`). |
| `test_parity_smoke.py` | parity, slow | Every runnable case runs end-to-end on legacy + the public-API paths (round_trip/explain/retrain/session). |
| `test_conformance_examples_smoke.py` | parity, slow | The shipped `examples/user/` tutorials exit clean as subprocesses on **both** engines via `$N4A_ENGINE` (4 examples × 2 = 8). |
| `test_conformance_export_roundtrip.py` | parity, slow | `export_model → reload → predict` on both engines; native single-model dag-ml export reproduces final-(test) y_pred within `1e-6`. |
| `test_generators_conformance_extra.py` | parity | `_depends_on_` is a dead no-op + the EXACT constraint-survivor set is locked vs registry drift. |
| `test_dagml_*` (bridge_spike 6 · dataplane 14 · node_runner 5 · run_selector 10 · cli_runner 103 · native_results 17 · native_export_model 6 · operator_generation_phase7 49) | parity (some slow) | Single-engine dag-ml internals: graph lowering, identity-keyed dataplane, NodeTask FIT_CV vs sklearn, engine resolution+fallback, real `dag-ml-cli` OOF vs sklearn KFold, native results writer + path-traversal hardening, native export, operator-`_or_` JSON-sanitization + demote-to-python-expand. |

**Case corpus (95):** baseline 8 · branches_merges 7 · multi_source 5 · aggregation_reps 6 · augmentation 5 · generators 10 · generators_conformance 40 · tags_exclude 8 · refit_predict 6. Datasets (`_datasets.py`): `regression`, `regression_2`, `multi` (3 NIR sources), `binary`, `classification` + parser fixtures (`dual_source`, `nir_markers`, `aggregate_mean/outliers`, `custom_folds`, `with_metadata`).

> The dag-ml-side war-room doc (`dag-ml/docs/migration-nirs4all/PARITY_AND_PERF_HARNESS.md`) still says "~35 cases" — **stale**; it is 95.

There is a **second, complementary oracle on the dag-ml side**: `dag-ml/docs/contracts/parity_oracle.v1.json` + `conformance_pack.v1.json` gate the dag-ml↔dag-ml-data Rust/WASM/wheel contracts (leakage refusal, OOF join, generation-constraint survivor counts, C-ABI symbols). That is `LOCK-LOCKSTEP`/L20 territory. **L17 owns the pipeline-shape RunResult parity; L20 owns the contract/fixture lockstep.** They meet at the missing `compatibility.md` ledger (§5).

---

## 2. `PYREF-000` — the 3-tier authority registry (DRAFT)

The mission's three tiers exist today but are spread across `_registry.py` (`skip_kind`) and five dicts/sets in `test_conformance_dual_engine.py` (`KNOWN_DIVERGENCES :78`, `NUM_PREDICTIONS_DIVERGENCE :189`, `Y_PRED_TOL_OVERRIDES :244`, `SAME_WINNER_CASES :265`, `EXPECTED_FALLBACK :310`). **`PYREF-000` = lift these into one imported authority module** (proposed `tests/integration/parity/_authority.py`) so `LOCK-PYREF` can be signed against a single fixed table instead of five scattered ones. Below is the consolidated content (this is the deliverable; the module is a proposal, not implemented — no `LOCK-PYREF` yet).

### Tier 1 — **Python (legacy) authoritative** (default; oracle of record, ADR-01)
The ~65 runnable cases that run native on dag-ml and must equal legacy within tolerance (score `1e-3`, y_pred `1e-3`, or the case's `metric_tolerances`; `baseline_vertical_slice` at `1e-6`). No marker; PASS = green parity. This is the implicit majority tier — all green per ADR-17's 273/0.

### Tier 2 — **dag-ml authoritative** (legacy is wrong or was changed)
| Case | Mechanism | Disposition | Evidence |
|---|---|---|---|
| `rep_to_sources_basic` | legacy DOUBLE-COUNTS overlapping rep OOF folds (cv 6.6735); dag-ml aggregates each sample once (6.1906 = correct) | `xfail(strict=True)` vs legacy gold — PERMANENT | dual_engine `:127` |
| `rep_to_pp_basic` | same; legacy 6.1427 vs dag-ml 6.1906 (correct) | `xfail(strict=True)` — PERMANENT | dual_engine `:129` |
| `generator_or_models_pls_ridge` | operator-SELECT refits WINNER only (32); legacy refits losers (34) | **PASS** as documented parity-note; num_predictions pinned 34/32 | `:190` |
| `generator_chain_model_configs` | same, `_chain_` of distinct models (47 vs 49) | **PASS** parity-note; pinned 49/47 | `:196` |
| *(contract-wide)* `best_rmse`/`best_r2`/`best_accuracy` re-anchored on the **SELECTED** model | 0.9.x **bugfix** (legacy pre-fix returned a non-selected fold's metric) | enforced by `assert_runresult_contract` (`best_score` = selected metric) | `CHANGELOG.md:44-56`; helper `:290` |

### Tier 3 — **oracle non-executable / skip_unknown_semantics / rng_nondeterministic** (comparison invalid)
| Case | Sub-class | Disposition | Evidence |
|---|---|---|---|
| `branch_separation_by_tag` | legacy_bug (0.9.1 `_preprocess_steps` string-only) — no legacy oracle | `xfail(strict=True)` | cases_branches_merges `:254` |
| `branch_separation_by_filter` | legacy_bug (0.9.1 `branch.py:643` missing-module import) | `xfail(strict=True)` | `:296` |
| `sample_augmentation_gaussian` / `_chained` / `_after_savgol` | rng_nondeterministic (augmentation RNG/order differs) | `xfail(strict=True)` | dual_engine `:82-84` |
| `feature_augmentation_replace_three_views` | rng (feature-view build order) | `xfail(strict=True)` | `:87` |
| `concat_transform_pca_svd_plsr` | rng (view order/decomposition) | `xfail(strict=True)` | `:88` |
| `generator_finetune_params_optuna` | rng (Optuna trial sequence differs) | `xfail(strict=True)` | `:102` |
| `generator_sample_log_uniform_alpha` | rng (unseeded `_sample_`, different winner) | `xfail(strict=True)` | `:115` |
| `generator_or_count_seed` / `generator_or_weights_count_seed` | skip_unknown_semantics (`_seed_` not threaded into `OrStrategy` → nondeterministic even within ONE engine) | `skip` | cases_generators_conformance `:1072`,`:1097` |
| `refit_params_use_all_partitions` | skip_unknown_semantics (refit_params 0.9.x semantics unpinned) | `skip` | cases_refit_predict `:124` |

### Orthogonal axes (NOT authority tiers — track separately so they don't pollute the registry)
- **Coverage debt — fixture skips (3):** `branch_separation_by_metadata_auto` (no `variety` column), `exclude_multi_any_y_and_x` (corpus too small for 2-filter union), `aggregation_classification_vote` (needs a classification rep fixture). These *can't run*, they make no authority claim.
- **Native-coverage boundary — `EXPECTED_FALLBACK` (11):** shapes the dag-ml **host bridge** does not serialize yet, so `engine="dag-ml"` transparently re-runs legacy. 4 branch/merge (`branch_dup_*`), 4 multi-source (`multi_source_*`), 3 preprocessing-keyword (`preprocessing_explicit_keyword`/`_fit_on_all`/`_force_layout_2d`). **This is the LOCK-DROP blocker, owned by L5/A3** (the dag-ml ENGINE supports branch/merge natively per ADR-17 §2.2; the gap is host serialization). The oracle already pins it (`test_native_fallback_boundary`): when L5 lands coverage, the entry must leave the allowlist or the test fails.
- **Y_PRED_TOL_OVERRIDES (6)** + **SAME_WINNER_CASES (~22):** not divergences — same-winner FirstDerivative-amplified PLS Rust-vs-sklearn noise relaxed to `5e-3` under a load-bearing `assert_same_winner` guard. Keep, but document them in the registry so a future reader does not mistake them for parity debt.

**XPASS discipline (already enforced, keep as a LOCK-PYREF invariant):** every Tier-2-permanent/Tier-3 strict-xfail XPASS-flips the suite RED the moment engines converge — a fixed divergence can never silently vanish from coverage.

---

## 3. Coverage matrix — feature → current test → gap

### 3a. DSL keyword surface (`CANONICAL_KEYWORDS`, enforced by `test_parity_compiles.py`)
Every canonical keyword has ≥1 case **except** the documented allowlist: `auto_transfer_preproc`, `na_policy`, `fill_value` (`test_parity_compiles.py:53-60`). Generator + constraint keywords (`_or_`/`_grid_`/`_range_`/`_cartesian_`/`_zip_`/`_chain_`/`_sample_`, `_mutex_`/`_requires_`/`_exclude_`, `count`/`_weights_`/`then_pick`/`then_arrange`) are densely covered by `cases_generators_conformance.py` (40 cases) and the survivor-set lock. **Gap: 3 allowlisted keywords (transfer-preproc + NA-handling) carry zero parity evidence.**

### 3b. Controller / capability surface (`COMMON_CAPABILITIES`)
| Capability | Cases | Verdict |
|---|---|---|
| sklearn models (PLS/Ridge/RF/GBR), preprocessing, y_processing, splitters/CV, OOF, exclude/tag, branch/merge, multi-source, generators, aggregation/rep | many | **Covered** (Tier 1, green) |
| stacking_meta_model | 2 | Covered (thin) |
| explain_path / retrain_path / session_api / bundle_io | 1 each | **Thin** — single smoke each; SHAP `explain` not numerically compared cross-engine |
| **pytorch_model / tensorflow_model / jax_model** | **0** | **GAP** — the oracle is sklearn-only. DL is inherently RNG (Tier 3) and stays Python-side per the North Star, but there is currently *no* evidence the dag-ml path drives the DL controllers identically. Flag as accepted-Tier-3 or add a fixed-seed smoke. |

### 3c. Cross-engine surface (mission item 4) — detailed in §4
| Surface | Current test | Verdict |
|---|---|---|
| `.n4a` export round-trip | `test_conformance_export_roundtrip.py` | Partial — export+reload+predict on both engines, BUT not "legacy bundle → predicted by dag-ml" |
| Workspace (SQLite/Parquet/manifest) | — | **GAP** |
| Artifacts (`export_model` joblib) | `test_conformance_export_roundtrip.py`, `test_dagml_native_export_model.py` | Covered (native single-model exact; bridge for multi-model) |
| Errors / refusals | — | **GAP** |
| Studio routes on the oracle | — | **GAP** |
| methods-installed CI lane | `tests/unit/operators/methods/test_n4m_ops.py` (skipped in CI) | **GAP (skips silently)** |
| `.so`/wheel freshness | dag-ml CI only | **GAP on nirs4all side** |

---

## 4. Uncovered surfaces (mission item 4) — EXISTS / GAP with evidence

**(1) `.n4a` cross-engine — PARTIAL / GAP.** `test_conformance_export_roundtrip.py` proves `export_model → reload → predict` on both engines and that a *native single-model* dag-ml export reproduces final-(test) y_pred within `1e-6`. **Not covered (PYREF-009):** a **legacy-written `.n4a` bundle loaded and predicted through the dag-ml/runtime path** (and vice-versa). Today this claim is unproven.

**(2) Workspace cross-engine — GAP.** By design the engines write **non-overlapping on-disk formats**: legacy writes `store.sqlite` + `arrays/*.parquet` + `runs/manifest.yaml`; the dag-ml backend returns native scores with **no workspace** (its only on-disk output is the additive, off-by-default native results dir, which `test_dagml_native_results.py:210-219` asserts the legacy engine *ignores*). No test reads/diffs the SQLite rows / parquet / manifest across engines. PYREF-009's real question is "can a legacy workspace be inspected/predicted via the runtime V1 path", not "byte-identical writes".

**(3) Artifacts — COVERED.** Native single-model export is exact (`1e-6`); multi-model/branch falls back to the legacy-refit bridge and only asserts "still round-trips" (`test_conformance_export_roundtrip.py:115`). `test_dagml_native_export_model.py` adds fingerprint-checked verify-then-load. The remaining work (replace the bridge with a native export for the multi-model/fold cases) is an ADR-17 §3 step-9 **LOCK-DROP** item, not a parity gap per se.

**(4) Errors / refusals — GAP.** No test feeds the SAME invalid pipeline to BOTH engines and asserts the same refusal. Every `pytest.raises` in the parity dir is a **single-engine dag-ml-only** rejection (`DagMlUnsupported` in `test_dagml_operator_generation_phase7.py:93…206`; unknown-engine `ValueError` and bug-propagation in `test_dagml_run_selector.py:186-193`; bridge `NotImplementedError` `test_dagml_cli_runner.py:101`). The dual harness asserts agreement only on **successful** runs. Leakage refusal lives on the dag-ml side (`parity_oracle.v1.json` case `repetition_group_leakage_refusal`) but is not asserted as a *cross-engine* equality.

**(5) Studio routes — GAP (PYREF-008).** `NativeResultsAdapter` (`nirs4all-studio/api/native_results_adapter.py:570`) correctly reads the dag-ml native results dir via `nirs4all.pipeline.dagml.native_results.read_native_results` — **no parity gap for the adapter itself.** But: `/api/runs/execution-backends` (`api/runs.py:1543`) selects the execution *environment* (`local-python`/`cluster`/`wasm-local`), **not** the ML engine; Studio **never passes `engine=` and never records which engine ran** (`runs.py:1431`, `training.py:466`, `automl.py:903`, `predict.py:81/89` all call `nirs4all.run/predict` with no engine kwarg), so there is **no evidence Studio workflows are dag-ml-native** — they ride the internal default + silent legacy fallback. No Studio test runs a pipeline through both engines. **Worse:** four backend routes **re-implement nirs4all logic outside the oracle entirely** (`api/transfer.py:412-466` composes preprocessing with raw sklearn scalers + hand-chained SNV/MSC/SG; `api/predict.py:114-122` computes RMSE/R2/MAE/RPD via `sklearn.metrics`; `api/predict.py:283-295` reads CSV/Excel with pandas; `api/analysis.py:553/749/755` runs permutation/MI/F importances in-backend). These violate `BACKEND_RULES.md` and are unverifiable by the PYREF oracle — overlaps **L12**.

**(6) methods-installed CI lane — GAP (PYREF-010).** nirs4all-methods HAS a CI-wired parity ledger (`nirs4all-methods/parity/tolerances.md` + golden `parity/fixtures/*.json` IEEE-754 hex + comparator; workflows `parity-gate.yml`, `cross-binding-parity.yml` (n4m-vs-sklearn), `nightly-parity.yml`). nirs4all HAS the optional native path (`nirs4all/operators/methods/n4m_ops.py:17-38`, `METHODS_AVAILABLE`, `MethodsSNV`/`MethodsPLS`→`libn4m`) and a gating test (`tests/unit/operators/methods/test_n4m_ops.py`: golden SNV `atol=1e-12`, PLS `<1e-9`, dual-engine). **The gap:** that test is `pytest.importorskip("n4m")` (`:29`) and **nirs4all CI never installs `n4m`** (`requirements-test.txt` pins `dag-ml>=0.2.1` but not `nirs4all-methods`), so the entire methods-installed parity **silently skips in CI**. A declared-portable capability must not be a silent skip.

**(7) `.so` / wheel freshness — GAP on nirs4all side (PYREF-011).** dag-ml HAS `scripts/check_so_freshness.py` (guards the tracked `_dag_ml.abi3.so` vs its Rust sources by last-commit timestamp; CI-wired `dag-ml/.github/workflows/ci.yml:89-90`). **nirs4all has nothing analogous:** it tracks zero compiled artifacts and reaches the native engine through the **installed `dag_ml`/`n4m` wheels** — there is no check that the installed wheel's `.so` is fresh vs its upstream sources, so nirs4all CI can go **falsely green against a stale dag-ml/methods build**. (ADR-17 §2.1's "`.so` freshness guard" refers to the dag-ml repo's guard, which protects dag-ml's own committed `.so`, not nirs4all's consumption.)

---

## 5. The tolerance-ledger blocker (must be resolved before `LOCK-PYREF` can fix tolerances)

`dag-ml/docs/contracts/parity_oracle.v1.json` declares:
```
consumer_ledger: { repo: "nirs4all", path: "docs/compatibility.md", required_before_bridge: true }
tolerance_profiles: regression.default abs/rel 1e-9 ; classification.default 0
```
**`nirs4all/docs/compatibility.md` does not exist.** And the *enforced* tolerance is **not** `1e-9` — it is `1e-3` (`_conformance_helpers.py:60` `_DEFAULT_SCORE_TOL`, `:65` `_DEFAULT_YPRED_TOL`), justified by measured sklearn-vs-Rust PLS noise ~`1e-4` and y_processing-inverse ~`6e-4`. So "the tolerance" lives in **three inconsistent places**: the dag-ml contract (`1e-9`), the Python helper default (`1e-3`), and per-case `metric_tolerances` (e.g. `baseline_vertical_slice` `1e-6`). `PARITY_AND_PERF_HARNESS.md:76` already flags "the ADR-01 per-model-class tolerance table must be authored/located" as an open input.

**Action (gates `LOCK-PYREF`):** author `nirs4all/docs/compatibility.md` as the single ADR-01 per-model-class tolerance table; reconcile it with the measured `1e-3` reality (the `1e-9` contract value is aspirational and currently false for PLS); make `LOCK-PYREF` fix *these* numbers. Until then the lock has no stable "tolerances" to sign.

---

## 6. Proposed PYREF commands (deliverable item 5)

Markers already exist (`pyproject.toml:223-227`). Proposed two-tier entry (PYREF-006 wraps these behind one `nirs4all parity` CLI / `make parity`):

**Fast PYREF — every commit, < 1 min, no engine run:**
```bash
pytest tests/integration/parity/test_parity_compiles.py \
       tests/integration/parity/test_generators_conformance_extra.py -q
```
(compile-clean every case + DSL survivor-set lock — pure structure, no dual run.)

**Full PYREF — PR→`core/dagml` + nightly:**
```bash
# 1. the dual-engine pipeline oracle (legacy ↔ dag-ml), all slow cases
pytest tests/integration/parity/ -m parity -q
#    XPASS on any strict-xfail = RED; test_native_fallback_boundary must stay green.
# 2. methods-installed lane (PYREF-010) — install n4m first so it does NOT skip
pip install nirs4all-methods && pytest tests/unit/operators/methods/test_n4m_ops.py -q
# 3. cross-repo freshness + contract lockstep (PYREF-011 / LOCK-LOCKSTEP)
python ../dag-ml/scripts/check_so_freshness.py
DAG_ML_DATA_REPO=../dag-ml-data python ../dag-ml/scripts/validate_contracts.py
```
**Still to add before the full command is complete:** `.n4a`+workspace cross-engine (PYREF-009), error-parity (item 4), a nirs4all-side wheel-freshness gate (PYREF-011), and a Studio runtime-route evidence test (PYREF-008).

---

## 7. Proposed gates for `LOCK-PYREF` (sign-off checklist)

`LOCK-PYREF` may be signed (`DEC-PYREF-001`+`002` → accepted) when:

- **G1 — `PYREF-000` consolidated.** The 3-tier authority table (§2) lives in ONE imported module; the five scattered dicts/sets become views over it; every Tier-2/Tier-3 entry carries a written reason + measured delta. *(spec ready; needs the lock to implement)*
- **G2 — tolerance ledger authored.** `nirs4all/docs/compatibility.md` exists, reconciles `1e-9`(contract)/`1e-3`(helper)/per-case, and is the fixed `LOCK-PYREF` tolerance. *(blocker §5)*
- **G3 — commands fixed.** Fast + full PYREF (§6) frozen behind one local entry point (PYREF-006).
- **G4 — boundary invariants frozen.** `test_native_fallback_boundary` never xfailed; XPASS = RED; exact-count pins for the num_predictions divergences. *(already true — lock it)*
- **G5 — `.n4a`+workspace cross-engine proven** (PYREF-009). *(GAP)*
- **G6 — error-parity proven** for shapes both engines should reject. *(GAP)*
- **G7 — methods-installed lane un-skipped in CI** (PYREF-010). *(GAP)*
- **G8 — nirs4all-side `.so`/wheel freshness gate** (PYREF-011). *(GAP)*
- **G9 — Studio rides the oracle** (PYREF-008): records the engine, and the 4 backend re-implementations get a parity check or move into nirs4all. *(GAP; overlaps L12)*

Output guarantee (roadmap): *no backend/controller replacement merges without green on the relevant oracle slice; the existing tests stay the reference, never a weaker parallel suite.*

---

## 8. Proposed gates for `LOCK-DROP` (from ADR-17 §3 + roadmap DROP-001)

`LOCK-DROP` (cutover `DEFAULT_ENGINE="dag-ml"`, remove legacy) requires, in order:

- **D1 — `EXPECTED_FALLBACK == empty`.** The 11 fallback shapes (4 branch/merge + 4 multi-source + 3 preprocessing-keyword) run **native**. *(L5/A3; the #1 blocker — host-bridge serialization, not dag-ml-core.)*
- **D2 — native `.n4a` export** covers all required cases (retire the P1c legacy-refit bridge — ADR-17 §3.9).
- **D3 — 3-tier oracle green** under `DEFAULT_ENGINE="dag-ml"` (§7 satisfied).
- **D4 — no stale `.so`** (G8 freshness gate green).
- **D5 — Studio/Web on the runtime route** with engine recorded (G9 / PYREF-008).
- **D6 — migration tool available** for legacy `.n4a`/workspace (`L18`/`LOCK-MIG`).
- **D7 — maintainer gate:** backups verified + legacy users migrated/warned (ADR-17 §3 explicit gate).
- **D8 — dual-engine layer retirement plan:** per ADR-17 §3.4, `test_conformance_dual_engine.py` / `test_parity_baseline.py` / `baselines/` / `test_dagml_run_selector.py` are dead weight once legacy is gone; keep the single-engine dag-ml oracle (`cases_generators_conformance.py`, `test_dagml_operator_generation_phase7.py`). **PYREF and DROP are sequenced: PYREF green proves the cutover safe, then the dual-engine layer is retired.**

---

## 9. Blockers (record, do not resolve by editing shared contracts)

| ID | Severity | Blocks | Description | Owner |
|---|---|---|---|---|
| `BLK-PYREF-1` | **high** | `LOCK-PYREF` sign | ADR-01 tolerance ledger `nirs4all/docs/compatibility.md` MISSING; `1e-9` contract vs `1e-3` enforced vs per-case — no fixed tolerance to sign. | L17 + L20 |
| `BLK-PYREF-2` | med | `LOCK-PYREF` G5, `LOCK-DROP` D2 | `.n4a` + workspace **cross-engine read/predict** unproven (PYREF-009). | L17 + L5 |
| `BLK-PYREF-3` | med | `LOCK-PYREF` G6 | **Error/refusal parity** unproven (no same-input both-engine refusal). | L17 |
| `BLK-PYREF-4` | med | `LOCK-PYREF` G7/G8 | methods-installed lane silently **skips in CI** (`importorskip("n4m")`); no nirs4all-side `.so`/wheel freshness gate. | L17 + L9 |
| `BLK-PYREF-5` | med | `LOCK-PYREF` G9, `LOCK-DROP` D5 | Studio bypasses the oracle (no engine recorded) + 4 backend re-implementations outside nirs4all. | L17 + L12 |
| `BLK-DROP-1` | **high** | `LOCK-DROP` D1 | `EXPECTED_FALLBACK` non-empty (11 shapes fall back) — host-bridge serialization gap. The oracle already gates it; closing it is runtime work. | **L5/A3** |

---

## 10. Tests / gates executed + evidence + limitations

- **Read-only inventory** of the full parity tree, `_oracle.py`/`_registry.py`/`_conformance_helpers.py`/`test_conformance_dual_engine.py`, dag-ml contracts (`parity_oracle.v1.json`, `conformance_pack.v1.json`, `PARITY_AND_PERF_HARNESS.md`), `ADR-17_LEGACY_DROP_HANDOFF.md`, roadmap PYREF-000..011 + LOCK-DROP, and three sub-agent inventories (Studio engine surface; methods ledger + `.so` freshness; test-file map + workspace/error gaps). All findings above are file:line-anchored.
- **Did NOT execute the suite.** `pytest --collect-only` on the parity dir **fails to collect** here: `tests/conftest.py:34 import matplotlib` → `ModuleNotFoundError` (the `.venv` lacks `matplotlib`, which the integration conftest imports at load). The green numbers cited (273/0, 8220 passed, 11 xfailed) are **ADR-17's, on `core/dagml`/`dagml-adr17-complete-2026-06-30`**, not re-verified by me on `main@e41362b4`. The KNOWN_DIVERGENCES(9)+legacy_bug(2)=11 xfail count I read on `main` matches ADR-17's "11 xfailed", indicating `main` carries the same harness state. **Recommend A0/A2-impl re-run the full PYREF once `matplotlib` is in the venv** to confirm parity on `main`.
- **No implementation code or shared contracts modified.** This report is the only file written.

---

## 11. Sync board handoff (for A0 to integrate — I did not edit `PARALLEL_REFACTORING_SYNC.md`)

**Lane line (`L17`):**
```
| `L17` Oracle parite Python | review | A2 | nirs4all, dag-ml, dag-ml-data, nirs4all-methods, nirs4all-studio | PYREF-000 3-tier registry drafted (report §2); blocked on BLK-PYREF-1 (compatibility.md ledger) before LOCK-PYREF sign; G5-G9 gaps (.n4a/workspace/error/Studio/methods CI) itemised. | PRE-3, LOCK-CAP, BLK-PYREF-1 |
```
**`LOCK-PYREF`** stays `review`; add G1–G9 (§7) as sign conditions; **`BLK-PYREF-1` is the gating one.**
**`DEC-PYREF-002`**: PYREF-000 registry **DELIVERED** as draft (report §2); move toward `accepted` once the consolidated `_authority.py` module + `compatibility.md` ledger land.
**`PRE-3`** evidence refines to: *oracle exists at 95 cases / dual-engine green per ADR-17; the lock still needs the 3-tier consolidation + the missing `compatibility.md` ledger + the 5 cross-engine gaps (.n4a/workspace/error/Studio/methods-installed+.so).*
**New blockers** to register: `BLK-PYREF-1..5`, `BLK-DROP-1` (§9). `BLK-DROP-1` reassigns to **L5/A3** (EXPECTED_FALLBACK==empty is runtime work).

**Worklog (append-only):**
```
2026-06-30 | A2/L17 | review | Adopted existing parity oracle (95 cases, dual-engine harness); extracted PYREF-000 3-tier authority registry from the 5 scattered structures; mapped coverage matrix + the 7 cross-engine surfaces; found compatibility.md ledger MISSING (1e-9 contract vs 1e-3 enforced) as the LOCK-PYREF tolerance blocker; proposed fast/full PYREF commands + LOCK-PYREF(G1-9)/LOCK-DROP(D1-8) gates. | read-only; report A2_A2-pyref.md; collect blocked by missing matplotlib in .venv; green numbers are ADR-17's on core/dagml | BLK-PYREF-1 (ledger) before LOCK-PYREF; BLK-DROP-1 (EXPECTED_FALLBACK) is L5/A3.
```
