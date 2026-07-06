# WAVE 6C - Full parity skip/xfail reduction

Date: 2026-07-06
Agent: Codex main, lane C/L17 parity reduction
Scope: `nirs4all` Python reference parity only. No production release/tag.

## Starting point

Last full parity batch before this wave:

```text
745 passed, 30 skipped, 11 xfailed, 1754 warnings in 1942.35s (0:32:22)
```

This was not treated as a production gate because skips/xfails remained.

## Changes integrated locally

Files modified in `nirs4all`:

- `nirs4all/pipeline/config/_generator/strategies/or_strategy.py`
- `nirs4all/pipeline/config/pipeline_config.py`
- `nirs4all/controllers/data/branch.py`
- `nirs4all/controllers/data/branch_utils.py`
- `nirs4all/controllers/data/merge.py`
- `tests/integration/parity/cases_generators_conformance.py`
- `tests/integration/parity/cases_refit_predict.py`
- `tests/integration/parity/cases_branches_merges.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `tests/integration/parity/test_generators_conformance_extra.py`
- `tests/unit/controllers/data/test_branch_separation.py`
- `tests/unit/controllers/data/test_branch_value_mapping.py`
- `docs/compatibility.json`

Main fixes:

- `_or_` now honors local `_seed_` for `pick`/`arrange` and `count`, and applies `_weights_` to sampled count limits when the weights match expanded variants.
- `refit_params_use_all_partitions` is no longer skipped; targeted parity now passes.
- `PipelineConfigs._preprocess_steps` tolerates non-string keys, needed by boolean `by_tag` branch steps.
- `by_filter` no longer imports the missing `nirs4all.pipeline.steps.deserializer`; it uses `deserialize_component` and validates that the result is a `SampleFilter`.
- Separation branches now support branch-specific `steps` dicts, including `True`/`False` keys from existing examples.
- Separation branch selectors now carry the routed `sample` IDs, and disjoint merge restores the initial full feature snapshot before writing the reassembled merged matrix.
- `parse_value_condition` supports `numpy.bool_` and returns a Python `bool`.
- `docs/compatibility.json` was updated: case-level strict xfails drop from 11 to 9; coverage skips drop from 6 to 3; expected dag-ml fallbacks rise from 9 to 11 because by-tag/by-filter separation branches still use unsupported native `branch` serialization.

## Tests run

```text
.venv/bin/python -m ruff check ...
All checks passed!
```

```text
.venv/bin/python -m pytest -q <targeted parity/unit batch>
116 passed, 26 warnings in 38.73s
```

The targeted batch covered:

- branch value mapping and separation helper unit tests
- compatibility ledger validation
- generator `_or_` conformance extras
- compile/smoke/native-boundary/dual-engine conformance for:
  - `generator_or_count_seed`
  - `generator_or_weights_count_seed`
  - `refit_params_use_all_partitions`
  - `branch_separation_by_tag`
  - `branch_separation_by_filter`

## Remaining risks

- Full parity was not rerun in this wave, per instruction to reserve it for larger batches.
- `branch_separation_by_tag` and `branch_separation_by_filter` pass legacy and dual-engine conformance, but dag-ml still falls back because the native bridge does not serialize separation branch DAGs. This is recorded in `EXPECTED_FALLBACK`, not xfailed.
- Remaining coverage skips are fixture gaps:
  - `aggregation_classification_vote`
  - `branch_separation_by_metadata_auto`
  - `exclude_multi_any_y_and_x`
- Remaining strict xfails are semantic/nondeterministic divergences still requiring separate correction or explicit product decision.

## Decisions

- Do not mark branch separation native parity as solved. It is executable in legacy and guarded by dual-engine fallback, but native DAG support remains lane L5 work.
- Do not run full parity again until the next larger parity batch.
- Keep `nirs4all` Python unreleased for now, matching the active release constraint.
