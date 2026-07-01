# W34 report - multi-source shared preprocessing

Summary:
W34 drained `multi_source_by_source_branch_shared_preproc`. The native dag-ml path now handles shared by-source preprocessing followed by concat and one downstream model, applying preprocessing per source and preserving legacy prediction-row bookkeeping.

Code changed:
- Added detection for the shared by-source preprocessing + concat + downstream model shape.
- Added native runtime path that hstacks per-source transformed blocks before the downstream estimator.
- Replicated projected prediction rows per source to match legacy public bookkeeping.
- Removed `multi_source_by_source_branch_shared_preproc` from `EXPECTED_FALLBACK`.

Files touched:
- `nirs4all/pipeline/dagml/detect.py`
- `nirs4all/pipeline/dagml/node_runner.py`
- `nirs4all/pipeline/dagml/run_backend.py`
- `nirs4all/pipeline/dagml/run_paths.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `tests/integration/parity/_authority.py`
- `docs/compatibility.json`
- `docs/compatibility.md`

Commits:
- `nirs4all/refactor/W34-multisource-shared` `4ffff0d`
- Integrated into `nirs4all/refactor/integration-nirs4all` before final Wave-2E tip `e6299d52`

Tests run:
- Targeted native fallback boundary and dual-engine conformance for shared by-source preprocessing -> passed.
- `test_native_fallback_boundary.py` + `test_compatibility_ledger.py` -> `14 passed`.
- `coverage_meter --check` -> passed.
- Targeted `py_compile` and Ruff -> passed.

Impact:
Advances `B-010` for multi-source parity. Remaining multi-source fallbacks are distinct per-source preprocessing, per-source stacking, and source concat into RF.

Next action:
Add native per-source-dict branch contracts or keep them explicit until dag-ml has a stable per-source grouping/materialization contract.

Sync doc updated: yes
