# IMP-L6 — `dag-ml-data` representation-ID freeze/publish (B-014 / DMD-001 slice 1)

**Agent:** IMP-L6 (implementation) · **Lane:** L6 · **Worktree:** `/home/delete/nirs4all/_worktrees/L6-dmd-registry` (`dag-ml-data`, base `347c15f`)
**Scope:** first B-014 slice — make the existing built-in representation IDs **discoverable / frozen / published** from the current builtin model registry, **without inventing a new vocabulary**. Spectra+image MVP status included.
**Status:** ✅ implemented, full local gate green, changes **staged** (not committed). Ready for review.

---

## 1. What B-014 actually needed (confirmed against code)

B-014 is a **freeze/publish problem, not an invention problem** — verified. The stable representation-ID catalogue already exists in `crates/dag-ml-data-core/src/builtin_models.rs`:
- representation `pub const` strings (`:36-62`), `BuiltinDataModel` enum (`:64-93`), `BUILTIN_DATA_MODELS` array (`:95-122`) — **26 builtins**, each with a frozen id, `type_id`, key, modality, axes, dtype.
- The existing test `builtin_data_models_validate_and_have_unique_keys_and_representations` already guarantees the 26 ids/keys are unique.

So no new strings were added. The deliverable was the **frozen, published list + a drift test**, exactly per `IO_spec.md` §5 / `SW1_IO_DMD_spec.md` §7 item 1.

## 2. What was implemented

A generated-from-source **static manifest + Rust drift test + public API + CLI accessor** (all four reinforce one another; each maps to a named B-014 goal: discoverable = API/CLI, frozen = drift test, published = JSON manifest).

| Goal | Deliverable |
|---|---|
| **Published** | `docs/contracts/representation_registry.v1.json` — the 26 frozen representation IDs, each with `representation_id`, `builtin_key`, `modality`, optional `mvp` annotation, and the full frozen `RepresentationSpec` (axes/rank/dtype/container). |
| **Discoverable (API)** | `representation_registry()` → `RepresentationRegistry` in new core module `representation_registry.rs`; re-exported flat via `lib.rs` like every other module. |
| **Discoverable (CLI)** | `dag-ml-data-cli representation-registry` prints the manifest (the regeneration path), matching the existing `fingerprint-*` subcommand pattern. |
| **Frozen** | drift test `published_registry_matches_builtin_models` asserts the committed JSON == `serde_json::to_value(representation_registry())`; any change to a builtin representation fails it until the manifest is regenerated. |
| **Spectra+image MVP status** | per-entry `mvp` block (profile `spectra_image`): **8 `emitted`** (`signal_1d`, `signal_with_processings`, `feature_block_set`, `target_numeric`/`_categorical`/`_numeric_matrix`/`_categorical_matrix`, `sample_metadata`) + **4 `landed_pending_emit`** image IDs (`gray_image`, `rgb_image`, `mc_image`, `multispectral_image`). = the 12-ID MVP set. |

### Image MVP status (answer to "if image IDs are not yet implemented")
The 4 image representation IDs **are fully landed in `dag-ml-data`** (consts + enum + ctors + axes incl. `rgb_image` `channel`=3, dtype `uint8`/`float32`). They are **not yet emitted by `nirs4all-io`** (`IO-010`). The manifest records this precisely as `emission: "landed_pending_emit"`, so the freeze is honest about cross-repo readiness without claiming downstream support.

### Boundary discipline
- **No new vocabulary**; the manifest re-publishes `builtin_models.rs` verbatim.
- Core data *types* (`RepresentationSpec`, `AxisKind`, …) are **untouched** — the MVP annotation lives only on the new publish-layer wrapper (`RegisteredRepresentation`/`MvpStatus`) in the registry module, not on core types, so the "no NIRS-specific assumptions in core types" boundary holds.
- The `mvp` emission status is documented as sourced from `IO_spec.md` §5, not a runtime fact verified by this crate.

## 3. Files changed (L6 worktree only — staged)

| File | Δ | Purpose |
|---|---|---|
| `crates/dag-ml-data-core/src/representation_registry.rs` | **new (294 L)** | types (`RepresentationRegistry`, `RegisteredRepresentation`, `MvpStatus`, `MvpEmissionStatus`), `representation_registry()` builder, 5 tests (drift + MVP-consistency + coverage + header + round-trip). |
| `docs/contracts/representation_registry.v1.json` | **new (923 L)** | the published frozen manifest (CLI-generated). |
| `crates/dag-ml-data-core/src/lib.rs` | +2 | `pub mod` + `pub use` the new module (flat re-export convention). |
| `crates/dag-ml-data-cli/src/main.rs` | +14/−4 | `representation-registry` subcommand. |
| `docs/contracts/README.md` | +39 | "Representation Registry v1" contract section (incl. regen command + next-slice note). |
| `docs/STATUS.md` | +12 | "Implemented" entry for the frozen registry. |

No other repos/worktrees touched. `PARALLEL_REFACTORING_SYNC.md` / `AGENT_RUN_SUPERVISION.md` not edited.

## 4. Tests / gates run — all green

| Gate | Result |
|---|---|
| `cargo fmt --all --check` | OK |
| `cargo clippy --workspace --all-targets -- -D warnings` | 0 warnings |
| `cargo test --workspace` | **263 passed**, 0 failed, 2 ignored (199 in core lib incl. 5 new registry tests) |
| `cargo test -p dag-ml-data-core representation_registry` | 5/5 pass (drift, header, coverage, mvp-consistency, json round-trip) |
| `RUSTDOCFLAGS="-D warnings" cargo doc -p dag-ml-data-core --no-deps` | OK (no broken intra-doc links) |
| `dag-ml-data-cli fingerprint-schema examples/minimal_schema.json` (working-gate smoke) | OK |
| CLI `representation-registry` ⟷ committed manifest | **byte-identical** (regeneration is stable/idempotent) |
| `scripts/validate_contracts.py` (local) | pass |
| `DAG_ML_REPO=…/dag-ml scripts/validate_contracts.py` (cross-repo vs real sibling) | pass — **no lockstep contract touched** |

## 5. Deliberate scope boundary (next slice)

This slice **does not** wire the registry into `conformance_pack.v1.json` / the cross-repo `validate_contracts.py` digest path. That is intentional and correct for a first slice:
- It is a **lockstep change** requiring a simultaneous `dag-ml` edit; `validate_contracts.py` enforces `local_pack == sibling_pack` when a sibling is present, so adding a pack digest here alone would break the cross-repo equality check — and editing the sibling is out of scope ("do not edit sibling repos").
- The **Rust drift test is the freeze** for now; the published JSON + README document the artifact.
- Per `SW1_IO_DMD_spec.md` §7 item 1, the conformance-pack + drift-digest wiring is the **next L6+L20 lockstep slice**, done jointly with `dag-ml` (whose `ModelInputSpec.accepted_representations` is a `Vec<String>`, and which does **not** depend on `dag-ml-data` — so the frozen list must be a shared contract file, which this manifest now is).

## 6. Residual risks / notes for reviewers

- **Manifest is hand-regenerated, not build-time generated.** If a future change edits `builtin_models.rs` without rerunning `cargo run -p dag-ml-data-cli -- representation-registry`, the drift test fails loudly (by design) — the dev must regenerate. No silent drift possible.
- **MVP `emitted`/`landed_pending_emit` labels are coordination metadata** sourced from `IO_spec.md` §5, not verified by `dag-ml-data` at runtime. If `nirs4all-io` ships image emission (`IO-010`), the 4 image entries should flip to `emitted` (one-line change in `MVP_SPECTRA_IMAGE_PENDING` + regen).
- **Not yet a cross-repo-enforced contract** (see §5). Until the lockstep slice lands, the manifest can be referenced by `L16`/`L7` but its parity with `dag-ml` is not CI-gated.
- The 4 post-image/post-MVP "bounds" IDs (`cube_hwb`, masks, series, genotype, raman/ftir, tabular, mass_spectrum, text) are present in the manifest with **no `mvp` annotation** (correct — declared/frozen, emission deferred).

## 7. Review readiness

**Ready.** Self-contained, additive, full local gate green, no shared/lockstep contract touched (cross-repo validator passes against the real `dag-ml` sibling), changes staged in the L6 worktree. Suggested follow-ups: (a) L6+L20 conformance-pack/`validate_contracts.py` lockstep wiring with `dag-ml`; (b) L16 wires `ControllerManifest.data_requirements` ports to these frozen strings → closes B-014; (c) L7 flips image entries to `emitted` once `nirs4all-io` `IO-010` lands.
