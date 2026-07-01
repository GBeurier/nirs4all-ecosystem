# W73 Branch Dup Named MetaModel

Status: drained `EXPECTED_FALLBACK` case `branch_dup_named_with_metamodel`.

## Outcome

- Added a narrow dag-ml native detector for the exact legacy shape:
  `KFold` + named duplication branch + branch-local `MetaModel` + structured per-branch best-by-RMSE prediction merge with `output_as="features"` + downstream estimator.
- Added a host-side compatibility run path that preserves the legacy row contract:
  - branch preprocessing fits on the full train pool before branch-local CV;
  - base branch model rows, branch-local `Ridge_MetaModel` rows, and downstream `Ridge` rows are emitted;
  - row count remains 75 for the parity fixture;
  - no `fold_id="final"` rows are emitted, matching legacy named-dict stacking refit behavior;
  - model surface remains `PLS_Latent`, `RF`, `Ridge_MetaModel`, `Ridge`.
- Removed `branch_dup_named_with_metamodel` from `EXPECTED_FALLBACK`.
- Updated `docs/compatibility.md` and `docs/compatibility.json`: fallback count 3 -> 2, native count 84 -> 85.

## Verification

Required gates:

- `rtk proxy /home/delete/miniconda3/bin/python3 -m py_compile nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_backend.py nirs4all/pipeline/dagml/run_paths.py`
- `rtk ruff check nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_backend.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_dual_engine.py`
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python /home/delete/miniconda3/bin/python3 -m pytest -k "branch_dup_named_with_metamodel or native_fallback_boundary or coverage_meter"`

Result: `103 passed, 3 skipped, 8361 deselected`.

Note: running the pytest selector without the local `dag-ml-py/python` `PYTHONPATH` fails broad native boundary cases with `ModuleNotFoundError: No module named 'dag_ml'`. The successful gate used the local sibling binding and did not install dependencies or edit dependency state.

## Blockers

None for this target. The case now runs natively and satisfies parity for scores, y_pred, prediction-row count, and RunResult surface.
