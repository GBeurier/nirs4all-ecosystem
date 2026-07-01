# W41 report - fallback final

Summary:
Inspected the six remaining EXPECTED_FALLBACK cases and tried three narrow native lowerings. None survived parity, so no native coverage was claimed and the allowlist/ledger remain unchanged at fallback=6.

Code changed:
No surviving code change. Temporary experiments were reverted before final verification.

Files touched:
- /home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/W41_FALLBACK_FINAL.md

Commits:
None.

Tests run:
- `.venv/bin/pytest tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance[branch_dup_three_way_merge_predictions] -q` on a temporary named-dict stacking detector: failed with dag-ml runtime validation, `OOF predictions do not cover the refit sample universe`.
- `.venv/bin/pytest tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance[multi_source_per_source_models_stacking] -q` on a temporary by-source stacking path: failed parity, legacy num_predictions=90 vs dag-ml=16 and RMSE delta about 0.11.
- `.venv/bin/pytest tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance[multi_source_by_source_branch_distinct_preproc] -q` on a temporary source-specific concat transformer: failed parity, RMSE 12.634815803699208 vs 12.513325334728366.
- `.venv/bin/pytest tests/integration/parity/test_native_fallback_boundary.py tests/integration/parity/test_compatibility_ledger.py -q`: 14 passed.
- `.venv/bin/python -m tests.integration.parity.coverage_meter --check`: OK, fallback=6.
- `.venv/bin/python -m py_compile nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/test_conformance_dual_engine.py tests/integration/parity/coverage_meter.py`: passed.
- `.venv/bin/ruff check nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/test_conformance_dual_engine.py tests/integration/parity/coverage_meter.py`: passed.
- `.venv/bin/mypy nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py`: passed.

Tests not run and why:
Full slow dual-engine parity was not run because no native lowering survived and the final tracked backend code is unchanged.

Blockers:
- `branch_dup_three_way_merge_predictions`: named-dict duplication stacking can be detected, but the native merge-model refit requires complete validation OOF coverage. This case uses ShuffleSplit, and dag-ml rejects with `OOF predictions do not cover the refit sample universe`. Legacy also logs `Stacking refit expects duplication branches (list). Skipping`, so native needs an explicit CV-only/refit-skip or OOF coverage/imputation contract before this can leave fallback.
- `branch_dup_named_with_metamodel`: still needs structured per-branch prediction selectors plus MetaModel coverage options (`DROP_INCOMPLETE`, `min_coverage_ratio`) and branch-local concat_transform/model bookkeeping. The current native stacking detector only covers plain `merge: predictions` with a default MetaModel/plain estimator.
- `branch_dup_merge_all`: needs a native `merge: all` contract that combines branch features and branch OOF predictions in the same downstream feature matrix, plus matching branch-model score/refit projection. Existing native paths cover feature-only duplication concat or prediction stacking, not the combined mode.
- `multi_source_by_source_branch_distinct_preproc`: a simple per-source split/fold-local preprocessing transformer is not parity. Legacy shape logging shows `[2151, 2151, 2151] -> [6453, 2151, 2151]`, and the attempted native value missed RMSE by about 0.12. Needs an exact legacy by-source dict reassembly/layout contract before native lowering is honest.
- `multi_source_per_source_models_stacking`: a native by-source merge-model path runs but is not parity: legacy emits 90 prediction rows and model labels `PLSRegression`/`Ridge`, while dag-ml emitted 16 rows and a single meta-model label, with RMSE delta about 0.11. Needs a decided by-source stacking result/refit contract or a new authoritative engine decision, not an allowlist drop.
- `multi_source_sources_concat_then_rf`: still blocked by the explicit source-concat merge boundary and RF sensitivity. Native early-fusion preprocessing does not reproduce legacy's per-source preprocessing plus merge/storage round-trip behavior within tolerance.

Impact on blockers/locks:
No reduction to EXPECTED_FALLBACK. LOCK-DROP D1 remains blocked at fallback=6, but the failed probes narrow the missing contracts for three cases.

Next action:
Do not drain these by detector widening alone. The next useful slice is a contract decision for stacking with incomplete OOF/refit skip, or a dag-ml-data/native contract for exact by-source dict feature reassembly.

Sync doc updated: no
