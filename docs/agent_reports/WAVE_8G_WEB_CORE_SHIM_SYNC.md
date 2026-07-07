# Wave 8G - Web Core Shim Sync

Date: 2026-07-07

## Scope

- Repository: `nirs4all-web`
- Commit: `da8a3de` (`chore(studio-lite): sync vendored core shim`)
- Files changed:
  - `studio-lite/vendor/nirs4all/package.json`
  - `studio-lite/package-lock.json`
- Ecosystem integration:
  - `nirs4all-web` submodule advanced from `526984d` to `da8a3de`

## Decision

Synchronized the vendored `nirs4all` browser package with the current
`nirs4all-core/bindings/wasm` package metadata. GitHub Actions failed the Web
and Pages jobs on `NIRS4ALL_CORE_SHIM_REQUIRED=1 npm run check:core-shim` because
`vendor/nirs4all/package.json` still advertised `0.2.12` while the source shim is
`0.2.13`. The npm lock entry for the vendored package was also refreshed to
`0.2.13`.

## Tests

Executed locally in `nirs4all-web/studio-lite`:

- `npm ci` -> OK
- `NIRS4ALL_CORE_SHIM_REQUIRED=1 npm run check:core-shim` -> OK
- `NIRS4ALL_UI_SHIM_REQUIRED=1 npm run check:ui-shim` -> OK
- `NIRS4ALL_METHODS_ABI_REQUIRED=1 NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1 npm run validate:catalog` -> OK
- `npm run test` -> 148 passed
- `npm run typecheck` -> OK
- `npm run build:single` -> OK
- `npm run build` -> OK
- `npm run smoke -- rt-fallback` -> OK

## Risks

- GitHub Actions still need to confirm the pushed `da8a3de` head.
- The build still emits the existing large-chunk and browser-external warnings;
  they were present before this metadata sync and did not block the CI gate.
