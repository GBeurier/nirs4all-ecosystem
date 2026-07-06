# Wave 7I - custom app host integration

Date: 2026-07-06

## Scope

Validated and tightened the `nirs4all-core` + `nirs4all-ui` composition path used
by `nirs4all-web/studio-lite` as the reference client-side-only custom app host.

## Files modified

- `nirs4all-web/studio-lite/scripts/sync-ui-shim.mjs`
- `nirs4all-web/studio-lite/src/app/shared-ui-contract.test.ts`
- `nirs4all-web/studio-lite/README.md`
- `nirs4all-web/studio-lite/vendor/nirs4all/**`
- `nirs4all-web/studio-lite/vendor/nirs4all-ui/assets/brand/**`
- `nirs4all-core/bindings/wasm/README.md`

## Decisions

- The Web vendor now includes `nirs4all-ui` brand assets, so custom hosts can
  consume package assets without adding a backend dependency.
- `sync-ui-shim.mjs` reads `package.json`, `README.md`, `src`, and `assets` from
  the upstream `nirs4all-ui` `HEAD`, not from its dirty worktree. This avoids
  accidentally vendoring the concurrent `nirs4all-quality` UI work.
- `dist/` remains copied from the upstream filesystem because it is build output
  and not tracked by `nirs4all-ui`.
- No `nirs4all-ui` main checkout files were edited.

## Validation

- `npm run vendor:ui`
- `npm run check:ui-shim`
- `npm run smoke:shared-ui-contract`
- `npm run smoke:custom-app-host`
- `npm run typecheck`
- `npm run validate:catalog`
- `npm run test` -> 23 files, 144 tests.
- `npm test --prefix bindings/wasm` -> 16 JS tests passed, then local `tsc`
  wrapper failed with `Permission denied`.
- `node bindings/wasm/node_modules/typescript/bin/tsc --project bindings/wasm/tsconfig.typecheck.json` -> OK.

## Risks

- The branch `codex/ui-assets-brand-system` for the full reusable UI asset system
  is still not merged into `nirs4all-ui/main`; Web therefore vendors only the
  brand assets currently tracked on UI `HEAD`.
