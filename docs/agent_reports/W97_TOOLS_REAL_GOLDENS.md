# W97 - Tools Legacy Converter Real Golden Fixtures

Date: 2026-07-01

## Summary

Added checked-in reduced legacy converter fixtures to move `nirs4all-tools`
coverage beyond fully synthetic sources. The new tests exercise old loose
prediction files, legacy run/pipeline manifests, opaque workspace payload
preservation, and a legacy SQLite `prediction_arrays` workspace that lowers to
workspace-v2 metadata and runtime array sidecars. Runtime packages were not
changed and no legacy readers were added outside `nirs4all-tools`.

## Changed Files

Repository/worktree: `/home/delete/nirs4all/_worktrees/W97-tools-real-goldens`

- `README.md`
- `tests/fixtures/legacy/README.md`
- `tests/fixtures/legacy/old_workspace_mixed/run_predictions.json`
- `tests/fixtures/legacy/old_workspace_mixed/runs/run-2024-legacy/pipeline-pls/manifest.yaml`
- `tests/fixtures/legacy/old_workspace_mixed/sample.meta.parquet`
- `tests/fixtures/legacy/old_workspace_mixed/store.duckdb`
- `tests/fixtures/legacy/sqlite_legacy_arrays_workspace.sql`
- `tests/test_real_golden_fixtures.py`

## Commit

- `c10934a test(migration): add real legacy golden fixtures`

## Verification

- `PYTHONPATH=src python3.11 -m pytest tests/test_real_golden_fixtures.py -q` - passed, 4 tests.
- `PYTHONPATH=src python3.11 -m pytest -q` - passed, 82 tests.
- `python3.11 -m ruff check .` - passed.
- `PYTHONPATH=src python3.11 -m mypy` - passed.
- `git diff --check` - passed before staging.
- `git diff --cached --check` - passed for the staged fixture files.

## Failures / Notes

- Initial new dry-run assertion expected `would_preserve` items not to count as
  `preserved`; the current unsupported report intentionally counts dry-run
  preservation candidates under `counts.preserved`. The test was corrected to
  match the existing machine-readable contract.

## Blockers

- None.

## Follow-up Coordinator Integration

- Needed: merge `refactor/W97-real-goldens` into the tools integration flow.
- No central control-board or runtime package updates were made.
