# WAVE 10AF - methods libn4m fixture gate

Date: 2026-07-09

## Scope

Fix the strict E2E blocker from GitHub run `28987345182` in
`e2e-formats-io-datasets-methods-language-bindings`.

## Files changed

- `nirs4all-methods/scripts/e2e/cross_binding_methods_parity.py`
- `nirs4all-methods/scripts/e2e/test_cross_binding_methods_parity.py`
- `nirs4all-methods` submodule pin

## Decision

The methods cross-binding gate already builds and runs subprocess parity
against the local `dev-release` `libn4m`. The in-process Python fixture used
for the WASM orchestrator import did not receive `PLS4ALL_LIB_PATH` /
`N4M_LIB_PATH`, so CI could import the source binding before it knew where the
fresh `libn4m` lived.

The fix makes the gate export the `dev-release` library directory explicitly
for subprocesses and for the current Python process before importing
`pls4all`.

## Validation

- `nirs4all-methods`: `python3.11 -m pytest scripts/e2e/test_cross_binding_methods_parity.py -q` -> 6 passed.
- `nirs4all-methods`: `python3.11 -m py_compile scripts/e2e/cross_binding_methods_parity.py` -> OK.
- `nirs4all-methods`: `python3.11 scripts/e2e/cross_binding_methods_parity.py --artifacts-dir /tmp/n4a-methods-libn4m-env-fix --skip-build --timeout 240` -> `status=pass`.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-methods-libn4m-fix run e2e-formats-io-datasets-methods-language-bindings --execute` -> passed.

## Risks

- The full ready-scenario GitHub run still needs to be relaunched after the
  ecosystem repin.
