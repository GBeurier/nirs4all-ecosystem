# RC Skip / Xfail Audit

Date: 2026-07-02  
Agent: Codex/Laplace, read-only; coordinator refresh after Python `42448821`

## Scope

Read-only audit of skip/xfail debt visible in the current RC gates:

- `RC-v1-studio`
- `RC-v1-web`
- `RC-v1-nirs4all-python`
- prior targeted benchmarks result

The initial audit was read-only. The coordinator later refreshed this report
after the full Python parity rerun on `42448821`.

## Findings

- Studio operator fixture debt has been burned down after the original audit:
  - `tests/test_operator_definitions.py` now passes with `445 passed` and 0 skips after replacing skipped fixture families with deterministic local inputs;
  - the combined Studio runtime/operator/quick-run RC stack gate passes with `464 passed`.
- Studio full-backend result is refreshed after the current batch: `2324 passed, 6 skipped` in `1465.99s`. Remaining skips are Windows-only/env/example-access categories, not operator-definition fixture debt.
- Studio frontend `1 skipped` is Windows-only path behavior in `electron/portable-paths.test.ts`.
- Benchmarks `1 skipped` is optional CI/runtime coverage and should be rerun in the service-extra environment if zero skips is required.
- Python parity `30 skipped / 11 xfailed` is stale. Current targeted accounting after `99d57b7e` was stricter on real parity debt:
  - `1234db31 fix(parity): remove registry skip debt` implements the four registry cases previously listed here;
  - `99d57b7e fix(parity): burn down native xfail debt` removes five strict xfails from `KNOWN_DIVERGENCES`;
  - targeted four-case parity gate passed with `20 passed`;
  - targeted dual-engine burn-down gate passed with `10 passed`;
  - broader compile/smoke/fallback gate passed with `203 passed, 6 skipped`;
  - marker audit still reports sanctioned `registry_skip` call sites by AST, which are distinct from live disabled `PipelineCase` entries;
  - strict xfails are now 6: 4 known divergences plus 2 branch native-boundary cases.
- Python full parity was refreshed after `42448821 fix(parity): handle disabled chart steps in dagml`:
  - `tests/integration/parity`: `853 passed, 14 skipped, 6 xfailed` in `2281.65s`;
  - the previous four failures are closed: disabled chart-only example steps, public example refusal ledger drift, and two sample-augmentation direct-baseline mismatches;
  - remaining skips are explicit: missing local `n4m` binding, empty fallback-boundary sentinel, six legacy-bug branch instances across baseline/compile/smoke, optional SHAP, and optional `referencing` for RT schema goldens;
  - remaining strict xfails are unchanged at 6 and listed below.

Xfail classification after the RC reviewer audit:

- Fix first: `concat_transform_pca_svd_plsr`.
- Justify or replace with a non-equivalence contract: `generator_sample_log_uniform_alpha`, `rep_to_sources_basic`, `rep_to_pp_basic`.
- Correct or reclassify native-boundary behavior if V1 keeps the DSL path: `branch_separation_by_tag`, `branch_separation_by_filter`. The explicit legacy path is now locked by dedicated tests.

## Required Follow-Up

- Track remaining Studio skips as optional/environment gates, not operator debt.
- Full Python parity has been refreshed on `42448821`; do not cite `99d57b7e` as the current proof head.
- Decide release treatment for the 14 skipped instances:
  - install/prove `n4m` for methods binding parity instead of accepting the local environment skip;
  - either keep the two branch legacy-bug cases as legacy-oracle defects or implement the bridge path and remove the skips;
  - install SHAP / `referencing` in the release-proof environment or move them to explicit optional-environment gates with replacement coverage;
  - keep the empty fallback-boundary sentinel only while `EXPECTED_FALLBACK` is empty.
- Do not force dag-ml to reproduce documented legacy double-count bugs for `rep_to_sources_basic` / `rep_to_pp_basic`; adapt/remove those dual-engine expectations when the legacy layer is retired.

## Risk

The audited skip/xfail counts remain release blockers unless each item is either implemented or moved to a clearly separate optional-environment gate with replacement coverage.
