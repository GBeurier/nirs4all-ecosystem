# IMP-L16 — `OperatorController → ControllerManifest` adapter foundation (dag-ml)

**Agent:** IMP-L16 (implementation) · **Lane:** L16 Controllers/bindings · **Decision:** `DEC-CTRL-001` (accepted)
**Date:** 2026-06-30 · **Mode:** implementation, single dag-ml worktree
**Worktree:** `/home/delete/nirs4all/_worktrees/L16-dagml-controllers` · **Branch:** `refactor/L16-controller-manifests`
**Status:** landed locally, gate green, ready for review. Narrow first slice of the B1 adapter.

> Scope honored: only the dag-ml worktree was touched. No sibling repo code, no
> sync board edit, no other agent's work reverted. This report file is the only
> write outside the worktree (as instructed).

---

## 1. What was built

A native, tested **manifest-derivation API** in `dag-ml-core` — the dag-ml side of
the `OperatorController → ControllerManifest` adapter (the "B1" adapter that
`DEC-CTRL-001` requires *before* `CTRL-001`, and that A0's pass-2 re-audit
confirmed absent: *"B1: pas d'adapter `OperatorController → ControllerManifest`"*).

Instead of every host hand-authoring static manifest literals (the nirs4all
bridge ships 5 in `dagml_bridge.controller_manifests()`; Studio rebuilds a
*parallel* node registry by walking importable Python classes), a host now
declares a thin descriptor and dag-ml **mechanically derives a validated
`ControllerManifest`**. The per-kind facts that are actually deterministic are
encoded once, natively, so every binding (Python / R / WASM / cluster) gets the
same answer for free instead of re-deriving — or drifting from — them. This is
the concrete first step of the North-Star "migrate coordination down into dag-ml"
mandate for the controller surface.

New public surface (all in `crates/dag-ml-core/src/controller_adapter.rs`,
re-exported from the crate root):

| Item | Kind | Role |
|---|---|---|
| `HostControllerSpec` | struct (serde) | Host-side description of one `OperatorController`: id, version, `operator_kind`, plus optional priority / added capabilities / selectors / policies / port overrides / `data_requirements`. |
| `HostControllerSpec::new(id, version, kind)` | ctor | Spec with policy/priority defaults and no overrides. |
| `HostControllerSpec::derive() -> Result<ControllerManifest>` | method | Compose kind template + overrides, then **run `ControllerManifest::validate()`** and return the validated manifest (or the validation error). |
| `manifest_kind_template(&NodeKind) -> ManifestKindTemplate` | fn | The deterministic per-kind defaults (phases, fit scope, capabilities, ports). Public so Studio/runtime can introspect "what would this kind default to". |
| `ManifestKindTemplate` | struct | The template value object. |
| `derive_host_controller_registry(&[HostControllerSpec]) -> Result<ControllerRegistry>` | fn | One call: derive every spec and register it into a fresh `ControllerRegistry` — the replacement for a hardcoded static node registry. |
| `HOST_CONTROLLER_TABULAR_REPRESENTATION` | const | The coarse `"tabular_numeric"` default stamped on data/target ports (the L6/L7-blocked placeholder the bridge already uses). |

---

## 2. Why it is shaped this way (alignment with the accepted specs)

The design follows the **two-layer projection** that `A4_A4-controllers.md` §2.1
and `DEC-CTRL-002/003` establish, and it deliberately reuses the existing
vocabulary that `CAP_spec.md` froze under `LOCK-CAP` (no parallel vocabulary):

- **Layer 1 (keyword / DSL position → `operator_kind`)** is a *compile-time
  lowering rule* owned by the DSL compiler (`DEC-CTRL-003`: "DSL lowering
  authoritative"). By the time a manifest is derived the host already knows the
  `NodeKind`, so the kind is an **input** to the descriptor — `HostControllerSpec`
  takes `operator_kind: NodeKind` directly (no invented "role" enum). dag-ml then
  fills the rest mechanically via `manifest_kind_template`.
- **Layer 2 (operator class / type → `operator_selectors`)** is supplied
  verbatim by the host as existing `OperatorSelector`s. This is how a
  *specialization* manifest out-ranks a generic kind-level catch-all (the
  binding-extension path, A4 §2.7 ex.3).
- **No new manifest/capability vocabulary.** A derived manifest is an ordinary
  `ControllerManifest` over the frozen `ControllerCapability` / `ControllerFitScope`
  / `RngPolicy` / `ArtifactPolicy` enums. `added_capabilities` only *selects from*
  the existing enum (e.g. `needs_python_gil` for a DL model). The output is the
  schema-governed wire contract (`controller_manifest.schema.json`); the
  descriptor is an ergonomic constructor, not a second contract — so there is no
  new schema to keep in lockstep (`validate_contracts.py` unaffected).
- **Validation is never bypassed.** `derive()` calls the existing
  `ControllerManifest::validate()`, so the API cannot emit a manifest the
  registry would reject (e.g. a prediction port without `emits_predictions`, an
  `inference_only` controller that trains, a nondeterministic-but-deterministic
  combo). The `CAP_spec.md` cross-field invariants (§1e) are enforced for free.
- **Per `DEC-DESIGN-001`** (core = inspect/validate/capability only), this is a
  *derivation/validation* facility, not an executor. It produces and validates
  manifests; it runs nothing.

This is the seam `CAP_spec.md` open-question #5 asked L16 to confirm: *"the
`OperatorController→ControllerManifest` adapter is the producer of these
capabilities from Python. CAP fixes the target vocabulary; L16 must emit it."*
`HostControllerSpec` is that producer's native core.

---

## 3. Real controller mappings (the parity contract)

The four generic kind-level catch-alls reproduce the nirs4all bridge's
hand-authored manifests **field-for-field**, proving the bridge can stop
hand-writing them and call `derive()` instead:

| Bridge manifest (`dagml_bridge.py:1026-1127`) | Reproduced by | Verified fields |
|---|---|---|
| `controller:nirs4all.transform` | `HostControllerSpec::new(id, v, Transform)` | phases, caps `{deterministic, thread_safe, process_safe, uses_core_rng}`, ports `x→x_out` (data, tabular_numeric), fold_train, uses_core_seed, serializable |
| `controller:nirs4all.y_transform` | `…, YTransform` | same caps, ports `y→y_out` (target) |
| `controller:nirs4all.model` | `…, Model` | + `{emits_predictions, emits_artifacts, stateful}`, ports `x →[y_hat(pred), model(artifact)]` |
| `controller:nirs4all.merge_concat` | `…, PredictionJoin` | caps `{deterministic, thread_safe, process_safe, consumes_oof_predictions, emits_predictions}` (no `uses_core_rng`), ports `oof[many]→oof[one]` |
| `controller:nirs4all.meta_model` | `Model` + `added_capabilities{consumes_oof}` + `input_ports` override `oof[many]` + `refs` selector | the specialization pattern (port override + extra cap + selector) |

Plus a **sixth, forward-looking** mapping — `controller:methods.pls` (`aliases:
["PLSRegression","PLS"]`, kind `model`) — exercised through
`derive_host_controller_registry` + `resolve_for_node` to prove the selector
specialization out-ranks the generic model controller for `PLSRegression` while a
bare `Ridge` still falls through to the generic one (A4 §2.7 ex.3, the
"add idiomatic methods without forking dag-ml" path).

---

## 4. Files changed

| File | Change | Lines |
|---|---|---|
| `crates/dag-ml-core/src/controller_adapter.rs` | **new** module: API + 11 unit tests | +~620 |
| `crates/dag-ml-core/src/lib.rs` | `pub mod controller_adapter;` + `pub use controller_adapter::*;` | +2 |

Nothing else in the working tree is modified (`git status` = 1 M + 1 ??).

---

## 5. Tests (all in-module, `#[cfg(test)]`)

11 new tests, all passing:

1. `transform_template_matches_bridge_manifest` — full field-for-field parity.
2. `y_transform_template_targets_y_ports`
3. `model_template_emits_prediction_and_artifact_ports`
4. `prediction_join_template_matches_merge_concat`
5. `meta_model_specialization_overrides_ports_and_caps` — port override + added cap + selector.
6. `selector_specialization_outranks_generic_in_registry` — registry resolution (PLS vs Ridge vs generic).
7. `derive_propagates_validation_failure_for_empty_version` — validate() error surfaced.
8. `derive_rejects_override_that_violates_capability_invariant` — prediction port on a transform → "lacks emits_predictions".
9. `generic_template_for_unmapped_kind_validates` — unmapped kind (`Tag`) still derives a valid generic manifest.
10. `host_controller_spec_round_trips_through_json` — serde round-trip + identical derivation (the cross-language wire path).
11. `minimal_json_descriptor_applies_defaults` — 3 required fields, policies/priority/ports defaulted.

---

## 6. Gate run (the dag-ml green gate)

| Step | Command | Result |
|---|---|---|
| fmt | `cargo fmt --all --check` | ✅ pass |
| lint | `cargo clippy --workspace --all-targets -- -D warnings` | ✅ "No issues found" |
| test | `cargo test --workspace` | ✅ **548 passed, 2 ignored** (13 suites) |
| CLI smoke | `cargo run -p dag-ml-cli -- validate-graph examples/minimal_graph.json` | ✅ "valid graph" |
| contracts | `python3 scripts/validate_contracts.py` | ✅ "validated dag-ml contract" |
| .so freshness | `python3 scripts/check_so_freshness.py` | ✅ pass **(uncommitted — see blocker B-L16-1)** |

Targeted: `cargo test -p dag-ml-core controller_adapter` → 11 passed.

---

## 7. Blockers & review readiness

**Review readiness: ready.** The change is additive, isolated to `dag-ml-core`,
fully tested, and passes the full green gate. No existing behavior changes; no
contract/schema touched.

Notes / follow-ups (none block this slice landing, but the reviewer should know):

- **B-L16-1 (commit-time `.so` freshness).** `check_so_freshness.py` compares
  *git commit timestamps* and skips untracked files, so it passes now. Once the
  `lib.rs` edit is **committed**, the tracked `_dag_ml.abi3.so` will predate the
  newest Rust commit and the guard will fail until the `.so` is rebuilt and
  committed (standard maturin step in this repo). The new module changes **no
  PyO3-exposed surface**, so the rebuild is only to satisfy the guard — I did not
  rebuild the binary (it would be a no-op binding-wise and is outside this slice).
  *Action for the landing commit:* rebuild + commit `_dag_ml.abi3.so` alongside.
- **Binding wiring is the explicit next step (not done here, by design).** The
  core API exists but is not yet surfaced through PyO3 (`dag-ml-py`), the C ABI
  (`dag-ml-capi`), the CLI (`dag-ml-cli`), or WASM. To actually let the nirs4all
  bridge and Studio consume it: (a) expose `derive`/`derive_host_controller_registry`
  (or accept `HostControllerSpec[]` JSON) through PyO3; (b) have
  `dagml_bridge.controller_manifests()` call it instead of the 5 literals;
  (c) back Studio's planned `GET /api/operators/manifests` (A4 §4.3) with the
  derived registry. These are separate, mechanical lanes gated on `LOCK-RT` for
  the route shape.
- **Layer-1 lowering (keyword → `NodeKind`) stays host-side for now.** This slice
  takes `operator_kind` as an input (correct per `DEC-CTRL-003`). Migrating the
  keyword→kind table (A4 §2.3) natively into the DSL compiler is a separate,
  larger surface and was left untouched to keep scope narrow.
- **`data_requirements` ports stay coarse (`tabular_numeric`)** — blocked on the
  dag-ml-data representation IDs (`B-CTRL-2` / `B-014`, lanes L6/L7), exactly as
  the bridge is today. The API already accepts a `data_requirements` JSON
  override and validates it as a `ModelInputSpec` when present, so it is ready to
  carry richer reps the moment the registry is published.
- **No new `ControllerRole` vocabulary** was introduced (kept `NodeKind` as the
  input), so `LOCK-CAP` is not touched and there is nothing new for A0 to sign on
  the capability side.

---

## 8. Suggested sync-board worklog line (for A0 — I did not edit the board)

`2026-06-30 | IMP-L16 | landed | dag-ml-core: new controller_adapter module — HostControllerSpec → derive() → validated ControllerManifest (the B1 adapter's native core). manifest_kind_template gives per-NodeKind defaults; 4 generic kind catch-alls reproduce dagml_bridge.controller_manifests() field-for-field; meta_model + methods.pls specializations covered; derive_host_controller_registry builds a resolvable ControllerRegistry. Reuses existing enums/validate(); no new vocabulary/schema. | gate green: fmt+clippy(-D warnings)+test(548 passed)+validate-graph+validate_contracts; 11 new tests. | Next: surface via PyO3/CLI so dagml_bridge + Studio /api/operators/manifests consume it (gated LOCK-RT); rebuild+commit .so on landing (B-L16-1).`

---

## 9. Evidence (heads, files read)

- dag-ml worktree `refactor/L16-controller-manifests`; core contract
  `crates/dag-ml-core/src/{controller.rs, controller_registry.rs, graph.rs,
  phase.rs, ids.rs, lib.rs}`; CLI `crates/dag-ml-cli/src/main.rs`;
  `scripts/{check_so_freshness.py, validate_contracts.py}`.
- de-facto adapter (read-only, sibling): `nirs4all/nirs4all/pipeline/dagml_bridge.py::controller_manifests()` (lines 1008-1127).
- specs: `docs/agent_reports/{A4_A4-controllers.md, CAP_spec.md, RT_spec.md}`;
  `docs/PARALLEL_REFACTORING_SYNC.md` (L16 row line 78, `DEC-CTRL-001` line 104, B1 line 271).
