# W68 report - stacking OOF/refit contract audit

Date: 2026-07-01

Summary:
Audited dag-ml's stacking OOF/refit contract and the current nirs4all lowering paths against the
INT baselines. dag-ml already exposes the needed runtime contract; nirs4all only needed explicit
metadata emission on native stacking `merge_model` nodes that are proven full-coverage.

Code changed:
- Plain duplication stacking now emits
  `metadata.stacking_oof_refit_contract = {"policy": "require_full_coverage"}`.
- The current by-source stacking path already emitted the same explicit metadata and was left unchanged.
- No dag-ml code changed.
- `EXPECTED_FALLBACK` was not changed.

Files changed:
- `nirs4all/pipeline/dagml/run_paths.py`
- `nirs4all-ecosystem/docs/agent_reports/W68_STACKING_OOF_CONTRACT_AUDIT.md`

Audit findings:
- dag-ml INT baseline already reserves metadata key `stacking_oof_refit_contract` and validates
  `require_full_coverage`, `cv_only`, and `skip_refit_on_incomplete_oof` in
  `validate_stacking_oof_refit_contract`.
- `validate_refit_oof_edge` reads that metadata from the target `merge_model` node, so nirs4all must
  place the contract on the meta node, not on base branch model nodes.
- Full-coverage native duplication stacking uses duplication-mode branches over the full train/refit
  sample universe. It should emit `require_full_coverage` explicitly. The dag-ml default is the same,
  but explicit metadata keeps the cross-repo contract visible.
- By-source stacking is also full sample coverage when each source-bound base producer sees all
  samples and only changes the feature block. It should emit `require_full_coverage` for targets that
  expect final/refit rows.
- Legacy CV-only stacking behavior should use `cv_only`, not synthesized native refit rows.
- Incomplete but otherwise valid OOF should use `skip_refit_on_incomplete_oof` only when nirs4all has a
  documented legacy drop/coverage policy and the intended behavior is to skip REFIT. Invalid OOF must
  remain invalid under every policy.

W62/W63/W66 policy recommendation:
- W62 full duplication stacking: set the meta `merge_model` metadata to
  `{"controller_id": "controller:nirs4all.meta_model", "stacking_oof_refit_contract":
  {"policy": "require_full_coverage"}}`.
- W63 named `MetaModel` with `DROP_INCOMPLETE` / `min_coverage_ratio`: keep fallback until the
  branch-local MetaModel, structured per-branch selector, and coverage semantics are implemented and
  green. If a future detector proves the selected OOF is complete, use `require_full_coverage`; if it is
  valid but intentionally incomplete and legacy skips refit, use `skip_refit_on_incomplete_oof`. Do not
  map `DROP_INCOMPLETE` or `min_coverage_ratio` to metadata alone.
- W66 by-source stacking: use `require_full_coverage` when every source-bound base producer covers the
  full CV train/refit universe and final/refit rows are expected. Use `cv_only` only for a documented
  legacy CV-only/no-refit case; use `skip_refit_on_incomplete_oof` only for a documented valid partial
  OOF case where REFIT must be skipped.

Blockers / non-goals:
- The W63 `branch_dup_named_with_metamodel` case is still not represented by this contract alone. It
  needs branch-local MetaModel execution, a structured branch prediction selector, and a decision on the
  legacy branch-local refit-skip row surface before leaving `EXPECTED_FALLBACK`.
- The current workspace has no `W66*` worktree to inspect directly; the by-source stacking guidance is
  based on the current nirs4all working copy plus the dag-ml INT contract.

Tests:
- `/home/delete/miniconda3/bin/python3 -m py_compile nirs4all/pipeline/dagml/*.py
  nirs4all/pipeline/dagml_bridge.py` - passed.
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python
  /home/delete/miniconda3/bin/python3 -m pytest -q
  tests/integration/parity/test_dagml_cli_runner.py::test_stacking_branch_detection` - passed.
- `PYTHONPATH=/home/delete/nirs4all/dag-ml-data/crates/dag-ml-data-py/python:/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python
  /home/delete/miniconda3/bin/python3 -m pytest -q
  tests/integration/parity/test_dagml_cli_runner.py::test_public_run_engine_dagml_stacking_branch` - passed.
- dag-ml validation was not run because dag-ml was not changed.
