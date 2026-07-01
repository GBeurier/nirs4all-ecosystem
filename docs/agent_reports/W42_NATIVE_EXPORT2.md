# W42 report - native export coverage expansion

Summary:
Extended true native `.n4a` export beyond the W33 branch-fusion subset to by_source mean-fusion artifacts. Added a source-splitting wrapper that replays one captured REFIT model per source and averages predictions without invoking the legacy bridge. Pinned stacking native `.n4a` export as a strict xfail blocker because native results still lack a replay manifest for base-prediction meta-feature construction.

Code changed:
Yes.

Files touched:
`nirs4all/api/result.py`
`nirs4all/pipeline/dagml/native_results.py`
`tests/integration/parity/test_dagml_native_n4a_bundle.py`

Commits:
`8bba1f51a1a97e57b3e0649d757a600b43762db2` (`feat(dagml): export by-source native n4a bundles`)

Tests run:
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_dagml_native_n4a_bundle.py::test_by_source_fusion_n4a_export_never_refits_on_legacy`
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_dagml_native_n4a_bundle.py`
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_conformance_n4a_cross_engine.py`
`PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -q tests/integration/parity/test_dagml_native_results.py::test_native_results_model_artifact_round_trip tests/integration/parity/test_dagml_native_results.py::test_native_results_model_artifact_tamper_raises_before_load`
`/home/delete/miniconda3/bin/python3 -m py_compile nirs4all/api/result.py nirs4all/pipeline/dagml/native_results.py tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_conformance_n4a_cross_engine.py`
`/home/delete/.local/bin/ruff check nirs4all/api/result.py nirs4all/pipeline/dagml/native_results.py tests/integration/parity/test_dagml_native_n4a_bundle.py tests/integration/parity/test_conformance_n4a_cross_engine.py`

Tests not run and why:
Full native-results suite not run; focused artifact round-trip/tamper tests plus the full native bundle suite covered the changed manifest and export paths. No cross-engine by_source fusion case was added because the legacy engine rejects `merge: "mean"` for that shape, making interchange coverage inapplicable.

Blockers:
Native stacking `.n4a` export remains blocked: native artifacts include base and meta REFIT models, but native results do not persist the replay graph/column-order manifest needed to build meta-features from raw X.

Impact on blockers/locks:
B-011 advanced for by_source mean-fusion native artifacts. Stacking is now pinned with a precise strict xfail blocker. `EXPECTED_FALLBACK` was not changed.

Next action:
Define and persist a native stacking replay manifest that records base producer order, meta-feature construction, and any source/block routing needed to replay the meta-model from raw bundle input.

Sync doc updated: no
