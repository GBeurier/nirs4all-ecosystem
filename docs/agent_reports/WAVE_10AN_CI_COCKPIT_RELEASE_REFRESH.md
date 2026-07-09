# Wave 10AN - CI, Cockpit, Release Refresh

Date: 2026-07-09
Owner: Codex
Mode: integration/review with parallel Claude audit attempts

## Files / repos modified

- `nirs4all-ui`: added Node type declarations for the Pages Vite config.
- `nirs4all-studio`: disabled the sibling `nirs4all-ui` prepare hook in CI and Playwright workflows.
- `nirs4all-org`: refreshed `nirs4all-ui`, `nirs4all-methods`, and ecosystem-map package labels.
- `nirs4all-ecosystem`: repinned `nirs4all-cockpit`, `nirs4all-core`, `nirs4all-org`, `nirs4all-studio`, `nirs4all-ui`, and `nirs4all-web`.
- `nirs4all-cockpit`: marked the `nirs4all-quality` GitHub Release target as tracked and refreshed `data/current.json`.

## Tests / checks run

- `nirs4all-ui`: `npm run ci` - 24 test files / 114 tests passed, build and React 18/19 packed-consumer smoke passed.
- `nirs4all-studio`: GitHub Actions `version-guard`, `CI`, `Playwright E2E Tests`, and manual `Release` dispatch all passed on `4c61379`.
- `nirs4all-studio`: downloaded `installer-windows-x64` from run `28994057636`; installer and portable `.sha256` checks passed locally.
- `nirs4all-org`: version-guard and Pages passed on `f391269`.
- `nirs4all-ecosystem`: `pytest -q` - 170 passed; cross-language E2E workflow passed on `b48eb6b`.
- `nirs4all-ecosystem`: `n4a_e2e_scenarios.py validate` and coverage report - 11/11 ready, `full_strict_ready=true`, zero strictness gaps.
- `nirs4all-cockpit`: `n4a-cockpit validate-targets`, `pytest -q` - 132 passed, `smoke_dashboard_dom.py` passed, collect and Pages passed.

## Decisions

- Kept `nirs4all` Python and production `nirs4all-studio` release held.
- Produced a Studio Windows RC artifact through Actions rather than switching production.
- Did not chase the ecosystem/cockpit gitlink circularity indefinitely; cockpit snapshot remains the authoritative status surface.
- Treated the GitGuardian cluster alert as requiring token rotation/confirmation even though current HEAD and redacted local history scan found no live token-shaped match.

## Remaining risks / blockers

- Manual blocker: smoke-test the Windows Studio RC installer before any production switch.
- Manual CRAN actions remain: `n4m`, `pls4all`, `nirs4allio`, `nirs4alldatasets`, and R aggregate `nirs4all`.
- Claude parallel audits for UI/Web/Studio, security, and E2E stopped on quota reset limits; only the cockpit/release audit returned an actionable report.
- Full Python-reference parity and long runtime parity gates remain intentionally deferred until the next large batch.
