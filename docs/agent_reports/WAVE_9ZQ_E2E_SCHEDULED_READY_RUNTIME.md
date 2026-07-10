# WAVE 9ZQ - Scheduled ready runtime E2E

## Scope

- Closed the E2E freshness gap found after the `core 0.3.11` cascade.
- Changed the scheduled cross-language E2E workflow from a single cluster smoke to the full ready runtime suite.
- Kept push and pull-request behavior as contract validation/planning only; long runtime execution remains scheduled or manual `workflow_dispatch execute=true`.

## Files changed

- `.github/workflows/cross-language-e2e.yml`
- `tests/test_e2e_scenarios.py`

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 -m pytest -q tests/test_e2e_scenarios.py`
- YAML parse smoke for `.github/workflows/cross-language-e2e.yml`

Result: 11 scenarios validated; 136 E2E contract tests passed.

## Decisions

- Scheduled runs now install the same runtime dependencies as manual `execute=true` runs.
- Scheduled runs execute `run-ready --execute`, then verify `evidence --ready-only`, then check `evidence-ledger --check` with the 4-hour freshness window.
- The previous weekly single-scenario cluster smoke was removed to avoid a misleading green signal.

## Risks

- Weekly scheduled runtime cost is higher because all ready scenarios run, including methods/R/WASM setup.
- The currently running manual dispatch that was started before this patch still uses the previous workflow revision.
