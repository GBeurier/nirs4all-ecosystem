# WAVE 10I - multisource full-strict promotion

## Scope

Promote `e2e-multisource-branching-stacking-replay` from `hybrid` to `strict`
for its declared deterministic duplication-branch stacking fixture.

This promotion is based on fresh runtime evidence, not on relaxed validation:
the scenario executes Python oracle generation, native/core replay, score-set
parity, predictions.parquet schema audit, and native prediction-vector parity.

## Files modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/CROSS_LANGUAGE_E2E.md`
- `tests/test_e2e_scenarios.py`
- `docs/agent_reports/WAVE_10I_MULTISOURCE_FULL_STRICT.md`

## Tests run

- `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `OK: 11 cross-language E2E scenarios`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - `129 passed`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  - `full_strict_ready=true`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-multisource-strict run --execute e2e-multisource-branching-stacking-replay`
  - passed
- `PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-multisource-strict evidence --scenario e2e-multisource-branching-stacking-replay --json`
  - `verified_count=1`, `artifact_count=5`, `failure_count=0`

## Evidence

`/tmp/n4a-e2e-multisource-strict/multisource-stacking/native-replay.json`
records:

- `status=passed`
- `checks.native_engine=true`
- `checks.native_num_predictions=true`
- `score_set_parity.cv_best_score_abs=1.7763568394002505e-15`
- `score_set_parity.best_rmse_abs=0.0`
- `score_set_parity.tolerance=0.001`
- `prediction_vector_parity.available=true`
- `prediction_vector_parity.compared_rows=59`
- `prediction_vector_parity.max_abs_delta=6.716849298982197e-14`
- `prediction_vector_parity.target_max_abs_delta=0.0`
- `prediction_vector_parity.tolerance=1e-08`
- `prediction_vector_parity.within_tolerance=true`
- `prediction_table.sample_fold_partition_target_alignment.gaps=[]`

## Decisions

- Treat the deterministic duplication-branch multisource fixture as fully strict
  because the produced artifacts now include score and prediction-vector numeric
  parity against the Python oracle.
- Keep `wasm_web_reuse`, `papers_export`, and `repository_forced_best_refit` as
  `not_applicable` for this lane, matching its declared objective.
- Keep source-aware `by_source` legacy stacking and broader external
  multisource/catalog corpora outside this scenario. They should be introduced
  as separate strict scenarios if they become release-gating surfaces.

## Risks

- This does not prove arbitrary future multisource corpus coverage.
- This does not add a Web/WASM consumer for multisource stacking; Web reuse is
  covered by other scenarios and remains not applicable here.
