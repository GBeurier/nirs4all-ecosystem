# SW1 — IO/DMD validation audit of `IO_spec.md` / `LOCK-IO`

**Agent:** SW1 (second-wave, IO/DMD/multimodal data contracts) · **Mode:** READ-ONLY (only this file written; no code, no sync board)
**Audits:** `docs/agent_reports/IO_spec.md` (194 lines, landed) + the `LOCK-IO` row, `B-014`, `B-019` in `PARALLEL_REFACTORING_SYNC.md`
**Method:** direct `git`/`rg`/`sed`/`Read` against working heads. Verified heads: `nirs4all-io` `84ab189` (tree clean), `dag-ml-data` `347c15f`, `nirs4all` `e41362b4`, `nirs4all-datasets` `ae414964`, `nirs4all-formats` `89231b2`.

---

## 0. Verdict — **PASS WITH CONCERNS** · `LOCK-IO` is safe to keep landed

The IO_spec's **contracts are sound and its core factual claims are verified** (DatasetSpec v2 as an additive superset, DatasetPackage + payload manifest, identity = `SampleRelationTable`, extend-the-bridge, DMD-001 = freeze the existing builtins, MVP = spectra + image). The representation-ID evidence is correct. **Keep the lock landed.**

But there is **one factual error** that the IO_spec inherited from a stale doc and that has propagated into the sync board (`B-019`), plus **two scope omissions** that implementers must not miss. None invalidate the frozen contracts; all are correctable in place.

| # | Item | Audit result |
|---|---|---|
| C1 | `nirs4all-io-dagml` is "workspace-EXCLUDED" (IO_spec §0/§8, sync `B-019`, io `CLAUDE.md:50-51`) | **WRONG at HEAD** — it is a workspace **member**. Correct the claim + re-scope the CI hazard. |
| C2 | "io → dag-ml-data → core/runtime" reads as the live producer path | **Aspirational, not current** — nirs4all core builds its own (richer) envelope and the Python `nio` emit is `NotImplementedError`. |
| C3 | DatasetPackage on-disk form / DMD-001 freeze mechanics | **Under-specified** — reconcile with the existing `nirs4all-datasets` canonical layout; make DMD-001 a lockstep contract artifact. |

---

## 1. Claims that PASS (verified against code)

| IO_spec claim | Evidence (verified) | Result |
|---|---|---|
| **DMD-001 catalogue already exists** | `dag-ml-data-core/src/builtin_models.rs`: representation `pub const`s `:36-62`, `BuiltinDataModel` enum `:64-93`, `BUILTIN_DATA_MODELS` array `:95-122`, `builtin_data_model_specs()`/`builtin_representations()` `:254-268`. | **PASS** |
| **26 builtins** | `BUILTIN_DATA_MODELS` has exactly 26 entries (`:96-121`); enum has 26 variants. | **PASS (exact)** |
| **MVP spectra IDs emitted (8)** | bridge `crates/nirs4all-io-dagml/src/lib.rs` emits `signal_1d`/`signal_with_processings` (`source_representation` `:213-239`), `feature_block_set` join (`:566-581`), `target_numeric/categorical[_matrix]` (`emit_target_specs` `:280-316`), `sample_metadata` (`:355-396`). | **PASS** |
| **MVP image IDs landed but not emitted (4)** | `rgb_image:47`, `gray_image:48`, `mc_image:49`, `multispectral_image:50` exist as consts + enum + ctors; bridge `feature_axis()` `:90-108` only ever produces Wavelength/Wavenumber/Feature → image emission genuinely absent. | **PASS** |
| **Required axis kinds all exist** | `model.rs` `AxisKind` includes `Height/Width/Channel/Depth/Time/Token/Variant/Frequency` alongside spectral kinds. | **PASS** |
| **`Modality.image` in vocab but dead** | `spec/enums.py:66 IMAGE = "image"` present; `rg image` in `src/nirs4all_io/materialize/` + `infer/` → **0 hits**. | **PASS** |
| **Bridge never emits FoldSet; relations hard-code source_id/origin/augmented** | `lib.rs:465-481` builds each `SampleRelation` with `source_id: None`, `origin_id: None`, `augmented: false`; doc `:11-12`. | **PASS** |
| **Identity target contract is `SampleRelationTable`** | `relation.rs:49-75` (`SampleRelation` + table); wire mapping `coordinator.rs:283-329` (`coordinator_relations_from_sample_table`). | **PASS** |
| **README "Phase 2 gated" is stale; bridge implemented+tested** | `to_dag_ml_data` `lib.rs:598-603`, `build_dag_ml_data_parts` `:398-595`, 4 unit tests `:664-771`. | **PASS** |

**B-014 is a freeze/publish problem, not an invention problem** — confirmed. The catalogue is landed; the MVP needs no new strings.

---

## 2. C1 — REQUIRED CORRECTION: the bridge crate is a workspace **member**, not excluded

The IO_spec (§0: *"the crate is **workspace-EXCLUDED** (`CLAUDE.md:50-51,126`)"*; §8 CI hazard: *"`nirs4all-io-dagml` is workspace-excluded → the bridge is **not** covered by `cargo test --workspace`"*) and sync `B-019` (*"EXCLU du workspace → `cargo test --workspace` ne le build jamais (faux vert possible)"*) are **false at `84ab189`**.

**Direct evidence (committed HEAD, clean tree):**
- `git show HEAD:Cargo.toml` → `[workspace].members` = `nirs4all-io-core, nirs4all-io, nirs4all-io-capi, nirs4all-io-cli, **nirs4all-io-dagml**`; `exclude` = only `bindings/python`, `bindings/wasm`; **no `default-members`** (so every member, incl. the bridge, is in the default build/test set).
- The exclusion was real **before** commit `b54b48d` *("chore(deps): depend on published dag-ml-data 0.2.2 (drop local path)")*, which changed `crates/nirs4all-io-dagml/Cargo.toml`: `dag-ml-data = { path = "../../../dag-ml-data/crates/dag-ml-data" }` → `dag-ml-data.workspace = true`, and the workspace dep `0.1.0-alpha.0` → **`0.2.2`** (crates.io). Dropping the local path dep is exactly what let the crate join the workspace while keeping standalone CI ecosystem-free. The crate keeps `publish = false`.
- io `CLAUDE.md:50-51` ("deliberately workspace-EXCLUDED") is the **stale source** the IO_spec trusted; it predates `b54b48d`.

**Consequence — the hazard is real but narrower than stated.** `cargo test --workspace` (and `cargo build --workspace --no-default-features`, both in io's green gate) **do** now build and run the bridge + its 4 tests — **against the published `dag-ml-data 0.2.2`, not the local sibling `347c15f`**. So:
- "Not covered / false-green" → **incorrect**; basic coverage exists.
- The **actual** risk is **version drift**: the bridge is gated against frozen crates.io `0.2.2` while `LOCK-IO`/`B-014`/`DMD-001` work happens on the local `dag-ml-data` head. A representation/envelope change in the sibling won't be caught by io's default gate until the next `0.2.x` publish. The fix is an **ecosystem-gated job that path-overrides `dag-ml-data` to the local sibling** (drift catch under `LOCK-LOCKSTEP`), not "add the crate to CI."

This C1 correction does not weaken any LOCK-IO contract — it strengthens the gate story.

---

## 3. C2 — SCOPE OMISSION: io is **not yet** the producer into core/runtime

The IO_spec frames `io → dag-ml-data` as *the* dataset→envelope path. Today the **runtime path bypasses io entirely**, and the spec does not say so. Two facts implementers need:

1. **nirs4all core has its own, richer envelope builder.** `nirs4all/nirs4all/pipeline/dagml/envelope.py:297-370` `build_envelope(SpectroDataset, IdentityMap, …)` calls `dag_ml_data.build_coordinator_data_plan_envelope(...)` directly from a `SpectroDataset` — **not** from io's `AssembledDataset`/`to_dag_ml_data`. It already carries what io's bridge hard-codes away: per-relation `excluded`, `tags`, `augmentation`, `group_id`, fold-scoped sample universes (its own docstring says it "mirrors nirs4all-io-dagml"). So there are **two parallel AssembledDataset/SpectroDataset → envelope implementations**, and the live one is in nirs4all core.
2. **The Python `nio` emit is not wired.** `nirs4all-io/src/nirs4all_io/api.py:185-186` — `load(target="dag-ml-data")` raises `NotImplementedError`. The envelope is reachable only via the Rust CLI `emit-dagml` / the bridge crate. (`nirs4all`'s `data/config.py` does use `nio.load`/`nio.infer` to build the `SpectroDataset`, but the envelope is then rebuilt by `envelope.py`, not by io.)

**Why it matters for LOCK-IO:** "io is the single dataset→envelope producer" is the *target*, not the *current* state. The convergence work (reconcile io's bridge with `envelope.py`: dataset-grain identity + relations owned by io; CV/fold-scoping stays in nirs4all/dag-ml) is a cross-lane item (`L5`/`L7`/`L17`) the IO_spec should name so nobody assumes the runtime already flows through io. **Recommend adding it as an explicit gap/dependency in the lock notes** (not a blocker on the contracts themselves).

---

## 4. C3 — UNDER-SPECIFIED (constructive, non-blocking)

- **DatasetPackage on-disk form has prior art that the spec ignores.** `nirs4all-datasets` already materializes a canonical package: `canonical/dataset.json` (manifest) + `sources/<source_id>.parquet` (observation_id, sample_id, float32 spectra) + `variables.parquet` (sample_id + Y/metadata) + `splits/<name>.parquet`, plus a `Manifest` with `processing_hash`/`metadata_hash`/per-file `sha256`/`row_counts` (verified via repo audit, `nirs4all-datasets` `ae414964`). The IO_spec §2 designs `DatasetPackage` + payload manifest from scratch. **Reconcile the two** so the ecosystem grows one materialized-package format, not two; the datasets `Manifest` is a ready model for the §2 payload manifest (`content_hash` + URI refs).
- **The richer wire relation fields are unused.** `coordinator_data_plan_envelope.schema.json` `coordinator_relation` already supports `unit_level ∈ {physical_sample, source_sample, observation, combo}`, `unit_id`, `derived_unit_id`, `component_observation_ids`, `sample_influence_weight`, `quality_flag` — the multimodal/fusion identity the IO_spec §3 wants is partly **already in the wire contract**, populated by neither the core mapping (`coordinator.rs:313-324`) nor the bridge. §3's "carry `source_id`/multi-obs-per-sample" work should target these existing fields rather than imply new ones.
- **DMD-001 freeze must be a real artifact.** §5 says "freeze + drift test" but names no carrier. Recommend: a published representation-ID enum (JSON) + an entry in `dag-ml-data` `conformance_pack.v1.json`, validated by `scripts/validate_contracts.py` (the `LOCK-LOCKSTEP`/`L20` path), so `L16` `ControllerManifest.data_requirements` ports cite frozen strings. Note dag-ml's `ModelInputSpec.accepted_representations` is `Vec<String>` (`dag-ml-core/src/data.rs:972`) and dag-ml does **not** depend on dag-ml-data — so the frozen list must be a **shared contract file**, not a Rust re-export.

---

## 5. Is `LOCK-IO` safe to keep landed? — **Yes.**

The signed contracts (DatasetSpec v2 additive superset; DatasetPackage + payload manifest; identity = SampleRelationTable; extend-the-bridge; DMD-001 = freeze the 26 landed builtins, MVP = the 12 spectra+image IDs; MVP = spectra + image with validate-envelope/validate-data-binding gates) are **internally consistent and evidence-backed**. The defects are a stale CI claim (C1) and two omissions (C2/C3) — all in the *commentary/hazard* layer, none in the *frozen interface*. **Do not re-open the lock.** Apply the corrections below.

---

## 6. Required sync-board / doc corrections (I did not edit them)

1. **`B-019` (sync board)** — restate. Current: *"crate EXCLU du workspace → cargo test --workspace ne le build jamais (faux vert)."* Correct to: *"crate is a workspace **member** since `b54b48d` (dep = published `dag-ml-data 0.2.2`); `cargo test --workspace` builds it, but **against published 0.2.2, not the local sibling** → drift risk. Action: add an ecosystem-gated job that path-overrides `dag-ml-data` to the local sibling."* (Downgrade from "false-green" to "drift".)
2. **`IO_spec.md` §0 + §8** — drop "workspace-EXCLUDED"; replace the §8 CI hazard with the drift-against-published-`0.2.2` framing above.
3. **`nirs4all-io/CLAUDE.md:50-51` (and the `:126` ref)** — stale; the bridge is now a workspace member. (Flag for the io maintainer; outside my write scope.)
4. **`LOCK-IO` row** — add a one-line gap note: *"io is the target producer; the live runtime envelope path is still `nirs4all/pipeline/dagml/envelope.py` (richer) + Python `nio` emit = NotImplementedError → convergence is `L5`/`L7`/`L17`."*

---

## 7. Next implementation actions (ordered)

1. **Land the DMD-001 freeze as a contract** (`L6`+`L20`): publish the 26 representation IDs as a shared JSON list + `conformance_pack.v1.json` entry + drift test; then `L16` wires `data_requirements` ports → **closes `B-014`**.
2. **Fix the gate before v2 emit** (`L7`): ecosystem-gated CI building `nirs4all-io-dagml` against the **local** `dag-ml-data` (path override), so representation/envelope drift is caught pre-publish. (Not "add to CI" — it is already in the workspace.)
3. **Image emission MVP** (`L7`, `IO-010`): extend `feature_axis()`/`source_representation()` to emit `gray_image`/`rgb_image` with `Height`/`Width`/`Channel` axes; add the `NdTensor`/`UriBackedPayload` payload variants (§2) so image bytes are referenced, not inlined. Confirm image-decode ownership = `nirs4all-formats` (OQ-1; `L8` request) before claiming support.
4. **Wire the Python emit** (`L7`): replace `api.py:185-186` `NotImplementedError` with a real `target="dag-ml-data"` path over the bridge, so a Python consumer can obtain an envelope.
5. **Converge the two envelope builders** (`L5`/`L7`/`L17`): make io own dataset-grain identity/relations; keep fold-scoping in `envelope.py`/dag-ml; reconcile `DatasetPackage` on-disk form with the `nirs4all-datasets` canonical layout. Gate every fixture on `dag-ml-data validate-envelope` + `dag-ml validate-data-binding`.

---

### Evidence index (read-only; no code/sync-board modified)
`nirs4all-io`: `git show HEAD:Cargo.toml`, `git show b54b48d -- Cargo.toml crates/nirs4all-io-dagml/Cargo.toml`, `crates/nirs4all-io-dagml/src/lib.rs`, `src/nirs4all_io/spec/{dataset_spec,enums}.py`, `src/nirs4all_io/api.py`, `CLAUDE.md`. `dag-ml-data`: `crates/dag-ml-data-core/src/{builtin_models,model,relation,coordinator}.rs`, `docs/contracts/coordinator_data_plan_envelope.schema.json`. `dag-ml`: `crates/dag-ml-core/src/data.rs`. `nirs4all`: `nirs4all/pipeline/dagml/envelope.py`, `nirs4all/data/config.py`. `nirs4all-datasets` `ae414964`, `nirs4all-formats` `89231b2` (canonical-layout / record-shape cross-checks). Only this file was written.
