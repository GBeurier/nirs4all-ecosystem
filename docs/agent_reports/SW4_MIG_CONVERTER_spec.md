# SW4 — `LOCK-MIG` concrete spec: `nirs4all-tools` legacy converter

**Agent:** SW4 (second wave, L18 — Tools/migration legacy)
**Lane / lock:** `L18` / `LOCK-MIG`
**Decision source:** `DEC-MIG-001` (accepted — `ARB-006`=A: new repo, offline/one-way/no-in-place, absorbs `pipeline/storage/migration.py`, legacy out of runtime V1)
**Supersedes (into a signable contract):** `A8_A8-migration.md` (audit/draft). This document freezes A8's drafts into the concrete `LOCK-MIG` vocabulary, CLI, policy, fixtures and gates.
**Date:** 2026-06-30
**Mode:** read-only audit + spec. No implementation code, no `PARALLEL_REFACTORING_SYNC.md` edit (A0 owns the board). Only this file was written.
**Method:** CodeGraph + direct `Read`/`Grep`/`rtk` against working-tree heads (`nirs4all e41362b4`, `dag-ml f58d7bf`, `nirs4all-studio 2ccbf68`). Every code claim below is `path:line` verified, not CodeGraph-only.

---

## 0. One-line thesis

`nirs4all-tools` resolves the V1 contradiction — **"no legacy reader code in the runtime"** vs **"never lose old predictions/pipelines/workspaces"** — by being an **offline, one-way, no-in-place** converter that lands legacy stores into the **already-readable `nirs4all-workspace-v2`** shape (current SQLite v2 + Parquet sidecars), preserving everything it cannot lower as **byte-checksummed opaque provenance**. Because the Phase-1 target is the format the V1 runtime *already* reads, V1 keeps zero legacy-reader code, yet no user data is lost.

---

## 1. Scope and the V1 contradiction it resolves

Two V1 constraints (roadmap §3) appear to conflict:

- *"Le code legacy de lecture des anciens workspaces/bundles ne reste pas dans le runtime V1."*
- *"les utilisateurs ne perdent pas leurs predictions/pipelines existants."*

The resolution is a **layering split**, not a compromise:

| Concern | Owner in V1 | Evidence today |
|---|---|---|
| Read DuckDB `store.duckdb` / `prediction_arrays` | **`nirs4all-tools` only** | `migration.py:38-42` (optional `duckdb`), `:228`, `:560` |
| Read legacy filesystem manifests / `*.meta.parquet` / `*_predictions.json` | **`nirs4all-tools` only** (lift from Studio `workspace_scanner.py`) | `workspace_scanner.py:445,501,751,835,852` |
| Auto-migrate-on-open (DuckDB→SQLite, arrays→Parquet) | **REMOVED from runtime; replaced by tool** | `workspace_store.py:278-285`, `store_schema.py:267,803-804` |
| Read `nirs4all-workspace-v2` (SQLite v2 + Parquet) | **runtime V1 (unchanged)** | `store_schema.py:28` `SCHEMA_VERSION=2`; `array_store.py` |
| Inspect `.n4a` / native results | runtime V1 (read), tool (preserve opaque) | `bundle/loader.py`; `native_results.py:363` |

**Net effect:** the legacy *readers* and the auto-migration triggers leave the runtime and live only in the bounded, support-windowed tool. The runtime keeps only the v2 reader it already has. Old data survives because the tool converts it **into** v2 offline.

**Out of scope for this lock:** flipping `DEFAULT_ENGINE` (`LOCK-DROP`/`L19`), the native dag-ml export path (`A3` DML-008), and the actual *removal* of `migration.py` from `nirs4all` (a coordinated `L18`+`L19` change executed only after the tool ships and `LOCK-MIG` is signed).

---

## 2. `nirs4all-tools` repo shape

- New sibling repo `nirs4all-tools/` (Python, packaging `pyproject.toml`, console entry point `nirs4all-tools`). NOT in `nirs4all` runtime deps.
- Optional extras: `duckdb`, `pyarrow`/`polars` pinned **in the tool**, not in `nirs4all` core. `duckdb` is required **only** for a DuckDB-kind source.
- `nirs4all` is a *read peer*: the tool may `import nirs4all` for **target-schema authorship** (`create_schema`, `ArrayStore` writer) and version stamping, but never invokes runtime auto-migration paths.
- **Absorb (lift pure read/normalize helpers, drop the in-place behaviors)** from `migration.py`:
  carry forward — DuckDB read-only connect pattern (`:228`,`:454`,`:560`), FK-safe table order `_MIGRATION_TABLES` (`:493`), `_sqlite_compatible_value` (`:90`), `ArrayStore.save_batch` record shape (`:368`), lock concept (`:143`), `MigrationReport` counters (`:48`).
  drop/supersede — every in-place write listed in §4.
- **Support window** (`TOOL-011`): the tool migrates legacy formats for an announced number of releases; the runtime carries none of it. The window is recorded in the manifest `tool` block and in repo docs.

---

## 3. No-in-place policy (hard, pre-flight enforced)

The single most important contract. Today's code violates it in five places — all must be **superseded, not reused**:

| # | In-place behavior to eliminate | Evidence |
|---|---|---|
| 1 | `WorkspaceStore.__init__` auto-runs `migrate_duckdb_to_sqlite`, renames `store.duckdb`→`.bak` | `workspace_store.py:278-285`; `migration.py:646-649` |
| 2 | `create_schema(workspace_path=...)` → `_auto_migrate_prediction_arrays` drops the source table | `store_schema.py:614,803-804`; `:305,371` |
| 3 | `migrate_arrays_to_parquet` writes Parquet into the **source** workspace, `DROP TABLE` + `VACUUM` | `migration.py:270,296-297` |
| 4 | Error rollback `shutil.rmtree(arrays_dir)` can delete a **pre-existing** user `arrays/` | `migration.py:289,308` |
| 5 | Verification samples ~1 % of rows, only `y_true`/`y_pred` | `migration.py:382-384,397-424` |

**Tool rules (enforced before any byte is written):**

1. **Source is read-only.** SQLite via `file:<path>?mode=ro&immutable=1`; DuckDB via `connect(..., read_only=True)`; ZIP/Parquet/JSON opened read-only. **Never** construct `WorkspaceStore`, **never** call `create_schema` against the source, **never** pass `workspace_path=` into source connections.
2. **`--output` is mandatory and disjoint.** `realpath(output)` must not equal, contain, or be contained by `realpath(input)`. Aliasing → refusal (exit `40`).
3. **Output must be empty** unless `--resume` is given *and* a prior tool-written manifest in the output validates (same `source_fingerprint`, same `tool_schema_version`).
4. **Output rollback deletes only what the tool created**, only the run's own output subtree, and only if the tool created it this run (never a pre-existing directory — fixes violation #4).
5. **Whole-source-tree integrity assertion.** The tool snapshots `(path, size, mtime_ns)` for the entire source tree before and after every run (incl. failure/abort paths) and asserts byte-for-byte equality; a mismatch is an internal error (exit `70`) and a test gate (§14 G1).

---

## 4. Source schema detection (no `WorkspaceStore`, read-only stat-first)

Detection is filesystem-stat + read-only-parse first, mirroring A8's detector. `source_kind` ∈:

| `source_kind` | Detect by | Versioned by |
|---|---|---|
| `duckdb-workspace` | `store.duckdb` present | DuckDB table set; presence of `prediction_arrays` |
| `sqlite-workspace-v2` | `store.sqlite` present | `PRAGMA user_version` (`store_schema.py:28` → expect `2`) |
| `sqlite-workspace-legacy-arrays` | `store.sqlite` **with** a `prediction_arrays` table | `user_version` + table presence (`store_schema.py:296`) |
| `fs-runs-v2` | `runs/<run_id>/run_manifest.yaml` | manifest schema marker (`workspace_scanner.py:445,648`) |
| `fs-runs-legacy` | `runs/<dataset>/<pipeline_id>/manifest.yaml` | manifest fields (`workspace_scanner.py:751,771`) |
| `loose-predictions` | root `*.meta.parquet` / `*_predictions.json` | column/field probe (`workspace_scanner.py:835,852`) |
| `n4a-bundle` | `*.n4a` (ZIP) | `manifest.json["bundle_format_version"]` / `BUNDLE_FORMAT_VERSION="1.0"` (`generator.py:54,444`) |
| `n4a-py-bundle` | `*.n4a.py` | embedded header marker |
| `native-results-v1` | dir with `manifest.json`+`score_set.json`+`predictions.parquet` | `manifest["schema_version"]` (`native_results.py:58` `MANIFEST_SCHEMA_VERSION=2`) |

A workspace is a **set** of these (e.g. `duckdb-workspace` + `arrays/` + `.n4a` exports + loose parquet). Detection emits one `input_inventory` entry per discovered artifact with its `source_kind` + `source_detected_version`.

**Forward-version refusal:** if any source artifact declares a version **newer** than the tool supports, the tool refuses that artifact (exit `20`) rather than guess — symmetric with dag-ml's own policy (§5) and with `store_schema.py:599-602` (`existing_version > SCHEMA_VERSION` raise).

---

## 5. Target schema policy

Two targets, **phased**. The lock signs Phase 1 now; Phase 2 is gated.

### Phase 1 — `nirs4all-workspace-v2` (sign now)

- The current readable shape: `store.sqlite` at `SCHEMA_VERSION=2` (`store_schema.py:28`) authored via `nirs4all.pipeline.storage.store_schema.create_schema` **against the OUTPUT path only**, plus `arrays/<dataset>.parquet` via `ArrayStore`, plus opaque-preserved files.
- Chosen because it **exists today** and the V1 runtime reads it with **zero new code**. This is what makes "no legacy reader in runtime" and "no data loss" simultaneously true.
- Tables copied in FK-safe order (`projects, runs, pipelines, chains, predictions, artifacts, logs`; `migration.py:493`); arrays landed as full-fidelity Parquet (all of `y_true/y_pred/y_proba/sample_indices/weights` + row metadata — not the legacy 2-column sample).

### Phase 2 — `native-results-v1` / dag-ml (gated)

Blocked until `LOCK-MIG` signed **and** `LOCK-REL` + dag-ml V1 schema decisions land **and** `A3` DML-008 native export exists. The target must obey dag-ml's **`SchemaMigrationPolicy`** verbatim (`bundle.rs:51-119`):

- version `0` invalid (`bundle.rs:54-62`);
- **future** versions refused (`version > current_version` → error, `:106-111`);
- an **older** version is accepted **only** when an `automatic_migrations` edge is declared (`:112-117`).
- Today `EXECUTION_BUNDLE_SCHEMA_VERSION=1` and `PREDICTION_CACHE_PAYLOAD_SCHEMA_VERSION=1` with **empty** `automatic_migrations` (`bundle.rs:20-21,128`) → **no legacy→bundle migration edge exists yet**. The tool MUST NOT mint `ExecutionBundle`s until one does.

A native target may be claimed **replayable** only when every dag-ml invariant is reconstructible and validates (A8 list, confirmed against contracts): graph/campaign/controller fingerprints, selected variant id, prediction requirements + caches, data requirements, artifact refs + content fingerprints, optional `ScoreSet` with matching `plan_id` (`score_set.schema.json:7-16`). Otherwise the tool preserves pipeline/artifact metadata as **opaque provenance** and reports `replayable:false`.

---

## 6. CLI surface

```
nirs4all-tools --version
nirs4all-tools legacy inspect  <input> [--format json|text] [--report PATH]
nirs4all-tools legacy migrate  <input> --output DIR --target nirs4all-workspace-v2
                                       [--manifest PATH] [--report PATH] [--id-map PATH]
                                       [--checksums sha256]
                                       [--dry-run | --verify]
                                       [--strict | --best-effort]
                                       [--copy-only] [--resume] [--trusted-load-joblib]
nirs4all-tools legacy verify   <output-dir> --manifest PATH [--report PATH]
```

Phase-2 form (gated): `--target native-results-v1`.

**Mode semantics:**

| Mode | Reads source | Writes output store | Writes report/manifest | Loads joblib |
|---|---|---|---|---|
| `inspect` | yes (ro) | no | optional (`--report`, outside source) | no |
| `migrate --dry-run` | yes (ro) | no | manifest-preview + report only, to explicit paths outside source | no |
| `migrate` (default `--best-effort`) | yes (ro) | yes (new/empty/`--resume`) | yes | no (opaque) unless `--trusted-load-joblib` |
| `migrate --strict` | yes (ro) | yes; abort on first unsupported | yes (partial, status=`unsupported_input`) | as above |
| `migrate --verify` | yes (ro) | yes, then full §13 verify | yes (incl. `verification_summary`) | as above |
| `migrate --copy-only` | yes (ro) | yes — copy + checksum + manifest, **no schema transform** | yes | no |
| `verify` | **no source read** | no | yes | no |

`--copy-only` is the safety hatch: a faithful checksummed copy + manifest with **no** interpretation, for unknown/partly-unsupported workspaces a user still wants archived.

**Exit codes** (the five A8 classes, made concrete):

| Code | Meaning |
|---|---|
| `0` | success, no warnings |
| `10` | migrated-with-warnings (best-effort preserved opaque / non-fatal skips) |
| `20` | unsupported-input (unknown/forward-version source, or strict-mode unsupported item) |
| `30` | verification-failed |
| `40` | refused-by-policy (in-place/aliased output, non-empty output without `--resume`) |
| `70` | internal-error (incl. source-tree integrity assertion failure) |

---

## 7. Manifest vocabulary — `legacy_migration_manifest.v1`

Durable JSON sidecar (default `migration-manifest.json`), schema `$id` `nirs4all-tools/contracts/legacy_migration_manifest.v1.json`. The **complete inventory + map**; the audit trail of record.

```jsonc
{
  "schema_version": 1,
  "tool":   { "name": "nirs4all-tools", "version": "x.y.z",
              "support_window": "…", "created_at": "…", "completed_at": "…" },
  "source": { "path": "…", "fingerprint": "sha256:…",          // tree fingerprint (no-in-place anchor)
              "kinds": ["duckdb-workspace", "…"],
              "detected_versions": { "duckdb-workspace": null, "sqlite": 2, "n4a": "1.0" } },
  "target": { "kind": "nirs4all-workspace-v2", "schema_version": 2 },
  "input_inventory":  [ { "path": "…", "source_kind": "…", "tables": {…}, "row_counts": {…},
                          "discovered_manifests": […], "discovered_bundles": […] } ],
  "output_inventory": [ { "path": "…", "tables": {…}, "row_counts": {…}, "generated_manifests": […] } ],
  "checksums":        { "<rel/path>": "sha256:…", "arrays:<prediction_id>": "sha256:…" },
  "old_to_new_ids":   { "$ref": "legacy_id_map.v1" },
  "preserved_opaque": [ { "path": "…", "reason": "n4a_bundle|joblib|unknown_column|…",
                          "checksum": "sha256:…" } ],
  "unsupported":      [ { "item": "…", "reason": "…", "disposition": "refused|preserved" } ],
  "warnings":         [ "…" ],
  "environment":      { "python": "…", "nirs4all": "…|null", "duckdb": "…|null", "pyarrow": "…|null" }
}
```

`source.fingerprint` is the no-in-place + `--resume` anchor. Every output file MUST have a `checksums` entry; every `checksums`/`output_inventory` entry MUST correspond to a real output file (self-consistency, §13).

## 8. Report vocabulary — `legacy_migration_report.v1`

Human/UX-facing summary (default `migration-report.json`), schema `$id` `…/legacy_migration_report.v1.json`. Distinct from the manifest: the manifest is the exhaustive ledger, the report is the digest + next action.

```jsonc
{
  "schema_version": 1,
  "status": "success | migrated_with_warnings | unsupported_input | verification_failed | refused | error",
  "source_summary": { "kinds": […], "row_counts": {…}, "bundles": N, "artifacts": N },
  "target_summary": { "kind": "nirs4all-workspace-v2", "path": "…" },
  "migrated_counts":    { "runs": N, "pipelines": N, "chains": N, "predictions": N, "arrays": N, "artifacts": N },
  "preserved_counts":   { "n4a": N, "joblib": N, "unknown_columns": N },
  "unsupported_counts": { "refused": N, "preserved": N },
  "verification_summary": { "ran": true, "passed": true, "checks": {…}, "mismatches": 0 },
  "errors":   [ { "code": "…", "cause": "…", "message": "…", "mitigation": "…" } ],
  "warnings": [ "…" ],
  "recommended_next_command": "nirs4all-tools legacy verify <out> --manifest …"
}
```

`errors[].{cause,mitigation}` reuse the **CAP-004-owned** `unsupported` cause vocabulary surfaced by `RtError` (`RT_spec.md` RT-003): `unsupported_shape | unsupported_capability | invalid_request | runtime_error`, plus migration-local `forced_in_place_refused | non_empty_output | forward_version | verification_failed`. The report does **not** invent the cross-cutting cause vocab — it references it, exactly as RT does.

## 9. Checksum vocabulary

- **File-level:** SHA-256 over raw bytes of **every** copied or generated file (`checksums["<rel/path>"]`). Standardize on SHA-256 — the legacy `_array_checksum` uses MD5 (`migration.py:88`); the tool replaces it.
- **Array-level:** `checksums["arrays:<prediction_id>"]` = SHA-256 over a **canonical** encoding of `y_true,y_pred,y_proba,sample_indices,weights` + row metadata. Canonicalization MUST fix: dtype (`float64`/`int64`), C-contiguity, a **shape prefix**, and a NaN normalization rule (NaN bit-patterns canonicalized) — so a reshaped multi-target row cannot collide with a flat one. (The current sampler hashes only `y_true`/`y_pred` and ignores shape — `migration.py:405-424` — which is insufficient.)
- **Native:** verify `manifest["score_set_hash"]` (`native_results.py:298,383-388`) for `native-results-v1`.
- **`.n4a`:** verify ZIP CRC and parse `manifest.json`; **never execute** bundle contents.
- **joblib / model artifacts:** **bytes only** by default; for native artifacts verify the recorded `content_fingerprint` **before** any `joblib.load` (verify-then-load; matches `native_results.py:371-374`). Loading is gated behind `--trusted-load-joblib`.

## 10. ID-map vocabulary — `legacy_id_map.v1`

```jsonc
{ "schema_version": 1,
  "entities": {
    "project|run|pipeline|chain|prediction|artifact|dataset|bundle": [
      { "old": "…", "new": "…", "relation": "identity|synthetic",
        "derivation": { "inputs": […], "rule": "…" }   // present only when relation=synthetic
      } ] } }
```

Policy: preserve stable ids when no collision and the target allows (relation `identity`, recorded **explicitly**, never implicitly); when the target forces a synthetic id, record `derivation.inputs` + a **deterministic** rule; **never discard** an old id — it stays in the map even when `new` differs.

## 11. Dry-run behavior

`--dry-run` performs detection + mapping **simulation** + unsupported enumeration + output **size estimate**, and writes **nothing** to the source or the output store. It may write only a manifest-preview/report to explicit `--manifest`/`--report` paths, and only if those paths resolve **outside** the source tree (else refusal). The pre/post source-tree integrity assertion (§3.5) still runs and must show zero change. Dry-run is the Studio "estimate" path's replacement (supersedes the in-process `migrate --dry-run` at `router_maintenance.py:310-317`).

## 12. Failure semantics

- **Pre-flight refusals (no writes):** aliased/in-place output (`40`), non-empty output without `--resume` (`40`), unknown or forward-version source (`20`), missing `duckdb` for a `duckdb-workspace` source (`20`, with install hint mirroring `migration.py:68-71`).
- **`--strict`:** first unsupported item → abort; roll back **only** the tool-created output subtree; `status=unsupported_input` (`20`); source untouched.
- **`--best-effort` (default):** unsupported item → `preserve_opaque` + continue; `status=migrated_with_warnings` (`10`).
- **Verification failure:** `status=verification_failed` (`30`); **leave output for inspection** (do not auto-delete — opposite of the legacy `rmtree`); source untouched.
- **Internal error / integrity-assertion trip:** `70`; partial output rolled back (tool-created only); source proven untouched.
- **Never** delete a pre-existing output directory; **never** write to the source on any path including aborts.

## 13. Verification requirements (`--verify` and `legacy verify`)

`nirs4all-workspace-v2` (minimum, all of these — no sampling):

- SQLite `PRAGMA integrity_check = ok` (mirrors `migration.py:627`).
- `PRAGMA user_version == 2` and table row counts equal source table row counts.
- Prediction ids in metadata ↔ prediction ids in array sidecars are 1:1 where arrays exist.
- **Full** array checksum coverage for **all** migrated rows (not 1 %); Parquet schema validated for every sidecar.
- Artifact path existence + byte checksum for every artifact.
- Opaque-preserved files match source checksums.
- Manifest self-consistency: no output file without an inventory+checksum entry, and no inventory/checksum entry without an output file.

`native-results-v1` (Phase 2, gated): `score_set_hash` valid; dag-ml `SchemaMigrationPolicy.validate_read_version` passes for bundle + prediction cache; `ArtifactRef` content fingerprints valid; **refuse** any `replayable` claim unless dag-ml validation succeeds.

## 14. Studio integration

**New, non-mutating detector endpoint** (A8 shape, frozen):

```
GET /workspace/legacy-status
→ { legacy_status: "none|detected|unsupported|migrated|unknown",
    detected_formats: […], supported_by_tool: bool,
    blocked_reason: "…|null", recommended_command: "nirs4all-tools legacy migrate …",
    report_path_hint: "…|null" }
```

Detector rules: stat-first; detect `store.sqlite`/`store.duckdb`/`arrays/`/`.n4a`/`.n4a.py`/root `*.meta.parquet`/`*_predictions.json`/run-manifest layouts; read SQLite via read-only URI, DuckDB read-only only if the optional dep is present; parse ZIP manifests without extraction; read Parquet **schema only**. **Never construct `WorkspaceStore`.**

**Supersede the in-process migration surface** (the B8 blocker — Studio currently reaches `WorkspaceStore` via `StoreAdapter` during status, which can trigger auto-migration: `store_adapter.py:1-5,41` → `_get_storage_status_for_workspace` `_shared.py:192` → `StoreAdapter(store_root)`; and `POST /workspace/migrate` runs `_call_migrate_arrays_to_parquet` in-process at `router_maintenance.py:301-366`):

- `GET /workspace/migrate/status` (`router_maintenance.py:267`) → return **detector** status, never `WorkspaceStore`-derived for a legacy store.
- `POST /workspace/migrate` (`router_maintenance.py:297`) → **deprecate** in-process migration; return a refusal + the external `nirs4all-tools` command.
- `GET /workspace/storage-status` / `storage-health` (`router_maintenance.py:247,581`) → for a legacy store, report `legacy_status` + command, do **not** open it through `WorkspaceStore`.
- UI: "Legacy workspace detected" with a copyable command; after external migration the user **selects the output** workspace. Migration never runs in the Studio backend process.

This Studio change is owned jointly with `L12`, gated on `LOCK-MIG` acceptance, and must not regress the pristine `PRE-2` baseline.

## 15. Test fixtures (`migration-conformance-pack`, cross-repo gate)

Lift `_make_duckdb_workspace` (`tests/unit/pipeline/storage/test_migration.py:46-127`, with the `prediction_arrays` DDL at `:109`) into the tool's fixture builders. Pack:

- Minimal `duckdb-workspace`: 1× run/pipeline/chain/prediction/artifact + `prediction_arrays`.
- Multi-dataset / multi-fold DuckDB with `y_proba`, `sample_indices`, `weights`, branch metadata.
- `sqlite-workspace-legacy-arrays`: SQLite with a `prediction_arrays` table (JSON-serialized arrays).
- Workspace with a **pre-existing `arrays/`** → proves no source deletion (fixes `migration.py:289` rmtree).
- Corrupt/tampered Parquet sidecar → verification failure (exit `30`).
- Missing artifact record / missing artifact file / orphan artifact file.
- `.n4a` and `.n4a.py` → preserved + inspected, never executed.
- `fs-runs-legacy` (`runs/<dataset>/<pipeline_id>/manifest.yaml`) and `fs-runs-v2` (`runs/<run_id>/run_manifest.yaml`).
- Root `*.meta.parquet` + `*_predictions.json`.
- `native-results-v1` dir (manifest+score_set+predictions+artifacts).
- **Forward-version** SQLite (`user_version=99`), `.n4a` (`bundle_format_version` newer), native manifest (`schema_version` newer) → clean refusal.
- joblib artifact whose class is missing → proves default migration does **not** load it.

Gates: pytest unit (inspect, dry-run, no-in-place, manifest/report/id-map/checksum emission, verify-only); pytest integration on **copied** fixtures with whole-tree mtime/byte assertions; Studio backend test where a legacy workspace returns a clean refusal + external command and **no `store.sqlite` is created**; Phase-2 dag-ml gates only when a native target exists.

## 16. V1 acceptance gates (signable checklist)

| Gate | Statement |
|---|---|
| **G1 No-in-place** | Source tree byte/mtime-identical pre/post across **all** fixtures incl. failure/abort/strict paths. |
| **G2 Inspect/dry-run** | `inspect` and `--dry-run` write nothing to source or output store. |
| **G3 Contracts emitted** | `migrate` emits manifest + report + id-map + checksums; all self-consistent (§13). |
| **G4 Full array coverage** | Verification checksums **every** migrated array row (no sampling), shape-aware. |
| **G5 V1 reads output** | `nirs4all-workspace-v2` output opens read-only in the V1 runtime, `integrity_check=ok`, prediction rows + scores match source. |
| **G6 Preserve-opaque** | `.n4a`/`.n4a.py`/joblib/unknown columns preserved with byte-identical checksums; nothing executed/loaded by default. |
| **G7 Studio refusal** | `GET /workspace/legacy-status` returns clean refusal + external command; **no `WorkspaceStore` constructed**, no `store.sqlite` created for a duckdb-only workspace. |
| **G8 Runtime carries no legacy reader** | (Coordinated with `L19`) `nirs4all` runtime import pulls no `duckdb`; `WorkspaceStore.__init__`/`create_schema` no longer auto-migrate. Gated — executed at cutover. |
| **G9 Forward-version refusal** | Source newer than tool support → exit `20`, no writes. |
| **G10 Phase-2 replay honesty** | Native target refuses `replayable` unless dag-ml `SchemaMigrationPolicy` + fingerprint validation pass. Gated on `LOCK-REL` + DML-008. |

---

## 17. `LOCK-MIG` blockers — disposition vs A8's 10

| A8 blocker | Disposition here |
|---|---|
| 1. `DEC-MIG-001` not accepted | **Resolved** — accepted on the board (`DEC-MIG-001`, `ARB-006`=A). |
| 2. Target schema unresolved | **Resolved** — Phase 1 `nirs4all-workspace-v2` now; Phase 2 native gated (§5). |
| 3. Manifest/report/checksum/id-map vocab not accepted | **Resolved** — frozen as `legacy_migration_manifest.v1` / `legacy_migration_report.v1` / `legacy_id_map.v1` (§7–10). |
| 4. `LOCK-REL` window/manifest coupling | **Open (noted)** — support window in manifest `tool` block; release manifest coupling deferred to `LOCK-REL`. |
| 5. Artifact/joblib trust | **Resolved** — bytes-only default, verify-then-load, `--trusted-load-joblib` opt-in (§9). |
| 6. Score mapping exact | **Open → Phase 2** — legacy scalar columns ↔ dag-ml `ScoreSet` not 1:1; Phase 1 preserves scores as v2 rows, no native claim. |
| 7. Pipeline lowering | **Open → Phase 2** — no replayable-dag-ml claim without validated fingerprints (§5). |
| 8. Studio reaches `WorkspaceStore` | **Resolved (design)** — `legacy-status` detector + supersession (§14); implementation gated on sign. |
| 9. Verification insufficient | **Resolved** — full, shape-aware, manifest-consistent verification (§13). |
| 10. No fixtures gate | **Resolved** — `migration-conformance-pack` (§15). |

## 18. Proposed `LOCK-MIG` content (for A0 to sign)

> **`LOCK-MIG` — Legacy migration policy & schema.** Source `DEC-MIG-001` (accepted). Owner L18.
> 1. `nirs4all-tools` is a standalone, offline, **one-way, no-in-place** converter; the V1 runtime carries **no** legacy reader and **no** auto-migration trigger (§1, §3). The legacy readers + `migration.py` behaviors move into the tool under a declared **support window**.
> 2. **Phase 1 target = `nirs4all-workspace-v2`** (current SQLite `user_version=2` + Parquet + opaque preservation), authored against the **output** only. **Phase 2 native/dag-ml target is gated** on `LOCK-REL` + dag-ml V1 schema + a declared `SchemaMigrationPolicy.automatic_migrations` edge (today empty: `bundle.rs:128`).
> 3. **Three frozen contracts:** `legacy_migration_manifest.v1`, `legacy_migration_report.v1`, `legacy_id_map.v1` (§7–10). Report `cause`/`mitigation` vocab is **referenced from CAP-004**, not redefined (`RT_spec.md` RT-003).
> 4. **CLI** = `legacy {inspect,migrate,verify}` with modes `dry-run/verify/strict/best-effort/copy-only/resume/trusted-load-joblib` and exit codes `{0,10,20,30,40,70}` (§6).
> 5. **No-in-place is enforced by a whole-source-tree integrity assertion** on every path; checksums are SHA-256 + shape-aware array hashes; verification is **full**, not sampled (§3, §9, §13).
> 6. **Studio** gains a non-mutating `GET /workspace/legacy-status` and deprecates in-process `POST /workspace/migrate`; legacy stores are **never** opened via `WorkspaceStore` for status/health (§14). Gated on sign, owned with `L12`, must not regress `PRE-2`.
> 7. **Watchlist surface** `Legacy migration manifest/report` (sync board) is bound to this lock.

## 19. Evidence (heads; read-only; no code/tests/board modified)

- `nirs4all e41362b4`: `nirs4all/pipeline/storage/migration.py` (`:38-42,68-71,88,228,270,289,296-297,308,382-424,493,560,627,646-649`); `storage/store_schema.py` (`:28,267,296,599-602,614,803-804`); `storage/workspace_store.py` (`:268-285`); `pipeline/dagml/native_results.py` (`:58,255-308,311-360,363-388`); `pipeline/bundle/generator.py` (`:54,348-352,444-479`); `tests/unit/pipeline/storage/test_migration.py` (`:46-127,109`) + sibling `test_schema_version.py`/`test_export_roundtrip.py`.
- `dag-ml f58d7bf`: `crates/dag-ml-core/src/bundle.rs` (`:20-27,51-130`); `docs/contracts/score_set.schema.json` (`:7-16`).
- `nirs4all-studio 2ccbf68`: `api/store_adapter.py` (`:1-5,41`); `api/workspace/_shared.py` (`:168-196`); `api/workspace/router_maintenance.py` (`:247,267,297-366,581`); `api/workspace/models.py` (`:147-228`); `api/workspace_scanner.py` (`:361,445,501,648,751,835,852,922-935`).
- Reports read: `A8_A8-migration.md`, `RT_spec.md`, `A3_A3-dagml.md`, sync board + roadmap.

Sync doc updated: no (A0 owns the board). Only `SW4_MIG_CONVERTER_spec.md` was written.
