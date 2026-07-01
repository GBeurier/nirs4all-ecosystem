# W84 - nirs4all-tools Legacy Converter Hardening

Date: 2026-07-01

## Summary

Hardened the standalone legacy converter so recognized non-lowerable artifacts are preserved by default in best-effort migrations instead of requiring runtime legacy readers or user-selected copy-only mode. Added a durable machine-readable `unsupported-report.json` contract and extended dry-run/verify coverage around legacy workspace inputs and native-results sidecars.

## Changed Files

Repository/worktree: `/home/delete/nirs4all/_worktrees/W84-tools-legacy-converter`

- `README.md`
- `src/nirs4all_tools/cli.py`
- `src/nirs4all_tools/commands.py`
- `src/nirs4all_tools/contracts.py`
- `tests/conftest.py`
- `tests/test_cli.py`
- `tests/test_commands.py`
- `tests/test_contracts.py`

## Commit

- `b01eae3 fix(migration): harden legacy converter preservation`

## Verification

- `PYTHONPATH=src python3.11 -m pytest` - 78 passed
- `PYTHONPATH=src python3.11 -m ruff check src tests` - passed
- `PYTHONPATH=src python3.11 -m mypy` - passed
- `git diff --check` - passed

## Failures / Notes

- Initial direct `pytest` collection failed because the package was not installed/importable in this worktree; final runs used `PYTHONPATH=src`.
- The system `python3` is 3.10 while the project targets 3.11+, so final checks used `python3.11`.
- `pyarrow` was initially absent; installed `pyarrow 24.0.0` for Python 3.11 to exercise parquet/native-results sidecar coverage.

## Blockers

- None.
