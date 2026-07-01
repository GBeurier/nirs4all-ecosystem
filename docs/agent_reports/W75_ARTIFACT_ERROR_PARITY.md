# W75 report - artifact/error parity

Summary:
Advanced the B-011 workspace/artifact parity gate in `_worktrees/W75-nirs4all-artifact-error-parity`. The workspace/native-results integration test now asserts that a dag-ml native-results directory projects through `RtResult.from_native_dir()` to the same runtime ScoreSet hash, reports, and final-test predictions as the live dag-ml `RunResult.to_rt_result()` projection.

Code changed:
- `tests/integration/parity/test_conformance_workspace_cross_engine.py`: added the runtime projection parity assertion on top of the existing native triple read-back and cross-engine comparisons.
- `nirs4all/api/result.py`: renamed native by_source export locals so mypy keeps the by_source fusion wrapper type distinct from the single-model export wrapper.
- `nirs4all/pipeline/dagml/detect.py`: tightened source-concat strategy parsing to accept only string strategies.
- `nirs4all/pipeline/dagml/run_paths.py`: added explicit local types for source layout lists, cloned prediction payloads, and named-stacking meta fold predictions.

Behavior notes:
- No fallback numerics changed.
- No fallback allowlists changed.
- The code edits outside the test are type-shape cleanups only; runtime control flow and calculations are unchanged.

Reports/tests inspected:
- `W22_ARTIFACT_PARITY.md`
- `W23_ERROR_PARITY.md`
- `W42_NATIVE_EXPORT2.md`
- `W43_PY_RT_GOLDENS.md`
- Current B-011 parity tests for export surface, error/refusal, workspace/native-results, `.n4a` cross-engine, and native `.n4a` bundles.

Tests run:
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH rtk pytest -q tests/integration/parity/test_conformance_workspace_cross_engine.py` -> 2 passed.
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH rtk pytest -q tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_conformance_error_parity.py tests/integration/parity/test_conformance_workspace_cross_engine.py tests/integration/parity/test_conformance_n4a_cross_engine.py tests/integration/parity/test_conformance_n4a_bundle_parity.py` -> 19 passed.
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH rtk pytest -q tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_conformance_error_parity.py tests/integration/parity/test_conformance_workspace_cross_engine.py tests/integration/parity/test_conformance_n4a_cross_engine.py tests/integration/parity/test_conformance_n4a_bundle_parity.py` -> 27 passed.
- `rtk /home/delete/miniconda3/bin/python3 -m py_compile nirs4all/api/result.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_workspace_cross_engine.py` -> passed.
- `rtk ruff check nirs4all/api/result.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_workspace_cross_engine.py` -> passed.
- `rtk /home/delete/miniconda3/bin/python3 -m mypy tests/integration/parity/test_conformance_workspace_cross_engine.py` -> passed.
- `rtk git diff --check` -> passed.

Commit:
- `f13a86a8 test(dagml): pin native rt projection parity` in `_worktrees/W75-nirs4all-artifact-error-parity`.

Sync doc updated: no
