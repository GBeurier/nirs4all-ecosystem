# WAVE 10AI - quality local UI install gate

Date: 2026-07-09

## Scope

Fix the next strict E2E blocker exposed locally in
`e2e-core-ui-custom-app-host.quality-custom-host-smoke`.

## Files changed

- `nirs4all-ecosystem/scripts/e2e/run_quality_custom_host_smoke.py`
- `nirs4all-ecosystem/tests/test_quality_custom_host_smoke.py`

## Decision

`nirs4all-quality/app` consumes `nirs4all-ui` through a local
`file:../../nirs4all-ui` dependency. In a clean checkout, `npm ci` in quality
can trigger the local UI package `prepare` script before `nirs4all-ui` has its
own dev dependencies installed, so `tsc` is unavailable.

The runner now installs the local `nirs4all-ui` package dependencies first when
the workspace contains a UI checkout but no local `node_modules/.bin/tsc`.
This does not modify the quality-used UI components.

## Validation

- `nirs4all-ecosystem`: `python3.11 -m pytest tests/test_quality_custom_host_smoke.py -q` -> 2 passed.
- `nirs4all-ecosystem`: `python3.11 -m py_compile scripts/e2e/run_quality_custom_host_smoke.py` -> OK.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --workspace-root /home/delete/nirs4all/nirs4all-ecosystem --artifacts-dir /tmp/n4a-e2e-custom-host-submodule-quality-fix run e2e-core-ui-custom-app-host --execute` -> passed.

## Risks

- The full GitHub strict run still needs to be relaunched after committing this
  ecosystem runner fix and the `nirs4all-core` submodule repin.
