# W65 Multisource Distinct Preprocessing

## Status

Green in the W65 workspace.

`multi_source_by_source_branch_distinct_preproc` now runs natively for the exact target shape:

```python
[
    ShuffleSplit(n_splits=3, random_state=42),
    {"branch": {"by_source": True, "steps": {
        "source_0": [SNV()],
        "source_1": [MSC()],
        "source_2": [FirstDerivative()],
    }}},
    {"merge": "concat"},
    {"model": PLSRegression(n_components=10)},
]
```

## Implementation Notes

- Added a detector for the exact by_source DICT preprocessing + concat + one downstream model shape.
- The runner consumes `plan.source_layout.source_order` and rejects any source-step key mismatch; legacy keys are not inferred from dict order.
- Per-source preprocessing chains are lowered into model metadata and fitted fold-locally in the node runner before concatenation.
- The native estimator mirrors legacy concat behavior: after writing the merged block into source 0, non-primary sources remain visible to the downstream multi-source fit.
- The result projection duplicates the by_source merge result block per source to match legacy `RunResult.num_predictions` bookkeeping.
- Removed only `multi_source_by_source_branch_distinct_preproc` from the expected fallback set and updated the compatibility meter by one.

## Validation

Passed:

```bash
.venv/bin/python -m py_compile nirs4all/pipeline/dagml/envelope.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py nirs4all/pipeline/dagml/node_runner.py tests/integration/parity/test_dagml_cli_runner.py tests/integration/parity/test_conformance_dual_engine.py
.venv/bin/python -m pytest tests/integration/parity/test_dagml_cli_runner.py -k 'multi_source_emission_emits_feature_block_set or by_source_branch_detection' -q
.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py -k 'multi_source_by_source_branch_distinct_preproc' -q
.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py -k 'multi_source_by_source_branch_distinct_preproc or native_fallback_boundary or coverage_meter' -q
.venv/bin/python -m ruff check nirs4all/pipeline/dagml/envelope.py nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py nirs4all/pipeline/dagml/run_backend.py nirs4all/pipeline/dagml/node_runner.py tests/integration/parity/test_dagml_cli_runner.py tests/integration/parity/test_conformance_dual_engine.py
```

Full requested subset result: `88 passed, 94 deselected, 2 warnings`.

## Coordination Notes

W69 source-layout support is already present in this workspace baseline; W65 consumes that contract rather than restaging envelope changes. Concurrent source-concat and by-source stacking edits remain in the working tree but were kept out of the W65 staged diff.
