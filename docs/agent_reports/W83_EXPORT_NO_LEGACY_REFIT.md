# W83 Export No Legacy Refit

## Summary

Removed the default dag-ml export/export_model legacy-refit path in `nirs4all/api/result.py`.
Dag-ml results now export from captured native artifacts when replayable, otherwise raise a stable `RtError`
with `cause="unsupported_capability"` / `unsupported_capability="dagml_native_export"`, pointing to
`nirs4all-tools` conversion or the explicit `compatibility="legacy-refit"` opt-in.

The legacy refit machinery remains available only through that named compatibility keyword.

## Changed Files

- `nirs4all/api/result.py`
- `tests/integration/parity/test_cross_engine_export_surface.py`
- `tests/integration/parity/test_dagml_native_export_model.py`
- `tests/integration/parity/test_dagml_native_n4a_bundle.py`
- `tests/integration/parity/test_conformance_export_roundtrip.py`
- `tests/integration/parity/test_conformance_n4a_bundle_parity.py`
- `tests/integration/parity/test_dagml_cli_runner.py`

## Commit

- `dd640c14 fix(api): refuse dag-ml export without native artifacts`

## Verification

- `.venv/bin/python -m pytest tests/integration/parity/test_cross_engine_export_surface.py -q` -> 8 passed
- `.venv/bin/python -m pytest tests/integration/parity/test_dagml_native_export_model.py tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_conformance_export_roundtrip.py tests/integration/parity/test_conformance_n4a_bundle_parity.py tests/integration/parity/test_dagml_cli_runner.py::test_dagml_result_export_refuses_without_native_artifacts -q` -> 25 passed
- `.venv/bin/ruff check nirs4all/api/result.py tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_dagml_native_export_model.py tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_conformance_export_roundtrip.py tests/integration/parity/test_conformance_n4a_bundle_parity.py tests/integration/parity/test_dagml_cli_runner.py` -> passed
- `.venv/bin/mypy nirs4all/api/result.py` -> passed
- `git diff --check` -> passed

Initial pytest collection failed before the venv install because `matplotlib` was missing from the ambient Python. I created `.venv` in the assigned worktree, installed local `dag-ml` / `dag-ml-data` bindings plus `nirs4all[dev]`, then reran the checks above.

## Failures / Blockers

- No remaining blockers.
- One intermediate test expectation was corrected: `branch_dup_two_way_merge_features` captures one native final artifact, so default `export_model()` should succeed natively rather than refuse. The conformance test now asserts native-or-refuse without legacy refit.

