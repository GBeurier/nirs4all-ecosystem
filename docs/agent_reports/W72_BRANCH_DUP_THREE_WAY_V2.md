# W72 Branch Dup Three-Way V2

Status: complete, green, committed in the W72 nirs4all worktree.

Timestamp: 2026-07-01T05:55:11Z

## Summary

Drained `EXPECTED_FALLBACK` case `branch_dup_three_way_merge_predictions`.

The case can run natively without changing the legacy row/refit surface by using dag-ml's explicit `cv_only` stacking refit policy for legacy named-dict duplication stacking. The native run still executes the CV stacking path, while the nirs4all projection preserves legacy's CV-only no-refit prediction table and strips native refit artifacts from the projected `RunResult`.

`EXPECTED_FALLBACK` now has 2 cases and the coverage meter now reports fallback 2 / native 85.

## Files Changed

- `nirs4all/pipeline/dagml/detect.py`
- `nirs4all/pipeline/dagml/run_paths.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `docs/compatibility.md`
- `docs/compatibility.json`

Report only, not committed:

- `nirs4all-ecosystem/docs/agent_reports/W72_BRANCH_DUP_THREE_WAY_V2.md`

## Tests

- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:${PYTHONPATH:-} /home/delete/nirs4all/nirs4all/.venv/bin/python -m py_compile nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py`
- `/home/delete/nirs4all/nirs4all/.venv/bin/ruff check nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_dual_engine.py`
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:${PYTHONPATH:-} /home/delete/nirs4all/nirs4all/.venv/bin/mypy nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_dual_engine.py`
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:${PYTHONPATH:-} /home/delete/nirs4all/nirs4all/.venv/bin/python -m tests.integration.parity.coverage_meter --check`
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:${PYTHONPATH:-} /home/delete/nirs4all/nirs4all/.venv/bin/pytest -k 'branch_dup_three_way_merge_predictions or native_fallback_boundary or coverage_meter'`

Final pytest result: 103 passed, 3 skipped, 8372 deselected, 9 warnings in 376.37s.

## Blockers

None.
