# Wave 8E - Web Custom Host Template

Date: 2026-07-07

## Scope

- Repository: `nirs4all-web`
- Commit: `7023298` (`feat(studio-lite): add custom host template`)
- Files changed:
  - `studio-lite/examples/custom-app-host/**`
  - `studio-lite/src/app/custom-app-host-template.contract.test.ts`
  - `studio-lite/README.md`
  - `studio-lite/package.json`

## Decision

Added a copy-out custom app host template for client-side-only applications that compose public package surfaces:

- `nirs4all`
- `nirs4all-ui/components`
- `nirs4all-ui/dataset`
- `nirs4all-ui/runtime`

The template deliberately avoids `@/engine/*`, Web app routing, app state stores, and Web/Studio internal components. It includes its own Vite config with browser/WASM aliases pointed at the vendored release-candidate stack.

## Tests

Executed locally in `nirs4all-web/studio-lite`:

- `npm run smoke:custom-app-host-template` -> 2 passed
- `npm run test -- src/app/custom-app-host-template.contract.test.ts src/app/custom-app-host.contract.test.ts src/app/shared-ui-contract.test.ts` -> 6 passed
- `npm run typecheck` -> OK
- `npx tsc --noEmit --project examples/custom-app-host/tsconfig.json` -> OK
- `npx vite build --config examples/custom-app-host/vite.config.ts` -> OK
- `npm run build` -> OK

No backend was introduced; the app remains client-side-only.

## Risks

- The template uses file dependencies to the vendored RC packages, not published npm package installation yet.
- The template proves public imports and buildability; it is not a full Web/Studio feature parity smoke.
