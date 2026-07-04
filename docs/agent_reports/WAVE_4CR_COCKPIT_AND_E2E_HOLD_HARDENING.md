# WAVE 4CR - Cockpit and E2E hold hardening

Date: 2026-07-04
Owner: Codex integration

## Parallel audits consumed

- Mencius the 4th audited `nirs4all-ui`, `nirs4all-org`, and `nirs4all-cockpit`
  read-only. Main gap found: cockpit `ECO_PAGES` omitted `nirs4all-ui` even
  though `PAGES_URLS` and targets already tracked the UI showcase.
- Einstein the 4th audited the 10 cross-language E2E scenarios read-only. Main
  gap found: several scenarios are intentionally smoke/descriptor evidence, and
  the runner still accepted composed status strings such as
  `passed_web_with_studio_hold` and `not_executed_*`.

## Integrated changes

- `nirs4all-cockpit@4809a46`
  - Added `nirs4all-ui` to the Pages visits roster so the shared UI showcase is
    part of cockpit's explicit ecosystem page list.
- `nirs4all-web@cfa0343`
  - Converted the performance smoke runtime ledger from ambiguous
    Studio/Web-hold evidence to Web-only evidence.
  - New artifact name: `web-runtime.json`.
  - Runtime status is now `passed` only after the Web dag-ml WASM run executes.
  - Studio is recorded as `included_in_gate=false`, without any passing `hold`
    status.
- `nirs4all-ecosystem`
  - E2E runner now rejects JSON artifact status/result/verdict values containing
    `hold` tokens or `not_executed` substrings.
  - Scenario `e2e-pipeline-generation-performance-compare` no longer declares
    `nirs4all-studio` or a Studio hold marker as evidence; it is a Web-only
    runtime gate plus Python reference/dag-ml parity.

## Tests run

- Cockpit:
  - `python3.11 -m pytest -q`
  - `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  - `python3.11 -m cockpit.cli collect --offline --out /tmp/n4a-cockpit-offline-current.json`
  - `python3.11 -m ruff check .`
- Ecosystem:
  - `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-performance-compare run e2e-pipeline-generation-performance-compare --execute`
- Web:
  - `node --check tests/performance-compare-smoke.mjs`
  - `npm run typecheck`
  - `npm run test`
  - `npm run build`

## Produced performance artifacts

- `/tmp/n4a-e2e-performance-compare/performance-compare/pipeline-family.json`:
  `status=passed`
- `/tmp/n4a-e2e-performance-compare/performance-compare/python-vs-dagml.json`:
  `status=passed`
- `/tmp/n4a-e2e-performance-compare/performance-compare/web-runtime.json`:
  `status=passed`, backend `dag-ml-wasm + libn4m`,
  `studio.included_in_gate=false`

## Residual risks

- This closes the false-green hold marker, but it does not add a Studio runtime
  parity entrypoint. Studio remains outside final production release per current
  operating constraint.
- Some E2E scenarios still prove smoke/descriptor contracts rather than full
  numeric parity. The runner now makes those boundaries harder to hide in
  produced evidence.
