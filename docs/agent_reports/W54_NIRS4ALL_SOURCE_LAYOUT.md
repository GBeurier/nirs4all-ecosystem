# W54 report - nirs4all source layout parity

Summary:
W54 did not claim native coverage for the two prioritized by-source/source-concat failures. W41's failed probes still point to a missing source-layout contract rather than a detector-only gap, so this slice keeps the fallback entries unchanged and adds executable strict-xfail probes naming the fields needed from W53.

Code changed:
- Documented why `_detect_by_source_concat_shared_preproc` still excludes per-source dict bodies: exact lowering needs `source_layout.source_order` plus per-source preprocessing output layout.
- Added two strict xfail contract probes:
  - `multi_source_by_source_branch_distinct_preproc` requires `source_layout.source_order`, `source_layout.source_ids`, and `source_layout.per_source_preprocessing_outputs`.
  - `multi_source_sources_concat_then_rf` requires `source_layout.concat_layout` with concat strategy, source order, output source index, and storage round-trip preservation.

Files touched:
- `/home/delete/nirs4all/_worktrees/W54-nirs4all-source-layout/nirs4all/pipeline/dagml/detect.py`
- `/home/delete/nirs4all/_worktrees/W54-nirs4all-source-layout/tests/integration/parity/test_dagml_cli_runner.py`
- `/home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/W54_NIRS4ALL_SOURCE_LAYOUT.md`

Fallback ledger:
- `EXPECTED_FALLBACK` unchanged.
- `docs/compatibility.json` unchanged.
- No export/native-results files edited.
- Stacking untouched.

Tests run:
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_dagml_cli_runner.py -k 'w54_contract' -q` -> 2 xfailed.
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance -k 'multi_source_by_source_branch_distinct_preproc or multi_source_sources_concat_then_rf' -q` -> 2 passed.
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary -k 'multi_source_by_source_branch_distinct_preproc or multi_source_sources_concat_then_rf' -q` -> 2 passed.
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/test_native_fallback_boundary.py tests/integration/parity/test_compatibility_ledger.py -q` -> 14 passed.
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/python -m tests.integration.parity.coverage_meter --check` -> `coverage_meter OK (fallback=6, target=0)`.
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/python -m py_compile nirs4all/pipeline/dagml/detect.py tests/integration/parity/test_dagml_cli_runner.py` -> passed.
- `PYTHONPATH=$PWD /home/delete/nirs4all/nirs4all/.venv/bin/ruff check nirs4all/pipeline/dagml/detect.py tests/integration/parity/test_dagml_cli_runner.py` -> passed.

Blockers:
- `multi_source_by_source_branch_distinct_preproc`: exact native lowering needs a typed source-layout map from legacy source dict keys (`source_0`, `source_1`, `source_2`) to native source ids/block order (`src0`, `src1`, `src2`), plus a per-source preprocessing output layout. Without that, widening the shared-body detector would guess source identity and reproduce W41's non-parity result.
- `multi_source_sources_concat_then_rf`: exact native lowering needs `source_layout.concat_layout` for the explicit `{"merge": {"sources": "concat"}}` boundary, including source order, merged output placement, and whether the legacy storage round-trip is preserved. The fixed-seed RF remains sensitive to this boundary, so treating it as ordinary early fusion is not safe.

Next action:
After W53 lands the source-layout contract, remove the strict xfails only when the contract fields exist and rerun the two targeted dual-engine parity cases as native candidates. Until then, keep both fallback entries unchanged.
