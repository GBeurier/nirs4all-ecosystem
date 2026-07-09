# WAVE 10AS - UI publish guard, cockpit roadmap, and E2E refresh

Date: 2026-07-09

## Scope

- Harden `nirs4all-ui` npm publishing so prerelease tags cannot start the
  publish job.
- Align `nirs4all-cockpit` roadmap with the implemented local-only admin
  snapshot.
- Re-audit cross-language E2E evidence without launching the long full parity
  suite.
- Refresh the public cockpit after the UI and cockpit heads changed.

## Agents and review

- Codex explorer `019f46bc-b161-7f02-aa8e-70db39b16891`: read-only E2E audit.
  Result: 11 strict scenarios, 70 artifacts verified with
  `--max-age-seconds 14400`, 0 runtime evidence failure.
- Codex explorer `019f46bd-40b8-7b20-9f2b-17cb3f956567`: read-only
  core/ui/providers/cockpit debt audit. Result: core/providers docs already
  resolved, UI prerelease publish guard was the right patch, cockpit ROADMAP was
  stale.
- Claude Code session `cb8d0480-a6a1-44e7-b037-5f1165210262`: blocked by
  Claude weekly limit before doing work; no code or audit output produced.

## Files changed

- `nirs4all-ui/.github/workflows/release-npm.yml`
  - Commit: `3b87ccd ci(npm): skip publish job on prerelease tags`
  - Decision: keep build/tag validation on prerelease tags, but skip the
    publish job unless the tag is non-prerelease or manual dispatch explicitly
    sets `dry_run=false`.
- `nirs4all-cockpit/ROADMAP.md`
  - Commit: `0e63259 docs(roadmap): align admin snapshot status`
  - Decision: `admin collect`, Sentry/PR/security collectors, and
    `data/admin/snapshot.admin.json` are v1 local-only/admin features, not
    phase-2 TODOs. FastAPI/admin UI remains phase 2.
- `nirs4all-cockpit/data/current.json`,
  `nirs4all-cockpit/data/manual-actions.json`
  - Auto-collect commit:
    `8768371 chore(collect): refresh data/current.json`

## Tests and gates

- `nirs4all-ui`: `npm run ci` with Linux nvm Node 24.16.0
  - 115 Vitest tests passed.
  - Typecheck, build, dry-run pack, React 18/19 packed-consumer smoke passed.
  - GitHub checks for `3b87ccd`: CI success, version-guard success,
    GitHub Pages success.
- `nirs4all-cockpit`
  - `.venv/bin/pytest -q`: 133 passed.
  - `.venv/bin/pytest -q tests/test_targets_topology.py tests/test_admin.py`:
    31 passed.
  - `.venv/bin/ruff check .`: passed.
  - GitHub checks for `0e63259`: CI success, version-guard success.
  - Collect workflow `29016912698`: success.
  - Pages workflow for `8768371`: success.
  - Public `current.json` and `manual-actions.json` SHA256 hashes match local.
  - `python3 scripts/smoke_dashboard_dom.py --timeout 90`: passed.
- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py validate`: 11 scenarios OK.
  - `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`:
    11/11 ready, 0 strictness gap, 0 contract parity check.
  - `python3 -m pytest -q tests/test_e2e_scenarios.py`: 134 passed.
  - `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only
    --max-age-seconds 14400 --json`: 11 scenarios, 70 artifacts, 0 failure.

## Cockpit state after refresh

- Public snapshot generated at `2026-07-09T12:05:02.635309+00:00`.
- Summary: `green=96`, `stale=1`, `pending=4`, `missing=0`, `broken=0`,
  `unknown=0`, `excluded=1`.
- `nirs4all-ui` source commit in cockpit:
  `3b87ccd6bc37e4c4b5f9ccb3fc4642d65db2c33e`.
- `nirs4all-cockpit` source commit in cockpit:
  `0e632599e52e066efabf22708b14704f7b5e51f0`.

## Remaining risks

- The full Python-reference parity suite was intentionally not run in this
  batch; run it only after the next large integration batch.
- E2E runtime evidence is fresh for the current artifact set, but it must be
  rerun after selected-head changes or another major integration batch.
- CRAN manual submissions remain outside API automation. The current non-green
  cockpit statuses are still manual CRAN queue items plus one stale CRAN target.
