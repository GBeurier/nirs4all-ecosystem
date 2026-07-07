# Wave 9B - Custom Host Python Open/Rerun

## Scope

Close the `e2e-core-ui-custom-app-host` `python_open_pipeline` and `python_rerun_pipeline` contract debt without touching the dirty `nirs4all-ui` checkout.

## Files Modified

- `nirs4all-core/scripts/e2e/run_custom_app_host.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`

## Decisions

- Added a standalone `nirs4all-core` Python open/rerun ledger for the custom host scenario.
- Declared `nirs4all-methods` in the scenario repos because the strict Python rerun uses the local methods Python binding source.
- Promoted `python_open_pipeline` and `python_rerun_pipeline` from `contract` to `strict`.
- Kept `wasm_web_reuse` evidence in the existing Web/Vitest custom host smoke; no shared UI component changes were made.

## Tests

- `cd nirs4all-core && python3.11 -m ruff check scripts/e2e/run_custom_app_host.py`
- `cd nirs4all-core && PYTHONPATH=/home/delete/nirs4all/nirs4all-methods/bindings/python/src:bindings/python/src PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/e2e/run_custom_app_host.py --artifacts-dir /tmp/n4a-custom-host-core`
- `cd nirs4all-core && python3.11 -m py_compile scripts/e2e/run_custom_app_host.py`
- `cd nirs4all-core && PYTHONPATH=/home/delete/nirs4all/nirs4all-methods/bindings/python/src:bindings/python/src PYTHONDONTWRITEBYTECODE=1 python3.11 -m unittest bindings/python/tests/test_execution_parity.py -v`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `cd nirs4all-ecosystem && NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-custom-host-evidence run e2e-core-ui-custom-app-host --execute`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-custom-host-evidence evidence --scenario e2e-core-ui-custom-app-host --json`
- `cd nirs4all-ecosystem && python3.11 -m pytest tests/test_e2e_scenarios.py -q`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q`

## Risks

- The scenario still has two explicit strictness gaps: it is a Vitest/React contract rather than a packaged third-party app, and its R evidence remains structural rather than a full R numeric rerun.
- Local Web execution used a clean `nirs4all-ui` export from `origin/main` to avoid overwriting unrelated dirty UI work.
