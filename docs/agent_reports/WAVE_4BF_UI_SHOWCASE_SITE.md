# Wave 4BF - nirs4all-ui Showcase Site

Date: 2026-07-04

## Scope

Expanded the `nirs4all-ui` GitHub Pages single-page showcase so the package can
be reviewed independently before Studio/Web consume more shared components.

## Files changed

- `nirs4all-ui/site/src/App.tsx`
  - Documents the package export surface for root, `components`, `runtime`,
    `score`, and asset entries.
  - Renders the current React component surface honestly: `RuntimeEngineBadge`
    only, plus runtime/score helper examples.
  - Adds links to site assets and metadata files used by GitHub Pages.
- `nirs4all-ui/site/src/styles.css`
  - Reworks the site layout into responsive export, component, runtime, score,
    and asset sections.
  - Keeps cards limited to repeated showcase items and keeps sections unframed.

## Tests run

- `npm run typecheck`
- `npm test -- --run` -> 52 tests passed.
- `npm run build`
- `npm run site:build`
- `npm run pack:smoke`
- Playwright screenshots:
  - `/tmp/nirs4all-ui-showcase.png`
  - `/tmp/nirs4all-ui-showcase-mobile.png`

## Decisions

- The showcase does not invent missing shared UI. It calls out that only one
  React component is currently exported and presents runtime/score helpers as
  view-model contracts.
- The site anticipates GitHub Pages publication only; no custom subdomain was
  assigned in this batch.

## Risks

- Studio and Web still need follow-up integration work to consume this package
  for common runtime/result surfaces.
