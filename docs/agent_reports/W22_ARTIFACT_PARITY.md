# W22 report - artifact/workspace parity

Summary:
Closed the local Python-side blocker that prevented the B-011 workspace/artifact parity tests from exercising the native dag-ml path. The installed `dag_ml_data` wheel exposes the JSON envelope builder (`build_coordinator_data_plan_envelope_json`) rather than the older object-returning builder, so the nirs4all dag-ml envelope adapter now supports both APIs.

Code changed:
- `nirs4all/pipeline/dagml/envelope.py`: build schema/data-plan/relation payloads once, call the legacy object API when present, and otherwise call the JSON API and parse its JSON response back to the dict shape used by the rest of the bridge.

Parity coverage verified:
- `.n4a` cross-engine bundle round-trip coverage: legacy bundle vs dag-ml bundle, plus dag-ml bundle vs dag-ml native final-test predictions.
- Workspace/native-results read-back coverage: native `manifest.json` + `score_set.json` + `predictions.parquet` read back faithfully and agree with legacy within cross-impl bands.
- Bundle IO parity coverage: exported `.n4a` bundles reload through `BundleLoader` and reproduce selected held-out predictions.
- Export surface coverage: no-workspace/export selector behavior remains pinned without requiring a pipeline run.

Files touched:
- `nirs4all/pipeline/dagml/envelope.py`
- `docs/agent_reports/W22_ARTIFACT_PARITY.md`

Commits:
- `303ded0e fix(dagml): support json envelope builder` in `_worktrees/W22-nirs4all-artifacts`.

Tests run:
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH pytest tests/integration/parity/test_cross_engine_export_surface.py tests/integration/parity/test_conformance_workspace_cross_engine.py tests/integration/parity/test_conformance_n4a_bundle_parity.py tests/integration/parity/test_conformance_n4a_cross_engine.py -q`
  - Result: 15 passed, 2 expected transitional dag-ml export bridge warnings.
- `/home/delete/miniconda3/bin/python3 -m py_compile nirs4all/pipeline/dagml/envelope.py nirs4all/pipeline/dagml/native_results.py tests/integration/parity/test_conformance_n4a_cross_engine.py tests/integration/parity/test_conformance_workspace_cross_engine.py tests/integration/parity/test_conformance_n4a_bundle_parity.py tests/integration/parity/test_cross_engine_export_surface.py`
  - Result: passed.
- `ruff check nirs4all/pipeline/dagml/envelope.py nirs4all/pipeline/dagml/native_results.py tests/integration/parity/test_conformance_n4a_cross_engine.py tests/integration/parity/test_conformance_workspace_cross_engine.py tests/integration/parity/test_conformance_n4a_bundle_parity.py tests/integration/parity/test_cross_engine_export_surface.py`
  - Result: passed.

Environment note:
The pytest interpreter did not have `dag-ml` installed from the package index, and the configured index had no `dag-ml>=0.2.1` distribution. Verification used the existing sibling checkout artifacts: `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python` and `PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH`.

Blockers:
None remaining for the verified W22 Python-side parity slice. Native `.n4a` export remains transitional through the existing legacy-refit bridge; the tests pin that bridge and will tighten when native bundle export lands below Python.

Impact on blockers/locks:
`B-011` workspace/artifact half has real cross-engine round-trip coverage passing locally with native dag-ml artifacts available.

Sync doc updated: no
