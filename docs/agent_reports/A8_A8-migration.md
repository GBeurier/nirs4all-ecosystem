# A8 - L18 Migration And Tools Report

Date: 2026-06-30

Mode: read-only audit. Implementation code was not modified. `PARALLEL_REFACTORING_SYNC.md` was not edited because this run is in multi-CLI report mode and A0 owns sync-board integration.

## Scope And Evidence

Audited repositories and files:

- `nirs4all`: legacy workspace storage, current SQLite/Parquet storage, bundle export/load, native dag-ml result writer, and migration tests.
- `nirs4all-studio`: workspace scanning, maintenance migration APIs, storage health APIs, store adapter, and native results adapter.
- `dag-ml`: execution bundle schema policy, prediction cache store, artifact records, and score-set model.
- `nirs4all-ecosystem`: migration lane and lock status.

Evidence was gathered with CodeGraph and direct source/doc reads. No tests were run because the task was a read-only design audit and report.

## Executive Summary

The existing `nirs4all/pipeline/storage/migration.py` is useful compatibility code, but it is not a safe standalone V1 migration tool. It mutates workspaces in place, can be triggered simply by opening a legacy workspace, has partial verification, has no durable manifest/report files, has no full checksum inventory, and has no old-to-new ID map.

`nirs4all-tools` should absorb the detection, reading, normalization, and copy logic from the legacy migrators, but supersede the current behavior with an explicit no-in-place converter. Until `DEC-MIG-001` and `LOCK-MIG` are accepted, the tool should not invent a final dag-ml target schema. The safest staged target is:

- Phase 1: `nirs4all-workspace-v2`, a current SQLite plus Parquet sidecar workspace with opaque legacy files preserved and fully reported.
- Phase 2: `native-results-v1` or dag-ml execution-bundle outputs only after the score, pipeline, artifact, manifest, and release contracts are accepted.

Studio should stop treating migration as an in-process maintenance operation. It should detect legacy formats without constructing `WorkspaceStore`, refuse cleanly, and propose an external `nirs4all-tools legacy migrate ...` command.

## Legacy Format Inventory

| Format | Evidence | Current Behavior | Classification |
| --- | --- | --- | --- |
| DuckDB workspace store, `store.duckdb` | `migration.py`, `workspace_store.py`, migration docs | `WorkspaceStore.__init__` auto-migrates metadata to `store.sqlite` and renames DuckDB to `.bak` | Migrable, but current behavior must be replaced by explicit no-in-place conversion |
| DuckDB `prediction_arrays` table | `migration.py` | `migrate_arrays_to_parquet` writes Parquet sidecars in the same workspace, drops the table, and VACUUMs | Migrable, but unsafe in-place implementation |
| SQLite `prediction_arrays` table | `store_schema.py` | `create_schema(..., workspace_path=...)` auto-migrates arrays to `ArrayStore` and drops the table | Migrable, but current auto-mutation must be disabled or bypassed by tools |
| Current SQLite store schema v2 | `store_schema.py` | Metadata tables for runs, pipelines, chains, predictions, artifacts, logs, and projects | Preserve/copy/verify; migrate only if target mapping is accepted |
| Current Parquet sidecars under `arrays/` | `array_store.py` | One Parquet file per dataset with array columns and prediction IDs | Preserve/copy/verify; migrable to native results only with accepted target schema |
| Filesystem run manifests v2 | `workspace_scanner.py` | `workspace/runs/<run_id>/run_manifest.yaml` plus nested result manifests | Metadata migrable where fields map; preserve original manifests |
| Legacy filesystem run manifests | `workspace_scanner.py` | `workspace/runs/<dataset>/<pipeline_id>/manifest.yaml` | Metadata migrable where fields map; preserve original manifests |
| Root `*.meta.parquet` files | `workspace_scanner.py` | Legacy prediction metadata discovery | Migrable where columns are known; preserve unsupported columns |
| Root `*_predictions.json` files | `workspace_scanner.py` | Legacy prediction discovery fallback | Migrable where schema is known; preserve unsupported fields |
| `.n4a` bundles | `workspace_store.py`, `bundle/generator.py`, `bundle/loader.py`, Studio export scanner | ZIP with manifest, chain/pipeline metadata, optional relation replay manifest, and artifacts | Preserve opaque and inspect metadata; do not rewrite initially |
| `.n4a.py` portable bundles | `bundle/generator.py` | Python script with embedded artifacts | Preserve opaque; do not execute or rewrite by default |
| Joblib artifacts | `workspace_store.py`, `bundle/generator.py`, `native_results.py`, dag-ml artifact model | Stored as content-addressed files or bundle entries | Preserve opaque with byte checksums; never load by default during migration |
| Native dag-ml results | `native_results.py`, Studio native adapter | `manifest.json`, `score_set.json`, `predictions.parquet`, `artifacts/*.joblib` | Target/reference format; preserve and verify |
| Scores | `store_schema.py`, `native_results.py`, `dag-ml` `ScoreSet` | Legacy scalar columns and JSON summaries versus native score-set record | Blocked until exact mapping is accepted |
| Pipelines | `store_schema.py`, bundle generator/loader, Studio scanner | Expanded configs, original templates, chain manifests, bundle chain JSON | Preserve original opaque; only mark replayable after accepted lowering to dag-ml |

### Migrable Now

- DuckDB metadata tables to current SQLite tables, using the existing FK-aware table order as a starting point.
- DuckDB and SQLite `prediction_arrays` to Parquet sidecars.
- Current SQLite plus Parquet workspace copy with integrity checks.
- Legacy prediction metadata imports from known `*.meta.parquet` and JSON schemas.

### Preserve Opaque

- `.n4a` and `.n4a.py` bundles.
- Joblib artifacts and unknown artifact backends.
- Original pipeline templates, expanded configs, relation replay manifests, and unknown manifest fields.
- Unknown Parquet/JSON columns and files not covered by an accepted schema.

### Unsupported Until `LOCK-MIG`

- Rewriting `.n4a` bundles into dag-ml `ExecutionBundle`.
- Claiming replayable dag-ml bundles from legacy data without graph, campaign, controller, prediction-requirement, and data-requirement fingerprints.
- Loading untrusted joblib during migration.
- In-place migration.
- Invented old-to-new ID mappings without a manifest contract.

## Existing `migration.py` Assessment

Useful pieces to carry forward into `nirs4all-tools`:

- DuckDB optional dependency handling and read-only connection pattern.
- Existing table-copy order for `projects`, `runs`, `pipelines`, `chains`, `predictions`, `artifacts`, and `logs`.
- SQLite value normalization and row-count verification.
- ArrayStore record writing and batch migration scaffolding.
- Lock concept and report counters.
- Existing test helpers in `tests/unit/pipeline/storage/test_migration.py`.

Behaviors to supersede:

- `WorkspaceStore.__init__` auto-calls DuckDB-to-SQLite migration when `store.duckdb` exists.
- `create_schema(..., workspace_path=...)` auto-migrates SQLite `prediction_arrays`.
- `migrate_arrays_to_parquet` writes into the source workspace, drops the source table, and VACUUMs.
- Error rollback deletes the whole `arrays/` directory, which can remove pre-existing user data if the directory already existed.
- Verification samples about 1 percent of rows and checks only `y_true` and `y_pred`, not all arrays, metadata, artifacts, or every row.
- The CLI has no `--output`, no durable manifest/report files, no full checksum inventory, and no old-to-new ID map.
- Studio wrappers call this in-process migration API directly.

Recommended containment:

- Keep library compatibility readers only for the support window.
- Move explicit conversion into `nirs4all-tools`.
- Extract pure read/normalize helpers from `migration.py` only after `DEC-MIG-001` is accepted.
- Do not let normal workspace opening mutate legacy storage.

## `nirs4all-tools` CLI Draft

Proposed top-level commands:

```bash
nirs4all-tools legacy inspect <input> \
  --format json \
  --report legacy-inspect-report.json

nirs4all-tools legacy migrate <input> \
  --output <output-dir> \
  --target nirs4all-workspace-v2 \
  --manifest migration-manifest.json \
  --report migration-report.json \
  --id-map old-new-ids.json \
  --checksums sha256 \
  --dry-run

nirs4all-tools legacy migrate <input> \
  --output <output-dir> \
  --target nirs4all-workspace-v2 \
  --manifest migration-manifest.json \
  --report migration-report.json \
  --id-map old-new-ids.json \
  --checksums sha256 \
  --verify

nirs4all-tools legacy verify <output-dir> \
  --manifest migration-manifest.json \
  --report verification-report.json
```

Future target, gated on `LOCK-MIG` and dag-ml V1 decisions:

```bash
nirs4all-tools legacy migrate <input> \
  --output <output-dir> \
  --target native-results-v1 \
  --manifest migration-manifest.json \
  --report migration-report.json \
  --id-map old-new-ids.json \
  --checksums sha256 \
  --verify
```

### CLI Policy

- Source path is opened read-only.
- Output path must not equal the input path.
- Output path must be empty unless `--resume` is explicitly accepted by the manifest.
- No default joblib loading. Use `--trusted-load-joblib` only for explicitly trusted local artifacts.
- `--dry-run` performs detection, mapping simulation, unsupported-item reporting, and output size estimates without writes.
- `--verify-only` or `legacy verify` checks an existing output against a manifest and does not read or mutate the source.
- Exit codes should distinguish success, migrated-with-warnings, unsupported-input, verification-failed, and internal-error.

## Manifest And Report Contract Draft

Migration manifest fields:

- `schema_version`
- `tool_name`, `tool_version`, `created_at`, `completed_at`
- `source_path`, `source_kind`, `source_detected_versions`
- `target_kind`, `target_schema_version`
- `input_inventory`: files, tables, row counts, discovered manifests, discovered bundles
- `output_inventory`: files, tables, row counts, generated manifests
- `checksums`: SHA-256 for every copied/generated file and content checksums for array payloads
- `old_to_new_ids`: run, pipeline, chain, prediction, artifact, dataset, and bundle IDs
- `preserved_opaque`: paths and reasons
- `unsupported`: paths/items, reasons, and whether migration was refused or completed with preservation
- `warnings`
- `environment`: Python version, nirs4all version if installed, duckdb version if used, pyarrow version if used

Migration report fields:

- `status`
- `source_summary`
- `target_summary`
- `migrated_counts`
- `preserved_counts`
- `unsupported_counts`
- `verification_summary`
- `errors`
- `warnings`
- `recommended_next_command`

ID mapping policy:

- Preserve stable IDs when there is no collision and the target schema allows it.
- Record old-to-same mappings explicitly, not implicitly.
- For synthetic IDs required by a target, record generation inputs and deterministic derivation.
- Never discard old IDs; keep them in manifest metadata even when target IDs differ.

Checksum policy:

- SHA-256 all copied or generated files.
- For array records, hash canonical representations of `y_true`, `y_pred`, `y_proba`, `sample_indices`, `weights`, and row metadata.
- For native results, verify `score_set_hash`.
- For `.n4a`, verify ZIP CRC and parse `manifest.json`; do not execute bundle contents.
- For joblib artifacts, verify bytes only unless explicitly trusted loading is enabled.

## Verification Requirements

Minimum verification for `nirs4all-workspace-v2`:

- SQLite `PRAGMA integrity_check`.
- SQLite schema version and table row counts.
- Prediction IDs in metadata match prediction IDs in array sidecars where arrays exist.
- Full array checksum coverage for all migrated rows, not a sample.
- Parquet schema validation for all sidecar files.
- Artifact path existence and byte checksum validation.
- Opaque preserved files match source checksums.
- Manifest self-consistency: no output file without inventory entry and no inventory entry without output file.

Minimum verification for future native/dag-ml targets:

- Native `score_set_hash` validation.
- `dag-ml` schema policy validation for bundles or prediction caches.
- Artifact manifest validation against `ArtifactRef` requirements.
- Refuse replayability claims unless dag-ml validation succeeds.

## Target Schema Policy

Phase 1 should target current `nirs4all-workspace-v2` because its schema exists today and can represent the legacy workspace model without pretending to be replayable dag-ml.

Phase 2 can target `native-results-v1` once `LOCK-MIG`, `LOCK-REL`, and dag-ml V1 schema decisions are accepted. This target must respect dag-ml's explicit schema migration policy: old versions are accepted only when a declared migration edge exists, future versions are refused, and version zero is invalid.

Legacy data should not be rewritten into an `ExecutionBundle` unless all required dag-ml invariants can be reconstructed and validated:

- graph fingerprint
- campaign fingerprint
- controller fingerprint
- selected variant ID
- prediction requirements
- prediction caches
- data requirements
- artifact refs and content fingerprints
- optional `ScoreSet` with matching plan ID

If these cannot be reconstructed, the tool should preserve the original pipeline and artifact metadata as opaque provenance and report that the output is not a replayable dag-ml bundle.

## Fixture Plan

Create a migration conformance fixture pack after `DEC-MIG-001` is accepted:

- Minimal DuckDB workspace with one run, pipeline, chain, prediction, artifact, and `prediction_arrays`.
- Multi-dataset and multi-fold DuckDB workspace with `y_proba`, sample indices, weights, and branch metadata.
- SQLite workspace with legacy `prediction_arrays` serialized as JSON strings.
- Workspace with a pre-existing `arrays/` directory to prove no source deletion or mutation occurs.
- Corrupt or tampered Parquet sidecar to prove verification failure.
- Missing artifact record, missing artifact file, and orphan artifact file cases.
- `.n4a` bundle and `.n4a.py` bundle fixtures that are preserved and inspected without execution.
- Legacy filesystem run layout with `workspace/runs/<dataset>/<pipeline_id>/manifest.yaml`.
- Newer filesystem run layout with `workspace/runs/<run_id>/run_manifest.yaml`.
- Root `*.meta.parquet` and `*_predictions.json` files.
- Native results directory with `manifest.json`, `score_set.json`, `predictions.parquet`, and artifacts.
- Forward schema version cases for SQLite, bundles, and manifests.
- Joblib artifact requiring a missing class, proving default migration does not load it.

Proposed gates:

- Python unit tests for inspect, dry-run, no-in-place, manifest generation, checksum generation, and verify-only.
- Python integration tests using copied fixtures and mtime checks to prove the source tree is unchanged.
- Studio backend tests where a legacy workspace returns a clean refusal and external command suggestion.
- Future dag-ml gates only when native target exists: validate bundle, validate prediction cache, validate artifact manifest, and replay validation where applicable.

## Studio Integration Proposal

Studio needs a non-mutating legacy detector separate from `WorkspaceStore` and `StoreAdapter`.

Detector behavior:

- Use filesystem stat/read-only checks first.
- Detect `store.sqlite`, `store.duckdb`, `arrays/`, `.n4a`, `.n4a.py`, root `*.meta.parquet`, `*_predictions.json`, and known run-manifest layouts.
- Read SQLite through read-only URI and avoid schema creation.
- Read DuckDB in read-only mode only if the optional dependency is installed.
- Parse ZIP manifests without extracting or executing contents.
- Read Parquet schema only; do not load large payloads for status checks.
- Never call `WorkspaceStore` for legacy detection.

API shape:

```text
GET /workspace/legacy-status
```

Response fields:

- `legacy_status`: `none`, `detected`, `unsupported`, `migrated`, or `unknown`
- `detected_formats`
- `supported_by_tool`
- `blocked_reason`
- `recommended_command`
- `report_path_hint`

Existing endpoints to change after `LOCK-MIG`:

- `GET /workspace/migrate/status`: return detector status, not `WorkspaceStore`-derived status for legacy stores.
- `POST /workspace/migrate`: deprecate in-process migration and return a refusal plus external command.
- Storage health endpoints: avoid opening legacy stores through `WorkspaceStore`; report legacy status and command suggestion instead.

UI behavior:

- Show "Legacy workspace detected" in maintenance/storage health views.
- Present a copyable command, for example:

```bash
nirs4all-tools legacy migrate "<workspace>" \
  --output "<workspace>.migrated" \
  --target nirs4all-workspace-v2 \
  --manifest migration-manifest.json \
  --report migration-report.json \
  --verify
```

- After external migration, the user selects the output workspace.
- Do not run migration in the Studio backend process.

## `LOCK-MIG` Blockers

1. `DEC-MIG-001` is proposed but not accepted; `LOCK-MIG` has no decision source.
2. Target schema is unresolved: current SQLite/Parquet workspace, native dag-ml results, execution bundle, or multiple targets.
3. Manifest, report, checksum, and old-to-new ID vocabulary are not accepted.
4. `LOCK-REL` affects release manifest and compatibility-window commitments.
5. Artifact policy is unresolved: joblib trust model, artifact backend/plugin metadata, opaque preservation period, and loading rules.
6. Score mapping is not exact yet: legacy scalar columns and JSON summaries do not trivially map to dag-ml `ScoreSet` for every partition and prediction level.
7. Pipeline lowering is unresolved: legacy configs cannot be called replayable dag-ml graphs without validated fingerprints and data requirements.
8. Studio currently reaches `WorkspaceStore` and can trigger auto-migration during status or health checks.
9. Existing verification is insufficient: sampled rows only, partial arrays only, no full manifest-level checksum.
10. Migration conformance fixtures do not exist as an accepted cross-repo gate.

## Recommended Sync-Board Update For A0

Do not apply this directly from A8; A0 should integrate it into `PARALLEL_REFACTORING_SYNC.md`.

Suggested lane update:

```text
L18 Tools/migration legacy remains blocked.
Next action: review A8 migration/tools audit; decide DEC-MIG target and no-in-place manifest/report/checksum/id-map contract; replace Studio in-process migration with non-mutating detection and external command guidance after LOCK-MIG acceptance.
```

Suggested worklog entry:

```text
2026-06-30 | Codex/A8 | review | Produced migration/tools audit in docs/agent_reports/A8_A8-migration.md. Found current migration.py is in-place compatibility code, not a safe standalone migrator. Proposed nirs4all-tools no-in-place CLI, manifest/report/checksum/id-map contract, fixture plan, Studio external-command integration, and LOCK-MIG blockers. | Evidence: nirs4all migration/storage/bundle/native-results code, Studio scanner/maintenance/storage-health code, dag-ml schema/artifact/score/prediction-cache code. | Blocked by DEC-MIG-001/LOCK-MIG/LOCK-REL.
```

Sync doc updated: no. Reason: multi-CLI report mode; A0 owns board updates.
