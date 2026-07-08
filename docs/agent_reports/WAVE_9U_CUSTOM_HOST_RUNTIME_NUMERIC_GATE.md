# WAVE 9U - Custom Host Runtime Numeric Gate

Date: 2026-07-08

## Scope

Closed the strict-numeric proof gap for the custom-host runtime contract artifact without touching `nirs4all-ui` components or syncing against concurrent `nirs4all-ui` work.

## Files Modified

- `nirs4all-web/studio-lite/src/app/custom-app-host.contract.test.ts`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `nirs4all-web` submodule pointer

## Decisions

- Kept exact contract assertions:
  - `serialized_model_predict_surfaces == ["javascript_wasm"]`
  - `wasm_predict_entrypoint == "predictPortablePipeline"`
- Added numeric zero-tolerance evidence to `custom-host-runtime-contracts.json`:
  - `serialized_predict_surface_count_absolute_delta <= serialized_predict_surface_count_tolerance`
  - `wasm_predict_entrypoint_absolute_delta <= wasm_predict_entrypoint_tolerance`
- Removed `e2e-core-ui-custom-app-host` from `STRICT_NUMERIC_PROOF_EXEMPTIONS`.
- Did not run or sync `nirs4all-ui` because that repo contains concurrent external work.

## Tests Run

- `cd nirs4all-web/studio-lite && export PATH="$HOME/.nvm/versions/node/v22.21.1/bin:$HOME/.cargo/bin:$PATH" && npm run test -- --run src/app/custom-app-host.contract.test.ts`
  - `1 passed`
- `cd nirs4all-ecosystem && python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - `128 passed`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
  - OK
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage --json`
  - `strict_non_numeric_check_count: 1`

## Runtime Evidence

`/tmp/n4a-custom-host-next/custom-app-host/custom-host-runtime-contracts.json` was produced by the real custom-host Vitest step and validated directly with the ecosystem artifact contract. It reports both numeric deltas as `0`.

## Risks

- Full `e2e-core-ui-custom-app-host` still stops at `check:ui-shim` while `nirs4all-ui` has concurrent dirty work from another agent. This was intentionally not overwritten.
- Full parity was not launched in this batch.
