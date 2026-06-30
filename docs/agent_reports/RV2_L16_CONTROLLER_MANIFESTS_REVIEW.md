# RV2 — Review of IMP-L16 `OperatorController → ControllerManifest` adapter foundation

**Reviewer:** RV2 (read-only) · **Lane:** L16 Controllers/bindings · **Decision under test:** `DEC-CTRL-001` / the "B1" adapter
**Date:** 2026-06-30 · **Worktree:** `/home/delete/nirs4all/_worktrees/L16-dagml-controllers` · **Branch:** `refactor/L16-controller-manifests`
**Scope reviewed:** the 2 staged files in this worktree + `docs/agent_reports/IMP_L16_CONTROLLER_MANIFESTS.md`.
**Final disposition:** ✅ **`clean_with_notes`** — code is correct, tested, lint-clean and parity-accurate; no change required to the staged code. One mandatory *operational* landing action (rebuild+commit the `.so`, already documented as B-L16-1) and one substantive forward-looking API-shape note (F2) to track before binding wiring.

---

## 1. Scope & staging integrity

Exact staged set (unfiltered via `rtk proxy git`):

```
A  crates/dag-ml-core/src/controller_adapter.rs   (new, 649 lines incl. 11 unit tests)
M  crates/dag-ml-core/src/lib.rs                  (+2: pub mod + pub use glob)
```

- `git diff` (unstaged) is **empty** → both files fully staged, no partial-staging / no leftover hunks.
- No other modified/untracked files in the worktree → matches the report's "1 M + 1 A" claim. (`git diff --cached --name-only | wc -l` printing `5` is an RTK output-formatting artifact; `rtk proxy git` confirms 2.)
- The change is **additive and core-only**: no contract/schema, no C ABI, no CLI, no fixture touched.

---

## 2. Validation evidence (independently re-run, read-only)

| Check | Command | Result |
|---|---|---|
| Targeted tests | `cargo test -p dag-ml-core controller_adapter` | ✅ **11 passed**, 414 filtered out |
| Lint (affected crate) | `cargo clippy -p dag-ml-core --all-targets -- -D warnings` | ✅ **No issues found** |
| `.so` freshness (current state) | `python3 scripts/check_so_freshness.py` | ✅ **fresh, exit 0** — `_dag_ml.abi3.so` ct=1782807110 ≥ newest committed Rust src (`dsl/compat.rs`, ct=1782807110); 48 paths checked |
| Re-export collision | grep of all 5 new public names across `crates/` | ✅ each appears **only** in `controller_adapter.rs` → no ambiguous glob re-export |
| C ABI blast radius | grep `controller_adapter\|HostControllerSpec\|manifest_kind_template` in `crates/dag-ml-capi` | ✅ **0 hits** → C ABI untouched, no version-constant bump needed |
| Bridge parity (meta-model selector) | `_META_MODEL_REF` in `nirs4all/.../dagml_bridge.py` | ✅ `= "nirs4all.meta_model"` — **exact** match to the adapter test's selector |

The full green-gate run (fmt + clippy workspace + 548 tests + validate-graph + validate_contracts) is reported by IMP-L16; I re-verified the two cheap, load-bearing pieces (targeted tests + crate clippy) and the freshness guard, all green.

---

## 3. Findings (severity-ordered)

### F1 — [HIGH / required landing action, **not a code defect**] `.so` freshness flips to STALE on commit (B-L16-1, confirmed)

The gate is green **only because the changes are uncommitted.** `check_so_freshness.py` compares *git-commit* timestamps and skips paths with no commit history:
- `controller_adapter.rs` is untracked → no commit history → excluded from the "newest Rust source" max.
- `lib.rs` is staged but its **last commit** is still old.

The moment these two files are committed, both get a fresh commit timestamp that exceeds the tracked `_dag_ml.abi3.so` (ct=1782807110) → the guard returns **exit 1 (STALE)** and fails CI until the `.so` is rebuilt (`maturin develop --release` in `crates/dag-ml-py`) and committed **in the same landing commit**.

I confirmed the mechanism by reading the script (it walks `crates/dag-ml-core/src/**/*.rs`, so a new file there *does* count) and by running it now (exit 0). The report's B-L16-1 is accurate, including the key mitigation: the new module adds **no PyO3-exposed surface** (verified — no `#[pyfunction]`/`#[pymethods]`, and `dag-ml-py`/`dag-ml-capi` have zero references to it), so the rebuilt binary is behaviorally identical; the rebuild is purely to satisfy the timestamp guard.

**Action for landing:** rebuild + `git add` the `.so` in the landing commit. No source change required.

### F2 — [MEDIUM / API-shape, forward-looking] `added_capabilities` is additive-only; `Deterministic` is template-forced → nondeterministic controllers are underivable

Every kind template seeds `base_capabilities()` = `{Deterministic, ThreadSafe, ProcessSafe}`, and `derive()` only ever **extends** with `added_capabilities` — there is no way to *remove* a template-implied capability. Combined with the `ControllerManifest::validate()` cross-field rule (`Deterministic` + `rng_policy = Nondeterministic` → error), this means:

> A host that sets `rng_policy = RngPolicy::Nondeterministic` on a `Model`/`Transform`/`YTransform`/`PredictionJoin` spec **cannot derive a manifest at all** — `derive()` returns `ControllerValidation("… cannot be deterministic with nondeterministic RNG")`, with no escape hatch.

For *this* slice it is harmless: all four bridge controllers are deterministic, and the parity tests pass. But the module's stated purpose is the general "producer of capabilities from Python" (CAP open-question #5), and the report itself anticipates DL model controllers (`needs_python_gil`), which are commonly nondeterministic. A secondary symptom of the same additive-only model: a host that overrides `output_ports` to drop the `model` artifact port still keeps the template's `EmitsArtifacts` capability (validate only checks port→capability, not the reverse), so the manifest over-declares.

**Recommendation (before the binding-wiring lane, not this slice):** give the descriptor a way to subtract/override template capabilities — e.g. a `removed_capabilities` set, an explicit full-`capabilities` override, or making `Deterministic`/`UsesCoreRng` host-supplied rather than template-forced. Track explicitly so the DL/binding lane is not blocked.

### F3 — [LOW / design note] Generic `_ =>` fallback over-claims training for the 16 unmapped `NodeKind`s

`manifest_kind_template` templates 4 of 20 `NodeKind`s; the `_` arm gives the other 16 a **training-capable** (`FitCv/Refit/Predict`, `FoldTrain`), no-ports template. Calling that "conservative" (report §1, code doc) is generous — it is maximal training participation, applied to kinds that are semantically non-training: `Split` (which the dag-ml invariant explicitly says is a *campaign-plan splitter, never a controller node*), `Tag`, `Aggregator`, `Chart`, `Restructure`, etc. It *validates*, so this is not a correctness bug, and none of these kinds are routed through this adapter in the slice — but a naive `HostControllerSpec::new(id, v, NodeKind::Split).derive()` would silently yield a misleading manifest. The non-exhaustive `_` also means a future `NodeKind` inherits these defaults with no compile-time nudge to template it.

**Recommendation:** either return a genuinely minimal template (e.g. stateless / predict-only) for unmapped kinds, or make unmapped kinds an explicit error until templated. Optional for the foundation slice.

### F4 — [LOW / nit] Double validation on the registry path

`derive_host_controller_registry` calls `spec.derive()` (which runs `validate()`), then `ControllerRegistry::register()` runs `validate()` again on the same manifest. Harmless, minor redundancy; flagged only for completeness.

### F5 — [LOW / forward-looking] `HostControllerSpec` JSON wire path has no governing schema

The doc comment advertises shipping the descriptor "over JSON / PyO3 / the process adapter" directly. Today that is fine — `HostControllerSpec` is an ergonomic constructor and the only schema-governed wire artifact is the derived `ControllerManifest` (so `validate_contracts.py` is correctly unaffected). But if the descriptor is later *accepted as ABI input*, it becomes an ungoverned wire format; it should then get a JSON Schema + conformance-pack entry like the other contracts. No action now.

### F6 — [LOW / nit] `priority` is not kind-mechanical; bridge cutover must pass `priority = 20`

`priority` defaults to `0` in `HostControllerSpec::new`; the bridge manifests all use `20`. This is correct design (priority is host identity, not a kind default) and the report acknowledges it. The parity tests set `priority = 20` only for `transform`/`meta_model`; the `y_transform`/`model`/`merge_concat` tests assert caps+ports but not priority. Noted only so the eventual `controller_manifests()` cutover remembers to pass it, else generic host controllers stop out-ranking native specializations.

---

## 4. Confirmation of the slice's core claims

- **Manifest correctness / parity — verified.** The four kind-level catch-alls reproduce `dagml_bridge.controller_manifests()` field-for-field (supported_phases, fit_scope, capabilities incl. the `merge_concat` *omission* of `uses_core_rng`, ports incl. `tabular_numeric` reps on data/target ports and `None` on prediction/artifact ports, rng/artifact policies). `meta_model` (model + `consumes_oof` + `oof[many]` input override + `refs` selector) and `methods.pls` (alias selector out-ranking the generic model) behave correctly through the **existing** `ControllerRegistry::resolve_for_node` rank logic (OperatorSelector rank < GenericKind rank). The meta-model selector value matches `_META_MODEL_REF` exactly.
- **Validation invariants — never bypassed.** `derive()` calls `ControllerManifest::validate()` before returning; `register()` re-validates. The CAP cross-field rules (empty version, prediction-port⇒`emits_predictions`, artifact-port⇒`emits_artifacts`, inference-only-vs-training, deterministic-vs-nondeterministic-RNG, `ModelInputSpec` well-formedness) are exercised by tests 7–9 and inherited from `controller.rs`.
- **No new vocabulary / schema.** Derived manifests are ordinary `ControllerManifest`s over the frozen `ControllerCapability`/`ControllerFitScope`/`RngPolicy`/`ArtifactPolicy` enums; `LOCK-CAP` untouched; `validate_contracts.py` unaffected (re-confirmed: no schema/fixture in the staged set).
- **Import/re-export blast radius — minimal & safe.** `pub use controller_adapter::*;` adds exactly 5 public names (`HostControllerSpec`, `ManifestKindTemplate`, `manifest_kind_template`, `derive_host_controller_registry`, `HOST_CONTROLLER_TABULAR_REPRESENTATION`); none collide anywhere in the crate, so no `ambiguous_glob_reexports` (which would fail `-D warnings`). Helper fns are private and not glob-leaked. `PortSpec`/`NodeKind`/`ControllerId` usage matches the current definitions (all 8 `PortSpec` fields populated; `ControllerId::new` charset accepts the `controller:…` ids).
- **`DEC-DESIGN-001` boundary respected.** Derivation/validation only; produces and validates manifests, executes nothing; does not inspect feature matrices.

---

## 5. Risks

1. **CI break on commit if the `.so` is not rebuilt** (F1) — the single concrete risk; mitigated by the documented landing step.
2. **API gap for nondeterministic / capability-subtracting controllers** (F2) — will surface the first time the binding lane tries to express a DL/nondeterministic model; not a regression, but a foundation that the next lane must extend rather than work around.
3. **Misleading manifests for non-template kinds** (F3) — latent, low-probability (requires a host to derive an unmapped kind), no leakage/OOF impact.

No leakage-safety, OOF, fold, or determinism *invariant* is weakened by this change (it only adds a producer in front of the unchanged validator).

---

## 6. Disposition

**`clean_with_notes`.**

The staged code is correct, well-scoped, fully tested (11/11), clippy-clean under `-D warnings`, and parity-accurate against the live nirs4all bridge. Nothing in the staged source needs to change to land this slice.

- **Must do at landing:** rebuild + commit `crates/dag-ml-py/python/dag_ml/_dag_ml.abi3.so` in the same commit (F1 / B-L16-1).
- **Track before the binding-wiring lane:** capability subtraction / nondeterministic-controller support (F2).
- **Optional cleanups:** narrow the unmapped-kind fallback (F3); drop the double validation (F4); schema-govern `HostControllerSpec` only if it becomes ABI input (F5); remember `priority=20` at bridge cutover (F6).
