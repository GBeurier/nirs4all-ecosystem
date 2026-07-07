# Wave 8I - UI/Web Published Host And Cockpit

Date: 2026-07-07

## Scope

- `nirs4all-ui`: published package refresh from `5ce32e1` to `7ee1faa`
- `nirs4all-web`: custom-host published-package smoke from `da8a3de` to
  `82c9b58`
- `nirs4all-cockpit`: public snapshot refresh from `c11e0ad` to `2fb8f8d`
- `nirs4all-ecosystem`: submodules updated for those three heads

## Decisions

- Kept the main `nirs4all-ui` checkout untouched because it contains concurrent
  `nirs4all-quality` work under `src/lab`, `assets/theme.css`, and brand assets.
- Published `nirs4all-ui@0.1.5` from a clean detached worktree at `7ee1faa`.
- Added a Web smoke that installs pinned public packages in a temporary
  directory: `nirs4all@0.2.13` + `nirs4all-ui@0.1.5`.
- Added `NIRS4ALL_UI_SHIM_ROOT` to the Web UI-vendor sync script so local checks
  can target the clean UI release worktree instead of the dirty quality checkout.
- Refreshed Cockpit after Web CI and Pages were green on `82c9b58`.

## Files Modified

- `nirs4all-ui`
  - `package.json`
  - `package-lock.json`
- `nirs4all-web`
  - `studio-lite/README.md`
  - `studio-lite/package.json`
  - `studio-lite/scripts/smoke-published-custom-host.mjs`
  - `studio-lite/scripts/sync-ui-shim.mjs`
  - `studio-lite/vendor/nirs4all-ui/package.json`
- `nirs4all-cockpit`
  - `data/current.json`
- `nirs4all-ecosystem`
  - `docs/RELEASE_DISTRIBUTION_MATRIX.md`
  - `docs/agent_reports/WAVE_8I_UI_WEB_PUBLISHED_HOST_AND_COCKPIT.md`
  - submodules: `nirs4all-ui`, `nirs4all-web`, `nirs4all-cockpit`

## Published State

- `nirs4all-ui`: npm `0.1.5`, GitHub release `v0.1.5`, GitHub Pages green.
  The published tarball includes `./dataset`, `./runtime`, `./components`, and
  `./assets/*`.
- `nirs4all-web`: GitHub Pages green from `82c9b58`; app remains
  client-side-only.
- `nirs4all-cockpit`: snapshot summary `green=84 stale=5 pending=4 missing=7
  broken=0 unknown=0 excluded=1`; Web/UI Actions stats reflect the latest green
  runs.

## Tests

- `nirs4all-ui`: `npm ci`; `npm run ci`; `npm run site:build`; npm tarball
  inspection for `dist/dataset` and subpath exports.
- `nirs4all-web`: `npm run typecheck`; `npm run test` -> 148 passed;
  `NIRS4ALL_CORE_SHIM_REQUIRED=1 npm run check:core-shim`;
  `NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-ui-release-0.1.5 NIRS4ALL_UI_SHIM_REQUIRED=1
  npm run check:ui-shim`;
  `NIRS4ALL_METHODS_ABI_REQUIRED=1 NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1 npm run
  validate:catalog`; `npm run build`; `npm run build:single`; `npm run
  smoke:published-custom-host`.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets
  ops/targets.yaml`; `python3.11 -m cockpit.cli summarize data/current.json`;
  `python3.11 -m pytest -q` -> 117 passed.

## Risks

- PyPI Trusted Publisher blockers remain real for `nirs4all-core`,
  `nirs4all-providers`, `nirs4all-tools`, `dag-ml`, and `dag-ml-data`.
- CRAN/R-universe pending or stale cells remain visible in Cockpit; they were
  not masked.
- `nirs4all-quality` currently consumes `nirs4all-ui` via sibling source aliases,
  so `src/lab`, `assets/theme.css`, and quality brand assets stay protected
  until that work is merged or repackaged.
