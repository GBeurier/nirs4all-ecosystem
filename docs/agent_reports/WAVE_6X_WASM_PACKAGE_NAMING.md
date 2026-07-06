# Wave 6X - WASM Package Naming Audit And Web Alias Fix

Date: 2026-07-06

## Scope

- Repos audited: `nirs4all-core`, `nirs4all-formats`, `nirs4all-io`, `nirs4all-datasets`,
  `nirs4all-methods`, `nirs4all-web`
- Repos changed: `nirs4all-web`, `nirs4all-formats`
- Web head: `ffe6a87`
- Formats head: `7b213d0`

## Finding

The canonical public naming matrix is already implemented by the release manifests:

- Core aggregate npm package: `nirs4all`
- Component WASM packages:
  - `@nirs4all/formats-wasm`
  - `@nirs4all/io-wasm`
  - `@nirs4all/datasets-wasm`
  - `@nirs4all/methods-wasm`

The remaining runtime risk was in `nirs4all-web`: its vendored `nirs4all-core` shim imports
`@nirs4all/formats-wasm` and `@nirs4all/io-wasm`, but Web only aliased the older unscoped
`nirs4all-formats-wasm` and `nirs4all-io-wasm` names.

## Changes

- Added scoped Vite/Vitest aliases in `nirs4all-web/studio-lite` for:
  - `@nirs4all/formats-wasm`
  - `@nirs4all/io-wasm`
- Kept legacy unscoped aliases for one compatibility release.
- Updated `scripts/build-wasm.sh` so future local `wasm-pack` rebuilds rewrite staged `formats` and
  `io` package names to the scoped canonical names.
- Updated `nirs4all-formats` public WASM docs and README snippets to use
  `@nirs4all/formats-wasm` as the npm package name while preserving local wasm-bindgen filenames and
  the Rust crate name.

## Validation

From `nirs4all-web/studio-lite` with Node 22:

- `npm run typecheck`
- `npm test` - 140 tests
- `npm run build`
- `npm run build:single`
- `nirs4all-formats`:
  - `git diff --check`
  - lightweight doc-name validation for the touched README/docs/demo files
  - `sphinx-build -W -b html docs docs/_build/html` was attempted but still fails on pre-existing
    unrelated warnings in `docs/maintenance/*` (substitution plus orphan pages), not on the changed
    WASM docs.

## Remaining Follow-Up

- Consider adding datasets rebuild support to Web's `build-wasm.sh` in a dedicated WASM staging
  pass.
