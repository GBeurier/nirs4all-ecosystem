# W104 - Tools Golden Fixture Blocker Fix

Date: 2026-07-01

## Scope

Addressed W101's nirs4all-tools migration golden blocker in
`/home/delete/nirs4all/nirs4all-tools`. No converter runtime code was changed.

## Fact Check

W101's placeholder claim was correct before this fix:

- `tests/fixtures/legacy/old_workspace_mixed/store.duckdb` was ASCII text:
  `legacy duckdb workspace placeholder`.
- `tests/fixtures/legacy/old_workspace_mixed/sample.meta.parquet` started with
  `PAR1`, but had no valid Parquet footer and was not readable by
  `pyarrow.parquet.read_table()`.

Local dependency check:

- `pyarrow` was available (`24.0.0`), so the loose Parquet sidecar could be
  replaced with a small valid reduced fixture.
- `duckdb` and the DuckDB CLI were unavailable, so a valid reduced DuckDB store
  was not generated in this environment.

## Fix

Chosen release-honest fix:

- Replaced `sample.meta.parquet` with a valid reduced Parquet sidecar containing
  three rows for the existing `pred-loose-001` loose prediction fixture.
- Replaced the ambiguous DuckDB placeholder text with an explicit opaque
  sentinel payload at `store.duckdb`. The file is intentionally not a DuckDB
  database; it exists only to lock the current detect-and-byte-preserve behavior.
- Updated `tests/fixtures/legacy/README.md` to state the exact fixture claims.
- Added `test_golden_mixed_workspace_fixture_labels_are_release_honest()` so the
  release claim cannot silently regress to fake binary placeholders.

The converter behavior remains intact: `store.duckdb`, legacy run manifests, and
loose prediction sidecars are still preserved opaque in best-effort migration
mode. No legacy reader support was broadened.

## Commit

Repository: `/home/delete/nirs4all/nirs4all-tools`

- `9dc0c62 test(migration): label mixed golden fixture surfaces`

## Changed Files

- `tests/fixtures/legacy/README.md`
- `tests/fixtures/legacy/old_workspace_mixed/sample.meta.parquet`
- `tests/fixtures/legacy/old_workspace_mixed/store.duckdb`
- `tests/test_real_golden_fixtures.py`

## Verification

Run from `/home/delete/nirs4all/nirs4all-tools`:

- `PYTHONPATH=src python3.11 -m pytest tests/test_real_golden_fixtures.py -q`
  - passed, 5 tests.
- `PYTHONPATH=src python3.11 -m pytest -q`
  - passed, 83 tests.
- `python3.11 -m ruff check .`
  - passed.
- `PYTHONPATH=src python3.11 -m mypy`
  - passed.
- `git diff --check`
  - passed.

## Remaining Blockers

None for W101's mislabeled placeholder blocker.

Residual release scope note: nirs4all-tools still does not include semantic
DuckDB golden coverage because DuckDB authoring dependencies were unavailable
locally and the converter does not currently read DuckDB workspaces. The release
claim is now explicit: the DuckDB fixture is an opaque preservation sentinel,
not a real DuckDB golden.
