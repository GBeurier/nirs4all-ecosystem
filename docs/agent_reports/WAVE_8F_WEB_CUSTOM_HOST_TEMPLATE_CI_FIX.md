# Wave 8F - Web Custom Host Template CI Fix

Date: 2026-07-07

## Scope

- Repository: `nirs4all-web`
- Commit: `526984d` (`test(studio-lite): avoid duplicate react in host template gate`)
- Files changed:
  - `studio-lite/src/app/custom-app-host-template.contract.test.ts`
- Ecosystem integration:
  - `nirs4all-web` submodule advanced from `7023298` to `526984d`

## Decision

The custom app host template contract no longer server-renders `CustomAppHostDemo`
through `react-dom/server`. The full Vitest suite can load the vendored
`nirs4all-ui` package in a way that creates a second React instance; rendering
those components inside this contract can fail with a React-child object error
even when the template imports and runtime state are valid.

The test still validates the intended boundary:

- public imports from `nirs4all` and `nirs4all-ui/*`
- no imports from Web app internals
- expected runtime/predict surface state
- presence of the reusable UI component surfaces in the standalone template

## Tests

Executed locally in `nirs4all-web/studio-lite`:

- `npm run smoke:custom-app-host-template` -> 2 passed
- `npm run test` -> 148 passed
- `npm run typecheck` -> OK
- `npm run build` -> OK

## Risks

- The contract intentionally avoids SSR rendering of vendored React components;
  component rendering coverage remains in the `nirs4all-ui` package and Web app
  tests.
- GitHub Actions still need to confirm the pushed head on `main`.
