# Wave 10G - cockpit refresh and E2E runtime dispatch

Date: 2026-07-09

## Scope

- Refresh the public cockpit after the latest Web, Methods, Lite-retirement, and Ecosystem coordination commits.
- Re-check the current cross-language E2E contract state without launching local full parity.
- Dispatch the heavier GitHub Actions runtime evidence run for fresh E2E artifacts.

## Files changed

- `.github/workflows/cross-language-e2e.yml`
- `docs/agent_reports/WAVE_10G_COCKPIT_E2E_RUNTIME_REFRESH.md`
- `tests/test_e2e_scenarios.py`

## Evidence collected

- `nirs4all-methods` ABI Surface on `f99c78a67524c237435a68f3061ef143db3d3910`: success on Linux, macOS, and Windows.
- `nirs4all-cockpit` collect workflow `29003797986`: success.
- `nirs4all-cockpit` Pages workflow `29004076629`: success.
- Cockpit public snapshot `24163dc00d138428bcbc1d947cfc02a6d53ce3c7` is served at `https://cockpit.nirs4all.org/data/current.json?v=24163dc`.
- Cockpit snapshot summary: `green=96`, `pending=4`, `stale=1`, `missing=0`, `broken=0`, `unknown=0`, `excluded=1`.
- Manual action counts: `pending=6`, with one blocker (`studio-windows-rc-smoke`) and five important CRAN actions.
- E2E contract validation on `0622b4a2548936f1bbed6cae9df13b2fb56972bc`: 11 scenarios, 70 verified artifacts, 0 contract failures.
- E2E coverage gate: `full_strict_ready=true`, `contract_parity_checks=0`, `strictness_gaps=0`.
- GitHub Actions runtime E2E dispatch `29004421709`: launched with `execute=true` and `allow_blocked=true`; running at the time this report was written.
- The E2E workflow artifact upload now includes `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json` for future runtime runs, so the fresh ledger can be recovered directly from the run artifacts.
- The workflow topology test now asserts both runtime artifact uploads include `.n4a-e2e-artifacts/**` and the generated ledger path.

## Tests and commands

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- `python3 -m pytest -q tests/test_e2e_scenarios.py`
- `cd ../nirs4all-cockpit && ./.venv/bin/pytest -q`
- `cd ../nirs4all-cockpit && ./.venv/bin/n4a-cockpit validate-targets ops/targets.yaml`
- `cd ../nirs4all-cockpit && ./.venv/bin/n4a-cockpit summarize data/current.json`
- `cd ../nirs4all-cockpit && python3 scripts/smoke_dashboard_dom.py --timeout 90`

## Remaining risks

- The committed runtime evidence ledger remains a contract/inventory proof until the dispatched `execute=true` run finishes and its fresh evidence is folded back into the repo.
- Runtime run `29004421709` was launched before the workflow artifact-path improvement in this report, so a follow-up runtime dispatch may still be needed if the generated ledger is not recoverable from that run.
- Current cockpit non-green states are manual/external: CRAN `nirs4all`, `nirs4allio`, `n4m`, `pls4all`, stale CRAN `nirs4alldatasets`, plus excluded `nirs4allformats`.
- `nirs4all` Python production and `nirs4all-studio` production are still intentionally held outside the non-prod release train.
