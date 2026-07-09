# WAVE 10AD - repository consumer R methods gate

Date: 2026-07-09

## Scope

Fix the next strict E2E blocker from GitHub run `28986110696` after the
multimodal R/WASM dependency fix.

## Files changed

- `nirs4all-core/scripts/e2e/consume_repository_descriptor.py`
- `nirs4all-core/tests/test_consume_repository_descriptor.py`
- `nirs4all-core` submodule pin

## Decision

`e2e-dataset-provider-repository-roundtrip` now requires strict Python/R/WASM
runtime evidence. The repository consumer already executed R, but unlike the
multimodal runner it did not prepare a scenario R library with the
`nirs4all-methods` R package (`n4m`). The fix installs `n4m` from the pinned
`nirs4all-methods` checkout and the local `nirs4all` R binding into the scenario
library before executing the R surface.

This keeps numerical methods in `nirs4all-methods`; `nirs4all-core` only wires
the binding for the strict E2E runtime.

## Validation

- `nirs4all-core`: `python3.11 -m pytest tests/test_consume_repository_descriptor.py -q` -> 5 passed.
- `nirs4all-core`: `python3.11 -m py_compile scripts/e2e/consume_repository_descriptor.py` -> OK.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-provider-repo-fix run e2e-dataset-provider-repository-roundtrip --execute` -> passed.

## Risks

- The full ready-scenario GitHub run still needs to be relaunched after the
  ecosystem repin.
- The consumer now performs two R package installs during this strict scenario;
  this is intentional for hermetic runtime parity evidence and mirrors the
  multimodal runner.
