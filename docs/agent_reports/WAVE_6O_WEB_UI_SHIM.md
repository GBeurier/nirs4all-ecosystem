# Wave 6O - Web UI Shim Sync

Date: 2026-07-06

## Scope

- Repo: `nirs4all-web`
- Lane: Web / shared UI and core shim consumption
- Ownership:
  - `studio-lite/vendor/nirs4all-ui/README.md`
  - `studio-lite/vendor/nirs4all/README.md`
  - `studio-lite/vendor/nirs4all/package.json`

## Changes

- Resynchronised the vendored `nirs4all-ui` README used by `studio-lite`.
- Resynchronised the vendored `nirs4all-core` WASM package metadata used by `studio-lite`.
- No runtime source, built `dist`, or shared component code changed.
- Repinned the `nirs4all-web` submodule in `nirs4all-ecosystem` from `149d294` through the
  intermediate UI-shim fix `2285960` to the CI-complete shim fix `9a8c383`.

## Validation

From `nirs4all-web/studio-lite` with Node 22:

- `npm run check:ui-shim` - passed
- `NIRS4ALL_LITE_SHIM_REQUIRED=1 npm run check:lite-shim` - passed
- `npm run test:client-only` - passed, 2 tests
- `npm run smoke:shared-ui-contract` - passed, 2 tests
- `npm run validate:catalog` - passed
- `npm test` - passed, 140 tests
- `npm run typecheck` - passed
- `npm run build` - passed

Browser smokes were not rerun in this wave because the current sandbox blocks local server/Chrome
socket setup; earlier attempts failed at process/socket startup, not at application assertions.

## Risk

Low. The tracked changes are vendored shim metadata/docs only. The fix removes the remaining
`check:ui-shim` and `check:core-shim` drift while preserving the client-side-only, shared-UI,
catalog, unit, and build gates.
