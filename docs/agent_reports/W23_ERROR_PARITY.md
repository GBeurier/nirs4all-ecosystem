# W23 report - error/refusal parity

Summary:
Implemented the W23 Python-side error/refusal parity slice in `_worktrees/W23-nirs4all-errors`. The runtime envelope now has shared `RtError.invalid_request(...)` and `RtError.runtime_error(...)` constructors alongside the existing dag-ml fallback mapping, and parity tests consume those helpers instead of local cause strings. Also fixed the host envelope builder to support the installed `dag_ml_data` JSON-only API while preserving the dict-returning host contract.

Code changed:
- `nirs4all/pipeline/dagml/rt.py`: added shared `invalid_request` and `runtime_error` `RtError` constructors for bad dataset/spec/workspace/export selectors and genuine runtime failures.
- `nirs4all/pipeline/dagml/envelope.py`: added compatibility for `dag_ml_data.build_coordinator_data_plan_envelope_json` when the typed Python wrapper is not exposed.
- `tests/integration/parity/test_conformance_error_parity.py`: removed the stale local RT cause classifier; added focused coverage for unsupported operators and invalid dataset specs.
- `tests/integration/parity/test_rt_fallback_strict.py`: added strict-mode native-backend-unavailable coverage (`unavailable_backend`).
- `tests/integration/parity/test_cross_engine_export_surface.py`: added `RtError.invalid_request` projection checks for no-workspace/export-refusal cases while preserving the existing exception-type contract.

Files touched:
- `nirs4all/pipeline/dagml/rt.py`
- `nirs4all/pipeline/dagml/envelope.py`
- `tests/integration/parity/test_conformance_error_parity.py`
- `tests/integration/parity/test_cross_engine_export_surface.py`
- `tests/integration/parity/test_rt_fallback_strict.py`
- this report

Tests run:
- `pytest -q tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_conformance_error_parity.py tests/integration/parity/test_compatibility_ledger.py tests/integration/parity/test_dagml_dataplane.py::test_envelope_builds_and_validates_against_live_contract` — 27 passed.
- `pytest -q tests/unit/pipeline/test_rt_envelopes.py` — 15 passed.
- `ruff check nirs4all/pipeline/dagml/rt.py nirs4all/pipeline/dagml/envelope.py tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_conformance_error_parity.py` — passed.
- `/home/delete/miniconda3/bin/python3 -m py_compile nirs4all/pipeline/dagml/errors.py nirs4all/pipeline/dagml/rt.py nirs4all/pipeline/dagml/result.py nirs4all/pipeline/dagml/envelope.py tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_conformance_error_parity.py` — passed.
- `git diff --check` — passed.

Tests not run:
- Full `pytest tests/` and full `mypy` were not run; W23 gate was kept to targeted error/refusal/runtime-envelope/ledger/compile/Ruff coverage.

Rust/native stable codes:
No Rust edits were needed. No new Rust-native stable error codes are proposed in this slice; the Python host maps existing dag-ml fallback/unavailable/runtime/request failures into the coarse RT-003 `cause` vocabulary.

Commits:
W23 worktree local commit: `e3335e56` (`test(dagml): pin error refusal parity`). Not pushed.

Sync doc updated: no
