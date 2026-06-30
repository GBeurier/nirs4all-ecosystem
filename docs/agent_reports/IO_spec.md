# IO_spec.md — Lane L7 (IO-SPEC) lock spec for `LOCK-IO`

**Agent:** IO-SPEC (lane `L7`) · **Mode:** READ-ONLY (only this file written)
**Decision source:** `DEC-IO-001` (accepted) — *`DatasetSpec v2` + `DatasetPackage` are **NET-NEW** but built by **extending** the existing `io->dag-ml-data` bridge, not from scratch.*
**Verified heads:** `nirs4all-io` `84ab189`, `dag-ml-data` `347c15f` (match sync board re-audit pass 2).
**Roadmap tasks covered:** `IO-001`, `IO-002`, `IO-003`, `IO-005`, `IO-010`, `IO-011` + the `B-014`/`DMD-001` representation-ID blocker.
**Backlog cross-ref:** `NIRS4ALL_IO_MULTIMODAL_BACKLOG.md` IDs `IO-MM-001/002/003/005/010/011` (= roadmap `IO-001/002/003/005/010/011`).

**Legend used throughout:**
`[LANDED]` = already exists at the verified heads (evidence cited). `[NET-NEW]` = must be designed/built under this lock. `[STALE-DOC]` = a confidence hazard to flag.

---

## 0. Confidence hazard (must be recorded before signing) — `[STALE-DOC]`

The repo disagrees with itself on whether the Rust / `dag-ml-data` emit ("Phase 2") is done:

- `nirs4all-io/CLAUDE.md:19` — "**Both phases are complete.**"; `:178` — "The Phase-2 gate is GREEN … don't reintroduce a `NotImplementedError` stub."
- `nirs4all-io/docs/STATUS.md` — "**Phase 2 (Rust rewrite) — COMPLETE**"; EPIC 10 (dag-ml-data emit) "✅ + Codex (+3 fixes)".
- `nirs4all-io/docs/PHASE2_GATE.md` — "**Verdict: GREEN — UNBLOCKED**".
- **BUT** `nirs4all-io/README.md` (Status §) — "see `docs/PHASE2_GATE.md` for why the Rust / `dag-ml-data` target (Phase 2) **stays gated**." and the README only declares **Phase 1** complete.

**Resolution (verified against code, code wins):** the bridge **is implemented and tested** — `crates/nirs4all-io-dagml/src/lib.rs` defines `to_dag_ml_data()` (`:598-603`) + `build_dag_ml_data_parts()` (`:398-595`) with 4 passing unit tests (`:664-771`). So STATUS/PHASE2_GATE/CLAUDE.md are correct; **`README.md` "stays gated" is STALE**. Note for A0: the crate is **workspace-EXCLUDED** (`CLAUDE.md:50-51,126`) and path-deps `dag-ml-data`, so `cargo test --workspace` never builds it — the "green" is real but is *not* exercised by the default io gate. Treat the README line as the trust hazard; everything else lines up.

---

## 1. `IO-001` — `DatasetSpec v2` source model `[NET-NEW schema, extends v1]`

### What exists today — v1 `[LANDED]`
`DatasetSpec` (`src/nirs4all_io/spec/dataset_spec.py:523-560`, `SCHEMA_VERSION = 1`, mirrored byte-for-byte in the Rust core `crates/nirs4all-io-core/src/spec/`). The v1 source model is **table/lookup-centric**:

- `SourceSpec` (`dataset_spec.py:264-339`): `id`, `role` (`Role`: features/targets/metadata/weights/ignore/mixed — `spec/enums.py`), `kind` (`SourceKind`: `table`|`lookup`), `modality` (`Modality`: spectroscopy/markers/metadata/image — `spec/enums.py`; Rust `spec/enums.rs:114-117`), `input`, `merge` (`MergeMode`: concat_samples/concat_features/by_key/none), `partition`, `key`, `columns` (role selectors), `join`, `params` (`LoadingParams`), `variations` (pre-computed preprocessing variants → named processings).
- Multi-source + joins `[LANDED]`: `JoinSpec` (`dataset_spec.py:189-221`) with `Cardinality` (1:1 / m:1 / 1:m) and `Coverage` (complete/warn/drop/error); relational join engine `materialize/join.py`.
- Identity `[LANDED, partial]`: `SampleIndex` (`dataset_spec.py:345-384`) already carries `observation_id`, `repetition_id`, `group_id`, `key`, plus replicate-suffix `derive`. **These are parsed and carried but NOT materialized** into `SpectroDataset` (host has no slot — `docs/ROADMAP.md` "SpectroDataset extension" §).

> Key fact for scoping: `Modality.image`/`markers` are **already in the vocabulary** but **dead** — `grep` finds `image` only in `spec/enums.py` + JSON schema, **never in `materialize/` or `infer/`** (`crates/nirs4all-io-core/src/materialize/assemble.rs` has zero modality branching). So image is genuinely unbuilt.

### v2 additions `[NET-NEW]` (per `IO-MM-001`, aligned to `dag-ml-data` `SourceDescriptor`)
Extend `SourceSpec` (additive; v1 specs must round-trip byte-identical — that is the acceptance bar) with fields that map 1:1 onto the dag-ml-data `SourceDescriptor` (`dag-ml-data-core/src/model.rs`):

| v2 field on `SourceSpec` | Type / vocabulary | Maps to dag-ml-data |
|---|---|---|
| `type_id` | open string, default derived from representation | `SourceDescriptor.type_id` (`TYPE_DENSE_SIGNAL`, `TYPE_IMAGE_RGB`, …) |
| `native_representation` | representation-ID string (§5) + optional axis overrides | `SourceDescriptor.native_representation` (`RepresentationSpec`) |
| `granularity` | `per_sample` \| `per_sample_repeated` \| `per_sample_sequence` \| `per_sample_set` \| `per_group` \| `per_target` | `SourceGranularity` (`model.rs`, same 6 variants — already exists) |
| `payload_kind` | `table` \| `records` \| `nd_tensor` \| `sequence` \| `genotype_matrix` \| `mask` \| `uri_manifest` | drives §2 payload variant (no dag-ml-data equivalent; io-internal) |
| `shape_contract` | optional axis-size contract | `SourceDescriptor.shape_contract: Option<ShapeContract>` (already exists) |
| `axes` | optional explicit `AxisSpec[]` | `RepresentationSpec.axes` |
| `sidecars` / `annotations` | declared sidecar files + adapter id | io-internal; resolves via formats facade |
| `modality` | **widen** closed enum → open string (keep current 4 as known values) | `SourceDescriptor.modality: String` (already open string downstream) |

**Migration rule `[NET-NEW]`:** deterministic v1→v2 lift — a v1 `kind:table, role:features, modality:spectroscopy` source lifts to `type_id:dense_signal, native_representation:signal_1d, granularity:per_sample(_repeated if repetition set), payload_kind:table`. v1 goldens stay byte-identical through the v1 API; v2 is a superset behind an explicit constructor/flag.

---

## 2. `IO-002` — `DatasetPackage` / `AssembledDataset v2` (incl. payload manifest) `[NET-NEW]`

### What exists today `[LANDED]`
`AssembledDataset` (Rust `crates/nirs4all-io-core/src/materialize/assemble.rs:74-86`) is the target-agnostic seam: `name`, `task_type`, `signal_type`, `n_sources`, `blocks: IndexMap<String, PartitionBlock>`, `folds`, `repetition`, `aggregate`, `warnings`, `audits`. `PartitionBlock` (`assemble.rs:58-72`) carries `x: Vec<Matrix>`, `feature_headers`, `header_units`, `signal_types`, `processings: Vec<Vec<(String, Matrix)>>`, `y`, `y_headers`, `y_categorical`, `metadata: Option<Frame>`, `weights`. **`Matrix` is a dense row-major `Vec<f32>`** (`frame.rs:184-190`).

**Structural limit:** every payload is forced into an inline `f32` matrix. That is fine for 1-D spectra but **wrong for images/cubes** (wrong dtype — `uint8`/`int32`/`bool`; wrong rank — H×W×C; and pathological size if inlined into canonical JSON).

### v2 package `[NET-NEW]` (per `IO-MM-002`)
`DatasetPackage` = target-agnostic container of **typed payload blocks** + a **payload manifest**, replacing the "everything is a `Matrix`" assumption. Required payload variants (one Rust enum, serde-tagged):

- `FeatureMatrix` — dense numeric matrix (the current `Matrix` path; spectra/tabular). `[LANDED form, re-homed]`
- `SpectralRecordSet` — decoded `nirs4all-formats` records (already an input payload type: `SourcePayload::Records(Vec<Value>)`, `assemble.rs:40-49`). `[LANDED input, NET-NEW as package payload]`
- `NdTensor` — image/cube/tensor: `dtype`, `shape`, `axis_names`, `observation_ids`. `[NET-NEW]`
- `SequenceBlock` — fixed/ragged time series. `[NET-NEW]`
- `GenotypeMatrix` — variant/dosage, descriptor-first. `[NET-NEW]`
- `MaskBlock` — segmentation/ROI/label mask. `[NET-NEW]`
- `MetadataTable` / `TargetTable` — already separable from `PartitionBlock`. `[LANDED form]`
- `UriBackedPayload` — **the payload manifest**: `{uri, dtype, shape, axes, content_hash, byte_len, codec}` so large image/cube bytes are referenced, never embedded. `[NET-NEW]`

**Payload manifest (the load-bearing v2 contract) `[NET-NEW]`:** a per-block manifest row tying each payload to (a) its representation ID, (b) a `content_hash` (reuse the resolver's existing content hash from `resolve/resolver.py`), and (c) either inline bytes (small) or a URI ref (large). This is what lets `IO-006` populate dag-ml-data `NumericFeatureBufferStore` / `NdTensorStore` and lets fingerprints detect tampering. **Acceptance:** current `AssembledDataset` representable losslessly as a v2 package; canonical-JSON summary stable for goldens; no large bytes in JSON.

---

## 3. `IO-003` — identity / relation propagation → `SampleRelationTable` `[NET-NEW logic over LANDED contract]`

### Target contract `[LANDED]`
dag-ml-data already owns the full relation contract:
- `SampleRelation` (`dag-ml-data-core/src/relation.rs`): `observation_id`, `sample_id`, `source_id?`, `target_id?`, `group_id?`, `origin_id?`, `repetition_id?`, `augmented`, `excluded`, `metadata`, `tags`, `augmentation?`.
- `SampleRelationTable { rows }` → `coordinator_relations_from_sample_table()` (`coordinator.rs:283-329`) resolves `origin_id` (an **observation** ref, augmentation lineage) to `origin_sample_id`, sorts by `observation_id`, and validates. Identifier rule (`ids.rs:7-30`): ASCII alnum + `_-.`, 1..128 bytes.

### What the bridge does today `[LANDED, partial]`
`build_dag_ml_data_parts()` (`nirs4all-io-dagml/src/lib.rs:417-483`) derives identity from the **repetition key** only:
- if a `repetition` column is present & aligned in every partition (`:421-428`) → `sample_id` = sanitized repetition value, `observation_id = "{sample}.obs{n}"`, `group_id = sample`, `repetition_id = "rep.{n}"`, `granularity = PerSampleRepeated`;
- else → each row is its own 1:1 sample (`obs.{i}` / `s.{i}`), no group, `PerSample`.
- **Always** `source_id: None`, `origin_id: None`, `augmented: false`, `excluded: false` (`:465-481`).

### v2 gaps `[NET-NEW]` (per `IO-MM-003`)
- **`source_id` per relation row** — needed once a sample has >1 modality/source (image + spectra for the same sample). Today it is unconditionally `None`.
- **Multiple observations per sample across modalities** — the obs-counter is per repetition key within one block; v2 must let an image obs and a spectra obs share a `sample_id` with distinct `observation_id`s and distinct `source_id`s.
- **`origin_id` / `augmented`** — reserved for augmentation lineage (origin must reference an existing observation id; `coordinator.rs:300-311` enforces this). io should leave these empty until an augmentation profile exists, but the carrier must be first-class, not hard-coded `false`.
- **Explicit, fingerprinted row-position fallback** — when no key exists, the "row index = identity" decision must be recorded as a diagnostic, not silent.
- **`SpectroDataset` becomes a projection of the relation model**, not the source of identity truth.

---

## 4. Emission to `dag-ml-data`: already done vs to extend

### `[LANDED]` — the bridge (this is the `DEC-IO-001` "extend, don't rewrite" anchor)
`crates/nirs4all-io-dagml/src/lib.rs` already maps `AssembledDataset` → `CoordinatorDataPlanEnvelope` via `CoordinatorDataPlanEnvelope::from_parts(&schema, plan, relations)` (`:601-602`; envelope self-computes the 3 fingerprints + validates, `coordinator.rs:216-238`). It emits:
- `DatasetSchema` with per-X-source `SourceDescriptor`s (`:486-528`) — logical feature sources = `b0.x.len()`, not the partition-table count (`:411-416`, a deliberate fix);
- spectral `RepresentationSpec` via `signal_1d` / `signal_with_processings` (`:213-239`), nm→`Wavelength`, cm⁻¹→`Wavenumber`, else `Feature` (`feature_axis`, `:90-108`);
- targets: numeric/categorical, single + uniform-matrix (`:280-316`);
- metadata: `sample_metadata` + `MetadataSchema` (`:355-396`);
- `DataPlan`: `Materialize` per source, `Join` → `feature_block_set` when multi-source (`:551-587`);
- `SampleRelationTable` (§3). **io deliberately does NOT emit `FoldSet`/`DataBinding`** — those are dag-ml's domain (`lib.rs:11-12`, `PHASE2_GATE.md`).

### `[NET-NEW]` — to extend (roadmap `IO-005` / `IO-MM-005`)
- **Generalize beyond spectroscopy:** today `source_representation()` only ever produces `signal_1d`/`signal_with_processings`. Add image (`gray/rgb/mc/multispectral_image`), then cube/series/genotype/mask emission, dispatched by the v2 `payload_kind`/`native_representation`.
- **`feature_axis()` is spectra-only** (`:90-108`): for image/cube sources it must emit `Height`/`Width`/`Channel` axes (`px` unit) instead of forcing a wavelength/feature axis.
- **Carry `source_id` into relations** (§3) so multi-modal-per-sample plans validate.
- **Payload export (`IO-006`):** beyond the envelope, populate `NumericFeatureBufferStore` (numeric) / an N-D tensor store (image/cube) / target & metadata tables, tied by the §2 payload manifest. `[NET-NEW]` (in-memory provider exists on the dag-ml-data side, `DMD-003`, audit-don't-recreate).
- **Validation gate:** every new fixture must pass `dag-ml-data validate-envelope` **and** `dag-ml validate-data-binding` (the latter wraps the envelope as an `ExternalDataPlanEnvelope` behind a fixture `DataBinding`, `PHASE2_GATE.md` item 6).

---

## 5. `DMD-001` representation IDs — PROPOSAL (unblocks `B-014`)

**`B-014` (open):** *"Representation IDs manquants (`L6`/`L7`) bloquent les ports `data_requirements` du `ControllerManifest`."* Next action on the board: *"Definir representation IDs stables (`DMD-001`)."*

**Core finding — `B-014` is largely a publish/freeze problem, not an invention problem `[LANDED]`:** the stable representation-ID catalog **already exists** as `pub const` string IDs + a `BuiltinDataModel` enum + constructors in `dag-ml-data-core/src/builtin_models.rs:36-62` (constants), `:64-93` (enum), `:518-799` (constructors). 26 builtins, each with a frozen string id, `type_id`, rank, axes and dtype. The backlog confirms: *"`dag-ml-data` already has the right vocabulary … The missing piece is not the schema vocabulary; it is the production dataset assembly path"* (`NIRS4ALL_IO_MULTIMODAL_BACKLOG.md:14-18`).

**Proposal for `B-014`:** **adopt the existing `builtin_models.rs` string IDs verbatim as the canonical `DMD-001` registry**, freeze them as a cross-repo contract (so `L16` `ControllerManifest.data_requirements` ports reference them by string), and have io emit them. No new strings are needed for the MVP. The only `DMD-001` deliverable that is `[NET-NEW]` is the **frozen published list** + a drift test; the IDs themselves are landed.

### Representation IDs the **spectra + image MVP** requires (the `B-014` answer)

| Representation ID | dag-ml-data const · `builtin_models.rs` | Axes / rank | Status |
|---|---|---|---|
| `signal_1d` | `REPRESENTATION_SIGNAL_1D:36` · ctor `:518` | sample, wavelength[nm] · r2 | `[LANDED]` emitted by bridge |
| `signal_with_processings` | `:37` · ctor `:531` | sample, processing, wavelength[nm] · r3 | `[LANDED]` emitted by bridge |
| `feature_block_set` | `:42` · ctor `:579` | sample, block, feature · r3 | `[LANDED]` emitted (multi-source join) |
| `target_numeric` | `:56` · ctor `:748` | sample · r1 | `[LANDED]` emitted |
| `target_categorical` | `:57` · ctor `:758` | sample · r1 | `[LANDED]` emitted |
| `target_numeric_matrix` | `:58` | sample, target · r2 | `[LANDED]` emitted |
| `target_categorical_matrix` | `:59` | sample, target · r2 | `[LANDED]` emitted |
| `sample_metadata` | `:55` · ctor `:735` | sample, field · r2 | `[LANDED]` emitted |
| `gray_image` | `:48` · ctor `:648` | sample, height[px], width[px] · r3 | `[NET-NEW]` io must emit |
| `rgb_image` | `:47` · ctor `:633` | sample, height[px], width[px], channel=3 · r4 | `[NET-NEW]` io must emit |
| `mc_image` (multichannel) | `:49` · ctor `:662` | sample, height, width, channel · r4 | `[NET-NEW]` io must emit |
| `multispectral_image` | `:50` · ctor `:677` | sample, height, width, band · r4 | `[NET-NEW]` io must emit |

So: **MVP needs 12 representation IDs; 8 are already emitted by the bridge, 4 (the image set) are landed in dag-ml-data but not yet emitted by io.** Required axis kinds all exist: `AxisKind` (`model.rs`) = Sample/Feature/Processing/Time/Height/Width/Channel/Node/Edge/Variant/Token/Target/Wavelength/Wavenumber/Frequency/Depth.

### Post-MVP / bounds (declare the IDs now so `data_requirements` ports can reference them; emission deferred)
`cube_hwb` (= `hyperspectral_cube`, `:51-52`), `segmentation_mask` (`:53`), `roi_mask` (`:54`), `series_mv`/`climate_series_mv` (`:43-44`), `variant_matrix`/`dosage_matrix` (`:45-46`), `raman_signal`/`ftir_signal` (`:38-39`), `tabular_numeric`/`tabular_mixed` (`:40-41`), `mass_spectrum` (`:60`), `text_raw`/`text_token_ids` (`:61-62`) — all `[LANDED]` in dag-ml-data, emission `[NET-NEW]`/deferred.

---

## 6. Profiles in scope

**MVP first (M1) — emit `io → dag-ml-data → dag-ml` end-to-end:**
- `IO-011` Native spectra + reference table `[mostly LANDED]` — the existing vendor-corpus path (resolver sidecar grouping + join by filename stem) already feeds the spectra bridge; harden into a generic native-spectra profile; repeated measurements → observation/repetition relations.
- `IO-010` Image folder profile `[NET-NEW]` — `images/* + labels.csv (+ annotations/*)`; pair image↔sample by filename stem or manifest column; emit `rgb_image`/`gray_image` + a target table; produce `NdTensor` or `UriBackedPayload` (manifest) image payloads. **VDX annotation = spike** (no VDX reader found in any repo — `IO-MM-010` note; do not claim support).

**Bounds / diagnostics only (post-MVP M2–M3), declared not built:**
- `IO-012` hyperspectral cube → `cube_hwb` (ENVI `.hdr` sidecar; large-payload manifest by default).
- `IO-013` time-series → `series_mv` (long/wide/fixed; ragged = allowed-manifest or explicit refusal).
- `IO-014` genotype → `variant_matrix`/`dosage_matrix` **descriptor-first** (config-only; no genotype-byte parsing claim).
Each bound profile must fail with a **clear dataset-level diagnostic**, never a parser panic, when sidecars/readers are missing.

---

## 7. Proposed `LOCK-IO` content (for A0 to sign)

Signing `LOCK-IO` ratifies these as the frozen cross-repo contracts for `DatasetSpec v2` / `DatasetPackage` (interface watchlist owners `L7`+`L6`):

1. **`DatasetSpec v2` = additive superset of v1** (`SCHEMA_VERSION` bumps to 2; v1 specs round-trip byte-identical through the v1 API — non-negotiable acceptance bar). New fields: `type_id`, `native_representation`, `granularity`, `payload_kind`, `shape_contract`, `axes`, `sidecars`/`annotations`, open-string `modality`. Deterministic v1→v2 lift documented. `[NET-NEW]`
2. **`DatasetPackage` (= `AssembledDataset v2`)** = typed payload variants + a **payload manifest**; large payloads are URI/handle-referenced with `content_hash`, never embedded in JSON; current `AssembledDataset` is a lossless subset. `[NET-NEW]`
3. **Identity is the `SampleRelationTable`**, carried through assembly with first-class `source_id`/`observation_id`/`group_id`/`origin_id`/`repetition_id`/`augmented`/`excluded`; `SpectroDataset` is a **projection**. Row-position fallback is explicit + fingerprinted. `[NET-NEW logic, LANDED target contract]`
4. **Emission extends the existing bridge** `crates/nirs4all-io-dagml/src/lib.rs` (`DEC-IO-001`) — same `CoordinatorDataPlanEnvelope::from_parts` seam; io still **never** emits `FoldSet`/`DataBinding`. `[LANDED seam]`
5. **`DMD-001` registry = the existing `dag-ml-data builtin_models.rs` string IDs, frozen and published**; the MVP set is the 12 IDs in §5; `ControllerManifest.data_requirements` ports (`L16`) reference these strings → **closes `B-014`**. Freeze enforced by a cross-repo drift test (lockstep with `L6`/`L20`). `[LANDED IDs, NET-NEW freeze]`
6. **MVP scope = spectra (`IO-011`) + image (`IO-010`)** validating through `dag-ml-data validate-envelope` + `dag-ml validate-data-binding`; cube/series/genotype are bounded profiles with diagnostics. `[mixed]`

---

## 8. Open questions + gates

**Open questions (need an arbitration / `DEC-*` before build):**
- **OQ-1 (image decode ownership):** does generic image decode (JPG/PNG/TIF) live in `nirs4all-io` facade (via the Rust `image` crate) or a `nirs4all-formats` extension? Affects package size + WASM. `IO-MM-010`/risks §. **Recommend:** formats owns it (boundary rule: "parsers live only in Rust formats"), io only orchestrates — but formats coverage must be confirmed (`L8` request).
- **OQ-2 (payload manifest format):** exact schema + compatibility policy for `UriBackedPayload` (codec, chunking, hash algo — reuse resolver content-hash?). Milestone M0 exit criterion.
- **OQ-3 (modality widening):** widen `Modality` enum → open string now (v2) or keep closed + add per representation? Downstream `SourceDescriptor.modality` is already `String`, so widening is low-risk.
- **OQ-4 (`source_id` granularity in relations):** per-row `source_id` for multimodal-per-sample needs a naming convention shared with `DMD-004`; coordinate with `L6`.
- **OQ-5 (VDX spike):** unidentified annotation dialect — needs dialect/owner/parser decision before `IO-010` annotation support is claimed.

**Gates / dependencies:**
- `LOCK-IO` spec must merge into `nirs4all-ecosystem` **before** any `L7` implementation (Vague-1 rule).
- `L7` depends on `DMD-001` minimal (§5 — already satisfiable from landed IDs) + stable `nirs4all-formats` readers (`L8`).
- Any change to the shared `coordinator_data_plan_envelope` schema / representation-ID registry is a **lockstep** change with `dag-ml`/`dag-ml-data` (`LOCK-LOCKSTEP`, `validate_contracts.py` green both sides).
- **CI hazard to fix:** `nirs4all-io-dagml` is workspace-excluded → the bridge is *not* covered by `cargo test --workspace`. The MVP emit work should add an ecosystem-gated CI job that builds + tests the bridge against the sibling `dag-ml-data`, or the "green" emit can silently rot.
- Re-sync `README.md` Status § (the `[STALE-DOC]` from §0) when the lock lands.
