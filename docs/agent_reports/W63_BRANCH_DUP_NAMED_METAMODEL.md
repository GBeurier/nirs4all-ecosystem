# W63 report - branch_dup_named_with_metamodel

Summary:
Kept `branch_dup_named_with_metamodel` on the expected fallback boundary. The
case is not equivalent to the current native stacking path, and admitting it
would drop legacy-visible selector and branch-local MetaModel semantics.

Findings:
- The case uses named duplication branches `pls_latent` and `rf_path`, with
  `concat_transform` inside `pls_latent`.
- The top-level `Ridge_MetaModel` runs as a branch-local `MetaModel` after the
  branch step. Legacy emits prediction rows for `Ridge_MetaModel` under both
  branch ids.
- The later structured merge is
  `{"predictions": [{"branch": 0, "select": "best", "metric": "rmse"}, ...],
  "output_as": "features"}`. It is not the same as `{"merge": "predictions"}`:
  it selects the best model already present inside each branch and materializes
  those selected OOF predictions as features for the final `Ridge`.
- A legacy probe measured 75 prediction entries: 15 each for `PLS_Latent`,
  `RF`, and final `Ridge`, plus 30 for branch-local `Ridge_MetaModel`.
  Legacy also warns `Stacking refit expects duplication branches (list).
  Skipping.`, so the public row surface includes this refit-skip behavior.

Why native support is blocked:
- `nirs4all/pipeline/dagml/detect.py::_duplication_branch_bodies` already
  normalizes named-dict duplication branches and preserves insertion order, but
  `_detect_stacking_branch` does not use the normalized bodies. It still reads
  `branch_step["branch"]` directly and requires raw list-of-lists syntax. That
  is one concrete detector bug for this target, but fixing it alone is not
  enough.
- `nirs4all/pipeline/dagml/detect.py::_detect_stacking_branch` only admits
  simple duplication `{"merge": "predictions"}` followed by one handled
  downstream meta-learner. It explicitly rejects structured per-branch
  prediction configs.
- `nirs4all/pipeline/dagml/run_paths.py::_run_stacking_branch` lowers one
  native `merge_model` over base branch OOF. It does not model a branch-local
  `MetaModel` step first, then a second structured selector/merge, then a final
  downstream model.
- The native path has no API to express `select="best", metric="rmse"` per
  branch across all prior branch models, including a branch-local MetaModel.
- W51's `stacking_oof_refit_contract` is necessary for OOF/refit coverage
  decisions, but it does not cover this case's branch-local selector and
  `output_as="features"` materialization contract. Using it alone would still
  run a different graph.
- The target `StackingConfig(DROP_INCOMPLETE, min_coverage_ratio=0.95)` happens
  to be full-coverage for this dataset, but admitting the case on that basis
  would still ignore a non-default public option. A safe native detector needs
  an explicit proof/gate that coverage is complete before treating the option as
  a no-op.

Required contract/API changes:
- Add a dag-ml/nirs4all native representation for branch-local MetaModel
  execution inside duplication branches, preserving branch ids/names and the
  legacy prediction-row surface.
- Add a structured prediction-merge node that can select models per branch by
  validation metric, including models produced earlier in the branch, and emit
  the selected OOF/test predictions as a feature matrix for a downstream model.
- Define the coverage-policy contract for `CoverageStrategy.DROP_INCOMPLETE`
  and `min_coverage_ratio` in the host-to-dag-ml interface, including the
  full-coverage shortcut and failure diagnostics for partial coverage.
- Define whether legacy's branch-local MetaModel refit skip is a compatibility
  requirement or an intentional native divergence, then encode it in
  conformance before removing the fallback.

Code changed:
None in `nirs4all`. The expected fallback entry remains.

Files changed:
- `docs/agent_reports/W63_BRANCH_DUP_NAMED_METAMODEL.md`

Tests run:
- Pending in W63 validation.

Fallback status:
Still blocked. `branch_dup_named_with_metamodel` must remain in
`EXPECTED_FALLBACK` until the structured branch-local stacking/merge contract
exists and native parity is green.
