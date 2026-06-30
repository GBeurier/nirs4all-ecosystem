# SW5 — PYREF compatibility-ledger spec (resolves B-009 / B-011 / B-013 / B-015)

**Agent:** SW5 (second-wave, L17 PYREF compatibility ledger + parity gating) · **Date:** 2026-06-30
**Lane:** `L17` Oracle parité Python · **Lock:** `LOCK-PYREF` (in_progress) · **Decisions:** `DEC-PYREF-001`, `DEC-PYREF-002` (both accepted)
**Mode:** read-only audit + spec authoring. No code / test / sync-board / other-report edits. **This file is the only write.**
**Builds on (read in full):** `A2_A2-pyref.md`, `A3_A3-dagml.md`, `A5_A5-methods.md`, `CAP_spec.md`, `RT_spec.md`, `PARALLEL_REFACTORING_SYNC.md`.

**Heads verified (direct `ls`/`grep`/`sed`/`Read`, not CodeGraph):** `nirs4all e41362b4`, `dag-ml f58d7bf`. All numbers below are re-verified against working-tree source, not inherited from A2.

---

## 0. Mandate and what this spec is

A2 diagnosed the blocker ("`compatibility.md` is missing; 1e-9 contract vs 1e-3 enforced") and drafted `PYREF-000` as prose. A2 did **not** define the *file* — its structure, its machine-readable form, how the three tolerance sources reconcile into one authority, or the concrete tests/CI that turn the four open blockers green. **This document is that definition.** It is implementation-ready: an engineer on `L17` can build `compatibility.{md,json}` + `_authority.py` + the gates directly from §2–§9.

The four blockers this closes, and where:

| Blocker | One-line | Closed by |
|---|---|---|
| `B-009` | `compatibility.md` absent; 1e-9 vs 1e-3 unreconciled | §2 (ledger structure) + §3 (tolerance bands) + §4 (3-tier registry) |
| `B-011` | `.n4a`/workspace, error-parity, Studio-bypass not on the oracle | §6 (cross-engine parity tests) |
| `B-013` | suite does not collect on main; "oracle green" unproven | §7 (collection fix + CI wiring + `.so` freshness) |
| `B-015` | `test_n4m_ops` silently skips → false green | §8 (methods-installed CI gate) |

`B-010` (`EXPECTED_FALLBACK != empty`) is **owned by L5/A3**, not L17 — but the ledger is the instrument that *measures* it, so §5 specifies the ledger's fallback view and the boundary invariant (it does not attempt the runtime work).

---

## 1. Verified ground truth — the numbers the ledger must encode

These are the source-of-record facts the ledger consolidates. Every count is freshly verified.

### 1a. Case corpus (`tests/integration/parity/`, 95 `register()` calls)

| Population | Count | Source |
|---|---|---|
| Registered `PipelineCase`s | **95** | `cases_*.py` (`register()` calls) |
| Registry skips `skip_kind="fixture"` | 3 | `cases_*.py` (`branch_separation_by_metadata_auto`, `exclude_multi_any_y_and_x`, `aggregation_classification_vote`) |
| Registry skips `skip_kind="unknown_semantics"` | 5 | incl. `generator_or_count_seed`, `generator_or_weights_count_seed`, `refit_params_use_all_partitions` |
| Registry strict-xfail `skip_kind="legacy_bug"` | 2 | `branch_separation_by_tag`, `branch_separation_by_filter` (`_registry.py:37` SkipKind; `_params` `:346-347`) |
| `KNOWN_DIVERGENCES` strict-xfail | **9** | `test_conformance_dual_engine.py:78-150` |
| `EXPECTED_FALLBACK` boundary allowlist | **11** | `:310-326` (4 `branch_dup_*`, 4 `multi_source_*`, 3 `preprocessing_*`) |
| `NUM_PREDICTIONS_DIVERGENCE` parity-note (PASS) | 2 | `:189-202` (`generator_or_models_pls_ridge` 34/32, `generator_chain_model_configs` 49/47) |
| `Y_PRED_TOL_OVERRIDES` (5e-3) | 6 | `:244-251` |
| `SAME_WINNER_CASES` guard | ~22 | `:265-300` |

Strict-xfail total = **9 KNOWN_DIVERGENCES + 2 legacy_bug = 11** → matches ADR-17's reported "11 xfailed". Runnable (no `skip_reason`) = 95 − 8 skips − 2 legacy_bug = **85**; of those, 11 fall back, 74 run native. **The five authority structures are scattered across two files** (`_registry.py` `skip_kind`; the five dicts/sets in `test_conformance_dual_engine.py`). The ledger's job (§4) is to lift them into one authority that those structures become *views* of.

### 1b. Tolerance reality — three inconsistent sources (the B-009 core)

| Where | Value | Axis it actually governs | Evidence |
|---|---|---|---|
| dag-ml contract `parity_oracle.v1.json` `regression.default` | abs/rel **1e-9** | *(mislabeled — see §3)* claims to be the cross-engine number | `parity_oracle.v1.json:13-20`, owner `"nirs4all compatibility ledger"` |
| dag-ml contract `classification.default` | abs/rel **0** | class-label exact match | `:21-27` |
| helper `_DEFAULT_SCORE_TOL` | **1e-3** | legacy(sklearn) ↔ dag-ml(Rust) *pipeline score* | `_conformance_helpers.py:60` |
| helper `_DEFAULT_YPRED_TOL` | **1e-3** | per-sample y_pred cross-engine | `:65` |
| per-case `metric_tolerances` | **1e-6** | tight single-shape (e.g. `baseline_vertical_slice`) | `_registry.py:150-151`; `_oracle` |
| `Y_PRED_TOL_OVERRIDES` | **5e-3** | FirstDerivative-amplified PLS y_pred, under `assert_same_winner` | `:244-251`; measured ceiling 3.45e-3 (`:217`) |
| native export reproduce | **1e-6** | dag-ml native single-model export → final-(test) y_pred | `test_conformance_export_roundtrip.py` (A2 §4.3) |
| n4m kernel SNV | **1e-12** | n4m vs sklearn, same language | `test_n4m_ops.py:120,130` |
| n4m kernel PLS | **<1e-9** | n4m vs sklearn predictions, same language | `test_n4m_ops.py:169` |

**Measured cross-engine noise** (from the helper docstring + dual-engine comments): PLS rmse/r2 ~7e-6; per-sample PLS y_pred ~1.1e-4; y_processing-inverse ~6e-4; FirstDerivative-amplified ~3.45e-3. The crux: **1e-9 and 1e-3 are not the same axis** (§3).

### 1c. CI / collection reality (B-013 / B-015)

- **The parity suite is NOT wired into CI.** `nirs4all/.github/workflows/CI.yaml` runs only `tests/unit/` (`:101,103`) and `tests/integration/pipeline/` (`:118,126`). `tests/integration/parity/` is **never invoked in CI** → "oracle green on main" is unproven *by CI*, independent of the local venv.
- **`tests/conftest.py:34` does an unconditional top-level `import matplotlib`** (used at `:50` `matplotlib.use('Agg')`). Because this is the repo-root test conftest, a missing `matplotlib` makes the **entire** `tests/` tree (parity included) uncollectable. Locally the `.venv` lacks it → B-013's "8220/273 are from `core/dagml`, not re-run on main". In CI `matplotlib>=3.7.0` *is* present (`requirements-test.txt:22`), so the CI gap is purely "parity not invoked", the local gap is "conftest hard-imports an optional viz dep".
- **`test_n4m_ops.py:29` `pytest.importorskip("n4m")`** + `requirements-test.txt` pins `dag-ml`/`dag-ml-data` (`:64-65`) but **not** `nirs4all-methods` → the entire methods-installed parity silently skips. `[project.optional-dependencies]` (`pyproject.toml:101`) has `viz/explain/torch/...` but **no `methods` or `parity` extra**.
- **No nirs4all-side wheel/`.so` freshness gate.** `dag-ml/scripts/check_so_freshness.py` (8.4 KB) and `dag-ml/scripts/validate_contracts.py` (237 KB) exist; nirs4all has **no `scripts/validate_contracts.py`** and tracks no compiled artifact, so nirs4all CI can go green against a stale installed `dag_ml`/`n4m` wheel.

---

## 2. The compatibility ledger — structure and machine-readable source

### 2a. Three artifacts, one source of truth (resolves "or an equivalent machine-readable source")

The dag-ml contract requires a **human doc at `nirs4all/docs/compatibility.md`** (`required_before_bridge: true`). The oracle helpers + the dag-ml validator need a **machine-readable** form. To avoid drift between "what the doc says" and "what the tests enforce", there is **one typed source** and two generated faces:

```
nirs4all/tests/integration/parity/_authority.py   ← SOURCE OF TRUTH (typed Python)
        │   frozen dataclasses: ToleranceBand, AuthorityEntry, FallbackEntry, …
        │   imported DIRECTLY by _conformance_helpers.py + test_native_fallback_boundary
        │   (no file parsing at test time)
        ├── emits → nirs4all/docs/compatibility.json   ← machine face (validator-facing, pure JSON)
        └── renders → nirs4all/docs/compatibility.md    ← human face (dag-ml consumer_ledger target;
                                                          embeds the SAME json in one fenced ```json block)
```

A single snapshot test (`test_compatibility_ledger_in_sync.py`, §9) regenerates `compatibility.json` and the `.md`'s fenced block from `_authority.py` and asserts byte-equality — so the published ledger can never drift from the enforced code, and the dag-ml validator (pure stdlib, must not parse markdown) reads `compatibility.json`.

> **Why `_authority.py` is SoT, not the `.md`:** the repo already drives parity from typed import-time-validated dataclasses (`PipelineCase`, `_registry.py:128`). Runtime markdown-parsing would be fragile and violates "no abstractions for one-time ops". The `.md`/`.json` are *dumps*, not hand-maintained parallel truth.

**Alternative if the team prefers doc-first:** make `compatibility.md`'s fenced JSON the SoT and have `_authority.py` load `compatibility.json` (the emitted sibling) at import. Same three files, inverted generation direction. SW5 recommends the Python-SoT direction above; flag for L17/maintainer.

### 2b. `compatibility.md` document structure (the human ledger)

Sphinx-indexed under `nirs4all/docs/source/` (add to a `developer/` or `migration/` toctree — both exist). Sections, in order:

1. **Front matter / status** — `schema_version`, `owner: nirs4all compatibility ledger`, `consumer_of: dag-ml/docs/contracts/parity_oracle.v1.json`, last-reconciled commit, link back to `LOCK-PYREF`.
2. **§A Tolerance bands** (§3 of this spec) — the band table; the explicit 1e-9↔1e-3 reconciliation note.
3. **§B 3-tier authority registry** (§4) — Tier-1/2/3 tables, each row carrying `case, tier, mechanism, disposition, tolerance_band, measured_delta, evidence`.
4. **§C Orthogonal axes** (§4c) — `EXPECTED_FALLBACK` (11), fixture skips (3), `NUM_PREDICTIONS_DIVERGENCE` (2), `Y_PRED_TOL_OVERRIDES` (6), `SAME_WINNER_CASES` — explicitly *not* authority tiers.
5. **§D Cross-engine surface ledger** (§6) — `.n4a`/workspace/error/Studio rows with EXISTS/GAP + owning test.
6. **§E Coverage meter** (§5) — native / fallback / xfail / skip counts + the `EXPECTED_FALLBACK` shrink target (the LOCK-DROP instrument).
7. **The single fenced `​```json` block** = `compatibility.json` verbatim (the machine face).

### 2c. `compatibility.json` schema (the machine face)

```json
{
  "schema_version": 1,
  "owner": "nirs4all compatibility ledger",
  "consumer_of": "dag-ml.nirs4all.parity_oracle.v1",
  "tolerance_bands": [
    { "band_id": "cross_impl_score", "numeric_path": "cross_impl_pipeline",
      "metric_class": "score", "abs_tol": 1e-3, "rel_tol": 0.0,
      "measured_ceiling": 7e-6, "justification": "sklearn(legacy) vs Rust(dag-ml) PLS solve",
      "enforced_at": "_conformance_helpers.py:60" }
  ],
  "authority": [
    { "case": "rep_to_sources_basic", "tier": 2, "disposition": "xfail_strict",
      "mechanism": "legacy double-counts overlapping rep OOF folds; dag-ml aggregates once",
      "authoritative_engine": "dag-ml", "tolerance_band": "n/a_semantic",
      "measured_delta": "cv 6.6735 vs 6.1906", "evidence": "test_conformance_dual_engine.py:127" }
  ],
  "expected_fallback": [
    { "case": "branch_dup_merge_all", "shape": "branch+merge", "owner_lane": "L5",
      "reason": "host bridge does not serialize branch/merge step keywords yet",
      "evidence": "test_conformance_dual_engine.py:313" }
  ],
  "num_predictions_divergence": [
    { "case": "generator_or_models_pls_ridge", "legacy": 34, "dagml": 32,
      "reason": "operator-SELECT refits winner only", "disposition": "pass_parity_note" }
  ],
  "ypred_tol_overrides": [
    { "case": "generator_or_with_pick", "abs_tol": 5e-3, "band": "cross_impl_ypred_firstderiv",
      "guard": "assert_same_winner" }
  ],
  "same_winner_cases": ["generator_or_pick_mutex", "..."],
  "coverage_meter": { "total": 95, "runnable": 85, "native": 74, "fallback": 11,
                      "xfail_strict": 11, "skip": 8, "expected_fallback_target": 0 }
}
```

Field contracts: `tolerance_band` on an authority/override row must reference a `band_id` in `tolerance_bands` (or the sentinel `n/a_semantic`/`n/a_rng`); `expected_fallback[].owner_lane` is always `L5` (it is runtime work); `coverage_meter.expected_fallback_target` is `0` (the LOCK-DROP gate). The snapshot test asserts every referenced `band_id`/case name actually exists in the live test structures — so a renamed case or deleted band fails CI, not silently.

---

## 3. Tolerance bands — reconciling 1e-9 (contract) vs 1e-3 (enforced)  [B-009 core]

**The reconciliation is: they measure different axes and both are correct on their own axis.** A single global tolerance number is the bug; the ledger replaces it with **bands keyed by `(numeric_path, metric_class)`**.

- The dag-ml contract's `regression.default = 1e-9` is achievable **only on a same-implementation numeric path** — i.e. n4m-vs-sklearn kernel replacement (`test_n4m_ops` PLS `<1e-9`, SNV `1e-12`) or native-export-reproduces-itself (`1e-6`). It is **false** for the cross-implementation pipeline path the PYREF dual-engine oracle actually exercises (Rust-PLS vs sklearn-PLS), where measured noise is ~1e-4 and the enforced band is `1e-3`.
- Therefore `1e-9` is *not* "the tolerance" — it is the `kernel_pls` band mislabeled as the default. The ledger names every band and binds every parity assertion to one.

### 3a. The band table

| `band_id` | numeric_path | metric_class | abs_tol | measured_ceiling | enforced_at |
|---|---|---|---|---|---|
| `kernel_snv` | same_impl_kernel | y_transform | **1e-12** | exact | `test_n4m_ops.py:120,130` |
| `kernel_pls` | same_impl_kernel | prediction | **1e-9** | ~1e-10 | `test_n4m_ops.py:169` |
| `native_export_reproduce` | dag-ml native ↔ itself | prediction | **1e-6** | — | `test_conformance_export_roundtrip.py` |
| `per_case_tight` | cross_impl_pipeline | score | **1e-6** | — | case `metric_tolerances` (`baseline_vertical_slice`) |
| `cross_impl_score` | cross_impl_pipeline | score (rmse/r2/acc) | **1e-3** | ~7e-6 | `_conformance_helpers.py:60` |
| `cross_impl_ypred` | cross_impl_pipeline | prediction (per-sample) | **1e-3** | ~6e-4 | `_conformance_helpers.py:65` |
| `cross_impl_ypred_firstderiv` | cross_impl_pipeline | prediction (per-sample) | **5e-3** (guarded) | ~3.45e-3 | `Y_PRED_TOL_OVERRIDES:244`, under `assert_same_winner` |
| `classification_label` | any | class_label | **0 / exact** | exact | `parity_oracle.v1.json:21-27` |
| `n/a_semantic` | — | — | — | — | Tier-2/3 permanent divergence; never compared by tolerance |
| `n/a_rng` | — | — | — | — | Tier-3 RNG nondeterministic; **never** masked by tolerance (`DEC-PYREF-002`) |

**Invariant (lift from `DEC-PYREF-002`, sync board line 93):** an RNG-nondeterministic case is band `n/a_rng` and is **xfail/skip**, never relaxed into a wider tolerance band. Tolerance bands cover *float-noise* divergence only, never *stochastic-path* divergence.

### 3b. The contract amendment (lockstep with dag-ml — `LOCK-LOCKSTEP`/L20)

The dag-ml `parity_oracle.v1.json.tolerance_profiles` must stop asserting `1e-9` as the cross-engine default. Two options; SW5 recommends **(B)**:

- **(A)** keep one `regression.default` but change its value to `1e-3` and move `1e-9` into a new `regression.kernel` profile.
- **(B, recommended)** add explicit profiles so no number is mislabeled: `regression.cross_impl` (abs `1e-3`), `regression.kernel` (abs `1e-9`), `regression.native_export` (abs `1e-6`), keep `classification.default` (`0`). Each `parity_oracle.v1.json` *case* then references the profile that matches its numeric path.

Because the contract's `tolerance_profiles[].owner` is literally `"nirs4all compatibility ledger"`, **the ledger is the source of truth and the dag-ml JSON is the consumer** — the amendment is a paired dag-ml↔nirs4all change validated by `validate_contracts.py` (it must check `parity_oracle.v1.json` profiles ⊆ `compatibility.json.tolerance_bands`). This is the seam where `LOCK-PYREF` meets `LOCK-LOCKSTEP` (A2 §1, CAP `CON-001`).

---

## 4. The 3-tier authority registry (`PYREF-000` consolidated)  [B-009]

`_authority.py` lifts the five scattered structures into one table. Each tier is a *claim about which engine is correct*, distinct from coverage/skip/fallback (§4c).

### 4a. Tier definitions

- **Tier 1 — Python (legacy) authoritative.** Default. The ~74 native-runnable cases that must equal legacy within the matching `cross_impl_*` / `per_case_tight` band. No marker; PASS = green.
- **Tier 2 — dag-ml authoritative.** Legacy is wrong or was changed; dag-ml is the correct value. Disposition is `xfail_strict` vs the legacy gold (so it XPASS-flips RED if engines ever reconverge) **or** `pass_parity_note` (correctness asserted, only the legacy-bug dimension exempted).
- **Tier 3 — non-executable / RNG / unknown-semantics.** Comparison is invalid. Disposition `xfail_strict` (legacy_bug, no oracle) or `skip` (fixture / unknown_semantics / unseeded RNG). Band `n/a_semantic` or `n/a_rng`.

### 4b. Consolidated content (the ledger rows)

**Tier 2 (dag-ml authoritative):**

| case | mechanism | disposition | evidence |
|---|---|---|---|
| `rep_to_sources_basic` | legacy double-counts overlapping rep OOF folds (cv 6.6735); dag-ml aggregates once (6.1906) | `xfail_strict` | `:127` |
| `rep_to_pp_basic` | same (6.1427 vs 6.1906) | `xfail_strict` | `:129` |
| `generator_or_models_pls_ridge` | operator-SELECT refits winner only (32 vs legacy 34) | `pass_parity_note` (num_pred pinned) | `:190` |
| `generator_chain_model_configs` | same, `_chain_` of distinct models (47 vs 49) | `pass_parity_note` | `:196` |
| *(contract-wide)* `best_*` re-anchored on SELECTED model | 0.9.x bugfix | `assert_runresult_contract` | `_conformance_helpers.py:286-293` |

**Tier 3 (non-executable / RNG):**

| case | sub-class | disposition | band | evidence |
|---|---|---|---|---|
| `branch_separation_by_tag` | legacy_bug (no oracle) | `xfail_strict` | `n/a_semantic` | `cases_branches_merges.py` skip_kind |
| `branch_separation_by_filter` | legacy_bug | `xfail_strict` | `n/a_semantic` | skip_kind |
| `sample_augmentation_gaussian` / `_chained` / `_after_savgol` | RNG/order | `xfail_strict` | `n/a_rng` | `:82-84` |
| `feature_augmentation_replace_three_views` | RNG (view build order) | `xfail_strict` | `n/a_rng` | `:87` |
| `concat_transform_pca_svd_plsr` | RNG (view order/decomp) | `xfail_strict` | `n/a_rng` | `:88` |
| `generator_finetune_params_optuna` | RNG (Optuna trial seq) | `xfail_strict` | `n/a_rng` | `:102` |
| `generator_sample_log_uniform_alpha` | RNG (unseeded `_sample_`) | `xfail_strict` | `n/a_rng` | `:115` |
| `generator_or_count_seed` / `_weights_count_seed` | unknown_semantics (`_seed_` not threaded) | `skip` | `n/a_rng` | `cases_generators_conformance.py` |
| `refit_params_use_all_partitions` | unknown_semantics | `skip` | `n/a_semantic` | `cases_refit_predict.py` |

**Tier 1** is the implicit remainder (every runnable case not listed above and not in `EXPECTED_FALLBACK`), bound to `cross_impl_score` + `cross_impl_ypred` (or the case's `per_case_tight`).

**XPASS discipline (lock invariant):** every Tier-2/Tier-3 `xfail_strict` flips the suite RED the moment engines converge — a fixed divergence can never silently leave coverage. The ledger records this as a hard rule, not prose.

### 4c. Orthogonal axes (recorded in §C, **not** authority tiers)

- `EXPECTED_FALLBACK` (11) — native-coverage boundary, **owner L5** (§5).
- Fixture skips (3) — can't run; make no authority claim.
- `Y_PRED_TOL_OVERRIDES` (6) — same-winner float-noise relaxation, band `cross_impl_ypred_firstderiv`, guarded by `assert_same_winner`.
- `SAME_WINNER_CASES` (~22) — selection-agreement guard.
- `NUM_PREDICTIONS_DIVERGENCE` (2) — already in Tier 2 as `pass_parity_note`; the count is *pinned* (`assert_num_predictions_divergence`), never merely exempted.

---

## 5. Expected-fallback closure — the ledger view (B-010 instrument; L5 owns the work)

The ledger does **not** close `EXPECTED_FALLBACK`; it makes shrinking it *visible and gated*.

- **Coverage meter** (`compatibility.json.coverage_meter`) records `native / fallback / xfail_strict / skip` and `expected_fallback_target: 0`. Emitted by a meter runner (A3 `DML-003`) so each PR shows the fallback count moving.
- **Boundary invariant** stays in `test_native_fallback_boundary` (`:372`, never xfailed): a fallback off the allowlist = native-coverage REGRESSION → FAIL; a native case on the allowlist = STALE entry → FAIL. The ledger's `expected_fallback[]` **is** the allowlist's documented twin; the snapshot test asserts `compatibility.json.expected_fallback[].case` == the live `EXPECTED_FALLBACK` frozenset, so the doc can't drift from the gate.
- The 11 cases each carry `owner_lane: L5` + a reason. When L5/A3 lands native coverage for one (host-bridge serialization of branch/merge, multi-source, preprocessing-keyword — A3 §"Blockers"), the entry leaves *both* the frozenset and the ledger, and the meter decrements. **`coverage_meter.fallback == 0` is the `LOCK-DROP` D1 gate** (A2 §8 D1), not a `LOCK-PYREF` gate.

---

## 6. Cross-engine parity tests — the missing surfaces  [B-011]

A2 §4 itemized five GAP surfaces. This section specs the concrete tests; each becomes a `§D` ledger row (`surface, status, owning_test, tolerance_band`).

### 6a. `.n4a` cross-engine round-trip — `PYREF-009a` (GAP)
- **New test** `test_conformance_n4a_cross_engine.py` (marker `parity, slow`).
- **Asserts:** a `.n4a` bundle **written by legacy** loads and predicts through the **dag-ml/runtime** path (and the reverse) with final-(test) y_pred within band `cross_impl_ypred` (1e-3); native single-model export already proves `native_export_reproduce` (1e-6) self-consistency (`test_conformance_export_roundtrip.py`) — this adds the *cross*-engine leg that is unproven today.
- **Scope note:** export today delegates `.n4a` to a legacy refit bridge (A3 §8 step "Export"); until `DML-008` native export lands, this test pins the *bridge* round-trip, and tightens to `native_export_reproduce` when native `.n4a` arrives (the band reference makes the tightening a one-line ledger change).

### 6b. Workspace cross-engine — `PYREF-009b` (GAP)
- The engines write **non-overlapping on-disk formats** (legacy: `store.sqlite` + `arrays/*.parquet` + `runs/manifest.yaml`; dag-ml: additive off-by-default native-results dir, which the legacy engine ignores — `test_dagml_native_results.py:210-219`). So the real question is **not** byte-identity.
- **New test** asserts: a **legacy-written workspace** is *inspectable/predictable* via the runtime V1 read path (`RunResult`/`predict` over the legacy workspace), and a dag-ml run's native-results triple (`manifest.json + score_set.json + predictions.parquet`) reads back through `read_native_results` (`native_results.py:363`) to the **same** `RtResult` projection (RT `ScoreSet` anchor, `RT_spec.md` RT-002). Band: `cross_impl_score` on the projected metrics.

### 6c. Error / refusal parity — `PYREF-err` (GAP)
- Today every `pytest.raises` in the parity dir is **single-engine dag-ml-only** (A2 §4.4). No test feeds the **same** invalid pipeline to **both** engines and asserts the same refusal.
- **New test** `test_conformance_error_parity.py`: for a small set of shapes both engines should reject (leakage path; malformed step; unknown operator), assert legacy and dag-ml both raise, and that the dag-ml refusal maps to a **stable `RtError.cause`** (`RT_spec.md` RT-003: `DagMlUnsupported → unsupported_shape`, `DagMlUnavailable → unavailable_backend`). The cause vocabulary is owned by `CAP-004` (`CAP_spec.md` §5) — the test references it, does not invent it. Leakage refusal cross-engine equality also closes `parity_oracle.v1.json` case `repetition_group_leakage_refusal` on the *cross-engine* axis (A2 §4.4).

### 6d. Studio rides the oracle — `PYREF-008` (GAP; overlaps L12)
- `NativeResultsAdapter` already reads the native triple correctly (`nirs4all-studio/api/native_results_adapter.py`) — **no adapter gap**. The gap is that Studio **never passes `engine=` and never records which engine ran** (A2 §4.5: `runs.py:1431`, `training.py:466`, `automl.py:903`, `predict.py:81/89`), so there is no evidence Studio workflows are dag-ml-native.
- **Spec:** (1) Studio records the resolved engine on the run row; (2) a Studio-level smoke runs one pipeline through both engines and asserts the unified `RtResult` (`RT_spec.md`) matches within `cross_impl_score`; (3) the **four backend re-implementations** that bypass nirs4all entirely (`api/transfer.py:412-466` hand-chained SNV/MSC/SG; `api/predict.py:114-122` sklearn metrics; `:283-295` pandas CSV/Excel; `api/analysis.py` permutation/MI/F importances) are flagged in the ledger `§D` as **un-oracled** and get a parity check **or** move into nirs4all (`BACKEND_RULES.md`; this is L12 work — the ledger only records the debt).

### 6e. Ledger `§D` row shape

```
{ surface: ".n4a_cross_engine" | "workspace_cross_engine" | "error_parity" | "studio_engine_recorded" | "studio_backend_reimpl",
  status: "EXISTS" | "PARTIAL" | "GAP",
  owning_test: "<path::test>",
  tolerance_band: "<band_id>" | "n/a",
  owner_lane: "L17" | "L17+L5" | "L17+L12" }
```

---

## 7. Collection + CI + freshness  [B-013]

Three independent fixes; all required before "oracle green on main" is a true statement.

### 7a. Make collection robust to a missing optional viz dep
- `tests/conftest.py:34` hard-imports `matplotlib` at module load. **Fix:** guard it — move the import into a `try/except ImportError` that sets a sentinel, and call `matplotlib.use('Agg')` in `pytest_configure` only when present. The parity subtree exercises **no** charts, so it must collect with the minimal `[parity]` extra (numpy + dag-ml + sklearn), not the full viz stack. This is the minimal change; it does not remove matplotlib from the viz/explain test paths.

### 7b. Wire PYREF into nirs4all CI (it is absent today)
Add a CI job (or extend the integration job) that actually runs the parity tree. Two tiers (A2 §6, concretized):

```bash
# FAST PYREF — every commit, < 1 min, no engine run (pure structure):
pytest tests/integration/parity/test_parity_compiles.py \
       tests/integration/parity/test_generators_conformance_extra.py \
       tests/integration/parity/test_compatibility_ledger_in_sync.py -q

# FULL PYREF — PR + nightly (dual-engine, slow):
pytest tests/integration/parity/ -m parity -q
#   invariant: XPASS on any strict-xfail = RED; test_native_fallback_boundary must stay green.
```
The job installs `nirs4all[parity]` (new extra, §8) so `matplotlib` is **not** required for the fast tier and the dual run uses the pinned `dag-ml`/`dag-ml-data`.

### 7c. nirs4all-side wheel/`.so` freshness — `PYREF-011`
nirs4all reaches the native engine through the **installed** `dag_ml`/`n4m` wheels and tracks no compiled artifact, so CI can go green against a stale build. **Fix:** a nirs4all-side gate that asserts the installed wheel versions satisfy the pins **and** (when a sibling `../dag-ml` checkout is present) invokes `python ../dag-ml/scripts/check_so_freshness.py`. This is the consumer-side analogue of dag-ml's own guard (which only protects dag-ml's committed `.so`). Record the installed `dag_ml.__version__` / `n4m.abi_version()` in the run manifest so a stale-wheel green is auditable.

---

## 8. methods-installed CI gate  [B-015]

`test_n4m_ops.py:29` `importorskip("n4m")` + no `nirs4all-methods` dependency = a declared-portable capability that **silently skips**. Per A5's recommendation (V1 = sklearn-host + mandatory methods-installed gate; direct n4m controller deferred to V1.1 behind `ARB-003`):

1. **Add a `methods` extra** to `pyproject.toml:101`: `methods = ["nirs4all-methods>=<pin>"]`. Add a `parity` extra (`parity = ["dag-ml>=0.2.1", "dag-ml-data>=0.2.1"]` + the minimal run deps) so the fast PYREF tier needs neither viz nor methods.
2. **Dedicated CI job `methods-parity`** (separate from the default matrix so the common build stays light):
   ```bash
   pip install -e .[methods]
   python -c "import n4m; import nirs4all.operators.methods as m; assert m.METHODS_AVAILABLE"   # preflight; fail (not skip) if absent
   pytest tests/unit/operators/methods/test_n4m_ops.py -q -p no:cacheprovider --no-header
   #   asserts: SNV atol 1e-12 (band kernel_snv), PLS max|Δ| < 1e-9 (band kernel_pls),
   #            and one legacy + one dag-ml engine run over MethodsSNV→MethodsPLS (test_n4m_ops.py:216).
   ```
   The job **forbids skip**: a missing `n4m` after `pip install -e .[methods]` is a job failure, not a silent green (run with a guard that converts the `importorskip` outcome into an error in this lane — e.g. `PYTEST_METHODS_REQUIRED=1` honored by the test, or assert non-zero collected count).
3. **Ledger rows:** `test_n4m_ops` SNV → band `kernel_snv`, PLS → band `kernel_pls`. These are the *only* rows that legitimately carry the `1e-9`-class tolerance, which is exactly why §3 separates them from the `cross_impl_*` bands.

> Cross-repo: `nirs4all-methods` already has its own sklearn-oracle gates (`cross-binding-parity.yml` Gate 2, A5 §"methods/sklearn parity evidence"). This gate proves the *nirs4all-consumed* n4m path, not the methods kernels themselves — keep the two distinct in the ledger (`numeric_path: same_impl_kernel` vs methods-repo's own C++ ctest).

---

## 9. Commands + gates before `LOCK-PYREF` can land

### 9a. The one-entry command surface (`PYREF-006`)
Freeze the tiers behind one local entry (`make parity` / `nirs4all parity`):

```bash
# tier 0 — ledger sync (structure only, instant)
pytest tests/integration/parity/test_compatibility_ledger_in_sync.py -q

# tier 1 — fast PYREF (every commit)
pytest tests/integration/parity/test_parity_compiles.py \
       tests/integration/parity/test_generators_conformance_extra.py -q

# tier 2 — full PYREF (PR + nightly; needs dag-ml/dag-ml-data)
pytest tests/integration/parity/ -m parity -q          # XPASS=RED; boundary green

# tier 3 — methods-installed (separate job; forbids skip)
pip install -e .[methods] && pytest tests/unit/operators/methods/test_n4m_ops.py -q

# tier 4 — cross-repo freshness + contract lockstep
python ../dag-ml/scripts/check_so_freshness.py
DAG_ML_DATA_REPO=../dag-ml-data python ../dag-ml/scripts/validate_contracts.py   # must check parity_oracle profiles ⊆ compatibility.json bands
```

### 9b. `LOCK-PYREF` sign-off checklist (G1–G9, mapped to blockers + done-criteria)

| Gate | Done-criterion | Blocker | Owner |
|---|---|---|---|
| **G1** PYREF-000 consolidated | `_authority.py` exists; the 5 scattered structures are views over it; `test_compatibility_ledger_in_sync` green | B-009 | L17 |
| **G2** tolerance ledger authored | `compatibility.{md,json}` exist; §3 bands published; `parity_oracle.v1.json` amended (3b) + lockstep-validated | B-009 | L17 + L20 |
| **G3** commands frozen | §9a behind one entry point (`PYREF-006`) | B-013 | L17 |
| **G4** boundary invariants frozen | `test_native_fallback_boundary` never xfailed; XPASS=RED; num_pred counts pinned | — (already true; lock it) | L17 |
| **G5** `.n4a` + workspace cross-engine | §6a + §6b tests green | B-011 | L17 + L5 |
| **G6** error-parity | §6c test green | B-011 | L17 |
| **G7** methods-installed un-skipped | §8 job green, skip forbidden | B-015 | L17 + L9 |
| **G8** nirs4all-side freshness gate | §7c gate wired | B-013 | L17 + L9 |
| **G9** Studio rides the oracle | §6d (1)+(2) done; (3) backend reimpls flagged/triaged | B-011 | L17 + L12 |

**G2 + the collection fix (§7a) + CI wiring (§7b) are the minimum to retire B-009/B-013.** G5–G9 retire B-011/B-015. `LOCK-PYREF` may move `review → landed` when G1–G9 are green **on main** (not on `core/dagml`). `LOCK-DROP` remains downstream: it additionally needs `coverage_meter.fallback == 0` (B-010/L5) — sequenced *after* a green PYREF (A2 §8 D8: PYREF green proves the cutover safe, then the dual-engine layer is retired).

---

## 10. Blocker-resolution map + sync-board handoff (for A0 to integrate — I did not edit the board)

| Blocker | Resolved by this spec | Deliverable an engineer builds | Remaining external dep |
|---|---|---|---|
| `B-009` | §2 (3-artifact ledger, SoT = `_authority.py`), §3 (bands + contract amendment), §4 (3-tier) | `_authority.py`, `compatibility.{md,json}`, `test_compatibility_ledger_in_sync.py`, `parity_oracle.v1.json` amend | L20 lockstep PR for the dag-ml contract amend |
| `B-011` | §6 (4 cross-engine tests + ledger §D) | `test_conformance_n4a_cross_engine.py`, workspace test, `test_conformance_error_parity.py`, Studio engine-record + dual smoke | L5 (native export/`.n4a`), L12 (Studio backend reimpls) |
| `B-013` | §7 (conftest guard, CI wiring, freshness) | conftest matplotlib guard; CI parity job; nirs4all freshness gate; `[parity]` extra | none (matplotlib already a CI dep; just invoke parity) |
| `B-015` | §8 (`methods` extra + dedicated no-skip job) | `pyproject` `methods` extra; `methods-parity` CI job | `nirs4all-methods` wheel availability; `ARB-003` for direct n4m (V1.1) |

**Suggested `L17` lane line (A0 to paste):**
```
| `L17` Oracle parite Python | review | SW5 | nirs4all, dag-ml, nirs4all-studio, nirs4all-methods | Compatibility-ledger spec authored (SW5_PYREF_COMPATIBILITY_LEDGER_spec.md): 3-artifact ledger (_authority.py SoT → compatibility.{md,json}), tolerance BANDS reconcile 1e-9(kernel)/1e-3(cross-impl), 3-tier registry, §6 cross-engine tests, §7 CI+freshness, §8 methods gate, G1-G9 sign-off. | read-only; spec only; suite still not collected on main (B-013) | B-009/B-011/B-013/B-015 now have build-ready specs; LOCK-PYREF signs when G1-G9 green on main |
```

**Suggested worklog (append-only):**
```
2026-06-30 | SW5/L17 | review | Authored PYREF compatibility-ledger spec resolving B-009/011/013/015: defined compatibility.{md,json}+_authority.py (typed SoT, 3 faces, snapshot-synced), 9 tolerance BANDS reconciling the 1e-9 contract (same-impl kernel: n4m SNV 1e-12/PLS 1e-9) vs 1e-3 enforced (cross-impl pipeline) + dag-ml parity_oracle amend (lockstep), the consolidated 3-tier registry (9 KNOWN_DIVERGENCES + 2 legacy_bug xfail, Tier-2 dag-ml-authoritative, Tier-3 RNG never tolerance-masked), expected-fallback ledger view (11; L5-owned; meter target 0 = LOCK-DROP), 4 cross-engine tests (.n4a/workspace/error/Studio), CI fixes (conftest matplotlib guard + parity NOT in CI today + nirs4all-side .so freshness), methods-installed no-skip gate (new [methods]/[parity] extras), and the G1-G9 sign-off checklist. | read-only verify: nirs4all e41362b4 / dag-ml f58d7bf; 95 cases, parity absent from CI.yaml, conftest.py:34 hard matplotlib import, importorskip("n4m"), parity_oracle.v1.json:5-27. No code/board edits. | B-009/011/013/015 build-ready; LOCK-PYREF final sign needs G1-G9 GREEN ON MAIN (B-013 still open); B-010 (EXPECTED_FALLBACK==0) stays L5.
```

### Evidence (heads, read-only; only this file written)
`nirs4all/tests/integration/parity/{_oracle,_registry,_conformance_helpers,test_conformance_dual_engine,conftest}.py`; `nirs4all/tests/conftest.py:34,50`; `nirs4all/tests/unit/operators/methods/test_n4m_ops.py:29,120,130,169,216`; `nirs4all/.github/workflows/CI.yaml:86-128`; `nirs4all/requirements-test.txt:22,64-65`; `nirs4all/pyproject.toml:101,217-226`; `nirs4all/docs/` (Sphinx tree; `compatibility.md` absent); `dag-ml/docs/contracts/parity_oracle.v1.json:5-27`; `dag-ml/scripts/{check_so_freshness,validate_contracts}.py`. Prior reports `A2_A2-pyref.md`, `A3_A3-dagml.md`, `A5_A5-methods.md`, `CAP_spec.md`, `RT_spec.md`.
