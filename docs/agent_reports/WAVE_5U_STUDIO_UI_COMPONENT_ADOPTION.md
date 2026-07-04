# Wave 5U - Studio shared UI component adoption

Date: 2026-07-04

## Scope

Repository: `nirs4all-studio`

Commit pushed:

- `93013de feat(runtime): reuse shared UI primitives`
- `a8eda33 ci: install local dag-ml rc dependencies`
- `fd7269d ci: materialize shared ui sibling`
- `c80949a ci: resolve shared ui sources inside workspace`

Files changed:

- `src/components/runtime/RuntimeEngineBadge.tsx`
- `src/components/runtime/RuntimeDiagnosticsList.tsx`
- `src/components/runtime/RuntimeStatus.tsx`
- `src/ui/runtime/resultMetadata.test.ts`
- `.github/workflows/ci.yml`
- `.github/workflows/playwright.yml`
- `.github/workflows/release-unified.yml`
- `vite.config.ts`
- `vitest.config.ts`

## Implementation

- `RuntimeEngineBadge` now delegates its inner badge content to `nirs4all-ui/components` while preserving the Studio `Badge` wrapper, tone classes, icons, and title.
- `RuntimeDiagnosticsList` now uses `RuntimeDiagnosticList` from `nirs4all-ui/components` with a Studio row renderer, preserving current Studio visual rows while sharing list orchestration.
- `RuntimeStatusBadge` now uses `RuntimeResultStatusBadge` from `nirs4all-ui/components` for the label/icon content while preserving Studio badge variants and local status icons.
- `resultMetadata.test.ts` now expects the shared runtime diagnostic contract field `unsupportedCapability: null` instead of relying on its absence.
- CI/Playwright now install local `dag-ml` and `dag-ml-data` Python bindings before installing the source checkout of `nirs4all`, avoiding a false dependency on unavailable PyPI RC packages.
- CI/Playwright/release jobs now materialize the `file:../nirs4all-ui` sibling expected by `package.json`.
- Vite/Vitest resolve shared UI sources from the in-workspace `nirs4all-ui-lib/src` checkout when present, and fall back to `../nirs4all-ui/src` locally. This keeps external shared UI sources able to resolve Studio's `node_modules/react`.

## Review

- Kepler audit recommended this exact first lot as the lowest-risk Studio component convergence step.
- Local review checked that the imported shared components keep the same runtime labels and only add an inner shared presentation layer.
- This does not claim full Studio/Web UI convergence. Web already consumes `nirs4all-ui`; Studio now consumes selected shared runtime components, but broader component migration remains open.

## Verification

- `npm run test:frontend -- --run src/ui/runtime/resultMetadata.test.ts src/components/runtime/RuntimeComponents.test.tsx` (`9 passed`)
- `npm run test:frontend` (`3695 passed`, `1 skipped`)
- `npm run lint:tsc`
- `npm run lint:eslint -- src/components/runtime/RuntimeEngineBadge.tsx src/components/runtime/RuntimeDiagnosticsList.tsx src/components/runtime/RuntimeStatus.tsx src/ui/runtime/resultMetadata.test.ts`
- `npm run build` passed before the test expectation update; warnings were existing Vite/Tailwind chunk and ambiguous utility warnings.
- `npm run test:frontend -- --run src/components/runtime/RuntimeComponents.test.tsx src/pages/Runs.test.tsx` (`16 passed`)
- `npm run lint:eslint -- vite.config.ts vitest.config.ts`
- `npm run build` after the Vite/Vitest alias update
- `npm run lint:storage`
- `git diff --check`
- GitHub Actions on `c80949a`:
  - Studio `CI` success (`28711305238`)
  - Studio `Playwright E2E Tests` success (`28711305273`)

## Decisions

- No Studio tag or release was created; `nirs4all-studio` remains prod-sensitive and outside the final non-prod release batch except for the separate Windows RC installer path.
- No full parity run was launched for this small UI component batch; reserve full parity for larger runtime/refactor batches.
- The active refactor goal includes the ecosystem-level set of about 10 complex E2E cross-language/multimodal scenarios covering R/Python/WASM/Web, datasets/io, pipelines, repository, papers, saves, and predictions.

## Risks

- Studio and Web now share more runtime UI primitives, but React version compatibility remains important: Web uses React 18 while Studio uses React 19, so new `nirs4all-ui` components must stay React 18-compatible.
- The full component extraction target is not complete. Remaining Studio components still need staged migration after this first runtime badge/list lot.
