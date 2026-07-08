# WAVE 10S - Cockpit Evidence Ledger Repin

Date: 2026-07-09

## Scope

Refresh the public cockpit snapshot after the E2E runtime evidence ledger landed
in `nirs4all-ecosystem`.

## Files Modified

- `nirs4all-cockpit/data/current.json`
- `nirs4all-cockpit/data/manual-actions.json`
- `nirs4all-ecosystem/nirs4all-cockpit`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_10S_COCKPIT_EVIDENCE_LEDGER_REPIN.md`

## Tests And Gates

- `nirs4all-cockpit`:
  - `python3.11 -m cockpit.cli collect --only nirs4all-ecosystem --out /tmp/n4a-cockpit-ecosystem-refresh.json`
  - `python3.11 -m cockpit.cli admin actions --json-out data/manual-actions.json`
  - `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  - `python3.11 -m pytest -q` -> `132 passed`
  - `python3.11 scripts/smoke_dashboard_dom.py` -> `dashboard smoke OK via google-chrome`
- `nirs4all-ecosystem`:
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  - `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
  - `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_gitmodules_topology.py tests/test_e2e_scenarios.py`
  - `python3.11 scripts/n4a_release_surface_matrix.py validate`

## Outcome

- Cockpit package status remains `green=96 stale=1 pending=4 missing=0 broken=0 unknown=0 excluded=1`.
- The cockpit `nirs4all-ecosystem` source block now records the evidence-ledger
  head `c0ba46d`.
- `data/manual-actions.json` now shares the refreshed snapshot timestamp.
- The ecosystem submodule now points at cockpit `3ab738c`.

## Remaining Manual Items

- Studio Windows RC smoke on native Windows.
- CRAN submissions/resubmissions for the remaining R packages.
