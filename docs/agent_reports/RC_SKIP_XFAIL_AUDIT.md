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

- Studio backend `54 skipped` is not all optional environment debt:
  - about `46` skips are operator fixture debt in `tests/test_operator_definitions.py`;
  - native-results skips are environment/job-shape dependent and should live in a dedicated native-results job.
- Studio frontend `1 skipped` is Windows-only path behavior in `electron/portable-paths.test.ts`.
- Benchmarks `1 skipped` is optional CI/runtime coverage and should be rerun in the service-extra environment if zero skips is required.
- Python parity `30 skipped / 11 xfailed` is ledgerized, but not production-flip proof:
  - registry skips are real missing coverage;
  - xfails include known divergences plus legacy-bug cases.

## Required Follow-Up

- Replace Studio operator-definition skips with family fixtures for `y`, metadata, wavelengths, groups, NaN, graph inputs, and alias resolver behavior.
- Implement Python parity registry skips:
  - `branch_separation_by_metadata_auto`
  - `exclude_multi_any_y_and_x`
  - `aggregation_classification_vote`
  - `refit_params_use_all_partitions`
- Do not force dag-ml to reproduce documented legacy double-count bugs for `rep_to_sources_basic` / `rep_to_pp_basic`; adapt/remove those dual-engine expectations when the legacy layer is retired.

## Risk

The audited skip/xfail counts remain release blockers unless each item is either implemented or moved to a clearly separate optional-environment gate with replacement coverage.
