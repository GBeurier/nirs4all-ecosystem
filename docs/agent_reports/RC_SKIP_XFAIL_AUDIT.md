# RC Skip / Xfail Audit

Date: 2026-07-02
Last refresh: 2026-07-03 after Python `6a2c720` full split parity
Agent: Codex/Laplace, read-only; coordinator refresh after Python `6a2c720`

## Scope

Read-only audit of skip/xfail debt visible in the current RC gates:

- `RC-v1-studio`
- `RC-v1-web`
- `RC-v1-nirs4all-python`
- prior targeted benchmarks result

The initial audit was read-only. The coordinator later refreshed this report
after full Python parity reruns on selected RC Python heads, most recently
`6a2c720` with the selected RC `dag-ml` and `dag-ml-data` paths on `PYTHONPATH`
and `NIRS4ALL_REQUIRE_N4M=1`.

## Findings

- Studio operator fixture debt has been burned down after the original audit:
  - `tests/test_operator_definitions.py` now passes with `445 passed` and 0 skips after replacing skipped fixture families with deterministic local inputs;
  - the combined Studio runtime/operator/quick-run RC stack gate passes with `464 passed`.
- Studio full-backend result is refreshed after Wave 4W: `2335 passed, 0 skipped`, `301 warnings`. Locally coverable backend skips were removed; Windows host behavior remains a real external host gate, not a skipped Linux backend test.
- Studio frontend targeted portable-paths gate reports `4 passed`; Wave 4Y full
  frontend Vitest reports `517` test files and `3709` tests passed.
- Benchmarks `1 skipped` is optional CI/runtime coverage and should be rerun in the service-extra environment if zero skips is required.
- Python parity `30 skipped / 11 xfailed` is stale, and the intermediate
  `853 passed, 14 skipped, 6 xfailed` result is now superseded.
- Full Python parity on current selected RC head `6a2c720` now passes without
  parity skip or xfail debt:
  - non-slow command:
    `PYTHONDONTWRITEBYTECODE=1 NIRS4ALL_REQUIRE_N4M=1 PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python:. PATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug:$PATH /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -m "not slow" -q --tb=short -p no:cacheprovider`
  - non-slow result:
    `444 passed, 443 deselected, 510 warnings in 550.90s`.
  - slow command:
    `PYTHONDONTWRITEBYTECODE=1 NIRS4ALL_REQUIRE_N4M=1 PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python:. PATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug:$PATH /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -m "slow" -q --tb=short -p no:cacheprovider`
  - slow result:
    `443 passed, 444 deselected, 1309 warnings in 1843.08s`.
  - Combined interpretation: `887 passed`, `0 skipped`, `0 xfailed`, `0 failed`.
  - `deselected` are the opposite split, not skipped tests.
- The fallback coverage meter was checked before the full run:
  - `coverage_meter OK (fallback=0, target=0)`;
  - summary:
    `registered=95, non_runnable=0, runnable=95, fallback=0, native=95, xfail_strict=0, skip=0, num_predictions_divergence=2, run_only_nondeterministic=1, expected_fallback_target=0`.

## Required Follow-Up

- Track remaining Studio skips as optional/environment gates, not operator debt.
- Do not cite `99d57b7e`, `42448821`, or `3d568ab` as the current parity proof
  head; the current proof was run on RC Python `6a2c720`.
- Keep methods binding proof separate: JS/WASM/R/Octave/MATLAB methods gates
  still depend on their release environments even though Python parity is green.
- Preserve the distinction between `deselected` and `skipped` in release notes.

## Risk

Python-reference parity no longer has unexplained skip/xfail debt in the
selected split parity gates. Remaining skip risk is outside this gate:
R and Octave/MATLAB language binding environments still need their own final
release proofs, and full non-Python DatasetPackage materialization remains an
environment gate.
