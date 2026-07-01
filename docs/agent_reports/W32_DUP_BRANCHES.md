# W32 report - duplication branch feature merge

Summary:
W32 drained `branch_dup_two_way_merge_features`. The dag-ml backend now recognizes legacy duplication branches, including named-dict duplication syntax, followed by `merge="features"` and a downstream plain estimator. It lowers the branch feature chains into a fold-local sklearn-compatible transformer before the downstream model, preserving fold-local fitting.

Code changed:
- Added duplication branch body detection for list and non-`by_*` named-dict syntax.
- Added `DuplicationBranchMergeTransformer` for feature concatenation inside native CV folds.
- Routed the supported duplication `merge="features"` shape to the concrete native dag-ml path.
- Removed `branch_dup_two_way_merge_features` from `EXPECTED_FALLBACK`.
- Updated compatibility ledger counts to fallback `6`, native `81`.

Files touched:
- `nirs4all/pipeline/dagml/detect.py`
- `nirs4all/pipeline/dagml/run_paths.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `docs/compatibility.json`
- `docs/compatibility.md`

Commits:
- `nirs4all/refactor/W32-dup-branches` `0f772104`
- Integrated into `nirs4all/refactor/integration-nirs4all` as merge `e6299d52`

Tests run:
- In W32 worktree: `test_conformance_dual_engine.py -k 'branch_dup_two_way_merge_features or fallback_allowlist'` -> `2 passed`.
- In integration: `test_conformance_dual_engine.py -k 'branch_dup_two_way_merge_features or native_fallback_boundary'` -> `88 passed`.
- `test_native_fallback_boundary.py` -> `12 passed`.
- `test_compatibility_ledger.py` -> `2 passed`.
- `coverage_meter --check` -> `coverage_meter OK (fallback=6, target=0)`.
- `ruff check` on touched Python files -> passed.
- `py_compile`, JSON validation, `git diff --check` -> passed.

Impact:
Advances `B-010`; remaining fallback allowlist is now six cases.

Next action:
Target remaining duplication branch cases: `branch_dup_three_way_merge_predictions`, `branch_dup_named_with_metamodel`, and `branch_dup_merge_all`.

Sync doc updated: yes
