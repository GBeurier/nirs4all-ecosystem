# W62 Branch Dup Three-Way Stacking

## Status

Implemented in the W62 nirs4all worktree:
`/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way`.

`branch_dup_three_way_merge_predictions` now runs native on the dag-ml path and was removed from
`EXPECTED_FALLBACK`. The fallback meter moved from 6 to 5.

## Changed Files

- `nirs4all/pipeline/dagml/detect.py`
  - `_detect_stacking_branch()` now normalizes the branch step through `_duplication_branch_bodies()`, so
    named-dict duplication branches are accepted by the existing stacking detector.
- `nirs4all/pipeline/dagml/run_paths.py`
  - Adds the W51 `metadata.stacking_oof_refit_contract` policy
    `skip_refit_on_incomplete_oof` for the native stack meta node.
  - Adds a named-dict stacking compatibility projection that returns the same CV-only branch/meta row shape
    legacy exposes when its named-dict stacking refit is skipped: 60 score rows and no final/test refit rows.
  - The meta projection trains only on validation OOF branch predictions; test predictions are used only as
    prediction inputs for scoring.
- `nirs4all/pipeline/dagml/cli_runner.py`
  - Adds `metadata.source_index` to multi-source data bindings.
- `nirs4all/pipeline/dagml_bridge.py`
  - Declares model-controller `data_requirements` for W51 dag-ml planner compatibility with
    `tabular_numeric` and `feature_block_set` inputs.
- `tests/integration/parity/test_dagml_cli_runner.py`
  - Adds focused named-dict stacking detector coverage.
- `tests/integration/parity/test_conformance_dual_engine.py`
  - Removes `branch_dup_three_way_merge_predictions` from `EXPECTED_FALLBACK`.
- `docs/compatibility.json`, `docs/compatibility.md`
  - Update expected fallback count 6 -> 5 and native count 81 -> 82.

## Parity Evidence

All commands were run from the W62 nirs4all worktree. The worktree reuses the main nirs4all venv and pins
`PYTHONPATH` to the W51 dag-ml Python extension because the default venv still imports the older dag-ml
extension, which does not support `metadata.stacking_oof_refit_contract`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest \
  tests/integration/parity/test_conformance_dual_engine.py \
  -k 'branch_dup_three_way_merge_predictions' -q
```

Result: `2 passed, 180 deselected`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest \
  tests/integration/parity/test_conformance_dual_engine.py \
  -k 'branch_dup_three_way_merge_predictions or native_fallback_boundary or coverage_meter' -q
```

Result: `88 passed, 94 deselected`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest \
  tests/integration/parity/test_native_fallback_boundary.py -q
```

Result: `12 passed`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m tests.integration.parity.coverage_meter --check
```

Result: `coverage_meter OK (fallback=5, target=0)`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest \
  tests/integration/parity/test_compatibility_ledger.py -q
```

Result: `2 passed`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m py_compile \
  nirs4all/pipeline/dagml/detect.py \
  nirs4all/pipeline/dagml/run_backend.py \
  nirs4all/pipeline/dagml/run_paths.py \
  nirs4all/pipeline/dagml/cli_runner.py \
  nirs4all/pipeline/dagml_bridge.py
```

Result: pass.

```bash
ruff check nirs4all/pipeline/dagml nirs4all/pipeline/dagml_bridge.py tests/integration/parity
```

Result: `All checks passed!`.

```bash
PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/W62-nirs4all-branch-dup-three-way \
  /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest \
  tests/integration/parity/test_dagml_cli_runner.py -k 'stacking_branch_detection' -q
```

Result: `1 passed, 107 deselected`.

## Remaining Risk

- The named-dict projection is intentionally narrow and preserves legacy's CV-only row surface for this
  syntax. List-form stacking still uses the existing meta-node projection.
- The W51 planner compatibility fix for multi-source model data requirements was necessary for the
  requested fallback-boundary gate under the W51 dag-ml extension. It does not change the target fallback
  count directly, but it keeps the broader boundary matrix green in the current integration environment.
