# W74 multisource per-source stacking

## Disposition

Drained `EXPECTED_FALLBACK` case `multi_source_per_source_models_stacking`.

The dag-ml path now detects the narrow by-source shared-model stacking shape:

```python
KFold(...)
{"branch": {"by_source": True, "steps": [X-transform*, {"model": Base}]}}
{"merge": "predictions"}
{"model": Meta}
```

This shape is not lowered as normal 3-column OOF stacking. It replays the legacy source-layout contract:

- source branches mutate the shared source layout cumulatively;
- the branch models see `S,R,R` then `S,S,R` then `S,S,S`;
- `{"merge": "predictions"}` in source-branch mode writes the `S,S,S` concat back to source 0 and preserves sources 1 and 2;
- the downstream Ridge fits on the 10,755-column post-merge layout;
- public rows remain CV-only (`0`, `1`, `2`, `avg`, `w_avg`) with no `final` rows.

## Changed

- `nirs4all/pipeline/dagml/detect.py`
  - Added `_detect_by_source_stacking_branch`.
- `nirs4all/pipeline/dagml/run_backend.py`
  - Routed the detected by-source stacking shape before generic source-concat/stacking handling.
- `nirs4all/pipeline/dagml/run_paths.py`
  - Added `_run_by_source_stacking_branch` replay and small source-block helpers.
- `tests/integration/parity/test_conformance_dual_engine.py`
  - Removed `multi_source_per_source_models_stacking` from `EXPECTED_FALLBACK`.
- `docs/compatibility.md`
  - Updated fallback/native counts and documented the replay contract.
- `docs/compatibility.json`
  - Removed the fallback entry and updated coverage meter to fallback `2`, native `85`.

## Verification

- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest 'tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary[multi_source_per_source_models_stacking]' 'tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance[multi_source_per_source_models_stacking]' -q`
  - `2 passed`
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m py_compile nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_backend.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_dual_engine.py`
  - passed
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m ruff check nirs4all/pipeline/dagml/detect.py nirs4all/pipeline/dagml/run_backend.py nirs4all/pipeline/dagml/run_paths.py tests/integration/parity/test_conformance_dual_engine.py`
  - passed
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -k 'multi_source_per_source_models_stacking or native_fallback_boundary or coverage_meter' -q`
  - `103 passed, 738 deselected`
- `/home/delete/nirs4all/nirs4all/.venv/bin/python -m json.tool docs/compatibility.json`
  - passed

## Notes

Scoped mypy was run on the touched DAGML modules and still fails on pre-existing type errors outside this change (`nirs4all/api/result.py`) plus existing typed helper lines in `detect.py` and `run_paths.py`. The new replay path did not introduce a mypy-specific error in its own body.

