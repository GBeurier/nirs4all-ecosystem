# Wave 5Y - E2E coverage meter and semantic guards

Date: 2026-07-04

## Scope

- `nirs4all-ecosystem` cross-language E2E contract/orchestrator only.
- No full parity suite was run; this wave hardens the contract before the next large execution batch.

## Changes

- Added `scripts/n4a_e2e_scenarios.py coverage` to report:
  - scenario readiness,
  - required language/tag coverage,
  - evidence levels,
  - per-scenario step/artifact counts,
  - V1 refactor strict/contract/gap phase counts.
- Moved minimum complexity checks into the validator:
  - exactly 10 scenarios,
  - at least 2 executable steps per scenario,
  - at least 2 declared artifacts per scenario,
  - at least 1 strict V1 refactor phase per scenario.
- Added semantic guards:
  - `web` language and `web_results` tag must be declared together,
  - Web coverage requires a real `nirs4all-web` step and non-gap `wasm_web_reuse`,
  - `papers` tag requires `nirs4all-papers` and non-gap `papers_export`,
  - `repository` tag requires `nirs4all-repository` and a produced repository artifact,
  - strict parity checks may not be smoke-only or schema/array-coverage-only.
- Corrected `e2e-multimodal-python-r-wasm-roundtrip` so it no longer claims `web` until a real Web step exists.
- Split multisource replay evidence into strict score parity plus contract-level prediction-table schema/array coverage.

## Current coverage meter

- Scenarios: 10 / 10.
- Ready in the current checkout: 10.
- Evidence levels: 10 hybrid, 0 strict.
- Required languages covered:
  - Python: 10 scenarios.
  - R: 3 scenarios.
  - JavaScript/WASM: 7 scenarios.
  - Web: 4 scenarios.
- V1 phase counts:
  - `python_open_pipeline`: 2 strict, 2 contract, 6 gap.
  - `python_rerun_pipeline`: 4 strict, 3 contract, 3 gap.
  - `python_parity`: 10 strict, 0 contract, 0 gap.
  - `papers_export`: 1 strict, 0 contract, 9 gap.
  - `repository_forced_best_refit`: 0 strict, 2 contract, 8 gap.
  - `wasm_web_reuse`: 3 strict, 4 contract, 3 gap.

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate` passed.
- `python3 scripts/n4a_e2e_scenarios.py coverage` passed.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` passed.
- `python3 -m pytest -q tests/test_e2e_scenarios.py` passed, 46 tests.
- `python3 -m pytest -q` passed, 70 tests.

## Remaining debt

- The E2E board is orchestrated and executable, but not full strict: papers and repository forced-refit remain the dominant gaps.
- Multimodal still proves Python/R/WASM dense-fused proxy parity, not Web/Studio multimodal rendering.
- Multisource still lacks full vector-level native prediction parity; only score parity is strict.
