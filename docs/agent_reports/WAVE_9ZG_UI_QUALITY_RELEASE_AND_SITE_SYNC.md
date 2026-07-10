# Wave 9ZG - UI quality brand release and site sync

Date: 2026-07-10

## Scope

- Finalized the shared `nirs4all-quality` brand surface in `nirs4all-ui`.
- Published `nirs4all-ui` as `v0.1.11` / npm `0.1.11`.
- Synchronized the public org site and cockpit snapshot after the release.
- Updated ecosystem submodule pointers for `nirs4all-ui`, `nirs4all-org`, and `nirs4all-cockpit`.

## Files / repos changed

- `nirs4all-ui`
  - Commit: `01ec91f feat(brand): add quality reusable brand assets`
  - Tag / release: `v0.1.11`
  - Added reusable `nirs4all-quality` brand registry entry and generated SVG assets.
  - Exposed the quality brand asset in the GitHub Pages component/assets showcase.
  - Bumped package metadata from `0.1.10` to `0.1.11`.
- `nirs4all-org`
  - Commit: `45da523 docs(site): update ui release surface`
  - Updated `nirs4all-ui` static version surfaces from `0.1.10` to `0.1.11`.
  - Updated sitemap index lastmod entries for org, cockpit, and the UI showcase.
- `nirs4all-cockpit`
  - Commit: `9a46255 chore(collect): refresh data/current.json`
  - Snapshot now sees `nirs4all-ui` `0.1.11` green for GitHub Release, npm, and Pages.
- `nirs4all-ecosystem`
  - Updated submodule pointers for the three repos above.

## Validation

- `nirs4all-ui`
  - `tsc -p tsconfig.json --noEmit`
  - `vitest run`: 24 files / 115 tests passed.
  - `tsc -p tsconfig.build.json`
  - `vite build --config site/vite.config.ts`
  - `node scripts/generate-brand-assets.mjs --check`
  - `nirs4all-quality/app`: `tsc --noEmit`
  - `nirs4all-quality/app`: `vite build`
  - GitHub Actions on `01ec91f`: `CI`, `version-guard`, `GitHub Pages`, and `release-npm` all succeeded.
  - External checks: npm registry returns `nirs4all-ui@0.1.11`; Pages bundle and public SVG assets include `nirs4all-quality`.
- `nirs4all-org`
  - XML parse for `sitemap.xml` and `sitemap-index.xml`.
  - Static assertions for `nirs4all-ui` `0.1.11` JSON-LD and ecosystem badge.
  - GitHub Actions on `45da523`: `version-guard` and Pages deployment succeeded.
- `nirs4all-cockpit`
  - Manual `collect` workflow succeeded after the UI release.
  - Pages deployment for snapshot `9a46255` succeeded.

## Decisions

- Kept `nirs4all-quality` as a reusable brand asset/metadata surface in `nirs4all-ui`, without editing the `src/lab/*` components used by the quality host.
- Did not add legacy aliases for older UI package names.
- Treated GitHub Actions `npm run ci` as the authoritative package smoke because the WSL shell exposes only Windows `npm`; local validation covered the same TypeScript/test/build/site/generator paths through Linux Node and local binaries.

## Risks / follow-up

- The `nirs4all-quality` app still emits its existing Vite warning about `node:module` externalization from `nirs4all-web` WASM glue; it is unrelated to the UI brand release and does not fail the build.
- The broader goal remains open: cross-language E2E expansion, final full parity gates, and remaining release-candidate audit are not completed by this wave.
