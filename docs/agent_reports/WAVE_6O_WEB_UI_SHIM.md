# Wave 6O - Web UI Shim Sync

Date: 2026-07-06

## Scope

- Repo: `nirs4all-web`
- Lane: Web / shared UI consumption
- Ownership: `studio-lite/vendor/nirs4all-ui/README.md`

## Changes

- Resynchronised the vendored `nirs4all-ui` README used by `studio-lite`.
- No runtime source, built `dist`, package manifest, or shared component code changed.
- Repinned the `nirs4all-web` submodule in `nirs4all-ecosystem` from `149d294` to `2285960`.

## Validation

From `nirs4all-web/studio-lite` with Node 22:

- `npm run check:ui-shim` - passed
- `npm run test:client-only` - passed, 2 tests
- `npm run smoke:shared-ui-contract` - passed, 2 tests
- `npm run typecheck` - passed
- `npm run build` - passed

Browser smokes were not rerun in this wave because the current sandbox blocks local server/Chrome
socket setup; earlier attempts failed at process/socket startup, not at application assertions.

## Risk

Low. The only tracked source change is documentation in the vendored shared-UI shim. The fix removes
the remaining `check:ui-shim` drift while preserving the client-side-only and shared-UI contract
tests.
