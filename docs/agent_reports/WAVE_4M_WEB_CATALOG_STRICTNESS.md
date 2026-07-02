# Wave 4M - Web catalog strictness

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up to Wave 4L. The Web catalog gate was still partially optional:
without sibling checkouts, `validate:catalog` could skip the `nirs4all-methods`
ABI snapshot and the Studio canonical DAG registry subcheck. This wave makes
those upstream checks blocking in Web CI and Pages deployment.

## Published Code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-web` | `rc/v1-full-refactor` | `8a5dcff` / `n4a-v1-rc1-2026.07-refactor` | Web/Pages workflows, methods/studio sibling actions, `validate-catalog.mjs` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | control board, surface matrix, this report |

## Changes

- Added `.github/actions/nirs4all-studio-sibling` so Web CI can validate
  `dag.studioNodeType` ids against Studio's generated
  `src/data/nodes/generated/node-reference.json`.
- Added `.github/actions/nirs4all-methods-sibling` so Web CI can validate
  catalog `n4m_*` symbols against the canonical `nirs4all-methods` ABI snapshot.
- `studio-lite/scripts/validate-catalog.mjs` now supports strict modes:
  - `NIRS4ALL_METHODS_ABI_REQUIRED=1`
  - `NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1`
- RC worktree fallbacks were added for local validation from `_worktrees`.
- `.github/workflows/web-ci.yml` and `.github/workflows/deploy-pages.yml` now
  run strict catalog validation.

## Local Gates

From `RC-v1-web/studio-lite` with Linux Node 24:

- `NIRS4ALL_METHODS_ABI_REQUIRED=1 NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1 npm run validate:catalog`
  -> `64` catalog symbols checked against `702` exported upstream symbols, and
  `5` DAG operators checked against Studio (`branch.parallel`,
  `container.concat_transform`, `merge.sources`, `generator.or`,
  `generator.cartesian`).
- `npm run test:client-only` -> `2 passed`.
- `npm run typecheck` -> passed.
- `npm run test` -> `134 passed`.
- `npm run check:lite-shim` -> `vendor/nirs4all is up to date`.
- `npm run build:single` -> passed.
- `npm run build` -> passed.
- `npm run smoke -- rt-fallback` -> passed (`1` browser smoke).

## Remaining Risk

- This is still a focused browser smoke, not the full `tests/*smoke.mjs` suite.
- Web `npm audit` risk from Wave 4L remains unresolved; no dependency upgrade
  was included in this catalog-strictness change.
