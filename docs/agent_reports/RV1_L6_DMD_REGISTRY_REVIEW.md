# RV1 — Review of IMP-L6 `dag-ml-data` representation-ID freeze/publish (B-014 / DMD-001 slice 1)

**Reviewer:** RV1 (read-only) · **Lane:** L6 · **Worktree:** `/home/delete/nirs4all/_worktrees/L6-dmd-registry` (`dag-ml-data`)
**Branch:** `refactor/L6-dmd-registry` · **Base:** `347c15f`
**Scope reviewed:** the 6 staged files in this worktree + `docs/agent_reports/IMP_L6_DMD_REGISTRY.md`. No files edited, nothing staged/unstaged/committed.

## Final disposition: **`clean_with_notes`**

The slice is correct, additive, fully gated, and touches **no** lockstep/shared contract. I independently reproduced the entire green gate, regenerated the manifest and confirmed it is byte-identical to the committed file, and verified the cross-repo validator still passes against the real `dag-ml` sibling. **No correctness defects found.** Two low-severity advisory notes below; neither blocks.

---

## 1. What was reviewed (staged change set)

`git status --porcelain` shows exactly the 6 files the report claims, nothing stray, no untracked files:

| File | Type | Reviewed verdict |
|---|---|---|
| `crates/dag-ml-data-core/src/representation_registry.rs` | new (294 L) | correct, idiomatic, well-tested |
| `docs/contracts/representation_registry.v1.json` | new (923 L) | 26 entries, regenerable, byte-identical to CLI output |
| `crates/dag-ml-data-core/src/lib.rs` | +2 | flat `pub mod` + `pub use`, matches convention |
| `crates/dag-ml-data-cli/src/main.rs` | +14/−4 | `representation-registry` subcommand, matches `fingerprint-*` pattern |
| `docs/contracts/README.md` | +39 | accurate contract section |
| `docs/STATUS.md` | +12 | accurate "Implemented" entry |

## 2. Correctness verification

- **No new vocabulary** — confirmed. `representation_registry.rs` imports representation `pub const`s and `BUILTIN_DATA_MODELS` from `builtin_models.rs` and re-publishes them verbatim; it adds no new representation strings. Core data types (`RepresentationSpec`, `AxisKind`, …) are untouched.
- **26 builtins, 1:1 coverage** — `BUILTIN_DATA_MODELS` (builtin_models.rs:95–122) has 26 entries; the manifest has 26 `representation_id` blocks (verified by grep); `registry_covers_every_builtin_with_unique_ids` asserts `len == BUILTIN_DATA_MODELS.len()` plus id/key uniqueness and `representation_id == representation.id`.
- **MVP set 12 = 8 emitted + 4 pending** — manifest grep confirms exactly 8 `"emission":"emitted"` (signal_1d, signal_with_processings, feature_block_set, target_numeric/_categorical/_numeric_matrix/_categorical_matrix, sample_metadata) and 4 `"landed_pending_emit"` (rgb_image, gray_image, mc_image, multispectral_image). The `spectra_image_mvp_profile_is_consistent` test pins this split and the exact pending image set, and asserts the two groups are disjoint and every MVP id is a frozen representation.
- **Drift test is a real freeze** — `published_registry_matches_builtin_models` compares `serde_json::to_value(representation_registry())` against the `include_str!`-embedded manifest as parsed `Value`s. Any change to a builtin's id/key/modality/axes/dtype/container, or any added/removed/changed JSON key/value, fails the test until regeneration. (Pure object-key reordering is the only thing not caught — semantically irrelevant for JSON, and the canonical form is CLI-regenerable.)
- **Determinism** — built from `BUILTIN_DATA_MODELS` in array order; `RepresentationSpec`/`AxisSpec` contain no maps, so serialization is order-stable. The CLI uses `to_string_pretty` + `println!`; the committed file matches byte-for-byte (verified).
- **Wiring** — `lib.rs` flat re-export makes `representation_registry()` reachable from both the core crate and the `dag-ml-data` facade (`pub use dag_ml_data_core::*`); the CLI imports it from the facade. clap derives the `representation-registry` kebab subcommand (confirmed by running it).

## 3. Boundary / lockstep verification (the load-bearing claim)

The report's §5 claim — "no shared/lockstep contract touched" — is **accurate and verified**:

- `scripts/validate_contracts.py` validates a **fixed, enumerated** artifact list (coordinator envelope schema, feature-fusion schema, branch-view schema, fitted-adapter schema, `conformance_pack.v1.json`, parity oracle, fixtures, C header). It does **not** glob `docs/contracts/*.json`. The new `representation_registry.v1.json` is referenced nowhere in it.
- The cross-repo equality gate `local_pack == sibling_pack` (validate_contracts.py:1021) compares `conformance_pack.v1.json`, which is **unchanged** in this slice — so adding the new manifest cannot perturb it.
- Confirmed empirically: the cross-repo validator passes against the real sibling at `/home/delete/nirs4all/dag-ml` (see §4).

Deferring the conformance-pack/`validate_contracts.py` digest wiring to a joint L6+L20 `dag-ml` lockstep slice is the correct call — adding a pack digest here alone would break `local_pack == sibling_pack` until the sibling updates in tandem.

## 4. Validation commands run (read-only) & results

| Command | Result |
|---|---|
| `git status --porcelain` (+ untracked scan) | exactly the 6 expected files; no stray/untracked changes |
| `cargo test -p dag-ml-data-core representation_registry` | **5 passed**, 196 filtered out, exit 0 |
| `diff <(cargo run -q -p dag-ml-data-cli -- representation-registry) docs/contracts/representation_registry.v1.json` | **BYTE-IDENTICAL** (freeze is reproducible/idempotent) |
| `cargo fmt --all --check` | OK |
| `cargo clippy -p dag-ml-data-core -p dag-ml-data-cli --all-targets -- -D warnings` | clean, exit 0 |
| `python3 scripts/validate_contracts.py` (local) | pass — "sibling dag-ml checkout not present" path |
| `DAG_ML_REPO=/home/delete/nirs4all/dag-ml python3 scripts/validate_contracts.py` | **pass** — "validated dag-ml-data contract against dag-ml" |
| Manifest content cross-check (grep counts) | 26 representation entries; 12 mvp blocks (8 emitted / 4 pending) |

This reproduces every gate row the report claims (cargo fmt / clippy / targeted tests / CLI-vs-manifest byte parity / local + cross-repo validator). I did not separately re-run the full `cargo test --workspace` (263) — the targeted registry suite plus the workspace-wide gate claims were spot-validated and the touched surface is additive and isolated.

## 5. Findings (ordered by severity)

### LOW-1 (note) — cross-repo coordination metadata lives in `dag-ml-data-core`
`representation_registry.rs:41–64` and `:74–81` embed an MVP profile named `spectra_image` and per-id downstream-emission status that names `nirs4all-io` / `IO-010`. This is ecosystem-coordination metadata placed inside the data-contract **core** crate.

- **Not a boundary breach of the hard rule.** CLAUDE.md forbids NIRS-specific assumptions in core *types* and forbids owning ML phases / folds / OOF / selection — none of which happens here. The MVP annotation sits only on the new publish-layer wrappers (`RegisteredRepresentation` / `MvpStatus` / `MvpEmissionStatus`), the core types are untouched, and it adds no planning/selection logic.
- **Consistent with existing precedent.** `builtin_models.rs` already lives in core and already carries domain vocabulary (`nirs.signal_1d`, `raman_signal`, `ftir_signal`, modality `"nirs"`). The registry surfaces that same catalogue.
- **Why noted anyway:** it modestly increases domain coupling in the most domain-agnostic crate, and the `emitted`/`landed_pending_emit` labels are unverified coordination facts sourced from `IO_spec.md` (the report acknowledges this in §6). If the lockstep/L7 slice ever relocates emission-readiness toward the consumer side, this is the metadata to revisit. Advisory only.

### LOW-2 (note) — report §6 "one-line change" understates the image→emitted flip
The IMP report (§6, ~line 74) says flipping the 4 image ids to `emitted` is "a one-line change in `MVP_SPECTRA_IMAGE_PENDING` + regen." In practice the `spectra_image_mvp_profile_is_consistent` test hard-codes `emitted.len() == 8` / `pending.len() == 4` (representation_registry.rs:258–259) and the exact pending image `BTreeSet` (`:269–277`), so a flip also requires updating those assertions. This is a *good* property — the test freezes MVP composition — but the report's note is slightly optimistic. Documentation nuance only; no code change warranted.

## 6. Residual risks

- **Manifest is hand-regenerated, not build-time generated.** Mitigated by the drift test (fails loudly on un-regenerated edits). Confirmed reproducible (byte-identical regen). No silent drift possible.
- **Registry is not yet a CI-gated cross-repo contract** (no JSON Schema file, not in the conformance pack). Acknowledged and intentional for slice 1; the Rust drift test is the freeze until the L6+L20 lockstep wiring lands. Until then, parity with `dag-ml`'s `ModelInputSpec.accepted_representations` (`Vec<String>`) is documented but not machine-enforced.
- **MVP emission labels are coordination metadata, not runtime facts** — correct by design, but their accuracy depends on `IO_spec.md` staying in sync with actual `nirs4all-io` emission (tracked by `IO-010`).
- **Mild denormalization** — `representation_id` is duplicated at the entry top level and inside `representation.id`; kept consistent by the coverage test. Intentional for consumer convenience.

## 7. Conclusion

Self-contained, additive, correct, and green on every gate I independently reproduced (fmt, clippy `-D warnings`, targeted tests, byte-identical manifest regen, and the contract validator both locally and cross-repo against the real `dag-ml` sibling). No shared/lockstep contract is touched. The two findings are advisory notes, not change requests.

**Disposition: `clean_with_notes`.** Ready to merge as the first B-014/DMD-001 slice; carry LOW-1 (core-crate coordination coupling) and LOW-2 (report note nuance) forward as awareness items for the follow-up L6+L20 lockstep and L7 emission slices.
