# Wave 3AI - nirs4all seeded OR count sampling

Date: 2026-07-01
Lane: C/B - Python reference parity / generator runtime
Repo: `_worktrees/INT-nirs4all`
Commit: `174a9bd3 fix(generator): stabilize seeded or count sampling`

## Scope

Promote the two `_or_` count sampling parity cases from `unknown_semantics` skips to live dag-ml/Python parity assertions.

## Files Modified

- `nirs4all/pipeline/config/_generator/strategies/or_strategy.py`
- `nirs4all/pipeline/config/_generator/validators/schema.py`
- `nirs4all/pipeline/dagml/detect.py`
- `tests/unit/pipeline/config/test_generator_strategies.py`
- `tests/unit/pipeline/config/test_generator_validators.py`
- `tests/integration/parity/cases_generators_conformance.py`
- `tests/integration/parity/test_conformance_dual_engine.py`
- `tests/integration/parity/test_dagml_operator_generation_phase7.py`
- `docs/compatibility.json`
- `docs/compatibility.md`

## Decisions

- `OrStrategy` now honors node-local `_seed_` for `_or_` `count` sampling.
- Simple `_or_` + `count` + `_weights_` now uses weighted deterministic sampling.
- `_weights_` is rejected with `pick`, `arrange`, `then_pick`, or `then_arrange`; those modes produce combination/permutation survivors, so original choice weights would otherwise be applied to the wrong population.
- `generator_or_count_seed` and `generator_or_weights_count_seed` are now live parity cases and are included in `SAME_WINNER_CASES`.
- Compatibility meter updated from `non_runnable=8` / `skip=6` to `non_runnable=6` / `skip=4`; `fallback` remains `0`.

## Review

- Initial reviewer: `Halley the 2nd` - NO-GO on ambiguous `_weights_` with `pick/arrange` and stale comments.
- Fix applied: fail-closed validation/runtime error for weighted selection modes, schema validator coverage, stale comments corrected.
- Re-review: `Halley the 2nd` - GO.

## Tests

- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/unit/pipeline/config/test_generator_strategies.py tests/unit/pipeline/config/test_generator_validators.py -q -p no:cacheprovider` -> 70 passed.
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/integration/parity/test_parity_compiles.py -q -k "generator_or_count_seed or generator_or_weights_count_seed or keyword_coverage" -p no:cacheprovider` -> 3 passed.
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/integration/parity/test_compatibility_ledger.py tests/integration/parity/test_native_fallback_boundary.py -q -p no:cacheprovider` -> 13 passed, 1 skipped.
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m tests.integration.parity.coverage_meter --check` -> OK, `fallback=0`.
- `DAG_ML_CLI=/home/delete/nirs4all/dag-ml/target/release/dag-ml-cli PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:/home/delete/nirs4all/dag-ml-data/crates/dag-ml-data-py/python PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/integration/parity/test_conformance_dual_engine.py -q -k "generator_or_count_seed or generator_or_weights_count_seed" -p no:cacheprovider` -> 4 passed.
- `DAG_ML_CLI=/home/delete/nirs4all/dag-ml/target/release/dag-ml-cli PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:/home/delete/nirs4all/dag-ml-data/crates/dag-ml-data-py/python PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/integration/parity/test_dagml_operator_generation_phase7.py -q -k "sampling or count or weights" -p no:cacheprovider` -> 4 passed.
- `python3.11 -m ruff check ...` on touched Python files -> passed.
- `python3.11 -m mypy --follow-imports=skip nirs4all/pipeline/config/_generator/strategies/or_strategy.py nirs4all/pipeline/config/_generator/validators/schema.py` -> passed.
- `python3.11 -m py_compile ...` on touched Python files -> passed.
- `git diff --check` -> passed.

Full parity was not rerun after this focused promotion; user guidance is to reserve full parity for larger batches.

## Risks

- Weighted selection is intentionally limited to simple `_or_` sampling. Any future weighted combination semantics must define survivor-level weights explicitly before enabling `_weights_` with `pick/arrange`.
- The dual-engine targeted run requires local `dag-ml` and `dag-ml-data` Python bindings on `PYTHONPATH`; the system Python alone does not currently import those packages.
