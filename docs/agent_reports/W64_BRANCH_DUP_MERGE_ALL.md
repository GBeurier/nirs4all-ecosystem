# W64 Branch Dup Merge All

## Status

Implemented native parity for `branch_dup_merge_all` and removed it from the dag-ml expected fallback boundary.

## Changes

- Extended duplication branch detection to accept `{"merge": "all"}` only when every branch has a branch-local model.
- Added native merge-all projection for duplication branches:
  - branch feature blocks are collected before branch prediction columns;
  - branch-local model rows are projected with legacy-compatible fold, `avg`, and `w_avg` scores;
  - downstream rows are projected from a native-built merge-all matrix containing branch features plus OOF/imputed branch predictions.
- Added focused detector coverage for supported merge-all branches and rejection of feature-only merge-all branches.
- Removed only `branch_dup_merge_all` from `EXPECTED_FALLBACK`.
- Updated compatibility ledger coverage from fallback 6/native 81 to fallback 5/native 82.

## Validation

- `.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py -k 'branch_dup_merge_all or native_fallback_boundary or coverage_meter' -q`
  - `88 passed, 94 deselected`
- `.venv/bin/python -m pytest tests/integration/parity/test_native_fallback_boundary.py -q`
  - `12 passed`
- `.venv/bin/python -m pytest tests/integration/parity/test_dagml_cli_runner.py -k 'duplication_branch_detection' -q`
  - `1 passed`
- `.venv/bin/python -m tests.integration.parity.coverage_meter --check`
  - `coverage_meter OK (fallback=5, target=0)`
- `.venv/bin/python -m py_compile nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py`
- `.venv/bin/python -m ruff check nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/test_dagml_cli_runner.py tests/integration/parity/test_conformance_dual_engine.py`
  - `All checks passed`

## Notes

The native row projection intentionally mirrors the legacy branch merge-all scoring surface. In this shape, legacy branch rows are based on full-train branch preprocessing plus fold-local branch models, and the downstream matrix combines branch feature blocks with OOF/imputed branch prediction columns.
