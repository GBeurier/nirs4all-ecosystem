# WAVE 10AH - core custom host methods lib gate

Date: 2026-07-09

## Scope

Fix the strict E2E blocker from GitHub run `28988756461` in
`e2e-core-ui-custom-app-host.core-python-open-rerun`.

## Files changed

- `nirs4all-core/scripts/e2e/run_custom_app_host.py`
- `nirs4all-core/tests/test_run_custom_app_host_env.py`
- `nirs4all-core` submodule pin

## Decision

The custom app host Python rerun imports `nirs4all-methods` from source. In CI,
that source binding could not locate the freshly built `libn4m` because the
scenario command exposed only `PYTHONPATH`.

The fix makes the E2E script detect the sibling
`nirs4all-methods/build/dev-release/cpp/src` directory and export
`PLS4ALL_LIB_PATH`, `N4M_LIB_PATH`, and `LD_LIBRARY_PATH` before executing the
portable pipeline.

## Validation

- `nirs4all-core`: `python3.11 -m pytest tests/test_run_custom_app_host_env.py -q` -> 2 passed.
- `nirs4all-core`: `python3.11 -m py_compile scripts/e2e/run_custom_app_host.py` -> OK.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-custom-host-libn4m-fix run e2e-core-ui-custom-app-host --execute` -> passed, including R parity, UI shim, and published custom-host smoke.

## Risks

- The full GitHub strict run still needs to be relaunched after the ecosystem
  repin.
