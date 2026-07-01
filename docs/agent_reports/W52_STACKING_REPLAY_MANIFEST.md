# W52 report - native stacking replay manifest

Summary:
Advanced B-011 for branch stacking `.n4a` bundles. Native results now persist a `stacking_replay` manifest when a dag-ml stacking run has an unambiguous set of captured REFIT artifacts: base branch models plus one meta-model artifact. Native `.n4a` export consumes that manifest to rebuild ordered base-prediction meta-features from raw `X` and replay the captured meta REFIT model without the legacy bridge.

Code changed:
Yes.

Files touched:
`nirs4all/pipeline/dagml/native_results.py`
`nirs4all/api/result.py`
`tests/integration/parity/test_dagml_native_results.py`
`tests/integration/parity/test_dagml_native_n4a_bundle.py`

What changed:
- Bumped the native results manifest schema to v3 and added artifact `producer_node` metadata.
- Added `stacking_replay` with the meta artifact id, base producer/artifact order, and meta-feature construction contract (`base_prediction_column_stack`, sorted prediction-input base key order, original target prediction space).
- Added `_DagmlNativeStackingModel` and `.n4a` export wiring for manifest-backed branch stacking replay.
- Replaced the strict stacking xfail with an executable native bundle test that poisons the legacy bridge and checks final-test RMSE parity.
- Added a focused native-results test pinning the stacking replay manifest and rehydrated artifact metadata.

Tests run:
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_dagml_native_results.py::test_native_results_stacking_replay_manifest tests/integration/parity/test_dagml_native_n4a_bundle.py::test_branch_stacking_n4a_export_never_refits_on_legacy`
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_dagml_native_n4a_bundle.py`
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_dagml_native_results.py::test_native_results_model_artifact_round_trip tests/integration/parity/test_dagml_native_results.py::test_native_results_model_artifact_tamper_raises_before_load tests/integration/parity/test_dagml_native_results.py::test_native_results_stacking_replay_manifest`
`/home/delete/miniconda3/bin/python3 -m py_compile nirs4all/api/result.py nirs4all/pipeline/dagml/native_results.py tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_dagml_native_results.py`
`/home/delete/.local/bin/ruff check nirs4all/api/result.py nirs4all/pipeline/dagml/native_results.py tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_dagml_native_results.py`

Tests not run and why:
Full native-results suite not run; W52 touched artifact metadata and stacking replay, covered by focused artifact/manifest tests plus the full native `.n4a` bundle suite.

Blockers:
None for the handled duplication-branch stacking shape (`branch` list + `merge: "predictions"` + downstream meta model). Native export remains intentionally gated by manifest presence; malformed, older, subprocess/no-artifact, or richer unsupported composite shapes still fall through to the existing bridge path.

Impact on blockers/locks:
B-011 advanced: native branch stacking `.n4a` bundles can now replay from raw `X` without invoking the legacy bridge when v3 native results include the replay manifest. `detect.py` / `run_paths.py` fallback boundaries were not lowered.

Next action:
Broaden the replay manifest only after dag-ml exposes or nirs4all persists explicit contracts for richer stacking layouts (for example by-source stacking, transformed meta-feature variants, or non-default meta-model wrappers).
