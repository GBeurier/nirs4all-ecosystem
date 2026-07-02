# RC-H — Migration Converter Release-Candidate Proof

Date: 2026-07-02

Lane: RC-H (migration converter release proof).
Worktree: `/home/delete/nirs4all/_worktrees/RC-v1-tools` (branch `rc/v1-full-refactor`,
base `nirs4all-tools/main`).

## Summary

Audited the standalone legacy save/prediction/pipeline/workspace converter
(`nirs4all-tools`) for release-candidate readiness and **tightened golden test
coverage around the two surfaces the RC-H mandate calls out: preserved payloads
and native-result lowering**. No converter runtime behavior was changed — the
work is test-only. The converter was already green on this branch (111 tests);
it is now 114 tests with three new deterministic golden tests that lock
previously uncovered RC guarantees.

Key conclusion: the converter is a viable RC artifact for the "before production
switch" gate. It is offline, one-way, no-in-place; it lowers the supported
source shapes into runtime-readable `nirs4all-workspace-v2`; it preserves
non-lowerable and provenance payloads with checksums; and `verify` detects
tampering of every checksum surface (files, SQLite integrity/user_version,
runtime array-row digests, and preserved-payload ledger entries).

## Context Read / Audited

- `/home/delete/nirs4all/AGENTS.md`, ecosystem `CLAUDE.md`.
- Control board `RC_V1_FULL_REFACTOR_CONTROL.md` (RC-H scope, non-negotiables).
- Prior tools reports: `W30_TOOLS_MIGRATION.md`, `W78_TOOLS_MIGRATION_COMPLETE.md`,
  `W84_TOOLS_LEGACY_CONVERTER.md`, `W97_TOOLS_REAL_GOLDENS.md` (and the W39/W49/W59
  lineage they reference).
- Full converter source (`src/nirs4all_tools/*.py`) and the complete test suite.

Audit finding: the RC branch already contains the full W30→W97 lineage **plus
eight later commits** (loose-prediction lowering, single legacy-runs-manifest
lowering, preserved-payload checksum verification, non-finite prediction-value
rejection, mixed-golden labelling). The prior reports understate the current
state; the RC head is ahead of all of them and internally consistent.

## Changed Files (tools worktree, test-only)

- `tests/test_native_results.py` — added `test_native_results_proba_arrays_lower_to_flat_sidecar_record`.
- `tests/test_commands.py` — added `test_migrate_native_results_lowered_preserved_payload_is_byte_identical_and_verified`.
- `tests/test_real_golden_fixtures.py` — added `test_golden_sqlite_legacy_arrays_semantic_checksums_are_deterministic`.

`git diff --stat`: 3 files changed, +127 insertions, **0 source changes, 0 fixture changes**.

## Tests Added and Why

Each addition first probed real behavior (throwaway script) to characterize —
not assume — the contract, then locked it:

1. **Native-result proba lowering** (`test_native_results.py`). The native path
   carries `y_proba` as an already-flat projection and `y_proba_shape` verbatim
   from the parquet row (distinct from the legacy `prediction_arrays` path, which
   *derives* the shape). The only prior native-proba test covered the empty→`None`
   case. New test locks a multi-class row (`y_proba_shape=[4,2]`) passing through
   to the sidecar record, plus row-level `metric`/`task_type` precedence over
   manifest defaults.

2. **Native-result lowering keeps the source payload intact + verify guards it**
   (`test_commands.py`). On a fully-lowered `native-results-v1`, the original
   `manifest.json`/`score_set.json`/`predictions.parquet` are preserved
   byte-for-byte under `preserved/native-results-v1/<name>/` and every file is
   checksummed. New test asserts byte-identity, that `verify` passes clean, and
   that tampering the preserved `predictions.parquet` fails verification with the
   exact `mismatched_files` path. It also documents that `preserved_opaque` is
   intentionally empty in the fully-lowered case (protection is file-level).

3. **Determinism of semantic checksums** (`test_real_golden_fixtures.py`). Two
   independent migrations of byte-identical legacy sources must agree on every
   semantic checksum surface — `arrays:<prediction_id>` row digests, the runtime
   array sidecar files, and the preserved legacy-arrays JSONL — proving the RC
   artifact does not depend on wall-clock time or run order. Only `store.sqlite`
   is excluded (its `created_at` defaults are intentionally time-based, which is
   why the existing goldens never pin its bytes).

## Verification (exact results)

Interpreter: `python3.11` (3.11.15) with `pyarrow 24.0.0`, `pyyaml 5.4.1`
available; `duckdb` absent.

- `PYTHONPATH=src python3.11 -m pytest` → **114 passed, 1 warning** (baseline was
  111 passed; the warning is a `pytz` `DeprecationWarning` from a system package,
  not tool code).
- `python3.11 -m ruff check .` → **All checks passed**.
- `PYTHONPATH=src python3.11 -m mypy` (project gate, `files=src/nirs4all_tools`) →
  **Success: no issues found in 15 source files**.
- `git diff --check` → clean.
- New tests in isolation → **3 passed**.
- Tests-directory mypy is not part of the project gate; for good measure I
  confirmed my appended code adds **0** new errors (the 61 pre-existing errors in
  `test_real_golden_fixtures.py` are all at/below line 752, before the appended
  test; the `semantic()` helper narrows with `isinstance`).
- CLI smoke on the checked-in `sqlite_legacy_arrays_workspace.sql` golden:
  `legacy inspect` (exit 0, detects `sqlite-workspace-legacy-arrays` v2) →
  `legacy migrate --strict --verify` (exit 0, `verification_summary.passed=True`,
  emits `arrays/`, `preserved/`, and all four contracts) →
  `legacy verify` (exit 0).

## Risks / Open Questions

- **`preserved_opaque` ledger is empty for fully-lowered native/loose/runs
  sources.** The preserved provenance payload is protected only at the file-checksum
  level (`checksums`), not via the `preserved_opaque` ledger used by opaque
  preservation. `verify` still catches tampering (now locked by test #2), so this
  is not a correctness gap, but it is a manifest-semantics asymmetry a consumer
  might not expect. Left as-is deliberately (changing it would alter the manifest
  contract other lanes depend on); flagged for coordinator awareness.
- **No `duckdb` extra in this environment.** DuckDB-workspace handling is
  detect-and-preserve-opaque only; no semantic reader exists yet, and the golden
  `store.duckdb` is an explicit opaque sentinel, not a real DB. DuckDB semantic
  lowering remains a future slice, correctly out of RC scope.
- **Parquet sidecar file bytes are only pinned by presence, not value.** This is
  intentional (zstd/pyarrow-version sensitivity); determinism is guaranteed on the
  canonical-JSON row digests and JSONL bytes instead. Do not add parquet-byte
  golden pins.

## Fixture Gap (mandate)

Per the stop condition: **real production legacy workspaces are not available in
this worktree.** All goldens are small, checked-in, reduced synthetic payloads
under `tests/fixtures/legacy/` (mixed opaque workspace, loose predictions, a
single legacy runs manifest, and a `prediction_arrays` SQLite dump). No golden
fixture was changed or regenerated. The additions are the smallest deterministic
local coverage that exercises the named RC surfaces (preserved payloads,
native-result lowering) without inventing behavior. If/when a real pre-V1
workspace or a real dag-ml `native-results-v1` directory can be sanitized and
checked in, the highest-value additions would be (a) a real multi-artifact
native-results root and (b) a real `.n4a` bundle preservation golden.

## Decisions

- Test-only change; no converter runtime behavior touched (respects RC-H scope:
  do not edit parity runtime, Studio/Web/UI, or providers).
- Characterized behavior by probing before writing assertions; every new test
  reflects current behavior rather than a desired redesign.
- Did not expose converter benchmarks to RC-D: there is no existing converter
  benchmark harness in this worktree to stay "close to," so per the mandate
  ("only if already close to existing tooling") none was added.

## Follow-up Full Parity

Not required for this lane. Changes are additive tests in an independent repo
with no runtime/schema/contract impact; no Python-reference or dag-ml parity
re-run is triggered. Standard tools gate (pytest + ruff + mypy) is the relevant
gate and is green.

## Integration Note

The three test additions are left **uncommitted** in `RC-v1-tools` for coordinator
review (per "commit only when asked"). Suggested scoped commit once reviewed:

```
test(migration): lock native lowering + preserved-payload golden coverage
```
