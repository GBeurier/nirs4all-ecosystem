# Wave 8K - UI Visual System Release And Cascade

Date: 2026-07-07

## Scope

- `nirs4all-ui`: reusable graphical asset layer, default CSS tokens, brand
  metadata helpers, motion motif, and GitHub Pages component/asset showcase.
- `nirs4all-web`: vendored shared UI package synchronized to the published
  `nirs4all-ui` 0.1.6 package and custom-app host smokes updated.
- `nirs4all-org`: public site copy refreshed so the shared UI package is
  described as components plus reusable ecosystem assets.
- `nirs4all-cockpit`: public snapshot refreshed after the UI/Web/Org cascade.
- `nirs4all-ecosystem`: submodule pointers updated for the reviewed heads.

## Decisions

- `nirs4all-ui` can evolve as the shared visual asset and component package, but
  paths actively consumed by `nirs4all-quality` remain protected:
  `src/lab`, `assets/theme.css`, `assets/brand/nirs4all`, and
  `assets/brand/quali`.
- The visual-system work was integrated from an isolated clean worktree,
  `/home/delete/nirs4all/_worktrees/nirs4all-ui-assets`, instead of the dirty
  main UI checkout used by concurrent quality work.
- `nirs4all-web` remains client-side-only; the cascade only updates vendored UI
  assets, shared package contract checks, and static build outputs.
- The cockpit remains an accuracy dashboard, not an artificial all-green board:
  PyPI Trusted Publisher, CRAN, and stale R-universe blockers remain explicit.

## Integrated Heads

- `nirs4all-ui`: `210217f62cd58975b1372fd8a097a5b1d915667d`
  (`v0.1.6`, npm `nirs4all-ui@0.1.6`, GitHub Release `v0.1.6`).
- `nirs4all-web`: `964b8f5a014726c26719fedd2c54d905b6c464fd`.
- `nirs4all-org`: `01a401a6bbb6d7d084321fcfcb9b42a1551bca25`.
- `nirs4all-cockpit`: `24dee9cd2082f2628258566ae32ae51fa87f139f`.

## Files Modified

- `nirs4all-ui`
  - `assets/brands/**`
  - `assets/styles/nirs4all-default.css`
  - `assets/motion/nirs-spectra.svg`
  - `scripts/generate-brand-assets.mjs`
  - `src/brand/**`
  - `src/styles/**`
  - `site/**`
- `nirs4all-web`
  - `studio-lite/vendor/nirs4all-ui/**`
  - `studio-lite/package-lock.json`
  - `studio-lite/scripts/smoke-published-custom-host.mjs`
  - `studio-lite/src/app/shared-ui-contract.test.ts`
- `nirs4all-org`
  - `index.html`
  - `open-source-nirs-tools.html`
- `nirs4all-cockpit`
  - `data/current.json`
  - `data/manual-actions.json`
- `nirs4all-ecosystem`
  - `docs/RELEASE_DISTRIBUTION_MATRIX.md`
  - `docs/agent_reports/WAVE_8K_UI_VISUAL_SYSTEM_RELEASE_AND_CASCADE.md`
  - submodules: `nirs4all-ui`, `nirs4all-web`, `nirs4all-org`,
    `nirs4all-cockpit`

## Tests

- `nirs4all-ui`: `npm run typecheck`.
- `nirs4all-ui`: `npm test` -> 76 tests passed.
- `nirs4all-ui`: `npm run build`.
- `nirs4all-ui`: `npm run site:build`.
- `nirs4all-ui`: `npm run smoke:react-consumers`.
- `nirs4all-ui`: `npm pack --dry-run`.
- `nirs4all-ui`: `npm run ci`.
- `nirs4all-ui`: published package smoke for `nirs4all-ui@0.1.6`, importing
  `brand`, `styles`, and `runtime` subpath exports and checking packaged assets.
- `nirs4all-web`: `npm run check:ui-shim` with
  `NIRS4ALL_UI_SHIM_REQUIRED=1`.
- `nirs4all-web`: `npm run smoke:shared-ui-contract`.
- `nirs4all-web`: `npm run smoke:custom-app-host`.
- `nirs4all-web`: `npm run smoke:custom-app-host-template`.
- `nirs4all-web`: `npm run smoke:published-custom-host`.
- `nirs4all-web`: `npm run typecheck`.
- `nirs4all-web`: `npm run test` -> 148 tests passed.
- `nirs4all-web`: `npm run validate:catalog` with methods ABI and Studio
  registry required.
- `nirs4all-web`: `npm run build`.
- `nirs4all-web`: `npm run build:single`.
- `nirs4all-org`: HTML parser/string sanity check.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets
  ops/targets.yaml`.
- `nirs4all-cockpit`: `python3.11 -m pytest -q` -> 119 tests passed.
- `nirs4all-cockpit`: `node --check web/app.js`.
- `nirs4all-cockpit`: JSON assertions for UI/Web/Org heads and secret-free
  manual action payload.

## Remote Validation

- `nirs4all-ui` GitHub Actions on `210217f`: UI CI, GitHub Pages, and
  `release-npm` passed.
- `nirs4all-web` GitHub Actions on `964b8f5`: version guard, web CI, and Pages
  deployment passed.
- `nirs4all-org` GitHub Actions on `01a401a`: version guard and Pages passed.
- `nirs4all-cockpit` GitHub Actions on `24dee9c`: version guard and Pages
  passed.

## Risks

- Seven PyPI targets remain blocked by Trusted Publisher setup or deliberate
  token-based publication: `dag-ml`, `dag-ml-data`, `nirs4all-core`,
  `nirs4all-providers`, `nirs4all-tools`, `nirs4all-benchmarks`, and
  `nirs4all-repository`.
- CRAN publication remains manual/human-reviewed for the current R packages;
  stale or pending cells must stay visible in the cockpit until live registries
  confirm them.
- Full Python-reference parity was not rerun for this UI/Web/Org/cockpit batch;
  reserve the expensive parity gate for the next larger runtime/core batch.
