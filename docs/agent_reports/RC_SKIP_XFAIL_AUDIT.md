# RC Skip / Xfail Audit

Date: 2026-07-02  
Agent: Codex/Laplace, read-only

## Scope

Read-only audit of skip/xfail debt visible in the current RC gates:

- `RC-v1-studio`
- `RC-v1-web`
- `RC-v1-nirs4all-python`
- prior targeted benchmarks result

No files were modified by the audit agent.

## Findings

- Studio operator fixture debt has been burned down after the original audit:
  - `tests/test_operator_definitions.py` now passes with `445 passed` and 0 skips after replacing skipped fixture families with deterministic local inputs;
  - the combined Studio runtime/operator/quick-run RC stack gate passes with `464 passed`.
- The older Studio full-backend result `2276 passed, 54 skipped` is stale for operator-definition accounting and must be refreshed after the current batch.
- Studio frontend `1 skipped` is Windows-only path behavior in `electron/portable-paths.test.ts`.
- Benchmarks `1 skipped` is optional CI/runtime coverage and should be rerun in the service-extra environment if zero skips is required.
- Python parity `30 skipped / 11 xfailed` is now stale for live PipelineCase registry-skip accounting:
  - `1234db31 fix(parity): remove registry skip debt` implements the four registry cases previously listed here;
  - targeted four-case parity gate passed with `20 passed`;
  - broader compile/smoke/fallback gate passed with `203 passed, 6 skipped`;
  - marker audit still reports sanctioned `registry_skip` call sites by AST, which are distinct from live disabled `PipelineCase` entries;
  - xfails include known divergences plus legacy-bug cases.

Xfail classification after the RC reviewer audit:

- Fix first: `sample_augmentation_gaussian`, `sample_augmentation_chained`, `sample_augmentation_after_savgol`, `feature_augmentation_replace_three_views`, `concat_transform_pca_svd_plsr`, `generator_finetune_params_optuna`.
- Justify or replace with a non-equivalence contract: `generator_sample_log_uniform_alpha`, `rep_to_sources_basic`, `rep_to_pp_basic`.
- Correct if V1 keeps the DSL path: `branch_separation_by_tag`, `branch_separation_by_filter`.

## Required Follow-Up

- Refresh full Studio backend pytest after current Studio head `1d1ded5`.
- Refresh full Python parity after current Python head `1234db31`.
- Classify the remaining 6 targeted parity skips:
  - legacy-bug skips for `branch_separation_by_tag` and `branch_separation_by_filter`;
  - optional SHAP dependency skip;
  - empty fallback-boundary sentinel.
- Do not force dag-ml to reproduce documented legacy double-count bugs for `rep_to_sources_basic` / `rep_to_pp_basic`; adapt/remove those dual-engine expectations when the legacy layer is retired.

## Risk

The audited skip/xfail counts remain release blockers unless each item is either implemented or moved to a clearly separate optional-environment gate with replacement coverage.
