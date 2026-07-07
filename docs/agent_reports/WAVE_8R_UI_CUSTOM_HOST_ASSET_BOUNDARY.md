# Wave 8R - UI Custom Host Asset Boundary

Date: 2026-07-07

## Scope

- Re-validated `nirs4all-ui` as the reusable visual-system package after the
  quality-agent warning, without touching quality-owned paths.
- Published `nirs4all-ui@0.1.7` and GitHub Release `v0.1.7`.
- Synced `nirs4all-web` to the published UI package, bumped Web to `0.1.5`,
  created GitHub Release `v0.1.5`, and confirmed the Pages deploy.
- Hardened `nirs4all-cockpit` with a machine-readable
  `release_bundles.v1-custom-app-host` grouping.

## Boundary

- Did not modify `nirs4all-ui` quality-owned paths:
  `src/lab/**`, `assets/theme.css`, `assets/brand/nirs4all/**`,
  `assets/brand/quali/**`, nor the dirty main-checkout `package.json` /
  `src/index.ts`.
- Used `/home/delete/nirs4all/_worktrees/nirs4all-ui-assets`, branch
  `codex/ui-assets-brand-system`, for UI edits and validation. That worktree is
  clean and points at the published `nirs4all-ui@0.1.7` head
  `4ab3eabb36604ffbede2b8f9bb6d2721164e3190`.
- Local `nirs4all-web` shim checks must set
  `NIRS4ALL_UI_SHIM_ROOT=/home/delete/nirs4all/_worktrees/nirs4all-ui-assets`
  while the main `nirs4all-ui` checkout contains quality work. The default
  sibling path intentionally sees that dirty checkout and reports drift.

## Changes

### nirs4all-ui

- Scoped inline brand SVG IDs per brand/variant.
- Fixed the optional animated wave by adding a matching dash pattern and
  embedding the animation in the animated path.
- Added regression assertions for scoped IDs and animation wiring.
- Kept existing default styles, reusable brand assets, spectra SVG motion asset,
  deterministic brand generators, package asset exports, and the GitHub Pages
  single-page showcase.

### nirs4all-web

- Synced `studio-lite/vendor/nirs4all-ui` to `0.1.7`.
- Bumped `studio-lite/package.json` to `0.1.5`.
- Updated the published custom-host smoke default to `nirs4all-ui@0.1.7`.
- Published GitHub Release `v0.1.5`; runtime deployment remains
  `https://web.nirs4all.org/`.

### nirs4all-cockpit

- Added `ReleaseBundle` to the targets model.
- Added `release_bundles.v1-custom-app-host` with included packages
  `nirs4all-core`, `nirs4all-ui`, `nirs4all-web` and held packages
  `nirs4all`, `nirs4all-studio`.
- Added offline topology tests that enforce this inclusion/hold boundary.
- Added a versioned GitHub Release target for `nirs4all-web`, alongside Pages.
- Refreshed `data/current.json` for core/ui/web using a clean UI worktree
  overlay so the dirty quality checkout does not pollute the public snapshot.

## Validation

### nirs4all-ui

- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run typecheck`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm test`
  -> 19 files, 76 tests passed.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run site:build`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm pack --dry-run --json`
  -> tarball includes `assets/brand`, `assets/brands`, `assets/styles`,
  `assets/motion`, and `dist`.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run smoke:react-consumers`
  -> React 18 and React 19 packed-consumer imports, render, and types passed.
- GitHub Actions on `4ab3eab`: `CI`, `release-npm`, and `GitHub Pages` passed.

### nirs4all-web / custom app host

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run check:ui-shim`
  with `NIRS4ALL_UI_SHIM_ROOT=/home/delete/nirs4all/_worktrees/nirs4all-ui-assets`
  -> vendored `nirs4all-ui` is up to date.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run test:client-only`
  -> 2 tests passed; client-side-only gate remains enforced.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run check:core-shim`
  -> vendored `nirs4all` core WASM shim is up to date.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run smoke:custom-app-host`
  -> 1 test passed.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run smoke:custom-app-host-template`
  -> 2 tests passed.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run smoke:published-custom-host`
  -> published custom-host smoke passed with `nirs4all@0.2.13` and
  `nirs4all-ui@0.1.7`.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run validate:catalog`
  -> 64 referenced symbols, 702 exported upstream, catalog/ABI in sync.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run typecheck`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run test`
  -> 24 files, 148 tests passed.
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run build`
- GitHub Actions on `ba66782`: `version-guard`, `web-ci`, and
  `Deploy nirs4all-web to GitHub Pages` passed.

### nirs4all-cockpit

- `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  -> 21 packages, 102 targets.
- `python3.11 -m pytest -q`
  -> 120 tests passed.
- `python3.11 -m ruff check .`
- `python3.11 scripts/smoke_dashboard_dom.py`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node --check web/app.js`
- `git diff --check`
- Snapshot after targeted refresh:
  `nirs4all-ui` green at GitHub Release/npm/Pages `0.1.7`;
  `nirs4all-web` green at GitHub Release/Pages `0.1.5`;
  `nirs4all-core` remains missing only on the known PyPI Trusted Publisher
  target and pending on CRAN.

### nirs4all-ecosystem

- Latest ecosystem Actions before this pin update on `a1dc7ad`:
  `version-guard` and `Cross-language E2E scenarios` passed.
- Submodule pins advanced to:
  `nirs4all-ui` `4ab3eabb36604ffbede2b8f9bb6d2721164e3190`,
  `nirs4all-web` `ba6678282c71f8239da28e57128d34fba3b39db8`,
  `nirs4all-cockpit` `0434d21665a20d257c2c681c955f38cff0f2f47a`.

## Decisions

- The custom app host claim is validated as a JS/WASM host composition path:
  published `nirs4all` runtime contracts plus published `nirs4all-ui` React
  components. Non-JS languages consume `nirs4all-core` capability/runtime
  contracts, not React components directly.
- The final V1 custom-app-host boundary is now machine-readable in cockpit:
  core/ui/web are in; Python oracle and production Studio are still tracked but
  held out of the final V1 RC batch.
- `nirs4all-web` is now auditable as both a deployed Pages app and a versioned
  GitHub Release, without turning it into a package-registry aggregate.

## Risks

- Full parity was not rerun in this batch by design; keep it for the next large
  integration batch or final selected heads.
- The main `nirs4all-ui` checkout remains intentionally dirty with quality work.
  Do not normalize or vendor from it until that agent finishes.
- R-universe rebuild latency keeps the cockpit manual action relevant until the
  live `dagmldata` index moves past `0.2.4`.
