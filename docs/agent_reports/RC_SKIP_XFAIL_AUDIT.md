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
- Studio full-backend result is refreshed after the current batch: `2324 passed, 6 skipped` in `1465.99s`. Remaining skips are Windows-only/env/example-access categories, not operator-definition fixture debt.
- Studio frontend `1 skipped` is Windows-only path behavior in `electron/portable-paths.test.ts`.
- Benchmarks `1 skipped` is optional CI/runtime coverage and should be rerun in the service-extra environment if zero skips is required.
- Python parity `30 skipped / 11 xfailed` is stale. Current targeted accounting after `99d57b7e` is stricter on real parity debt:
  - `1234db31 fix(parity): remove registry skip debt` implements the four registry cases previously listed here;
  - `99d57b7e fix(parity): burn down native xfail debt` removes five strict xfails from `KNOWN_DIVERGENCES`;
  - targeted four-case parity gate passed with `20 passed`;
  - targeted dual-engine burn-down gate passed with `10 passed`;
  - broader compile/smoke/fallback gate passed with `203 passed, 6 skipped`;
  - marker audit still reports sanctioned `registry_skip` call sites by AST, which are distinct from live disabled `PipelineCase` entries;
  - strict xfails are now 6: 4 known divergences plus 2 branch native-boundary cases.

Xfail classification after the RC reviewer audit:

- Fix first: `concat_transform_pca_svd_plsr`.
- Justify or replace with a non-equivalence contract: `generator_sample_log_uniform_alpha`, `rep_to_sources_basic`, `rep_to_pp_basic`.
- Correct or reclassify native-boundary behavior if V1 keeps the DSL path: `branch_separation_by_tag`, `branch_separation_by_filter`. The explicit legacy path is now locked by dedicated tests.

## Required Follow-Up

- Track remaining Studio skips as optional/environment gates, not operator debt.
- Refresh full Python parity after current Python head `99d57b7e`.
- Classify the remaining 6 targeted parity skips:
  - legacy-bug skips for `branch_separation_by_tag` and `branch_separation_by_filter`;
  - optional SHAP dependency skip;
  - empty fallback-boundary sentinel.
- Do not force dag-ml to reproduce documented legacy double-count bugs for `rep_to_sources_basic` / `rep_to_pp_basic`; adapt/remove those dual-engine expectations when the legacy layer is retired.

## Risk

The audited skip/xfail counts remain release blockers unless each item is either implemented or moved to a clearly separate optional-environment gate with replacement coverage.
