# Wave 7Y - Web Core Capability Consumption

Date: 2026-07-07

## Scope

Make `nirs4all-web/studio-lite` consume the new `nirs4all-core` WASM capability
manifest through its existing vendored core shim, without touching
`nirs4all-ui` or `nirs4all-quality`.

## Integrated heads

- `nirs4all-core`: `12d48fe feat(capabilities): expose custom host manifests`
- `nirs4all-web`: `162ac86 feat(web): consume core capability manifest`
- `nirs4all-ecosystem`: submodule pin updated for `nirs4all-web`

## Files changed in web

- `studio-lite/vendor/nirs4all/README.md`
- `studio-lite/vendor/nirs4all/src/index.js`
- `studio-lite/vendor/nirs4all/src/index.d.ts`
- `studio-lite/src/engine/nirs4all-core.ts`
- `studio-lite/src/engine/nirs4all-core.test.ts`
- `studio-lite/src/app/custom-app-host.contract.test.ts`

## Decisions

- `src/engine/nirs4all-core.ts` remains the single runtime adapter for the
  vendored aggregate.
- Web now re-exports `capabilityManifest`, `controllerCapabilities`, and
  `runtimeSurfaces` plus the related TypeScript types.
- The custom app host contract asserts that the runtime manifest and reusable
  UI component flow agree on the portable methods pipeline without modifying
  shared UI components.
- The vendored core shim was updated with `npm run vendor:core`; no
  `sync-core-shim.mjs` changes were needed because it already syncs
  `src/index.js` and `src/index.d.ts`.

## Tests run in `nirs4all-web/studio-lite`

- `NIRS4ALL_CORE_SHIM_REQUIRED=1 npm run check:core-shim`
- `npx vitest run --config vitest.config.ts src/engine/nirs4all-core.test.ts src/app/custom-app-host.contract.test.ts`
  - 10 passed.
- `npm run typecheck`
- `npm run test`
  - 146 passed.
- `npm run validate:catalog`
  - 64 referenced symbols, 702 exported upstream; catalog in sync.
- `npm run build`
- `npm run build:single`

## Risks

- `nirs4all-web` GitHub Actions had not yet appeared for `162ac86` when this
  report was written; local gates above passed.
- Full browser smoke suite was not rerun for this inspect-only contract change.
  Build and vitest coverage cover the changed path.
