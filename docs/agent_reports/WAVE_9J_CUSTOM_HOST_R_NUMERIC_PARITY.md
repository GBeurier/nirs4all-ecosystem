# WAVE 9J - Custom Host R Numeric Parity

## Scope

Closed the `e2e-core-ui-custom-app-host` R evidence gap without touching the
dirty `nirs4all-ui` checkout. The custom host lane now requires a numeric R
parity ledger against the portable Python oracle instead of a structural R
surface artifact.

## Files Modified

- `nirs4all-core/bindings/r/tests/parity.R`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

## Decisions

- No legacy alias was added or preserved.
- The R parity script keeps its default behavior unchanged. It writes
  `n4a.e2e.r_parity_ledger.v1` only when `NIRS4ALL_CORE_R_PARITY_LEDGER` is set.
- The E2E step was renamed from `core-r-surface-probe` to `core-r-parity`.
- The remaining custom-host strictness gap is only that the host is still a
  Vitest/React contract, not a packaged downstream application.

## Tests

- `cd nirs4all-core && PATH=/home/delete/miniconda3/envs/pls4all_r/bin:$PATH NIRS4ALL_CORE_R_PARITY_LEDGER=/tmp/n4a-custom-host-r-parity.json NIRS4ALL_CORE_R_PARITY_SCENARIO_ID=e2e-core-ui-custom-app-host make test-r-parity PYTHON=python3.11`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-coverage-after-r.json --markdown-out /tmp/n4a-e2e-coverage-after-r.md`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `cd nirs4all-ecosystem && NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-custom-host-r-evidence run e2e-core-ui-custom-app-host --execute`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-custom-host-r-evidence evidence --scenario e2e-core-ui-custom-app-host --json`
- `cd nirs4all-ecosystem && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`

## Result

- `custom-host-r-parity.json` verified with 4 cases and 104 prediction rows.
- Maximum R-vs-Python prediction delta: `2.79e-14` against tolerance `1e-5`.
- E2E coverage debt changed from `strictness_gaps=12` to `strictness_gaps=11`.
- Strict parity checks changed from 19 to 20.

## Risks

- The full ecosystem parity suite was not rerun; this was a targeted R/custom
  host gate.
- The live `nirs4all-ui` checkout is dirty from another agent. The custom host
  execution used `/tmp/n4a-clean-ui-origin` via `NIRS4ALL_UI_SHIM_ROOT` to avoid
  modifying or depending on that concurrent work.
