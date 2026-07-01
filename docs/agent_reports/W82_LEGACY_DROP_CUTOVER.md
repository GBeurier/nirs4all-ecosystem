# W82 Legacy-DROP Cutover

## Summary

Implemented the V1 cutover posture in `nirs4all`:

- Default engine resolution now returns `dag-ml`.
- Explicit `engine="legacy"` / `N4A_ENGINE=legacy` remains the compatibility path.
- Dag-ml fallback is strict by default: coverage/backend refusals raise structured `RtError`.
- Explicit `allow_fallback=True` preserves diagnosed legacy fallback and attaches `RtError` diagnostics to the returned legacy result.

## Changed Files

- `nirs4all/pipeline/engine.py`
- `nirs4all/api/run.py`
- `tests/integration/parity/test_dagml_run_selector.py`
- `tests/integration/parity/test_rt_fallback_strict.py`
- `tests/unit/pipeline/test_engine_selector.py`

Note: the unit selector test was updated minimally because it hard-coded the old legacy default and failed after the cutover.

## Commit

- `72c375e8 refactor(runtime): cut over default engine to dag-ml`

## Tests

All final verification used `/home/delete/nirs4all/nirs4all/.venv/bin/python` from the W82 worktree so imports resolved to `/home/delete/nirs4all/_worktrees/W82-nirs4all-cutover-strict`.

- `python -m pytest tests/integration/parity/test_dagml_run_selector.py tests/integration/parity/test_rt_fallback_strict.py -q`  
  Result: 24 passed.
- `python -m pytest tests/integration/parity/test_native_fallback_boundary.py -q`  
  Result: 11 passed, 1 skipped.
- `python -m pytest tests/integration/parity/test_dagml_run_selector.py::test_default_run_matches_legacy_on_representative_conformance_case tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance[baseline_vertical_slice] -q`  
  Result: 2 passed.
- `python -m pytest tests/unit/pipeline/test_engine_selector.py -q`  
  Result: 7 passed.
- `ruff check nirs4all/pipeline/engine.py nirs4all/api/run.py tests/integration/parity/test_dagml_run_selector.py tests/integration/parity/test_rt_fallback_strict.py tests/unit/pipeline/test_engine_selector.py`  
  Result: passed.
- `python -m mypy nirs4all/pipeline/engine.py nirs4all/api/run.py`  
  Result: passed.

## Failures / Blockers

- Initial `python3 -m pytest ...` used system Python 3.10 and failed before collection because `enum.StrEnum` is unavailable on 3.10.
- Initial `python3.11 -m pytest ...` failed before collection because that interpreter lacked repo test dependencies (`matplotlib`).
- `tests/unit/pipeline/test_engine_selector.py` initially failed on the stale `DEFAULT_ENGINE == "legacy"` assertion; fixed in the committed change.
- No remaining blockers.
