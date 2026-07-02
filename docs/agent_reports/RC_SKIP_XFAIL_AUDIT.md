# RC Skip / Xfail Audit

Date: 2026-07-02  
Agent: Codex/Laplace, read-only; coordinator refresh after Python `3d568ab`

## Scope

Read-only audit of skip/xfail debt visible in the current RC gates:

- `RC-v1-studio`
- `RC-v1-web`
- `RC-v1-nirs4all-python`
- prior targeted benchmarks result

The initial audit was read-only. The coordinator later refreshed this report
after the full Python parity rerun on the selected RC Python head `3d568ab`
with RC `dag-ml` `7f86a9b` and RC `dag-ml-data` `e681685` on `PYTHONPATH`.

## Findings

- Studio operator fixture debt has been burned down after the original audit:
  - `tests/test_operator_definitions.py` now passes with `445 passed` and 0 skips after replacing skipped fixture families with deterministic local inputs;
  - the combined Studio runtime/operator/quick-run RC stack gate passes with `464 passed`.
- Studio full-backend result is refreshed after the current batch: `2324 passed, 6 skipped` in `1465.99s`. Remaining skips are Windows-only/env/example-access categories, not operator-definition fixture debt.
- Studio frontend `1 skipped` is Windows-only path behavior in `electron/portable-paths.test.ts`.
- Benchmarks `1 skipped` is optional CI/runtime coverage and should be rerun in the service-extra environment if zero skips is required.
- Python parity `30 skipped / 11 xfailed` is stale, and the intermediate
  `853 passed, 14 skipped, 6 xfailed` result is now superseded.
- Full Python parity on the selected RC heads now passes without parity skip or
  xfail debt:
  - command:
    `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python:. PATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug:$PATH /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity/ -m parity -p no:cacheprovider -ra`
  - result:
    `659 passed, 227 deselected, 1530 warnings in 2037.46s (0:33:57)`.
  - `227 deselected` are tests outside the `parity` marker, not skipped tests.
  - No `skipped`, no `xfailed`, and no `failed` tests were reported in this gate.
- The fallback coverage meter was checked before the full run:
  - `coverage_meter OK (fallback=0, target=0)`;
  - summary:
    `registered=95, non_runnable=0, runnable=95, fallback=0, native=95, xfail_strict=0, skip=0, num_predictions_divergence=2, run_only_nondeterministic=1, expected_fallback_target=0`.

## Required Follow-Up

- Track remaining Studio skips as optional/environment gates, not operator debt.
- Do not cite `99d57b7e` or `42448821` as the current parity proof head; the
  current proof was run on RC Python `3d568ab`.
- Keep methods binding proof separate: JS/WASM/R/Octave/MATLAB methods gates
  still depend on their release environments even though Python parity is green.
- Preserve the distinction between `deselected` and `skipped` in release notes.

## Risk

Python-reference parity no longer has unexplained skip/xfail debt in the
selected `-m parity` gate. Remaining skip risk is outside this gate: Studio
environment skips and methods/language binding environments still need their
own final release proofs.
