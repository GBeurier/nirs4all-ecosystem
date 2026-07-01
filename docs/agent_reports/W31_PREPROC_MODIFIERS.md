# W31 report - preprocessing modifiers

Summary:
W31 drained the two safe preprocessing-wrapper fallback cases. `fit_on_all=True` now runs native when the wrapped operator is proven stateless, and `force_layout="2d"` now runs native for preprocessing because the legacy preprocessing controller does not consume that modifier.

Code changed:
- Extended dag-ml backend preprocessing unwrap logic for safe modifier-bearing `{"preprocessing": ...}` wrappers.
- Removed `preprocessing_fit_on_all` and `preprocessing_force_layout_2d` from `EXPECTED_FALLBACK`.
- Updated compatibility ledger counts and docs.

Files touched:
- `nirs4all/pipeline/dagml/run_backend.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `docs/compatibility.json`
- `docs/compatibility.md`

Commits:
- `nirs4all/refactor/W31-preproc-modifiers` `b6cd230f`
- Integrated into `nirs4all/refactor/integration-nirs4all` before final Wave-2E tip `e6299d52`

Tests run:
- Targeted dual-engine parity for the two preprocessing cases -> passed.
- `test_native_fallback_boundary.py` + `test_compatibility_ledger.py` -> passed.
- `coverage_meter --check` -> passed.
- Targeted `py_compile` and Ruff -> passed.

Impact:
Advances `B-010` by reducing legacy fallback coverage debt.

Next action:
Continue draining branch and multi-source fallback cases until `EXPECTED_FALLBACK == empty`.

Sync doc updated: yes
