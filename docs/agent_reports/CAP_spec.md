# CAP-SPEC report — LOCK-CAP capability / portability / unsupported vocabulary

**Lane:** L2 (Capabilities/conformance) · **Lock:** `LOCK-CAP` (in_progress) · **Decision:** `DEC-CAP-001` (accepted)
**Mode:** read-only audit. No code/test/sync-board edits. This file is the only write.
**Rule honored (DEC-CAP-001):** every capability/portability/unsupported token below is **DERIVED** from existing dag-ml artifacts. Anything not directly surfaced is tagged **`NET-NEW vs surfaced`**.

Verification method: direct `rg`/`sed`/`Read` against local heads (CodeGraph not relied on for facts). Heads per sync board pass 2: `dag-ml f58d7bf`, `nirs4all e41362b4`.

Cross-lane anchors (sync board `nirs4all-ecosystem/docs/PARALLEL_REFACTORING_SYNC.md`):
- `DEC-CAP-001` accepted — derive from controller `capabilities` + `rng_policy`/`fit_scope`/`artifact_policy`; no new vocab (line 90).
- `DEC-RT-001` accepted — runtime surface = `inspect/validate/plan/run/predict/replay/explain/export` referencing existing dag-ml contracts (line 98).
- `DEC-DESIGN-001` accepted (in part) — **core = inspect/validate/capability ONLY; `portable_run_subset`/`runPortable` REMOVED; execution lives in runtimes** (line 101). Portability here is therefore a *descriptor/classifier*, never a core executor.
- `DEC-CTRL-001` accepted — `ControllerManifest` is canonical; `transport`/`runtime_requirements`/`conformance_fixtures` are a *versioned extension* (line 104). CAP must not fork the manifest.
- Watchlist: "Capability vocabulary → L2" (line 127); "Bundle `.n4a` portability metadata → L2+L4+L5" (line 136). Consumers: `L9` methods "ledger parity portable subset" + `CON-001` (line 71); `L13` web "map subset browser et unsupported" (line 75).

**Key structural finding:** the four enums below are **declared but not yet consumed** anywhere in dag-ml beyond `ControllerManifest::validate()` and two helper methods. Repo-wide `rg` for `ControllerCapability|RngPolicy|ArtifactPolicy|ControllerFitScope` outside `controller.rs` returns **0 functional consumers** (only `lib.rs:10-11` `pub mod` re-exports and `controller_registry.rs` which round-trips YAML→the same type). LOCK-CAP's job is to **organize and surface** an existing-but-dormant contract, not to invent one.

---

## 1. Verified inventory — the four manifest enums

Source of truth: `dag-ml/crates/dag-ml-core/src/controller.rs`. Wire schema: `dag-ml/docs/contracts/controller_manifest.schema.json` (`$id …controller_manifest.v1.schema.json`, schema_version `1`, `controller.rs:12-14`). Rust↔schema parity is asserted by the test at `controller.rs:905-935`.

### 1a. `ControllerCapability` — exactly 19 values (`controller.rs:18-38`)

`#[serde(rename_all = "snake_case")]` → wire tokens match schema enum `controller_manifest.schema.json:149-171`.

| # | Rust variant | wire token | line |
|---|---|---|---|
| 1 | `Deterministic` | `deterministic` | controller.rs:19 |
| 2 | `ThreadSafe` | `thread_safe` | controller.rs:20 |
| 3 | `ProcessSafe` | `process_safe` | controller.rs:21 |
| 4 | `NeedsPythonGil` | `needs_python_gil` | controller.rs:22 |
| 5 | `EmitsPredictions` | `emits_predictions` | controller.rs:23 |
| 6 | `ConsumesOofPredictions` | `consumes_oof_predictions` | controller.rs:24 |
| 7 | `EmitsArtifacts` | `emits_artifacts` | controller.rs:25 |
| 8 | `Stateful` | `stateful` | controller.rs:26 |
| 9 | `EmitsRelation` | `emits_relation` | controller.rs:27 |
| 10 | `UsesCoreRng` | `uses_core_rng` | controller.rs:28 |
| 11 | `ShapeChanging` | `shape_changing` | controller.rs:29 |
| 12 | `GeneratesData` | `generates_data` | controller.rs:30 |
| 13 | `GeneratesModel` | `generates_model` | controller.rs:31 |
| 14 | `ExpandsVariants` | `expands_variants` | controller.rs:32 |
| 15 | `AggregatesPredictions` | `aggregates_predictions` | controller.rs:33 |
| 16 | `SupportsSampleWeights` | `supports_sample_weights` | controller.rs:34 |
| 17 | `SupportsRowResampling` | `supports_row_resampling` | controller.rs:35 |
| 18 | `SupportsBackendLossWeights` | `supports_backend_loss_weights` | controller.rs:36 |
| 19 | `SupportsMissingMasks` | `supports_missing_masks` | controller.rs:37 |

### 1b. `ControllerFitScope` — 4 values (`controller.rs:42-47` / schema:212-214)
`stateless` (43), `fold_train` (44), `full_train` (45), `inference_only` (46).

### 1c. `RngPolicy` — 4 values (`controller.rs:51-56` / schema:215-222)
`uses_core_seed` (52), `ignores_seed` (53), `externally_deterministic` (54), `nondeterministic` (55).

### 1d. `ArtifactPolicy` — 4 values (`controller.rs:60-65` / schema:223-225)
`serializable` (61), `host_only` (62), `content_addressed` (63), `replay_required` (64).

### 1e. Manifest cross-field invariants already enforced (`ControllerManifest::validate`, `controller.rs:141-224`)
These are the *existing* semantic couplings CAP-002/CAP-004 reuse verbatim:
- `nondeterministic` RNG ∧ `deterministic` capability → **reject** (167-176).
- `inference_only` ∧ (supports `FIT_CV`|`REFIT`) → **reject** (177-185).
- supports `FIT_CV` ∧ fit_scope ∈ {`full_train`,`inference_only`} → **reject** (186-196).
- prediction output port without `emits_predictions` → **reject** (197-209).
- artifact output port without `emits_artifacts` → **reject** (210-222).
- Helpers: `supports_parallel_invocation` = `thread_safe ∨ process_safe` (230-236); `capabilities_support_fit_influence` maps `FitInfluencePolicy`→required capability (257-280).

### 1f. Adjacent existing vocab (surfaced, not part of the 4 core enums)
- `Phase` (7): `Compile,Plan,FitCv,Select,Refit,Predict,Explain` (`phase.rs:5-13`; wire `COMPILE…EXPLAIN` schema:115-117). `is_training` = `FitCv|Refit` (`phase.rs:16-17`).
- `NodeKind` (20): schema:91-114 (`transform…chart`).
- `FitInfluencePolicy` (7): `policy.rs:78-87` (`auto,uniform_rows,equal_sample_influence,resample_equalized,backend_loss_weight,scorer_only,strict_weight_support`); schema:258-268. Lives under `model_input_spec`, not top-level manifest.
- **Process-adapter capabilities (a SECOND, distinct capability namespace):** `process_adapter_description.schema.json` — `protocol` const `dag-ml-process-adapter` (18), `supported_modes` ∈ {`one_shot`,`jsonl`} (29), free-form `capabilities` strings requiring `node_task_json_v1` + `node_result_json_v1` (32-49). This is the **transport/runtime** capability layer; it is NOT the `ControllerCapability` enum. Keep the two namespaces explicitly separate.
- **Python host capability surface (thin):** `nirs4all/nirs4all/controllers/controller.py` `OperatorController` — `priority` (16), `matches` (20, abstract), `use_multi_source` (26), `supports_prediction_mode` (31), `supports_step_cache` (42), `execute` (54). The `OperatorController→ControllerManifest` adapter is owned by **L16/`DEC-CTRL-001`** (B1, not yet built — sync board line 78, 233); CAP only specifies the *target* vocabulary, not the adapter.

---

## 2. CAP-001 — minimal capability/verb set mapped to existing artifacts

The 10 requested tokens split into **surfaced runtime verbs** (8, = `DEC-RT-001`) and **2 capability-classification outputs CAP owns**. Per `DEC-DESIGN-001`, only `inspect`/`validate`/`portable_level`/`unsupported` are *core*; `plan…export` are *runtime* verbs the capability vocabulary feeds.

| Verb/output | Side | Backed by existing artifact (file:line) | Net-new? |
|---|---|---|---|
| `inspect` | core | `ControllerRegistry::get`/`manifests` (controller.rs:305,309); manifest fields §1; example ledger `examples/controller_manifests.json` | surfaced |
| `validate` | core | `ControllerManifest::validate` (controller.rs:141); CLI `validate-controllers-yaml` (parity_oracle.v1.json:160), `validate-graph`/`validate-bundle` (CLAUDE.md:53; parity_oracle:203) | surfaced |
| `plan` | runtime | `ControllerRegistry::resolve_for_node` (controller.rs:313); `execution_plan.schema.json`; `Phase::Plan` (phase.rs:7) | surfaced |
| `run` | runtime | `Phase::FitCv/Refit` (phase.rs:8,10); `node_task`/`node_result` schemas (runtime flow, dag-ml/CLAUDE.md:107-118). *Core never runs (DEC-DESIGN-001).* | surfaced |
| `predict` | runtime | `Phase::Predict` (phase.rs:11); `prediction_cache_*_metadata.schema.json` | surfaced |
| `replay` | runtime | `bundle` validation; CLI `run-process-replay`/`run-mock-replay` (dag-ml/CLAUDE.md:74; parity_oracle:208) | surfaced |
| `explain` | runtime | `Phase::Explain` (phase.rs:12); `examples/controller_manifests_explain.json`; `research_provenance_package_profile.v1.json` | surfaced |
| `export` | runtime | CLI `export-research-provenance` (dag-ml/CLAUDE.md:74); `openlineage_dagml_facets.schema.json`; `.n4a` bundle (watchlist line 136) | surfaced |
| `portable_level` | core (classifier) | DERIVED from `rng_policy`+`artifact_policy`+`capabilities`+`fit_scope` (§3). The *ladder label* is **NET-NEW**; all inputs surfaced. | **NET-NEW (derived)** |
| `unsupported` | core (diagnostic) | DERIVED from `resolve_for_node` refusals (controller.rs:316,322,346,354) + `validate` refusals (§1e). The *normalized envelope* is **NET-NEW**; cause set surfaced. | **NET-NEW (derived)** |

`inspect`/`validate`/`plan`/`run`/`predict`/`replay`/`explain`/`export` are byte-for-byte the `DEC-RT-001` surface (sync board line 98). CAP adds only the two classification outputs, both derived.

---

## 3. CAP-002 — portability taxonomy (DERIVED predicates, not a stored field)

Per `DEC-DESIGN-001` portability is a **read-only classifier** over surfaced fields — no `portable_run_subset` is reintroduced (confirmed removed: repo-wide `rg portable_run_subset|runPortable` = 0 hits). The six requested levels are defined as predicates over existing enum values; the **ladder packaging is `NET-NEW vs surfaced`**, every predicate input is surfaced.

| Level (requested) | Predicate over EXISTING fields | Surfaced inputs (file:line) |
|---|---|---|
| `non_portable` / `unsupported` | No manifest resolves for the operator in the target runtime's registry, **or** required host capability absent in target runtime. | `resolve_for_node` "no controller registered"/"ambiguous" (controller.rs:346,354); `needs_python_gil` (controller.rs:22) |
| `host_specific` | `artifact_policy == host_only` **∨** `needs_python_gil ∈ capabilities`. Artifact/exec bound to one host. | controller.rs:62, 22 |
| `contract_portable` | Manifest validates against schema **and** all cross-ABI payloads are identity/descriptor/fingerprint only (the "portable shape"). Execution may still be host-bound. | schema validation (§1e); ownership table (dag-ml/CLAUDE.md:122-133); README "JSON Schema documents the portable shape" (docs/contracts/README.md:42-44) |
| `numerically_portable` | `rng_policy ∈ {uses_core_seed, externally_deterministic}` **∧** `deterministic ∈ capabilities` **∧** a `tolerance_profile` covers the metric. Predictions reproduce within tolerance across runtimes. | controller.rs:52,54,19; `parity_oracle.v1.json:13-28` (regression/classification tolerance profiles) |
| `artifact_portable` | `artifact_policy ∈ {serializable, content_addressed}` (artifact crosses runtimes without refit). `replay_required` = *conditional* (portable only with replay evidence); `host_only` = excluded. | controller.rs:61,63,64,62 |
| `full` | `numerically_portable ∧ artifact_portable ∧ ¬host_specific ∧` a parity-oracle case proves it across all required runtimes. | conjunction of the above + `parity_oracle.v1.json:256-262` required cases |

Notes:
- `fit_scope` modulates the ladder: `stateless`/`inference_only` need no artifact transfer (artifact-portability is vacuous/trivial); `fold_train`/`full_train` make `artifact_portable` load-bearing (controller.rs:43-46).
- `ignores_seed` and `nondeterministic` (controller.rs:53,55) **cap** a node at `contract_portable` (cannot reach `numerically_portable`) — consistent with the existing reject rule (controller.rs:167-176) and `DEC-PYREF-002`'s "never mask RNG by tolerance" (sync board line 93).

---

## 4. CAP-003 — ledger of operators × profiles × runtimes

The ledger is a **JOIN of three EXISTING tables** (packaging = `NET-NEW vs surfaced`; every row/column surfaced):

1. **Operators** = the controller registry. Type: `ControllerRegistry { manifests: BTreeMap<ControllerId, ControllerManifest> }` (controller.rs:282-285). Concrete on-disk ledgers already exist: `examples/controller_manifests.json` (JSON array of manifests), `examples/controller_manifests_alias_registry.json`, `examples/controller_manifests_explain.json`, and per-vendor `examples/controllers/{sklearn_production,prospectr,mdatools}.controller.{json,yaml}`. YAML→same Rust type via `controller_registry.rs` (authoring-only; JSON is the wire contract).
2. **Profiles** = the per-manifest policy tuple `(capabilities, rng_policy, fit_scope, artifact_policy, supported_phases)` (controller.rs:124,132,135-137) **+** the numeric `tolerance_profiles` (`parity_oracle.v1.json:13-28`, ids `regression.default`/`classification.default`). Concrete example tuple: `controller:sklearn.production` = caps{deterministic,thread_safe,process_safe,uses_core_rng,emits_predictions,consumes_oof_predictions,emits_artifacts,stateful}, fit_scope `fold_train`, rng `uses_core_seed`, artifact `serializable` (`examples/controllers/sklearn_production.controller.json:33-103`).
3. **Runtimes** = DERIVED from the parity-oracle gate targets + the C-ABI section (no runtime enum exists yet — this naming is `NET-NEW vs surfaced`):
   - `native` (Rust/C-ABI): `conformance_pack.v1.json:253-306` (`c_abi` ABI versions + required symbols); CLI gates `cargo …` (parity_oracle:155,160).
   - `python_wheel`: `parity_oracle.v1.json:77,240` (`smoke_python_*`); capability `needs_python_gil` marks python-bound nodes (controller.rs:22).
   - `browser_wasm`: `parity_oracle.v1.json:72,119` (`smoke_wasm_*`).
   - `out_of_process` (transport, not a target): `process_adapter_description.schema.json` (modes `one_shot`/`jsonl`).
   Runtime affinity is read from capabilities: `process_safe`/`thread_safe` (parallelizable), `needs_python_gil` (python-only) — controller.rs:20-22.

Ledger row shape (proposed, additive): `{ controller_id, operator_kind, profile_tuple, per_runtime: { <runtime>: portable_level | unsupported } }`. It **references** registry + parity-oracle ids; it stores no model bytes and re-pins no hash (consistent with `DEC-REL-001` "consume conformance hashes, don't re-pin", sync board line 96).

---

## 5. CAP-004 — normalized `unsupported` diagnostics (cause + mitigation)

Surface the existing refusal strings as a stable `{cause_code, mitigation}` envelope (envelope = `NET-NEW vs surfaced`; every cause is an existing error). Proposed `cause_code`s map 1:1 to current errors:

| `cause_code` (proposed) | Existing source error (file:line) | Mitigation (derived from the error's own remedy) |
|---|---|---|
| `no_controller_for_kind` | "no controller registered for node … kind …" (controller.rs:346-349) | Register a manifest for that `operator_kind`, or load the runtime that provides it. |
| `ambiguous_controller` | "ambiguous controllers … set metadata.controller_id" (controller.rs:354-357) | Set `metadata.controller_id` (the error's own instruction) or raise `priority`. |
| `unknown_requested_controller` | "requested unknown controller `…`" (controller.rs:316-320) | Fix `metadata.controller_id` or install the controller. |
| `kind_controller_mismatch` | "kind … incompatible with controller … kind …" (controller.rs:322-326) | Align node `kind` with the manifest `operator_kind`. |
| `cross_kind_alias` | "minimal operator alias matches controllers with different node kinds" (controller.rs:382-388) | Use explicit DSL syntax instead of a bare alias. |
| `rng_determinism_conflict` | "cannot be deterministic with nondeterministic RNG" (controller.rs:172-176) | Drop `deterministic` or change `rng_policy`. → caps at `contract_portable` (§3). |
| `inference_only_trains` | "inference_only but supports training phases" (controller.rs:181-185) | Remove `FIT_CV`/`REFIT` or change `fit_scope`. |
| `fit_scope_phase_mismatch` | "supports FIT_CV but has fit_scope …" (controller.rs:192-196) | Set `fit_scope = fold_train`. |
| `prediction_capability_missing` | "prediction output ports but lacks emits_predictions" (controller.rs:205-209) | Add `emits_predictions`. |
| `artifact_capability_missing` | "artifact output ports but lacks emits_artifacts" (controller.rs:218-222) | Add `emits_artifacts`. |

Runtime-level `unsupported` (for `L13` browser subset / `L9` portable subset) is the §3 `non_portable` predicate evaluated against a target runtime row in §4 — same cause vocabulary, no new strings.

---

## 6. CON-001 — cross-runtime conformance skeleton (REUSE, do not duplicate)

`parity_oracle.v1.json` **already is** the cross-runtime pack; CON-001 = a thin view that points at it. Do not fork hashes.

Existing reusable structure:
- `status: producer_handoff`; `consumer_ledger → nirs4all/docs/compatibility.md`, `required_before_bridge: true` (parity_oracle:4-9).
- `tolerance_profiles` (13-28) → feed §3 `numerically_portable`.
- 5 `cases`, each with `ledger_topics` / `fixtures` (cross-repo) / `gates` (`repo`+`command`+`proves`) / `invariants`; `required_case_ids` (256-262). Cases already span runtimes: `nirs4all_lite_browser_compile_plan` (wasm+python, 31-87), `controller_registry_selector_parity` (native, 130-169), `python_wheel_facade_integration` (219-254), plus `repetition_group_leakage_refusal` (89) and `branch_merge_oof_refit_replay` (171).
- `conformance_pack.v1.json`: contract/fixture digests (4-61), `scenarios` with `polarity` positive/negative (62-251), `c_abi` ABI versions (253-306), `cross_repo_conformance.required_when_sibling_checkout_present` (307-314).

Proposed CON-001 skeleton (additive, references-only):
```
conformance_cross_runtime.v1 = {
  reuses: { parity_oracle: "parity_oracle.v1.json", conformance_pack: "conformance_pack.v1.json" },
  runtimes: ["native", "python_wheel", "browser_wasm"],        # NET-NEW label set, derived from §4 gates
  matrix: [ { case_id: <from parity_oracle.required_case_ids>,  # reference, no copy
              per_runtime: { native|python_wheel|browser_wasm: pass|unsupported },
              portable_level: <§3>,                              # derived, not stored upstream
              tolerance_profile_id: <from parity_oracle.tolerance_profiles> } ]
}
```
The matrix stores only `case_id`/profile-id references + the derived `portable_level`/`unsupported` verdict. It adds **no** digests and **no** fixtures (respects `DEC-REL-001` + `LOCK-LOCKSTEP`). The `runtimes` list and `per_runtime` matrix are `NET-NEW vs surfaced` packaging.

**Gap (not net-new design, a missing file):** `nirs4all/docs/compatibility.md` — the parity-oracle `consumer_ledger` with `required_before_bridge: true` — **does not exist** (`ls` → not found). CON-001 cannot close until L17/nirs4all creates it. Flagged for A0/L17.

---

## 7. Proposed `LOCK-CAP` content (for A0 to sign)

```
LOCK-CAP (capability / portability / unsupported vocabulary) — derived from dag-ml, no new vocab.

C1. Capability enum = ControllerCapability (19 values, controller.rs:18-38 / schema:149-171),
    VERBATIM. No additions, removals, or renames under this lock.
C2. Policy enums = ControllerFitScope (4), RngPolicy (4), ArtifactPolicy (4) (controller.rs:42-65),
    VERBATIM. FitInfluencePolicy + process-adapter capabilities are SEPARATE namespaces,
    referenced, never merged into the manifest enum.
C3. Runtime verb surface = inspect, validate, plan, run, predict, replay, explain, export
    (= DEC-RT-001). CAP adds exactly two derived capability outputs: portable_level, unsupported.
    Per DEC-DESIGN-001, only inspect/validate/portable_level/unsupported are CORE; the rest are RUNTIME.
C4. portable_level is a READ-ONLY CLASSIFIER (6 levels: non_portable, host_specific, contract_portable,
    numerically_portable, artifact_portable, full), computed from C1+C2 by the §3 predicates.
    It is NOT a stored field and MUST NOT reintroduce portable_run_subset/runPortable (DEC-DESIGN-001).
C5. unsupported is a normalized {cause_code, mitigation} envelope whose cause set is exactly the
    existing resolve_for_node + validate() refusals (CAP-004 table). No new failure semantics.
C6. The operator×profile×runtime ledger and the cross-runtime conformance matrix (CON-001) are
    REFERENCE views over ControllerRegistry + parity_oracle.v1.json + conformance_pack.v1.json.
    They pin no new hashes and copy no fixtures (DEC-REL-001, LOCK-LOCKSTEP).
C7. NET-NEW (derived) items requiring explicit sign-off: the 6-level ladder labels (C4);
    portable_level + unsupported as outputs (C3); the {cause_code, mitigation} envelope (C5);
    the runtime label set {native, python_wheel, browser_wasm}; the ledger/matrix packaging (C6).
C8. Manifest field additions for transport/runtime are OUT OF SCOPE for LOCK-CAP and remain with
    DEC-CTRL-001 (transport/runtime_requirements/conformance_fixtures = versioned extension).
```

---

## 8. Open questions + gates

**Open questions (for A0 / maintainer):**
1. Sign-off on the C7 NET-NEW items — all derived, but they are net-new *labels/packaging*. Approve as-is or trim?
2. Where does `portable_level` get computed and cached — core inspect API output only (DEC-DESIGN-001), or also stamped into `.n4a` portability metadata (watchlist line 136, shared L2+L4+L5)?
3. Runtime label set: is `out_of_process` (process-adapter) a 4th runtime or only a transport modifier of the other three? (§4 treats it as transport.)
4. `nirs4all/docs/compatibility.md` (parity-oracle consumer ledger, `required_before_bridge`) is **absent** — who creates it, L2 or L17? Blocks CON-001 closure.
5. Coordinate with L16/`DEC-CTRL-001`: the `OperatorController→ControllerManifest` adapter is the *producer* of these capabilities from Python. CAP fixes the target vocabulary; L16 must emit it. Confirm the seam.

**Gates to run (none run here — read-only):**
- `cargo test -p dag-ml-core controller` — exercises the 19-cap enum + cross-field validate rules (controller.rs:633-935).
- `cargo test -p dag-ml-cli yaml_and_json_controller_manifests_match` (parity_oracle:155).
- `cargo run -p dag-ml-cli -- validate-controllers-yaml --dir examples/controllers` (parity_oracle:160).
- `python3 scripts/validate_contracts.py` with `DAG_ML_DATA_REPO` set — conformance/parity-oracle digest drift (dag-ml/CLAUDE.md:55).
- The 5 `required_case_ids` parity-oracle gates (parity_oracle:256-262) — the cross-runtime proof CON-001 references.

**Worklog line (for A0 to paste into the sync board — I did not edit it):**
`2026-06-30 | CAP-SPEC/L2 | review | LOCK-CAP spec: derived 19-cap + fit_scope/rng/artifact enums, 6-level portable_level classifier, {cause,mitigation} unsupported set, ledger+CON-001 as reference views over parity_oracle/conformance_pack. No code/sync edits. | read-only; gates listed not run | NET-NEW(derived): ladder labels, portable_level/unsupported outputs, runtime label set, ledger/matrix packaging; gap: nirs4all/docs/compatibility.md absent.`
