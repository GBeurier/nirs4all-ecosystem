# Critical Review — nirs4all Ecosystem Refactoring Roadmap & Design

**Date:** 2026-06-30
**Reviewers synthesized:** 4 Opus "lens" reviews (core/runtime/contracts; parity/oracle; UI/Studio/Web; ecosystem-roles/lanes) + 2 independent Codex reviews (incorrect-assumptions-vs-code; test-gate/parity-vs-suite), **confronted, not concatenated**.
**Documents under review:** `AGENTS.md`; `SYNTHESE_MULTIMODALE_NIRS4ALL.md`; `nirs4all-ecosystem/docs/MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md`; `nirs4all-ecosystem/docs/PARALLEL_REFACTORING_ROADMAP.md`; `nirs4all-studio/docs/STUDIO_PRISTINE_HANDOFF.md`; and `PARALLEL_REFACTORING_SYNC.md`.
**Code ground truth (heads, this review):** `nirs4all`/`nirs4all-core` `e41362b4`; `dag-ml` `f58d7bf` on `feat/native-scoring` (NOT merged to dag-ml main); `dag-ml-data` `b041019`; `nirs4all-methods` `7602eb08`; `nirs4all-io` `da24fb5`; `nirs4all-studio` `2ccbf68`; `nirs4all-web` `745eef8`.

---

## 0. Executive summary & verdict

**Is the roadmap implementable as written? No — not without correction first.** The architecture it describes (core vs runtime; capability-first; controllers as the binding surface; the Python-pipeline parity oracle; the lane DAG) is **directionally sound and worth executing**. But the roadmap was authored 2026-06-30 as if the program were greenfield, while the code at `e41362b4` already contains the dag-ml runtime backend (selectable, ~7,847-LOC Python bridge at `nirs4all/pipeline/dagml/`), the full L17 parity oracle (`nirs4all/tests/integration/parity/`, dual-engine harness, 273/0 + 8220/0), the dag-ml-data provider (landed `04ecf3a`), the entire fine-grained cluster (built, ~3,977 LOC, versioned protocol), and the legacy workspace migrator (`nirs4all/pipeline/storage/migration.py`, 27.3K). `PARALLEL_REFACTORING_SYNC.md:4` says **"Statut global: not started"** and marks `PRE-1` blocked. That single state-desync is the spine of almost every defect below: it makes the program re-plan landed work as future work, re-spec contracts that already exist as frozen versioned schemas, and — most dangerously — re-derive a parity oracle whose own definition is *self-contradictory* against the real engine.

**The single biggest risk:** an L17/L5 agent, told that the Python lib is "the oracle" and that V1 must produce "the same splits, predictions, scores, artifacts" with no pre-loaded accepted-incompatibility registry, will (a) burn cycles chasing **provably-impossible** bit-parity on unseeded-RNG shapes, (b) try to make dag-ml reproduce **known-wrong** legacy values (`rep_to_*` double-counting), (c) flag **already-shipped, CHANGELOG-noted** contract changes (`best_X` re-anchoring, winner-only `num_predictions`) as regressions, and (d) rebuild a 500 KB+ tagged harness as a weaker parallel suite — the exact failure the roadmap itself warns against at `ROADMAP.md:582`.

**One-paragraph verdict.** The roadmap is a good *target architecture document* wrapped around a *false present tense*. Fix it by (1) re-baselining `SYNC.md`/`PRE-*` from `e41362b4` with evidence so lanes harden-and-extend instead of rebuild; (2) replacing "same results" with a ledgered 3-tier oracle that imports the 11 strict-xfails + 2 shipped contract changes as an accepted-incompatibility registry; (3) disambiguating "controller" into the three distinct objects it currently conflates and mandating the missing `OperatorController → ControllerManifest` adapter; (4) demoting the "n4m on the dag-ml execution path" claim to roadmap status (it is unimplemented); (5) adding the two lanes the program's definition-of-done actually needs — the **legacy-DROP / `DEFAULT_ENGINE="dag-ml"` cutover** gate and the **dag-ml ↔ dag-ml-data lockstep byte-identity** CI obligation. With those corrections the lane DAG is executable; without them the program will spawn agents to re-plan and re-implement code that is already on main.

---

## 1. Convergent themes

These were found independently by **all or nearly all** reviews; they are the load-bearing flaws. Stated once, strongly.

**T1 — The roadmap re-plans already-built work as greenfield, and the sync board says "not started" when the backend migration is DONE on main.** (Lens 1 P1, Lens 2 §"most important finding", Lens 4 C1/C2/TL;DR, Codex-1 Crit-1, Codex-2 Findings 1-4.) `SYNC.md:4` = "Statut global: not started"; `:36` = `PRE-1` blocked / "Attendre la fin du chantier backend". Reality at `e41362b4`: `nirs4all/api/run.py` dispatches to `run_via_dagml` when `engine="dag-ml"`/`N4A_ENGINE=dag-ml` (default still legacy; `pipeline/engine.py:27-31` `DEFAULT_ENGINE="legacy"`, `Engine = Literal["legacy","dag-ml","dual"]`); the dag-ml Python bridge is 7,847 LOC; `ADR-17_LEGACY_DROP_HANDOFF.md` documents the migration as "fully implemented, integrated, and selectable." Every lane (`L5`, `L6`, `L16`, `L17`, parts of `L7`) that is written as "build X" where X exists is a defect, because it spawns agents to re-plan landed code.

**T2 — "Controller" is one word for three incompatible objects, with no adapter, and the anti-drift mandate is already violated inside the Python repo.** (Lens 1 C1 — BLOCKER; Lens 3 C2/G3/R3; Codex-1 Crit-2/Med-7; Lens 4 D2.) The design (`DESIGN_SCHEMAS.md:840-959`, `DQ-014`) treats *controller* as one first-class object. The code has three: (a) the dag-ml **`ControllerManifest`** declarative JSON (`dag-ml/crates/dag-ml-core/src/controller.rs:115-138`, schema-pinned, C-ABI'd); (b) the nirs4all **`OperatorController`** stateful Python ABC (`nirs4all/nirs4all/controllers/controller.py:14-82`, 31 registered subclasses, none of the manifest fields); (c) the **dag-ml-engine operator router** (`nirs4all/nirs4all/pipeline/dagml/operator_routing.py`, a 4-entry model table + sklearn-FQN import, consulting *neither* registry). No adapter maps (b)→(a). Worse, the design's own anti-drift argument ("Studio/Web/CLI/R/MATLAB/Python diverge without a shared controller", `DESIGN_SCHEMAS.md:67-72`) is already broken *inside one repo*. And in the UIs the "controllers-as-binding" surface has **zero foothold**: Studio drives its editor from the introspected node-registry over REST, never from ControllerManifests (Lens 3 C2).

**T3 — nirs4all-methods / n4m is NOT on the dag-ml execution path; the "kernel source of truth" *execution* promise is unimplemented.** (Lens 1 C2 — BLOCKER; Codex-1 Med-6; confirmed by this review's grep.) `DESIGN_SCHEMAS.md:1608-1609` (§7.2) lists "preprocessing via n4m" and "PLS/AOM via n4m" as *owned by methods, portable, exposed through core*, and §6.3 shows `DML → MTH fit/transform/predict`. Verified empty: `grep -rn n4m dag-ml/crates` (source) = none; `grep -rn n4m nirs4all/nirs4all/pipeline/dagml` = none. The only n4m reach in nirs4all is `operators/methods/n4m_ops.py`, an sklearn-shaped *legacy-engine operator*. methods is the **only** kernel home, and the coordinator does not call it. There is no kernel-ownership *conflict* (core/dag-ml have zero kernels) — there is an unbuilt integration described in present tense.

**T4 — The shipped dag-ml engine is a Python bridge that promotes only proven-equivalent shapes to native and DEMOTES everything else to the legacy orchestrator — the inverse of the North Star.** (Lens 1 C3/C8; Lens 4 C1 correction + T2; Codex-2 Finding 4.) The North Star says "variant generation + SELECT, filtering … must migrate DOWN into dag-ml." But `nirs4all/pipeline/dagml/detect.py` (1,004 LOC) is a gate that *falls back to the legacy Python orchestrator* whenever native semantics would diverge; `run_paths.py` (1,282 LOC) re-implements branch/stacking/rep-fusion/augmentation/generator expansion in Python; `node_runner.py:18-23` states it is "numerically correct for model-on-raw-features graphs" only and names the cross-node feature-chaining "A3 gap" as unresolved. This is a defensible migration *interim* and matches the ground-truth "legacy default, dag-ml opt-in" — but the design narrates it as if orchestration already lives natively, which mis-scopes every downstream lane.

**T5 — "Same predictions/scores/artifacts" (LOCK-PYREF) is unsatisfiable against the real engine; there is no accepted-incompatibility registry and the oracle identity is self-contradictory.** (Lens 1 C4/T1/T2; Lens 2 C1/C2/C3 — the spine; Codex-2 Findings 2/3/4/§"required corrections"; Lens 4 P2.) The real harness (`test_conformance_dual_engine.py`) carries **11 permanent strict-xfails** + **2 shipped intended contract changes**, and for some of them *the oracle is the bug or does not run*. Enumerated in §6. The design's two-way "pass / accepted break" rubric (`DESIGN_SCHEMAS.md:117`, `:136`) cannot represent "legacy is wrong, dag-ml is authoritative" or "legacy crashes." `PYREF-007` frames the ledger as a forward-looking, initially-empty list to populate as divergences are *discovered* — but they are already measured and tagged.

**T6 — Contracts the docs propose to *author* already exist as frozen, versioned, sha-pinned dag-ml schemas; re-authoring them creates the very drift the locks exist to prevent.** (Lens 1 C5/G5/P4; Codex-1 Crit-2/Med-6; Lens 4 D2.) `ControllerManifest`/`NodeTask`/`NodeResult`/`campaign_spec`/`execution_plan`/`graph_spec`/`pipeline_dsl`/`coordinator_data_plan_envelope`/`parity_oracle.v1`/`process_adapter_frame` all exist in `dag-ml/docs/contracts/` with `$id`s, schema-version constants, C-ABI version pins, and a `conformance_pack.v1.json` tying each to a `normalized_sha256` (validated by `dag-ml/scripts/validate_contracts.py` in lockstep with `dag-ml-data`). `CAP-*`/`CTRL-001`/`REL-*` must be reframed "surface + re-export the existing schema," not "define." (Caveat: 3 design-doc manifest fields — `transport`, `runtime_requirements`, `conformance_fixtures` — are NOT in the current Rust `ControllerManifest`; adding them is a versioned extension, not "make visible" — Codex-1 Crit-2.)

**T7 — The UI taxonomy is greenfield, not extracted; Studio and Web have already forked at the primitive level; no visual-baseline infra exists.** (Lens 3 C1/C3/C4/G1; Codex-2 Finding 6.) The design literally says organize "by reusable product responsibility, **not by where the component first appeared in Studio**" (`DESIGN_SCHEMAS.md:1882-1883`) — the opposite of "extract from Studio." Studio's 703 feature `.tsx` files don't cut cleanly into the 7 buckets; the `controllers` bucket maps to **zero** existing folder. Studio (32 shadcn primitives, split-variant generation) and Web (~47 primitives, newer `data-slot` generation) have diverged down to `button.tsx`. There is **no** Storybook/Chromatic/Percy/`toHaveScreenshot` baseline anywhere in Studio (`screenshot:'only-on-failure'` = debug only; Storybook was removed) — the "Studio baseline" gate is a **net-new lane**, not an artifact to extract against.

**T8 — The lanes are not as parallel as claimed; there are hidden serial chains and two missing lanes.** (Lens 1 P1/P2; Lens 3 R1/R4; Lens 4 P1/P3/P4/P5; Lens 2 P1/P3.) Hidden serial edges: UI(controllers/runtime/results) ← LOCK-RT + LOCK-CAP + CTRL-001 (not just LOCK-UI/LOCK-CAP); benchmarks `queue/evaluate` ← a runner that exists in no repo; cluster fine-grained DAG ← dag-ml-as-coordinator (L5/L16). Two missing lanes: **(a)** the legacy-engine DROP / `DEFAULT_ENGINE="dag-ml"` cutover — the program's actual definition-of-done, currently unowned; **(b)** the dag-ml ↔ dag-ml-data lockstep byte-identity CI obligation, a standing two-repo commit gate.

---

## 2. Critical findings (severity-ordered)

Deduplicated across all six reviews. Each: the claim, evidence (file:line), which review(s) raised it, the concrete correction.

### BLOCKER

**B1 — "Controller" conflates three incompatible objects with no adapter; the binding story has no foothold and the anti-drift rule is already violated.**
*Evidence:* dag-ml `ControllerManifest` (`dag-ml/crates/dag-ml-core/src/controller.rs:115-138`; `dag-ml/docs/contracts/controller_manifest.schema.json`); nirs4all `OperatorController` (`nirs4all/nirs4all/controllers/controller.py:14-82`; 31 `@register_controller`); dag-ml-engine router (`nirs4all/nirs4all/pipeline/dagml/operator_routing.py`, 4-entry model table); design treats one object (`DESIGN_SCHEMAS.md:840-959`, `DQ-014` `:2167`); UI has no manifest data (Studio editor on node-registry, Lens 3 C2).
*Raised by:* Lens 1 (C1, BLOCKER), Lens 3 (C2/G3/R3), Codex-1 (Crit-2, Med-7), Lens 4 (D2).
*Correction:* Add a mandatory lane task **before `CTRL-001`** that (i) defines the `OperatorController → ControllerManifest` projection, (ii) proves each of the 31 Python controllers maps to a manifest or is declared "legacy-only, no manifest," (iii) names an owner for the node-registry ↔ ControllerManifest reconciliation that Studio needs. Until that exists, `DQ-014` ("controllers are the primary binding surface") is aspiration, not fact. Treat `L16` as an early lock-adjacent lane, not a downstream leaf (see §5).

**B2 — n4m is not wired into the dag-ml execution path; the "PLS/AOM via n4m portable execution" promise is unimplemented and has no owning task on the dag-ml/bridge side.**
*Evidence:* `grep -rn n4m dag-ml/crates` (source) = empty; `grep -rn n4m nirs4all/nirs4all/pipeline/dagml` = empty (this review confirms; only matches are build-artifact `.rlib`/`.so` hashes under `target/release/deps`); `DESIGN_SCHEMAS.md:1608-1609` lists it as present-tense ownership; `MTH-001..006` are all methods-side (ledger/ABI-skew/fixtures), none calls the n4m C ABI from a host controller.
*Raised by:* Lens 1 (C2, BLOCKER; G2), Codex-1 (Med-6), corroborated by Lens 4.
*Correction:* Downgrade the §7.2 "via n4m" rows to ROADMAP with an explicit blocking dependency — a dag-ml ControllerManifest whose `artifact_policy` is serializable/portable and whose host controller invokes the n4m C ABI. Add a dag-ml/bridge-side task (the missing owner). Decide explicitly whether V1 ships **sklearn-only on the dag-ml engine** (honest) or commits to wiring n4m (net-new).

### CRITICAL

**B3 — LOCK-PYREF "same result" is already false; there is no accepted-incompatibility registry and the oracle's identity is self-contradictory.**
*Evidence:* `ROADMAP.md:55-57` ("memes splits, predictions, scores, artifacts et erreurs"), `:870-871` (DoD), `DESIGN_SCHEMAS.md:115-118`, `:196-197` ("cannot claim V1 parity if the Python reference pipeline fails"). Real engine: `test_conformance_dual_engine.py` `KNOWN_DIVERGENCES` (8 strict-xfails, `:78-150`) incl. `rep_to_*` where **dag-ml is correct and legacy double-counts** (`:127-130`); 2 `legacy_bug` strict-xfails where **the oracle crashes** (`cases_branches_merges.py:251-254`, `:293-296`); `NUM_PREDICTIONS_DIVERGENCE` (`:189-202`) + `best_X` selection-anchoring baked into `_conformance_helpers.py:253,315` and `CHANGELOG.md:44-58`. `ADR-17_LEGACY_DROP_HANDOFF.md:74-102` documents all of it as permanent debt + 2 shipped intended changes.
*Raised by:* Lens 2 (C1/C2 — the spine), Lens 1 (C4/T1), Codex-2 (Findings 2/3, required-correction 1/2), Lens 4 (P2).
*Correction:* Replace "same result" with a **3-tier ledgered oracle** (§6) + a `PYREF-000` task that imports the 13-entry registry (8 KNOWN_DIVERGENCES + 2 legacy_bug + best_X + 2 num_predictions) as accepted `DEC-*` items *before LOCK-PYREF can be signed*. State that for `rep_to_*` and the 2 shipped changes **the V1 value is dag-ml's, not the oracle's**. Scope `DESIGN_SCHEMAS.md:196-197` to Tier-1 only.

**B4 — Bit/numeric parity is structurally impossible for RNG-driven shapes; the comparator spec demands it anyway.**
*Evidence:* `ADR-17:64-65` (`_sample_`/`_weights_` RNG = "permanent acceptable residue", no cross-language-deterministic primitive); `test_conformance_dual_engine.py:109-116` (`generator_sample_log_uniform_alpha` "genuinely UNSEEDED … best_rmse differs run to run"), `:144-149` (`generator_or_count_seed` is a registry SKIP because `_seed_` is not threaded into `OrStrategy.sample_with_seed`, so a strict-xfail "would FLIP to XPASS whenever the two unseeded draws coincide"). `PYREF-003` (`ROADMAP.md:564-565`) demands "predictions/metrics numeriques avec tolerances."
*Raised by:* Lens 2 (C3), Lens 1 (T2), Codex-2 (Finding 2 nuance: strict-xfail vs skip are different risk classes).
*Correction:* Add a `rng_nondeterministic` disposition class (skip-with-evidence or strict-xfail, **never tolerance-loosened**) and a roadmap note at `:55-57` that bit-parity is explicitly NOT the target for unseeded `_sample_`/`_weights_`/augmentation/Optuna shapes; the target is "same winner / same value" for **seeded deterministic** shapes only. Decide whether to fix the `OrStrategy.sample_with_seed` seed-threading bug or leave it a documented skip.

**B5 — The shipped dag-ml engine inverts the North Star (Python orchestrates, dag-ml sub-executes a slice); the design narrates the opposite, mis-scoping L5.**
*Evidence:* `nirs4all/pipeline/dagml/detect.py:275-277,323` (native taken ONLY for proven-equivalent shapes; SAMPLING modifiers DEMOTE), `run_paths.py` 1,282 LOC, `node_runner.py:18-23` (model-on-raw-features only; A3 cross-node-feature gap unresolved); `DESIGN_SCHEMAS.md` §3.2 assigns "Orchestration ML / variant expansion / selection" to dag-ml as if present.
*Raised by:* Lens 1 (C3/C8), Lens 4 (C1 + T2), Codex-2 (Finding 4).
*Correction:* Re-scope `L5`/`DML-002` from "build predictions+aggregation native (incl. compat projections if necessary)" to "**migrate `run_paths.py`/`detect.py` orchestration DOWN into dag-ml + widen `detect.py` native coverage**," and add a measurable **native-vs-fallback coverage metric** ("% of the parity corpus that runs NATIVE vs falls back"). Annotate the §6.3/§4ter.5 sequence diagrams: the NodeTask path covers a vertical slice; branch/stacking/rep/aug/generator run in Python (interim). This is the 86 pw "host migration" line in `SYNTHESE §6.1`, not the 5-10 pw "close divergences" line the optimistic scenario leans on.

**B6 — Bundle/workspace cross-engine compatibility is a claimed gate with no test behind it, and `.n4a` export on dag-ml depends on a legacy-refit bridge that breaks at the legacy-DROP.**
*Evidence:* `DESIGN_SCHEMAS.md:164-166` claims artifact replayability + workspace migration parity; the only shipping cross-engine bundle test, `test_conformance_export_roundtrip.py`, asserts dag-ml-native single-model export reproduces *its own* run within 1e-6 (`:78-112`) and for branch/merge only "writes a loadable artifact" (`:115-139`), falling back to the legacy-refit bridge (`ADR-17:90-98`). No test proves a legacy `.n4a` reload-predicts identically on dag-ml, nor SQLite `user_version`/Parquet column identity across engines. Format/schema contracts ARE frozen (`tests/regression/test_bundle_contract.py`, `test_storage_schema_contract.py`) but that is not cross-engine artifact compatibility.
*Raised by:* Lens 2 (C6), Codex-2 (Finding 7), Lens 4 (T3 for cluster analog).
*Correction:* Mark bundle/workspace cross-engine parity **UNTESTED, not a passed gate**. Add a lane task (L17 or L4 `CORE-005`): cross-engine `.n4a` round-trip parity (legacy bundle → predict on dag-ml == legacy predict, within tol) + workspace-schema conformance across engines. Make "native export replaces the legacy-refit bridge" (ADR-17 §3 item 9) a **HARD blocker on the legacy-DROP** — the moment legacy is dropped, multi-model/non-joblib `.n4a` export breaks until native covers it.

**B7 — No lane owns the legacy-DROP / `DEFAULT_ENGINE="dag-ml"` cutover; it is the program's actual definition-of-done.**
*Evidence:* `nirs4all/api/run.py:287` "interim posture until the planned global refactoring lands"; `ADR-17_LEGACY_DROP_HANDOFF.md` documents the 9-step drop and that the flip is one line, deferred; the roadmap's DoD (`ROADMAP.md:864-885`) reads as if dag-ml-default is the MVP endpoint but never references `DEFAULT_ENGINE`, never states the interim-legacy-default posture, and assigns the cutover to no lane. The maintainer's stated sequencing: dag-ml `feat/native-scoring` merges to dag-ml main + the dag-ml-data lockstep release happens *at/after* the global refactoring.
*Raised by:* Lens 4 (P4 — "most consequential missing gate"), Lens 2 (P3/DEC-DROP-001), Codex-1 (Crit-1 impact), Codex-2 (Finding 4).
*Correction:* Add a first-class **cutover lane** (call it `L19` / `LOCK-DROP`): define the criterion for flipping default and removing the legacy path (e.g. "EXPECTED_FALLBACK == ∅ AND native `.n4a` export covers the bridge cases AND the 3-tier oracle is green AND Studio/Web consume the runtime route"), sequence it relative to the multimodal program (pre- or post-flip — DEC below), and own ADR-17's 9 steps.

### HIGH

**B8 — `dag-ml`/ecosystem already ship the contracts the roadmap proposes to author; `CAP-*`/`CTRL-001`/`REL-*` must surface, not define — and 3 proposed manifest fields are real net extensions.**
*Evidence:* `dag-ml/docs/contracts/*` ($id'd, schema-versioned, C-ABI-pinned); `conformance_pack.v1.json` (normalized_sha256 + cross_repo_conformance); current Rust `ControllerManifest` (`controller.rs:115-138`) lacks `transport`/`runtime_requirements`/`conformance_fixtures` named at `DESIGN_SCHEMAS.md:940-942`.
*Raised by:* Lens 1 (C5/G5/P4), Codex-1 (Crit-2), Lens 4 (D2).
*Correction:* Reframe every `CAP-*`/`CTRL-001`/`REL-*` task as "surface the EXISTING dag-ml schema, with `validate_contracts.py` as the drift gate"; derive the capability taxonomy (`CAP-002`) from the existing 19-value controller `capabilities` enum + `rng_policy`/`fit_scope`/`artifact_policy`, not a fresh vocabulary; make the aggregation manifest (`REL-*`) **consume** each repo's conformance-pack hashes rather than re-pin independently; specify `transport`/`runtime_requirements`/`conformance_fixtures` as a schema-versioned extension or registry sidecar.

**B9 — `dag-ml-data` provider plumbing and `nirs4all-io → dag-ml-data` emission already landed; `L6`/`L7` double-count "from scratch" base work.**
*Evidence:* `dag-ml-data` `04ecf3a` ("land the P4 provider-contract spike, Codex SHIP"); crate `crates/dag-ml-data-provider/` (full 7-method C-ABI vtable, ABI v2, zero `todo!/spike` markers); `nirs4all/pipeline/dagml/envelope.py` already emits `CoordinatorDataPlanEnvelope`/`DataPlan`/`SampleRelationTable`; `nirs4all-io` `da24fb5` ("emit dag-ml-data builtin-catalogue contracts"), `nirs4all-io/crates/nirs4all-io-dagml/src/lib.rs:398-603` maps `AssembledDataset → CoordinatorDataPlanEnvelope`, `PHASE2_GATE.md:10` GREEN. ADR-0001 (dag-ml-data) handed the bridge to nirs4all-io, which landed it.
*Raised by:* Lens 1 (P3), Lens 4 (C3), Codex-1 (High-5).
*Correction:* The brief's "provider spike is HELD (lockstep)" is **wrong** — it LANDED; "lockstep" means byte-identical contract-mirroring with dag-ml, not a development hold. Scope `DMD-003`/`IO-005` to **extend** (multimodal `SampleRelationTable`/materialization + production providers), not create. The `SYNTHESE §6.2` IO 26-44 pw estimate is mostly the *multimodal* extension (image/HSI/timeseries/genotype), not base plumbing. Note: `nirs4all-io/README.md:27-35` ("Phase 2 stays gated") contradicts `CLAUDE.md:19`/`STATUS.md:13`/`PHASE2_GATE.md:10` ("Phase 2 COMPLETE") — a test-trust hazard to fix.

**B10 — methods/sklearn numeric parity is necessary-but-not-sufficient (correctly stated) but is import-skipped by default, covers ~2 kernels, and is not a blocking prerequisite for any "numerically portable" capability claim.**
*Evidence:* `tests/unit/operators/methods/test_n4m_ops.py:34-46` (`pytest.importorskip("n4m")` + `skipif(not METHODS_AVAILABLE)` → does not run unless `libn4m` installed, which it is not by default); covers SNV (bit-exact vs `snv_v1.json`) + SNV→PLS only; methods repo's own Phase C parity rebuild is deferred (`nirs4all-methods/parity/SCENARIOS_MIN.md`, `Makefile:73`), cross-binding CI gate says Python-only is not cross-binding proof (`benchmarks/cross_binding/ci_parity_gate.py:65`).
*Raised by:* Lens 2 (C7), Codex-2 (Finding 5 + required-correction 4), Codex-1 (Med-6).
*Correction:* Make a **methods-installed CI lane a prerequisite** for any `CAP-002`/`MTH-006` "numerically portable" claim; expand fixtures to the kernels actually in the parity corpus (SavGol, Detrend, MSC, FirstDerivative — all appear in `KNOWN_DIVERGENCES` notes/`Y_PRED_TOL_OVERRIDES` as float-noise sources) so the host float32/float64 dtype issue ADR-17 fought (`test_conformance_dual_engine.py:93-99`) is caught at the kernel level. Do not bury methods parity in the generic gate table.

**B11 — Studio's "thin backend" rule is aspirational; the backend still performs substantial orchestration, so L12 must budget real extraction, not wiring.**
*Evidence:* `nirs4all-studio/api/runs.py:1311-1431,1488-1499,1749-1863` (mutates `sys.path`, imports nirs4all, builds dataset config, loads datasets, grouping/canonical-conversion/variant-expansion, calls `nirs4all.run`, exports `.n4a`); `api/nirs4all_adapter.py:62-258` (operator resolution, variant expansion, Python export, preflight). The execution-driver seam (`api/execution_driver.py`) is real and correctly 501-guards cluster/WASM — but it is a seam, not thin-layer compliance.
*Raised by:* Codex-1 (High-4), Codex-2 (Finding 6), Lens 3 (consistent).
*Correction:* `L12`/`STU-002` must budget adapter removal + extraction, not treat the execution-driver seam as proof Studio already consumes only stable runtime/capability APIs.

**B12 — Provider interfaces named by the roadmap (`PipelineProvider`/`BenchmarkProvider`/`PaperExporter`/`to_dataset_package`) exist in NO repo; benchmarks has no runner; the unifying provider layer is net-new, not wiring.**
*Evidence:* `ROADMAP.md:467-473`. Grep across repos: `PipelineProvider.list_pipelines/get_pipeline/get_bundle` = 0 hits (real API `n4r.list/get/fetch/card`); `BenchmarkProvider`/`def queue`/`def evaluate` = 0 hits, Arena "explicitly never runs compute" (`nirs4all-benchmarks/src/.../ingestion/upload.py:13-15`, `DESIGN.md:9`), only a write-only `planned_runs` table; `inspect_bundle/methods_report/build_repro_page` = 0 hits (real `read_bundle/build_bibliography/build`); `to_dataset_package` = 0 hits (real `to_nirs4all() -> SpectroDataset`).
*Raised by:* Lens 4 (C4), Codex-1 (Low-11).
*Correction:* Rename `PROV-*` tasks to the repos' real APIs, flag the unifying `*Provider` layer as **net-new core-side work**, and state that benchmarks "queue/evaluate" depends on a runner that lives in runtime-python/cluster (L5/L15) — an edge the DAG omits.

**B13 — UI runtime/results/export buckets depend on `LOCK-RT`, not just `LOCK-UI`/`LOCK-CAP`; the DAG edge is drawn backwards and Web is the more advanced runtime consumer treated as the follower.**
*Evidence:* `ROADMAP.md:693` `LOCK-UI = UI-001 + UI-002 + LOCK-CAP` (no LOCK-RT); Studio results are REST aggregated-prediction shaped (`api/aggregated_predictions.py`, `src/types/aggregated-predictions.ts`), Web results are in-WASM `RunResult` (`nirs4all-web/studio-lite/src/engine/types.ts`) running real dag-ml `SequentialScheduler` + `JsRuntimeController` in WASM (`dagml-engine.ts:1-6,386-445`) — two different objects; a shared `results`/`export` component needs a shared result schema = LOCK-RT.
*Raised by:* Lens 3 (C4/G4/R1/R2), Codex-1 (Med-8).
*Correction:* Re-draw `LOCK-UI` to add `LOCK-RT` for the runtime/results/export buckets; split the extraction ordering — `foundation`/`data`/`pipeline` Studio-first, `runtime`/`results`/`export` **contract-first**, deriving the shared prop schema from BOTH `studio-lite/src/engine/types.ts` + `contracts.ts` AND Studio's aggregated-prediction types simultaneously. Web's WASM `RunResult` + multi-node host-enumeration limit (`dagml-engine.ts:122-130`) is the de-facto runtime-contract evidence; treat it as a primary input, not a second-class adopter.

**B14 — Cluster is fully specified and built (versioned protocol, ~3,977 LOC, 66 tests); the roadmap/design treat it as TBD and over-label it a "scheduler/load-balancer."**
*Evidence:* `nirs4all-cluster` Pydantic wire contract (`schemas.py`), FastAPI server with concrete `/v1` routes, versioned handshake (`versioning.py:26-84`, `X-N4C-*`, HTTP 426 on protocol-major mismatch), content-addressed SHA-256 store, atomic leasing+TTL reaper, capability routing, client SDK; `DESIGN_SCHEMAS.md:1259` "Core should *probably* expose at least an optional cluster client" + `ROADMAP.md:495` `CLU-001` "spec client" read as not-done. Real gaps: RBAC (single static bearer token, `app.py:171-177`), fine-grained DAG (`WORKLOG.md:123`), Studio adapter. `cluster/docs/DISTRIBUTED_EXECUTION_DESIGN.md:19` "nirs4all does not integrate dag-ml today" is now STALE.
*Raised by:* Lens 4 (C5/P3), Codex-1 (consistent).
*Correction:* Revise `CLU-001` "spec" → "harden the existing `/v1` client"; the real gaps are RBAC (`CLU-002`) + Studio adapter + a "distributed == local" parity fixture; stop calling the pull-based lease queue a "scheduler/load-balancer" (`README.md:122-123` disclaims K8s/Ray/Dask-class scheduling); fine-grained `CLU-004` depends on dag-ml-as-coordinator (L5/L16), an undrawn edge. Cluster could ship an optional `nirs4all` client far earlier than the Vague-4 placement implies.

### MEDIUM

**B15 — Name collision: `dag-ml-core` vs `nirs4all-core` (historical pre-cutover ambiguity).**
*Evidence:* `dag-ml/crates/dag-ml-core` (real contract crate) vs `nirs4all-core` (multi-repo aggregate concept) vs the local `nirs4all-core` worktree (== `e41362b4`, "clone local temporaire" per `DESIGN_SCHEMAS.md:336`, `SYNTHESE §9`). Three meanings, one word "core."
*Raised by:* Lens 1 (C7/DEC), Codex-1 (High-3), Lens 4/SYNTHESE.
*Correction:* `LOCK-GOV` must explicitly reconcile `dag-ml-core` (contract crate) vs `nirs4all-core` (aggregate) — they are NOT the same layer and must not share "core" unqualified, or `L4`/`L5` agents collide. Current V1 state: `nirs4all-core` is the canonical aggregate repository; the old throwaway-clone interpretation is superseded.

**B16 — `core` is given execution semantics (`portable_run_subset`) it implements nowhere; that risks a second kernel/execution home.**
*Evidence:* `DESIGN_SCHEMAS.md:493` `CoreAggregate.portable_run_subset()`, `:39` "Execution ML: core = seulement portable subset si kernels et artifacts sont natifs"; B2 shows no n4m-in-dag-ml path exists, so core would hold an execution responsibility implemented nowhere; `RuntimeWasm.runPortable()` (`:516`) already places WASM execution in a runtime.
*Raised by:* Lens 1 (C6/DEC), Codex-1 (Med-6).
*Correction:* Remove `portable_run_subset`/`runPortable` from `CoreAggregate`; core exposes inspect/validate/capability only, never `run`. Push execution to `runtime-*`. This also cleanly resolves the core/runtime split.

**B17 — `nirs4all-lite`'s "aggregate" role is over-claimed; it is a scaffold/registry that compiles 2 of 6 upstreams and excludes datasets by default.**
*Evidence:* `nirs4all-lite/README.md:94-99` ("buildable aggregate *scaffold*"); Rust binding compiles only dag-ml + dag-ml-data (`Cargo.toml:24-26`), formats/io/methods/datasets via `libloading`; Python `all` extra excludes datasets (`bindings/python/pyproject.toml:31-46`), lazy proxies.
*Raised by:* Lens 4 (C6), Codex-1 (consistent), SYNTHESE.
*Correction:* The scaffold has been renamed/promoted to `nirs4all-core` with no public `nirs4all-lite` alias. `CORE-002` "direct exposition" of 6 upstreams remains real implementation work (vendoring/`pub use` vs `libloading`); decide whether datasets is in or out of the default aggregate; fix diagrams that place all six (incl. datasets) inside core without an executable capability gate.

**B18 — `nirs4all-tools`/`LOCK-MIG` ignores the existing in-tree workspace migrator; two migrators, no stated relationship.**
*Evidence:* `nirs4all/nirs4all/pipeline/storage/migration.py` exists (27.3K; `migrate_arrays_to_parquet`, `migrate_duckdb_to_sqlite` "Will be removed in v1.0"); `ROADMAP.md:585-646` `L18`/`TOOL-004` creates a new converter as if greenfield.
*Raised by:* Lens 4 (C7), Codex-1 (consistent).
*Correction:* State whether `nirs4all-tools` absorbs/supersedes `migration.py` and the support-window relationship.

**B19 — The `nirs4all-aom` ⇄ `nirs4all.operators.models` duplication is an undecided blocker for the methods/papers lanes.**
*Evidence:* `DESIGN_SCHEMAS.md:349,1765` flag aom "separate product or absorbed by methods"; AOM-PLS/POP-PLS exist in BOTH `nirs4all-aom` and `nirs4all/operators/models` (ecosystem `CLAUDE.md`).
*Raised by:* Lens 4 (D3).
*Correction:* Resolve AOM placement before any methods/papers lane touches AOM (DEC below).

**B20 — `datasets` "feeds IO/core" is half-true; it imports nirs4all core directly and nirs4all-io in exactly one file.**
*Evidence:* `nirs4all-datasets/.../dataset.py:38,324`, `qualify/profile.py:262-311` reach into `nirs4all.operators.filters`/`analysis.projections`/`data.detection`; `nirs4all_io` in `reproduce.py:85` only; no `nirs4all_formats` import; `DESIGN_SCHEMAS.md:334,430` advertise `DATASETS → IO`.
*Raised by:* Lens 4 (D4), Codex-1 (Low-11).
*Correction:* Mark `DATASETS → IO` as target-state, not current; decide the canonical read path (DEC below).

**B21 — Stale metadata: `nirs4all` package metadata still says dag-ml is the default engine, contradicting `DEFAULT_ENGINE="legacy"`.**
*Evidence:* `pyproject.toml:93-96`, `requirements.txt:35-37` comments say dag-ml default + `run()` dispatches to dag-ml by default; `engine.py:27-31` + `CHANGELOG.md:14-30` + `ADR-17:10-15` say default = legacy.
*Raised by:* Codex-1 (Med-9).
*Correction:* Fix the comments as part of any `PRE-1` audit (low effort, prevents downstream agents inferring wrong state).

**B22 — Doc-path drift weakens a load-bearing boundary citation.**
*Evidence:* Ecosystem `CLAUDE.md` + briefs cite `nirs4all-studio/BACKEND_RULES.md`; actual path `nirs4all-studio/docs/_internals/BACKEND_RULES.md` (content intact, `:1-64`).
*Raised by:* Lens 3 (G5).
*Correction:* Fix the link so roadmap-following agents find the canonical rule.

---

## 3. Opus vs Codex confrontation

### 3.1 Where they AGREE (high-confidence — treat as settled fact)

These convergences are independent (different reviewers, different code reads) and therefore the most trustworthy conclusions in this review:

- **The dag-ml backend is landed/selectable, not greenfield** — Lens 1 P1, Lens 4 C1, Codex-1 Crit-1, Codex-2 Findings 1-4 all reach this from `api/run.py`/`engine.py`/`ADR-17`. **Settled.**
- **The parity oracle exists and "same results" is false** — Lens 2 (entire), Lens 1 C4, Codex-2 Findings 2/3, Lens 4 C2. They independently enumerate the **same** 11 strict-xfails + 2 shipped contract changes from `test_conformance_dual_engine.py` and `ADR-17:74-102`. **Settled** — this is the most heavily corroborated finding.
- **dag-ml already owns `ControllerManifest`/`NodeTask`/`NodeResult`/registry/transport contracts** — Lens 1 C5, Codex-1 Crit-2 (with the same schema/Rust-type citations). **Settled.**
- **methods/sklearn parity is correct-in-principle but import-skipped and narrow** — Lens 2 C7, Codex-2 Finding 5. **Settled.**
- **dag-ml-data + io→dag-ml-data emission already landed; remaining work is multimodal/productization** — Lens 1 P3, Lens 4 C3, Codex-1 High-5. **Settled.**
- **The Studio native-results adapter is real and on main, read-only, manifest/legacy-shaped (not runtime/ControllerManifest)** — Lens 3 C5 (git-proven), Codex-1 High-4/Low-10, Lens 1 G3. **Settled** (this review re-verified: `feat/native-results-reader` = `91d5ba4`, 0 ahead of main, adapter PRESENT on main).
- **Bundle/workspace cross-engine compatibility is claimed but untested** — Lens 2 C6, Codex-2 Finding 7. **Settled.**

### 3.2 Where they DISAGREE or one caught what another missed (adjudicated)

**D-1 — Studio native-results reader: "present in working tree" (Lens 1) vs "merge-base of main, 0 ahead, ON MAIN" (Lens 3) vs the brief's "UNMERGED/dormant."**
*Adjudication:* **Lens 3 is correct and most precise.** This review re-ran git: `git rev-parse feat/native-results-reader` = `91d5ba4` (merge-base), `git rev-list --count feat/native-results-reader ^main` = **0**, main is **5 ahead**, `api/native_results_adapter.py` is **PRESENT on main**. Lens 1's "present in the working tree but on a dirty branch — pin the commit" was directionally right but conflated Studio (clean, `2ccbf68`) with the *closure-branch* dirtiness the handoff warned about. The brief's "UNMERGED" is the stalest framing. **Net:** any plan gated on "merge the dormant branch first" is moot; the adapter is on main, consumed via nirs4all read-only, manifest-shaped. The handoff's "1000+ untracked / hundreds modified" caution (`STUDIO_PRISTINE_HANDOFF.md:199-205`) is now **stale** for Studio main (`git status --short` = 0).

**D-2 — Lens 1 narrates the "two-controller" problem as the dag-ml-vs-nirs4all manifest split; Codex-1 caught a third issue Lens 1 partly missed — three of the proposed manifest fields don't exist in the Rust schema.**
*Adjudication:* **Both correct; Codex-1 sharpens.** Lens 1's three-objects framing (manifest / Python ABC / engine router) is the deeper structural point. Codex-1 Crit-2 adds the concrete schema delta: `transport`/`runtime_requirements`/`conformance_fixtures` (`DESIGN_SCHEMAS.md:940-942`) are NOT in `controller.rs:115-138`, so even "make the manifest visible" is partly "extend the manifest (versioned)." **Net:** B1 (adapter, the three objects) AND B8 (the field delta is a schema-versioned extension) — keep both.

**D-3 — Lens 2 says "adopt the tagged harness, it's the source of truth"; Codex-2 says the harness is *better than the docs imply in places but* split across multiple partial gates and not wired as a single release blocker.**
*Adjudication:* **Complementary, not contradictory; Codex-2 adds operational nuance Lens 2 underweights.** Lens 2 is right that L17 should adopt-not-rebuild. Codex-2 is right that "adopt" is not free: `test_parity_baseline.py` runs `engine="legacy"` only; `_oracle.py` records summary fields (`num_predictions`/models/datasets/scalar metrics), **not** the full artifact/workspace/error surface the design claims; there is no single command gating every claimed surface. **Net:** the correction is "adopt the harness as LOCK-PYREF **and** wire the missing surfaces (cross-engine `.n4a`/workspace, methods-installed lane, the 3 zero-coverage keywords) into one auditable gate" — Lens 2 §G2 + Codex-2 §"required corrections" combined.

**D-4 — Codex-2 caught a precision point the Opus lenses blurred: strict-xfail vs skip are *different risk classes*.**
*Adjudication:* **Codex-2 is right and it matters.** ADR-17 shorthand lumps `_sample_`/`_weights_` together, but in the real suite unseeded `_sample_` generators are **strict-xfails** (proven accepted incompatibilities) while `_or_ count`/`_weights_ count` are **skips** as unknown-semantics (`test_conformance_dual_engine.py:144-149`, `cases_generators_conformance.py:1030-1098`) — *untested*, not *accepted*. Lens 1/Lens 2 treat the residue more uniformly. **Net:** the registry (§6) must distinguish `accepted-strict-xfail` from `skip-unknown-semantics` (= unproven behavior, a real LOCK-PYREF gap), and `rng_nondeterministic` (B4).

**D-5 — Lens 4 says cluster is "built + protocol-specified, ship it earlier"; the design treats it as a future scheduler. Lens 4 also over-credits it slightly vs its own README.**
*Adjudication:* **Lens 4 correct on built-ness; the README disclaimer keeps it honest.** Cluster is a tested beta with a versioned `/v1` protocol — but `README.md:122-123` disclaims K8s/Ray/Dask-class scheduling, so "scheduler/load-balancer" overstates a pull-based lease queue. **Net:** B14 — revise `CLU-001` to "harden," fix the label, name RBAC + Studio-adapter + distributed==local parity as the real gaps.

**D-6 — What only Lens 3 caught: the UI taxonomy is greenfield (the doc's own words), Studio/Web forked at `button.tsx`, and the "Studio baseline" visual gate is net-new infra.** None of the Codex reviews or other lenses examined the frontend trees. **Net:** T7/B13 are Lens-3-unique and unrebutted — high-confidence because they are direct file reads (32 vs 47 primitives; `screenshot:'only-on-failure'`; Storybook removed).

**D-7 — What only Lens 4 caught: the dag-ml ↔ dag-ml-data lockstep PUSH is a standing CI obligation with no lane, and the cluster fine-grained DAG / benchmarks-runner edges are undrawn.** Lens 1 noted the conformance-pack pinning (P4) but not the recurring two-repo push obligation as a *lane*. **Net:** T8 missing-lane (b).

**Confrontation conclusion:** The Opus lenses are stronger on *architecture/structure* (three-controllers, core-vs-runtime, UI fork, lane DAG) and the Codex reviews are stronger on *test-suite operational precision* (strict-xfail-vs-skip, the harness's actual recorded fields, the methods import-skip, the per-method Phase-C deferral). They do not contradict on any load-bearing fact; where they differ, it is one adding precision the other blurred. The brief's three "ground-truth" framings that were *wrong* (native-reader unmerged; provider spike held; — and implicitly "not started") are corrected by the code in §9.

---

## 4. Design gaps

- **DG1 — No `OperatorController → ControllerManifest` adapter is specified** (B1). The single most load-bearing object in the binding story has no migration contract; `CTRL-002` assumes the manifest exists for the 31 Python controllers — it doesn't. (Lens 1 G1.)
- **DG2 — No task owns "invoke n4m from a dag-ml controller"** (B2). `MTH-001..006` are all methods-side; the portable-execution promise has no owner on the dag-ml/bridge side. (Lens 1 G2.)
- **DG3 — `data_views`/cross-node feature-chaining (the A3 gap) is unscoped** — `node_runner.py:18-23` names it the blocker between "model-on-raw" and "real pipelines run native," yet no lane owns the process-adapter delivering transformed features across nodes; `DML-001` and `IO-005` circle it. (Lens 1 G4.)
- **DG4 — Capability taxonomy has no link to the controller `capabilities` enum** — `CAP-002` invents portability *levels* while `needs_python_gil`/`thread_safe`/`process_safe` (the 19-value enum) ARE the runtime-portability signal; the taxonomy should be derived, not authored. (Lens 1 G5.)
- **DG5 — UI fixtures are claimed as existing seams but are runtime/core schemas that don't exist yet** — `UI-004`/`UI-009` want "fixtures de props runtime/core" but LOCK-RT/LOCK-CAP are unstarted; today's only fixture sources are Studio's REST DTOs + Web's engine types. Circular: the UI parity gate (`:1931`) needs a runtime schema the UI lane is scheduled in parallel with. (Lens 3 G2/T3, Lens 4 P1.)
- **DG6 — No visual-baseline harness exists** — `UI-009`/the UI gate assume a Studio screenshot baseline to extract against; there is none (net-new lane). (Lens 3 G1/T1/T2.)
- **DG7 — No "Studio absorbs the best_X / num_predictions contract change" item** — the moment Studio points at dag-ml, the webapp dashboards reading `best_X`/`num_predictions`/`score_maps` see changed numbers (`CHANGELOG.md:55-57`); this cross-cut spans L12+L17+the (already-merged) Studio reader and no lane owns it. (Lens 2 G3.)
- **DG8 — `.so` freshness / Rust-rebuild discipline is a parity hazard not surfaced in any gate** — `ADR-17:42` + `check_so_freshness.py`: a stale `.abi3.so` means tests run against an old engine and parity passes falsely; with L5/L9/L16 touching Rust in parallel, a stale-`.so` false-green is a realistic cross-lane failure. (Lens 2 G4.)
- **DG9 — No "fallback pass ≠ native parity" release rule** — the suite encodes `EXPECTED_FALLBACK` + `test_native_fallback_boundary`, but the design never states that a fallback pass is *compatibility evidence, not native dag-ml parity evidence* — critical before a default flip. (Codex-2 Finding 4.)
- **DG10 — No core/runtime package actually exists** — there is no `nirs4all-runtime-*` package; the de-facto runtime is `nirs4all` Python with the in-tree bridge. `DQ-003` concedes this; the lanes should say "runtime-python today = the in-tree bridge, harden in place," not imply an extraction is a prerequisite. (Lens 4 D1.)

---

## 5. Roadmap & parallelization gaps

### 5.1 The corrected lane DAG (what the dependencies actually are)

The roadmap's DAG (`ROADMAP.md:648-702`) is conceptually sound but mis-sequenced against reality and hides serial edges. Corrected:

```text
RATIFY (not re-verify) from e41362b4:
  PRE-1 (dag-ml selectable backend)  ──evidence: api/run.py, engine.py, ADR-17
  PRE-3 / LOCK-PYREF (oracle EXISTS) ──evidence: tests/integration/parity/, 273/0 + 8220/0
  + import the 13-entry accepted-incompatibility registry  →  LOCK-PYREF SIGNABLE IN VAGUE 0
        │
        ├─ LOCK-GOV (incl. dag-ml-core vs nirs4all-core reconciliation, B15)
        │
        ├─ LOCK-CAP  ── derive from existing controller capabilities enum (B8/DG4)
        │      │
        │      ├─ LOCK-RT  ──┬─► UI(runtime/results/export)   [B13: was wrongly under LOCK-UI/CAP only]
        │      │             ├─► RT-PY (= harden in-tree bridge, DG10)
        │      │             └─► RT-WASM (= harden Web's existing dag-ml-WASM, B13/Codex-1 Med-8)
        │      │
        │      └─ L16 CONTROLLERS  ── EARLY, not a leaf:
        │             OperatorController→ControllerManifest adapter (B1)  ◄── gates RT-PY, RT-WASM,
        │             node-registry↔manifest reconciliation (Studio)         STU-004, L9 methods, every binding
        │
        ├─ LOCK-IO  ──► DMD (EXTEND landed provider, B9) ──► IO multimodal v2 (the real net-new)
        │
        ├─ LOCK-REL ──► aggregation manifest that CONSUMES per-repo conformance-pack hashes (B8/T6)
        │
        └─ LOCK-UI = UI-001 + UI-002 + LOCK-CAP + **canonical-primitive decision** + **net-new visual-baseline lane**
               (B13/T7: foundation/data/pipeline Studio-first; runtime/results/export contract-first)

NEW, MISSING, FIRST-CLASS:
  LOCK-DROP / cutover lane (B7) ──► criterion = EXPECTED_FALLBACK==∅ AND native .n4a covers bridge cases
                                    AND 3-tier oracle green AND Studio/Web on runtime route  → DEFAULT_ENGINE="dag-ml"
  LOCK-LOCKSTEP (B-T8): dag-ml ↔ dag-ml-data byte-identity CI as a standing two-repo commit gate
```

### 5.2 Hidden serial chains the roadmap calls parallel

- **UI ← controllers ← contracts ← oracle** (T8, Lens 1 P2, Lens 3 R4, Lens 4 P1). `UI-007`/`UI-008` (controller badges, runtime events) cannot have stable fixtures until `LOCK-CAP` + `RT-002` + `CTRL-001` are frozen; the doc admits the deps but still places UI in the same wave (Vague 2). UI realistically serializes on: canonical-primitive decision → visual-baseline infra → shared runtime/result schema → per-bucket extraction. Three of those four are not `LOCK-UI` outputs.
- **benchmarks-evaluate ← a runner that does not exist** (B12, Lens 4 P1). `PROV-003` "queue/evaluate" depends on runtime-python/cluster (L5/L15), an undrawn edge; the Arena never runs compute.
- **cluster fine-grained DAG ← dag-ml-as-coordinator** (B14, Lens 4 P1). `CLU-004` is gated on dag-ml exposing nirs4all as a host controller for `NodeTask` distribution (L5/L16).
- **core aggregate ← lite-scaffold reality** (B17, Lens 4 P1). `CORE-002` "direct exposition" of 6 upstreams is blocked on vendoring/`pub use` vs today's `libloading` delegation.

### 5.3 The two missing lanes (restate, because they are the program's spine)

- **(a) The legacy-DROP / `DEFAULT_ENGINE="dag-ml"` cutover** (B7) — the real definition-of-done, currently owned by no lane. ADR-17's 9-step drop + the criterion must be a first-class `LOCK-DROP` lane.
- **(b) The dag-ml ↔ dag-ml-data lockstep byte-identity CI obligation** (T8) — `validate_contracts.py` enforces JSON-identical schemas/fixtures/headers across the two repos; every contract change in either is a two-repo lockstep commit. The roadmap's generic `DEC-*` protocol never names this standing obligation. The maintainer's plan (merge `feat/native-scoring` + the dag-ml-data lockstep release *at* the cutover) makes this lane and `LOCK-DROP` interdependent.

### 5.4 Wave-ordering corrections

- **LOCK-PYREF can be signed in Vague 0**, not Vague 1 (B3/Lens 2 P1) — it unblocks the entire right half of the DAG immediately; treating it as new work is a self-inflicted critical-path delay (the single biggest parallelizability win missed).
- **L5's native-coverage backlog IS L17's `EXPECTED_FALLBACK` list** (Lens 2 P2) — make L5's task literally "drive `EXPECTED_FALLBACK` to ∅ (11 shapes: branch+merge ×4, by-source multi-source ×4, explicit-`preprocessing` ×3) + close the deferred `avg/w_avg` OOF surface (`ADR-17:46`)." One shared measurable target instead of two prose descriptions that drift.
- **Cluster could ship earlier** than Vague 4 (B14/Lens 4 P3) — RBAC + Studio-adapter are small and independent of multimodal IO/UI work.

---

## 6. Test & parity gaps

### 6.1 LOCK-PYREF reconciliation

Replace the absolute "same result" (`ROADMAP.md:55-57`, `:870-871`; `DESIGN_SCHEMAS.md:115-118`, `:196-197`) with: **"the oracle is current Python `nirs4all` MINUS the registered accepted incompatibilities (where dag-ml is authoritative), and bit-parity is not the target for RNG-nondeterministic shapes."** Implement as a **3-tier oracle**:

- **Tier 1 — Python authoritative:** match within declared tolerance. Scope `DESIGN_SCHEMAS.md:196-197` ("cannot claim parity if the Python reference pipeline fails") to **Tier 1 only**.
- **Tier 2 — dag-ml authoritative (legacy is the bug, or the contract changed intentionally):** match dag-ml's value; strict-xfail / exact-count-pin against legacy. Members: `rep_to_sources_basic`, `rep_to_pp_basic` (legacy double-counts overlapping rep folds, `:127-130`); `best_rmse`/`best_r2`/`best_accuracy` selection-anchoring (`CHANGELOG.md:44-58`, `_conformance_helpers.py:253,315`); winner-only `num_predictions` for `_or_`/`_chain_` (`NUM_PREDICTIONS_DIVERGENCE:189-202`, exact counts pinned).
- **Tier 3 — oracle does not run (legacy crashes):** V1 must run them; no legacy comparison. Members: `branch by_tag` bool-keys crash (`cases_branches_merges.py:251-254`); `by_filter` missing-deserializer crash (`:293-296`).

### 6.2 The accepted-incompatibility registry (the missing artifact — enumerate it, do not start empty)

`PYREF-007` frames an initially-empty forward ledger. It must instead **import** the already-measured, already-tagged dispositions as accepted `DEC-*` items *before LOCK-PYREF can be signed* (`PYREF-000`). Five disposition classes; the 11 strict-xfails + 2 shipped contract changes:

| # | Case / contract | Disposition | Authority | Evidence |
|---|---|---|---|---|
| 1 | `sample_augmentation_gaussian` | strict-xfail (rng/order) | neither (residue) | `test_conformance_dual_engine.py:78-88` |
| 2 | `sample_augmentation_chained` | strict-xfail (rng/order) | neither | `:78-88` |
| 3 | `sample_augmentation_after_savgol` | strict-xfail (rng/order) | neither | `:78-88` |
| 4 | `feature_augmentation_replace_three_views` | strict-xfail (rng/order) | neither | `:78-88` |
| 5 | `concat_transform_pca_svd_plsr` | strict-xfail | neither | `KNOWN_DIVERGENCES` |
| 6 | `generator_finetune_params_optuna` | strict-xfail (Optuna trial seq) | neither | `:82-102` |
| 7 | `generator_sample_log_uniform_alpha` | strict-xfail (**unseeded**, run-to-run) | neither (`rng_nondeterministic`) | `:109-116` |
| 8 | `rep_to_sources_basic` | strict-xfail vs legacy | **dag-ml** (legacy double-counts; 6.6735 legacy vs 6.1906 dag-ml) | `:118-130` |
| 9 | `rep_to_pp_basic` | strict-xfail vs legacy | **dag-ml** (6.1427 vs 6.1906) | `:118-130` |
| 10 | `branch by_tag` bool-keys | legacy_bug (oracle crashes) | dag-ml (T3) | `cases_branches_merges.py:251-254` |
| 11 | `by_filter` missing deserializer | legacy_bug (oracle crashes) | dag-ml (T3) | `cases_branches_merges.py:293-296` |
| 12 | `best_rmse`/`best_r2`/`best_accuracy` anchor on SELECTED model | shipped contract change | dag-ml | `CHANGELOG.md:44-58`; `_conformance_helpers.py:253,315` |
| 13 | multi-model `_or_`/`_chain_` winner-only `num_predictions` (34→32, 49→47) | shipped contract change, exact-count-pinned | dag-ml | `NUM_PREDICTIONS_DIVERGENCE:189-202`; `cases_generators_conformance.py:47-59` |

Plus the **distinct risk class** Codex-2 D-4 flagged: `_or_ count`/`_weights_ count` are **skips-unknown-semantics** (`:144-149`, `cases_generators_conformance.py:1030-1098`) — *untested, not accepted* — and the 3 **zero-coverage public DSL keywords** `auto_transfer_preproc`/`fill_value`/`na_policy` (`README.md:50-54`). These are real LOCK-PYREF coverage holes, not accepted incompatibilities.

The harness's self-policing mechanism must be a named gate (`:851`, `:870-873`): **strict-xfail means XPASS = RED** (an accepted divergence accidentally fixed turns the suite red unless the registry entry is removed, `:16-26,59-60,78-80`); the native/fallback boundary is asserted by a **never-xfailed** `test_native_fallback_boundary` (`:372-403`); `num_predictions` divergences are pinned to **exact counts** (`assert_num_predictions_divergence`, `_conformance_helpers.py:220-243`). A gate table that says only "compare predictions/metrics" loses all three.

### 6.3 The missing gates (add before treating L17 as done or flipping default)

1. **Cross-engine `.n4a` round-trip parity** (B6) — legacy bundle → predict on dag-ml == legacy predict, within tol. Today: within-engine exactness + a weak "loads" check only.
2. **Cross-engine workspace-schema conformance** (B6) — same SQLite `user_version` / Parquet column contract on both engines. Today: contracts frozen, but not asserted *across* engines.
3. **methods-installed CI lane** (B10) — un-skip `test_n4m_ops`; make it a prerequisite for any `numerically portable` claim; expand to SavGol/Detrend/MSC/FirstDerivative.
4. **`.so`-freshness gate** (DG8) — `check_so_freshness.py` as a named cross-lane gate.
5. **`EXPECTED_FALLBACK == ∅` + native export covers the bridge cases** as a **HARD gate before the legacy-DROP** (B6/B7) — after the drop there is no fallback target.
6. **A single auditable command** gating every claimed surface (Codex-2 Finding 1/8) — Python dual-engine conformance (strict-xfail/skip/fallback/baseline-freshness accounting) + methods/sklearn + Studio non-mocked oracle-corpus run + `.n4a`/workspace cross-engine round-trips + the checked-in registry.

---

## 7. Decisions that must be made before implementation

**DEC-1 — Ratify-vs-re-plan.** *Question:* are `PRE-1`, `PRE-3`/`LOCK-PYREF`, and the built portions of L5/L6/L16/L17 ratified from landed code at `e41362b4`, or re-verified from zero? *Options:* (a) ratify with evidence + rescope lanes to "harden + extend"; (b) keep the greenfield framing. *Recommendation:* **(a).** Update `SYNC.md:4,36,38,47,48` off "not started"; record `PRE-1`/`PRE-3` SATISFIED with tag/commit + 8220/0 + 273/0; pivot Vague 0 to *importing* evidence. (Lens 4 DEC-1, Lens 2 G1.)

**DEC-2 — Which "controller" is the binding surface, and who owns the adapter?** *Options:* (a) dag-ml `ControllerManifest` is canonical + a mandatory `OperatorController → ControllerManifest` adapter + node-registry↔manifest reconciliation owner; (b) declare the Python ABC legacy-only. *Recommendation:* **(a)** — define the adapter as an early lock-adjacent task; manifests are the only cross-language object. Specify `transport`/`runtime_requirements`/`conformance_fixtures` as a versioned manifest extension or sidecar. (Lens 1 DEC-2, Lens 3 §3, Codex-1 Crit-2.)

**DEC-3 — Does `core` execute kernels, or only inspect?** *Options:* (a) remove `portable_run_subset`/`runPortable` from `CoreAggregate`, push execution to runtimes (core = inspect/validate/capability only); (b) accept core as a runtime and rename. *Recommendation:* **(a).** (Lens 1 DEC-3.)

**DEC-4 — Is n4m-in-dag-ml in V1 scope or post-V1?** *Options:* (a) V1 ships sklearn-only on the dag-ml engine (honest); (b) commit to wiring n4m via a host controller (net-new, needs a dag-ml/bridge-side task). *Recommendation:* **(a) for V1**, with (b) as an explicit post-V1 lane and §7.2 downgraded to ROADMAP. (Lens 1 DEC-4.)

**DEC-5 — Oracle identity + accepted-incompatibility registry.** *Question:* ratify the 3-tier oracle and pre-load the 13-entry registry as a precondition of signing LOCK-PYREF? *Recommendation:* **Yes** — accept that for `rep_to_*`, `best_X`, and `num_predictions` **dag-ml is the V1 truth, not legacy**; add `rng_nondeterministic` and `skip-unknown-semantics` as distinct dispositions. (Lens 2 DEC-PYREF-002/003/004, Codex-2 required-corrections 1/2.)

**DEC-6 — Legacy-DROP sequencing relative to the multimodal program.** *Question:* does the program assume `DEFAULT_ENGINE="dag-ml"` already flipped (post-drop) or interim-legacy-default (pre-drop)? *Options:* (a) pre-flip — run the whole refactor on legacy-default, flip at the end (matches ADR-17 "with/after the global refactoring to avoid double-churn"); (b) flip early. *Recommendation:* **(a)** — but make `LOCK-DROP` a first-class lane with the criterion in §5.3, and merge `feat/native-scoring` + the dag-ml-data lockstep release at the cutover. (Lens 2 DEC-DROP-001, Lens 4 DEC-2.)

**DEC-7 — Pre-drop native-coverage gate.** Make "`EXPECTED_FALLBACK == ∅` AND native `.n4a` export covers the bridge cases" a HARD gate before the drop (no fallback target after). *Recommendation:* **Yes.** (Lens 2 DEC-PYREF-005.)

**DEC-8 — Bundle/workspace cross-engine parity.** Add the missing cross-engine `.n4a` + workspace-schema tests; until they exist, mark bundle/workspace parity UNTESTED, not a passed gate. *Recommendation:* **Yes**, and make native-export-replaces-bridge a drop blocker. (Lens 2 DEC-BUNDLE-001, Codex-2 Finding 7.)

**DEC-9 — `LOCK-CAP` taxonomy provenance.** Derive from the existing controller `capabilities` enum + `rng_policy`/`fit_scope`/`artifact_policy`, or author fresh? *Recommendation:* **derive** (prevents a disjoint vocabulary). (Lens 1 DEC-6.)

**DEC-10 — Aggregation manifest vs existing conformance-pack pinning.** One pinning system or two-with-a-bridge? *Recommendation:* the aggregation manifest **consumes** each repo's conformance-pack hashes; do not re-pin. (Lens 1 DEC-7/P4.)

**DEC-11 — `nirs4all-core` name collision.** Pick distinct words for `dag-ml-core` (contract crate) vs `nirs4all-core` (aggregate) vs the throwaway integration clone (to be retired). *Recommendation:* qualify or rename; retire the clone worktree post-review. (Lens 1 DEC-1, Codex-1 High-3, Lens 4 DEC-5.)

**DEC-12 — Canonical UI primitive/token baseline + LOCK-RT as predecessor of runtime UI buckets + visual-baseline tool + node-registry↔manifest owner.** *Recommendation:* take Web's newer `data-slot` generation as the base (it must run in the constrained WASM target) and re-skin Studio; add LOCK-RT to LOCK-UI for runtime/results/export; pick Playwright `toHaveScreenshot` (Playwright already present) over resurrecting Storybook and own it as net-new infra **before** any extraction PR; assign the node-registry↔manifest reconciliation a `DEC-*` + owner. (Lens 3 DEC-1..7.)

**DEC-13 — lite→core reality; AOM placement; datasets canonical path; tools-vs-migrator; cluster RBAC priority.** *Recommendation:* decide whether core vendors 6 upstreams or stays a `libloading` registry (and whether datasets is in/out of the default aggregate — today out); resolve `nirs4all-aom` ⇄ `nirs4all.operators.models` before any methods/papers lane; decide datasets routes through io/formats (advertised) or keeps the direct-core path (built); state whether `nirs4all-tools` absorbs `migration.py`; make cluster RBAC (`CLU-002`) the named first gap. (Lens 4 DEC-3..8.)

---

## 8. Recommended doc corrections

Grouped per source doc; each is file:line → the exact correction.

### `PARALLEL_REFACTORING_SYNC.md`
- `:4` "Statut global: not started" → factually wrong; backend migration + parity oracle landed at `e41362b4`. Set to "in progress; backend + parity oracle landed, refactor framing pending."
- `:36` `PRE-1 = blocked / "Attendre la fin du chantier backend"` → `landed`, evidence `e41362b4`, `nirs4all/api/run.py` + `pipeline/engine.py:27-31`.
- `:38` `PRE-3 = blocked / "a verifier"` → mostly satisfied; evidence `nirs4all/tests/integration/parity/`, 8220/0 + 273/0.
- `:47` `LOCK-PYREF blocked/none` → ratify from the existing harness + import the 13-entry registry; signable in Vague 0.
- `:48` `LOCK-MIG` → note existing `nirs4all/pipeline/storage/migration.py` as prior art (B18).

### `PARALLEL_REFACTORING_ROADMAP.md`
- `:25-34` / `:31` (`PRE-1`) — strike "blocking prerequisite to open the program"; it is met. Add the interim-legacy-default posture + `DEFAULT_ENGINE` reference (B7/B21).
- `:33` / `:542-583` (`PRE-3` / `L17`) — re-point at `nirs4all/tests/integration/parity/` by name; re-scope `PYREF-002/003/004/006` from "build" to "adopt + extend"; add `PYREF-000` (import accepted-incompatibility registry, §6.2); add the named coverage gaps: `EXPECTED_FALLBACK`→native, `auto_transfer_preproc`/`fill_value`/`na_policy`, `avg`/`w_avg` OOF, cross-engine `.n4a`/workspace (B3/B4/B6/Lens 2 G2).
- `:54-57` — replace the absolute "memes splits, predictions, scores, artifacts et erreurs" with the 3-tier oracle + "sauf les incompatibilites enregistrees ou dag-ml fait autorite (`rep_to_*`, `best_X`, `num_predictions` winner-only) et les shapes RNG-nondeterministes non bit-reproductibles." Cite `test_conformance_dual_engine.py`.
- `:234-258` (`L5`, `DML-001..007`) — rescope from "build runtime/transport/predictions/lifecycle/parity" to "harden the in-tree `nirs4all/pipeline/dagml/` bridge + migrate `run_paths.py`/`detect.py` orchestration DOWN + widen `detect.py` native coverage"; add a native-vs-fallback coverage metric; make `L5` task = "drive `EXPECTED_FALLBACK` to ∅" (B5/T4/Lens 2 P2).
- `:260-280` (`L6`, esp. `DMD-003`) — the in-memory provider + 7-method C-ABI vtable already landed (`dag-ml-data` `04ecf3a`, `crates/dag-ml-data-provider/`); scope to multimodal `SampleRelationTable`/materialization + production providers only (B9).
- `:284-306` (`L7`) — the io→dag-ml-data emit already landed (`da24fb5`, `nirs4all-io-dagml`); fix the `README.md` "Phase 2 gated" vs `STATUS.md`/`PHASE2_GATE.md` "COMPLETE" contradiction; keep `DatasetSpec v2`/`DatasetPackage` as genuinely net-new (still `SCHEMA_VERSION=1`) (B9).
- `:467-473` (`PROV-001..004`) — rename to real APIs: `to_dataset_package`→`to_nirs4all`; `PipelineProvider.*`→`n4r.list/get/fetch/card`; `BenchmarkProvider`/`queue`/`evaluate` exist nowhere + Arena never runs compute (state the runner dependency on L5/L15); `inspect_bundle/methods_report/build_repro_page`→`read_bundle/build_bibliography/build`; flag the unifying provider layer as net-new (B12).
- `:486-507` (`L15`) — cluster is built + protocol-specified; revise `CLU-001` "spec"→"harden the existing `/v1` client"; "scheduler/load-balancer"→"pull-based lease queue + eligibility matcher"; `CLU-002` RBAC = the real gap; `CLU-004` fine-grained DAG depends on L5/L16 (B14).
- `:210-232` (`L4`/`CORE-002`) — lite is a scaffold/registry; "exposition directe" of 6 upstreams is net implementation work; datasets currently excluded from the default aggregate (B17).
- `:509-540` (`L16`) — add the `OperatorController → ControllerManifest` adapter task + node-registry↔manifest reconciliation owner BEFORE `CTRL-001`; reframe `CTRL-001` as "surface the EXISTING dag-ml schema" + note the 3 fields (`transport`/`runtime_requirements`/`conformance_fixtures`) are a versioned extension (B1/B8).
- `:585-646` (`L18`) — reconcile with existing `migration.py` (B18).
- `:693` — `LOCK-UI = UI-001 + UI-002 + LOCK-CAP` → add `+ LOCK-RT` for runtime/results/export; add canonical-primitive decision + net-new visual-baseline lane (B13/T7).
- `:851`, `:870-873` (gates/DoD) — add the strict-xfail/XPASS=RED mechanism, the never-xfailed native/fallback boundary, the exact-count `num_predictions` pin, the `.so`-freshness gate, and the "fallback pass ≠ native parity" rule (B3/DG8/DG9).
- **Add two lanes/gates:** `LOCK-DROP` / cutover (B7) and the dag-ml ↔ dag-ml-data lockstep byte-identity CI obligation (T8).

### `SYNTHESE_MULTIMODALE_NIRS4ALL.md`
- `:19, 67-84` (architecture: "lite = methods + dag-ml + dag-ml-data + io + formats") — as-realized, lite vendors only dag-ml + dag-ml-data (Rust) / lazy-proxies the rest (Python); datasets excluded from the default aggregate (B17).
- `:181-204, §6.1` — the optimistic "Reste 22-44 pw" must caveat that it excludes migrating the ~2.3k LOC Python orchestration (`run_paths.py`+`detect.py`) DOWN into dag-ml (the North Star requirement, part of the 86 pw line) AND that the parity oracle + JSONL transport already exist (so even the optimistic estimate over-counts L5/L17) (B5).

### `MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md`
- `:115-118` (LOCK-PYREF rule) + `:154-167` (comparison table) + `:196-197` — 3-tier amendment; the "explicitly declare a scoped, accepted incompatibility" must point to the registry of the 13 already-accepted items; add table rows for `num_predictions` (winner-only, exact-count-pinned), RNG-nondeterministic (no bit-parity), cross-engine `.n4a`/workspace (untested); scope `:196-197` to Tier 1 (B3/B4/B6).
- `:493` `CoreAggregate.portable_run_subset()` + `:39` "Execution ML: core = portable subset" + `:516` `runPortable` — remove execution from `core`; core = inspect/validate/capability only (B16/DEC-3).
- `:840-959` (§4ter) — add "Two/three controller objects today": dag-ml `ControllerManifest` (`controller.rs:115-138`) vs nirs4all `OperatorController` (`controllers/controller.py:14`) vs the engine router; state the binding surface is the manifest, reached via an adapter that does not yet exist; note `transport`/`runtime_requirements`/`conformance_fixtures` are NOT in the current Rust schema (B1/B8).
- `:962-981` (§6.3 / §4ter.5 sequence diagrams) — annotate that the NodeTask/NodeResult path (`node_runner.py`) currently covers a vertical slice (model-on-raw-features); branch/stacking/rep-fusion/augmentation/generator run in Python (`run_paths.py` 1282, `detect.py` 1004) and demote to legacy (`detect.py:275,323`) (B5).
- `:1608-1609` (§7.2 "Execution policy") — change "preprocessing via n4m"/"PLS/AOM via n4m" from present-tense ownership to "ROADMAP: not yet wired — n4m reachable only as a legacy-engine sklearn operator (`operators/methods/n4m_ops.py`); no dag-ml controller calls the n4m C ABI (`grep n4m dag-ml/crates` = empty)" (B2).
- `:1259` / `:1226-1264` (§5.5 cluster) — "Core should *probably* expose at least an optional cluster client" → the transport/contract is already specified and built; the client exists; re-frame as "core should wrap the existing `/v1` client" (B14).
- `:527-577, 745-799` (provider class diagrams) — the four provider interfaces are aspirational; annotate each with the real repo API + "core-side adapter = net-new" (B12).
- `:334, 430` (`DATASETS → IO`) — mark as target-state, not current (B20).
- `:349, 1765` (aom) — the `nirs4all.operators.models` duplication needs a decision lane (B19).
- `:1882-1883` (§10.2 taxonomy) — reconcile the contradiction: "organized by reusable product responsibility, not by where the component first appeared in Studio" vs the program premise "extract from Studio." State the taxonomy is a *target* re-organization; initial extraction is from Studio feature folders mapped INTO the taxonomy, not a 1:1 lift; the `controllers` bucket maps to zero existing folder (B13/T7).
- `:1925-1935` (§10.4 UI parity gates) — the visual baseline is net-new infra (no Storybook/Chromatic/`toHaveScreenshot` in Studio; `screenshot:'only-on-failure'`); pick the tool and own it before extraction (T7/DG6).

### `STUDIO_PRISTINE_HANDOFF.md`
- `:199-205` — the "very large dirty worktree / 1000+ untracked" caution is **stale**; Studio main (`2ccbf68`) is clean (`git status --short` = 0) and has absorbed the seams. Update status and record a `PRE-2` tag/commit (currently **none exists**) so `A2` has an immutable baseline.
- `:114-135` ("Native results and Inspector seams") — correct any "unmerged/dormant native-results reader" implication: `api/native_results_adapter.py` + `results_repository.py` + `score_maps` seams + `/api/runs/execution-backends` are **on main** (`feat/native-results-reader` = `91d5ba4` = merge-base, 0 ahead). The reader is present and consumed via nirs4all read-only, manifest-shaped — build on it, do not treat as future (D-1/B-Lens3-C5).
- `:164, 211, 218` — `:211` "Studio evidence … screenshots" implies a screenshot baseline; none exists. Add the coordinated item: when Studio points at dag-ml, the webapp WILL see changed `best_X` / `num_predictions` (per `CHANGELOG.md:44-58` + `NUM_PREDICTIONS_DIVERGENCE`); L12/L17 must own this contract migration, not defer it (DG7/Lens 2 G3).
- Ecosystem `CLAUDE.md` cross-cutting rule + briefs cite `nirs4all-studio/BACKEND_RULES.md`; actual path `nirs4all-studio/docs/_internals/BACKEND_RULES.md` — fix the link (B22).

### Ecosystem `CLAUDE.md`
- Several role lines now understate maturity: `nirs4all-cluster` (real beta, not in the index), `nirs4all-io` ("Rust planned phase 2" → Rust port complete, Phase-2 GREEN), `nirs4all-datasets` (Rust core + multi-lang bindings present). Refresh against the repos.

---

## 9. Ground-truth corrections to the brief

What the six reviews PROVED is already built/merged (re-verified by this review at the heads above). These correct the brief's framing where it was stale:

- **The dag-ml runtime backend is LANDED + selectable on `nirs4all` main `e41362b4`, not future work.** `nirs4all/api/run.py` dispatches to `run_via_dagml` when `engine="dag-ml"`/`N4A_ENGINE=dag-ml`; `pipeline/engine.py:27-31` `DEFAULT_ENGINE="legacy"`, `Engine = Literal["legacy","dag-ml","dual"]`; the Python bridge `nirs4all/pipeline/dagml/` = **7,847 LOC** (this review's `wc -l`); `ADR-17_LEGACY_DROP_HANDOFF.md` documents it "fully implemented, integrated, selectable," default legacy, drop deferred. `SYNC.md:4` "not started" is wrong. (All six reviews.)
- **The L17 / LOCK-PYREF parity oracle EXISTS and is green.** `nirs4all/tests/integration/parity/` ships `_oracle.py` (observe/compare/save_baseline), `test_conformance_dual_engine.py`, `_conformance_helpers.py` (`dual_engine_runner`, `assert_*`), the `cases_*.py` corpus, `baselines/`; `ADR-17` reports **8220 passed / 11 xfailed / 0 FAILED** on dag-ml default and **273/0** dual-conformance. L17's `PYREF-001..008` are mostly adopt-and-extend, not build. (Lens 2, Lens 4, Codex-2.)
- **The dag-ml-data provider spike LANDED (committed-local), not greenfield and not "held."** `dag-ml-data` `04ecf3a` "land the full P4 provider-contract spike … Codex SHIP"; crate `crates/dag-ml-data-provider/` with the full 7-method C-ABI vtable (ABI v2), zero `todo!/spike` markers; green gate 258 passed; NOT pushed. "lockstep" = byte-identical contract-mirroring with dag-ml, **not** a development hold. (Lens 4 C3, Codex-1 High-5.)
- **The `nirs4all-io → dag-ml-data` bridge LANDED.** `nirs4all-io` `da24fb5`; `nirs4all-io-dagml/src/lib.rs:398-603` maps `AssembledDataset → CoordinatorDataPlanEnvelope`; `PHASE2_GATE.md:10` GREEN; `nirs4all/pipeline/dagml/envelope.py` already emits the envelope/DataPlan/SampleRelationTable. (Lens 1 P3, Codex-1 High-5.)
- **The fine-grained cluster is BUILT (~3,977 LOC, 66 tests), with a versioned protocol.** Pydantic wire contract, FastAPI `/v1` server, `X-N4C-*` handshake + HTTP 426 on protocol-major mismatch, content-addressed SHA-256 store, atomic leasing + TTL reaper, capability routing, client SDK. Real gaps: RBAC (single static bearer token), fine-grained DAG, Studio adapter. (Lens 4 C5.)
- **The legacy-workspace migration tool EXISTS in-tree.** `nirs4all/pipeline/storage/migration.py` (27.3K; `migrate_arrays_to_parquet`, `migrate_duckdb_to_sqlite` "Will be removed in v1.0"). `L18`/`TOOL-004` re-creates it as if greenfield. (Lens 4 C7.)
- **The Studio native-results reader is ON MAIN, not unmerged.** `feat/native-results-reader` = `91d5ba4` = merge-base of `main`; `git rev-list --count feat/native-results-reader ^main` = **0**; main is **5 ahead**; `api/native_results_adapter.py` PRESENT on main (this review re-verified). Consumed via nirs4all read-only, manifest/legacy-shaped — not via runtime/ControllerManifest. Studio main worktree is **clean**. (Lens 3 C5, corrects the brief's "UNMERGED/dormant.")
- **Historical cutover context.** This bullet records a pre-core-cutover snapshot where `nirs4all-core` was still described as a redundant linked worktree. Do not use it as current topology: V1 now treats `nirs4all-core` as the canonical aggregate repository, while the full Python `nirs4all` package remains the production-held oracle until its explicit cutover.
- **n4m is NOT on the dag-ml execution path** (the one ground-truth the brief had right, re-confirmed): `grep -rn n4m dag-ml/crates` and `nirs4all/pipeline/dagml` return only build-artifact hashes, no source. methods is the only kernel home and is not plugged into the coordinator (B2/T3).
