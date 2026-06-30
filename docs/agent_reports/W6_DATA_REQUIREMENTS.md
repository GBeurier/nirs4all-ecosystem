# W6 — ControllerManifest `data_requirements` → frozen representation IDs (B-014b)

**Agent:** W6 (implementation) · **Lane:** L16 controller `data_requirements` · **Blocker:** `B-014b` · **Wave:** 2B
**Date:** 2026-07-01 · **Mode:** single dag-ml worktree, narrow slice.
**Worktree:** `/home/delete/nirs4all/_worktrees/W6-dagml` · **Branch:** `refactor/W6-data-requirements` · **Base:** committed L16 tip `2143c57` (`feat(core): derive controller manifests`).
**Status:** ✅ implemented, targeted gate green (fmt + clippy `-D warnings` + `dag-ml-core` + full workspace + CLI smoke + local `validate_contracts.py`), one local commit (source only). Not pushed.

> Scope honored: only `crates/dag-ml-core/src/controller_adapter.rs` was touched. Did **not** edit `scripts/validate_contracts.py` (W5), the export paths (W3), or `PARALLEL_REFACTORING_SYNC.md`. This report is the only write outside the worktree.

---

## 1. What this slice does

L16 (`IMP_L16`) built the native `HostControllerSpec → derive() → ControllerManifest` adapter but left the data/target ports stamped with the single coarse placeholder `HOST_CONTROLLER_TABULAR_REPRESENTATION = "tabular_numeric"` — the L6/L7-blocked default — on **both** data **and** target ports, and never populated `data_requirements` (`IMP_L16` §7). B-014b closes that gap now that the representation registry is frozen and published.

The slice does two things:

1. **Ports carry the semantically-correct frozen representation id.** The single coarse constant is replaced by two named, registry-frozen constants, assigned by port semantics:
   - **data** ports (`transform` `x`/`x_out`, `model` `x`) → `REPRESENTATION_TABULAR_NUMERIC` (`tabular_numeric`, registry `type_id = "table"`);
   - **target** ports (`y_transform` `y`/`y_out`) → `REPRESENTATION_TARGET_NUMERIC` (`target_numeric`, registry `type_id = "target"`).

   The target-port change is the real correctness fix: a *target* port was previously carrying a *feature-table* representation.

2. **`derive()` synthesizes a validated `ModelInputSpec` as `data_requirements`.** When the host leaves `data_requirements` unset, `derive()` builds a `ModelInputSpec` from the resolved data/target input ports — each contributing one `ModelInputPortSpec` that pins the port's frozen representation id and its registry `type_id` in `accepted_representations` / `accepted_types`. The result is run through the existing `ControllerManifest::validate()` (which validates the embedded `ModelInputSpec`), so a derived manifest can never carry a malformed requirement.

### Behavioural rules

- **Host override always wins.** An explicit `HostControllerSpec.data_requirements` is preserved verbatim; synthesis only fills the `None` case.
- **Synthesis follows the *resolved* ports.** If the host overrides the data port (e.g. to the NIRS `signal_1d`), the synthesized requirement re-pins to that id and its `type_id` — kept consistent automatically.
- **Opaque-only kinds get nothing.** A `prediction_join` (or any controller with no representation-bearing data/target input port) yields `data_requirements = None`; it consumes OOF predictions, not raw data.
- **Unknown representation → no synthesis.** A data/target port whose representation is outside the mirrored registry subset cannot be typed, so synthesis is skipped (`None`) and the host is expected to supply explicit `data_requirements`. `derive()` does not fail for this — the port representation itself is free-form.

---

## 2. Why it is shaped this way (boundary discipline)

- **Modality-neutral defaults — no NIRS logic in core.** `dag-ml-core` must not encode NIRS-specific assumptions (root `AGENTS.md`). The generic kind templates therefore default to the registry's *modality-neutral* `tabular_numeric` / `target_numeric`, **not** the NIRS `signal_1d`. NIRS-specific representations are a *host override* (the nirs4all bridge passes `signal_1d`), exercised by a test but never baked into the templates.
- **Registry IDs mirrored, not depended on.** `dag-ml` does not depend on `dag-ml-data`, and the core must not read a contract JSON at runtime. The IDs the adapter consumes are mirrored as the compile-time `const FROZEN_REPRESENTATION_TYPES` (`(representation_id → type_id)`), documented as sourced from `docs/contracts/representation_registry.v1.json`. The mirror covers the registry's **MVP-emitted profile** (`signal_1d`, `signal_with_processings`, `feature_block_set`, the four `target_*`, `sample_metadata`) plus the generic `tabular_*` ids — exactly the set a controller port realistically carries. Full 26-ID drift-gating across the sibling registry is W5's `validate_contracts.py` lockstep, not this slice.
- **No new vocabulary / no new schema.** `data_requirements` is an already-existing optional `ControllerManifest` field validated as the already-existing `ModelInputSpec`; this slice only *populates* it. No contract/schema changed, so `validate_contracts.py` is untouched and unaffected.
- **Validation never bypassed.** Synthesis routes through `serde_json::to_value` → `ControllerManifest::validate()` → `ModelInputSpec::validate()`, so the cross-field invariants (non-empty/unique `accepted_representations` & `accepted_types`, unique port names, schema version) hold for free.

---

## 3. Parity with the existing mappings

The 6 mappings L16 froze still derive valid manifests and pass; structural fields (phases, capabilities, port names, cardinalities, selectors, policies) are unchanged. Only two things move, both intended by B-014b:

| Mapping | Change |
|---|---|
| `controller:nirs4all.transform` (`transform`) | `x`/`x_out` representation now the named `tabular_numeric`; `data_requirements` synthesized (`x` → `[tabular_numeric]` / `[table]`). |
| `controller:nirs4all.y_transform` (`y_transform`) | `y`/`y_out` representation **`tabular_numeric` → `target_numeric`** (the fix); `data_requirements` synthesized (`y` → `[target_numeric]` / `[target]`). |
| `controller:nirs4all.model` (`model`) | `x` representation named `tabular_numeric`; `data_requirements` synthesized for `x`. |
| `controller:nirs4all.merge_concat` (`prediction_join`) | unchanged; `data_requirements = None` (opaque OOF port). |
| `controller:nirs4all.meta_model` (`model` + `oof` override + `consumes_oof` + `refs`) | unchanged; `data_requirements = None` (input overridden to an opaque `oof` port). |
| `controller:methods.pls` (`model` + `aliases` selector) | unchanged; `data_requirements` synthesized for `x`. |

The L16 "field-for-field bridge parity" claim *evolves* here exactly as `IMP_L16` §7 anticipated: the derived manifest now carries the richer `data_requirements` the bridge placeholder lacked. The bridge becomes the *consumer* of `derive()` (separate PyO3 lane), not the reference for the placeholder.

---

## 4. Files changed

| File | Change | Notes |
|---|---|---|
| `crates/dag-ml-core/src/controller_adapter.rs` | data/target port representations → frozen ids; `FROZEN_REPRESENTATION_TYPES` mirror + `representation_type_id()`; `default_data_requirements()` synthesis in `derive()`; `tabular_port` → `represented_port(name, kind, representation)`; +7 tests | only file touched |

No `lib.rs` edit needed: it already re-exports the module flat (`pub use controller_adapter::*;`), so the new public items (`REPRESENTATION_TABULAR_NUMERIC`, `REPRESENTATION_TARGET_NUMERIC`, `representation_type_id`) are exported automatically. The coarse `HOST_CONTROLLER_TABULAR_REPRESENTATION` const (introduced by L16, unused outside this module — verified by grep across the workspace) was replaced, per the repo's "no back-compat shim" rule.

---

## 5. Tests

`cargo test -p dag-ml-core controller_adapter` → **18 passed** (11 original + 7 new). The 7 new tests:

1. `representation_type_id_maps_frozen_registry_ids` — the mirror maps published ids to their registry `type_id`; unknown id → `None`.
2. `model_template_synthesizes_tabular_data_requirements` — `x` port `tabular_numeric`; synthesized `ModelInputSpec` port `x` accepts `[tabular_numeric]` / `[table]`.
3. `y_transform_synthesizes_target_data_requirements` — `y` port `target_numeric`; synthesized requirement pins `[target_numeric]` / `[target]`.
4. `prediction_join_has_no_data_requirements` — opaque OOF input → `data_requirements = None`.
5. `host_supplied_data_requirements_take_precedence_over_synthesis` — explicit host requirement preserved verbatim.
6. `port_override_with_known_representation_resyncs_data_requirements` — overriding `x` to `signal_1d` re-pins the synthesized requirement to `signal_1d` / `dense_signal`.
7. `port_override_with_unknown_representation_skips_synthesis` — unregistered representation → no synthesis (host must supply).

The 3 pre-existing parity tests (`transform_…`, `y_transform_…`, `model_…`) were updated to the new `represented_port(…)`/frozen-id assertions; the other 8 are unchanged.

---

## 6. Gate run

| Step | Command | Result |
|---|---|---|
| fmt | `cargo fmt --all --check` | ✅ pass |
| lint | `cargo clippy --workspace --all-targets -- -D warnings` | ✅ "No issues found" |
| test (touched crate) | `cargo test -p dag-ml-core` | ✅ **430 passed**, 2 ignored |
| test (workspace) | `cargo test --workspace` | ✅ **555 passed**, 2 ignored (548 → 555, +7 new) |
| CLI smoke | `cargo run -p dag-ml-cli -- validate-graph examples/minimal_graph.json` | ✅ "valid graph" |
| contracts | `python3 scripts/validate_contracts.py` | ✅ "validated dag-ml contract" (local; W5's cross-repo digest path is not on this branch) |
| .so freshness | `python3 scripts/check_so_freshness.py` | ⚠️ STALE — pre-existing `B-L16-1` (see §7) |

---

## 7. Blockers, dependencies & notes for the reviewer

- **`B-L16-1` (.so freshness) — pre-existing, deferred to land-time, not newly broken.** `check_so_freshness.py` was **already STALE at my base** `2143c57`: L16 committed its Rust sources without rebuilding the tracked `crates/dag-ml-py/python/dag_ml/_dag_ml.abi3.so`. My commit does not introduce *new* staleness beyond that. I deliberately did **not** hand-roll the binary, because:
  1. the documented rebuild path (`maturin develop --release`) requires Python ≥ 3.11 (the crate pins `abi3-py311`); this host has **Python 3.10.12**, so I can neither build via the documented path nor import the result to validate it;
  2. my change touches **no PyO3-consumed surface** — `dag-ml-py` does not wrap `controller_adapter` / `HostControllerSpec` / `derive()` (verified: the only `data_requirements` hits in `dag-ml-py/src` are hand-authored JSON test fixtures), so a rebuilt `.so` would be behaviourally identical — the rebuild is a pure timestamp formality;
  3. `RV10` §5 assigns the `.so` rebuild to the maintainer **at land-time**, serialized across the dag-ml tenants (W3/W6): *"rebuild+commit `.so` on whichever merges, re-rebuild on the next."*
  **Action for the landing maintainer:** `maturin develop --release` (or build a wheel) on a ≥3.11 host and `git add` the `.so` when W6 (and W3) merge.

- **Soft-dependency on W5 — now RESOLVED.** W5 is committed (`dag-ml-data refactor/W5-contracts-dmd @ 4f858c3`; `dag-ml refactor/W5-contracts-dagml @ e55d8aa`) and has published `docs/contracts/representation_registry.v1.json` into the `dag-ml` repo plus wired the `conformance_pack` + `validate_contracts.py` digest path. My worktree branches off **L16** (`2143c57`), so that file is not in my tree yet; it arrives when W6 merges alongside W5. The IDs my in-core mirror pins are **identical** to the W5-published registry (verified against the 923-line `representation_registry.v1.json`: same 26 ids, same `type_id`s). No code dependency, no rebase needed; the shared-contract file simply co-locates with my constants at land.

- **No new `ControllerRole`/capability vocabulary, no schema change** → `LOCK-CAP` untouched, `validate_contracts.py` unaffected, nothing new for A0/W5 to sign on the manifest side.

- **Out of scope (unchanged from `IMP_L16` / `RV10` §10):** the full per-operator `OperatorController → ControllerManifest` projection (CTRL-000), Layer-1 keyword→`NodeKind` lowering, and PyO3/CLI surfacing of `derive()` for the bridge & Studio `GET /api/operators/manifests`. This slice only enriches the kind templates' representation ports + `data_requirements`.

---

## 8. Suggested sync-board worklog line (for the board owner — I did not edit the board)

`2026-07-01 | W6 | landed | dag-ml-core controller_adapter: data ports → frozen tabular_numeric, target ports tabular_numeric→target_numeric (fix); derive() synthesizes validated ModelInputSpec data_requirements from resolved data/target ports (host override wins; opaque/unknown → None); registry ids mirrored as FROZEN_REPRESENTATION_TYPES + representation_type_id(). Closes B-014b. | gate green: fmt+clippy(-D warnings)+test(workspace 555, +7)+validate-graph+local validate_contracts; controller_adapter 18 tests. Source-only commit; .so rebuild deferred to land (B-L16-1, host py3.10 vs abi3-py311). | Soft-dep W5 resolved (ids match published registry).`

---

## 9. Evidence (files read / commands run)

- Plan & specs: `RV10_NEXT_WAVE_PLAN.md` (W6 row §4, deps §7, land order §5, .so §6.4), `IMP_L16_CONTROLLER_MANIFESTS.md` (§7 data_requirements blocker), `IMP_L6_DMD_REGISTRY.md` (§7b: "L16 wires `ControllerManifest.data_requirements` ports to these frozen strings"), root `AGENTS.md` (no-NIRS boundary), worktree `CLAUDE.md` (green gate).
- dag-ml-core: `crates/dag-ml-core/src/{controller_adapter.rs, controller.rs (ControllerManifest::validate, model_input_spec), data.rs (ModelInputSpec/ModelInputPortSpec, MODEL_INPUT_SPEC_SCHEMA_VERSION), graph.rs (PortSpec/PortKind/PortCardinality)}`.
- Registry source: `dag-ml-data` L6 worktree `docs/contracts/representation_registry.v1.json` (committed `4003480`) and the identical W5-published `dag-ml` copy (`e55d8aa`).
- dag-ml-py: `crates/dag-ml-py/{Cargo.toml (abi3-py311), src/in_process.rs}` — confirmed no consumption of the adapter API.
- Live git: `git status` (clean base), `git log -1` (`2143c57`), `check_so_freshness.py` (stale at base), W5 tips `4f858c3` / `e55d8aa`.
