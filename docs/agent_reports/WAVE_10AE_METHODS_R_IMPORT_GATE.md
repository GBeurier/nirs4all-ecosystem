# WAVE 10AE - methods cross-binding R import gate

Date: 2026-07-09

## Scope

Fix the strict E2E blocker from GitHub run `28986741024` in
`e2e-formats-io-datasets-methods-language-bindings`.

## Files changed

- `nirs4all-methods/scripts/e2e/cross_binding_methods_parity.py`
- `nirs4all-methods/scripts/e2e/test_cross_binding_methods_parity.py`
- `nirs4all-methods` submodule pin

## Decision

The methods parity gate creates an isolated R library for the local `pls4all`
binding. It previously replaced `R_LIBS_USER`, hiding `jsonlite` installed by
the GitHub setup-r step. The fix prepends the gate library while preserving
existing R library paths.

This keeps the R binding hermetic for `pls4all` while allowing ordinary CRAN
imports to resolve from the prepared runner library.

## Validation

- `nirs4all-methods`: `python3.11 -m pytest scripts/e2e/test_cross_binding_methods_parity.py -q` -> 5 passed.
- `nirs4all-methods`: `python3.11 -m py_compile scripts/e2e/cross_binding_methods_parity.py` -> OK.
- `nirs4all-methods`: `python3.11 scripts/e2e/cross_binding_methods_parity.py --artifacts-dir /tmp/n4a-methods-cross-binding-fix --skip-build --timeout 240` -> `status=pass`.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-methods-fix run e2e-formats-io-datasets-methods-language-bindings --execute` -> passed.

## Risks

- The full ready-scenario GitHub run still needs to be relaunched after the
  ecosystem repin.
