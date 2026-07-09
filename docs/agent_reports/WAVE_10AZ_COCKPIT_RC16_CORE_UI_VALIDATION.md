# Wave 10AZ - Cockpit rc16 refresh and core/UI/Web validation

Date: 2026-07-09

## Scope

- Audited the current `nirs4all-ui`, `nirs4all-core`, `nirs4all-web`,
  `nirs4all-ecosystem`, and `nirs4all-cockpit` state after the MATLAB/Octave
  E2E gate.
- Re-pinned the cockpit `nirs4all-core` coordination tag to
  `n4a-v1-rc16-2026.07-refactor`.
- Refreshed the public cockpit snapshot through the GitHub `collect` workflow.
- Aligned dashboard manual-action counters with the unresolved actions actually
  displayed at the bottom of the dashboard.

## Files Modified

In `nirs4all-cockpit`:

- `ops/targets.yaml`
- `tests/test_targets_topology.py`
- `cockpit/manual_actions.py`
- `data/current.json`
- `data/manual-actions.json`

In `nirs4all-ecosystem`:

- `docs/agent_reports/WAVE_10AZ_COCKPIT_RC16_CORE_UI_VALIDATION.md`

## Tests Run

Cockpit:

- `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`
- `.venv/bin/python -m pytest -q`
- `.venv/bin/python -m ruff check .`
- `python3 scripts/smoke_dashboard_dom.py`
- GitHub Actions: `version-guard`, `ci`, `collect`, and `pages` all succeeded.

Core/UI/Web:

- `cd nirs4all-ui && npm run brand:check && npm run prepublishOnly && npm run pack:smoke && npm run smoke:react-consumers && npm run site:build`
- `cd nirs4all-web/studio-lite && npm run typecheck && npm run test:client-only && npm run smoke:shared-ui-contract && npm run smoke:custom-app-host && npm run check:core-shim && npm run check:ui-shim`
- `cd nirs4all-core/bindings/wasm && npm test`
- `cd nirs4all-core && PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests`

## Results

- Cockpit snapshot `generated_at`: `2026-07-09T16:59:05.731476+00:00`.
- Cockpit summary: `95 green`, `2 stale`, `4 pending`, `0 missing`,
  `0 broken`, `0 unknown`, `1 excluded`.
- Manual actions: `23 total`, `7 pending`, `16 resolved`, with the sole blocker
  still `studio-windows-rc-smoke`.
- `nirs4all-core` now appears in cockpit from commit `727fad56`, manifest
  `0.3.8`, latest tag `v0.3.8`, with expected `stale` rollup only because
  R-universe remains `0.3.7` and CRAN is pending.
- `nirs4all-ecosystem` is reflected at commit `9ca5536`.
- `nirs4all-ui`, `nirs4all-web`, `nirs4all-providers`, and `nirs4all-org`
  remain green.

## Decisions

- Count any manual action whose auto-check is not resolved as pending in the
  public dashboard, even when the human step is declared `done`. This keeps the
  bottom manual-action section and its counters consistent.
- Keep `nirs4all-ui` unchanged: the integrated package already exposes shared
  components, default styles, brand assets/generators, motion assets, and the
  GitHub Pages showcase; the validation run left the repo clean.
- Do not rerun full Python parity in this wave. This pass touched cockpit
  topology/dashboard accounting and validation surfaces, not numerical behavior.

## Risks

- External/manual items remain: Studio Windows RC smoke, CRAN submissions, and
  public propagation of the R-universe core rebuild.
- `nirs4all-core` MATLAB/Octave proof remains public release/workflow evidence,
  not a fresh local Octave build on this Linux session.
