# WAVE 10BC - UI workflow modernization

Date: 2026-07-09T18:39:46Z

Lane: shared UI / GitHub Actions hygiene

## Summary

- Modernized `nirs4all-ui` first-party workflows without changing reusable
  React components or quality-facing component APIs.
- Moved CI and release workflows to `actions/checkout@v7`,
  `actions/setup-node@v6`, and `actions/setup-python@v6`.
- Moved the GitHub Pages publication workflow to
  `actions/upload-pages-artifact@v5` and `actions/deploy-pages@v5`.
- Kept this wave deliberately non-runtime: no full parity run, no component
  migration, and no changes to package exports.

## Repositories touched

- `nirs4all-ui`
  - Commit `bae1da7` (`ci(actions): modernize ui workflows`)

## Files modified

- `.github/workflows/ci.yml`
- `.github/workflows/pages.yml`
- `.github/workflows/release-npm.yml`
- `.github/workflows/version-guard.yml`

## Validation

Local:

- `npm run brand:check` -> OK.
- `npm run typecheck` -> OK.
- `npm test -- --run` -> 115 passed.
- `npm run ci` -> OK, including build, dry-run pack, and React 18/19
  packed-consumer smoke.
- `npm run site:build` -> OK.
- `git diff --check` -> OK.
- `rg --hidden -n "checkout@v4|setup-node@v4|setup-python@v5|upload-pages-artifact@v3|deploy-pages@v4|upload-artifact@v4|download-artifact@v4|cache@v4" .github/workflows`
  -> no matches.

GitHub:

- `CI` on `bae1da7` -> success.
- `GitHub Pages` on `bae1da7` -> success.
- `version-guard` on `bae1da7` -> success.

## Decisions

- Do not touch `nirs4all-ui` components in this wave because another agent had
  recently integrated quality-related UI work and the requested change was
  workflow/publication hygiene.
- Do not run full parity here; workflow action versions and Pages publication
  plumbing changed, not runtime behavior.

## Remaining risks / blockers

- The broader ecosystem still has workflow modernization debt in other repos as
  recorded by the read-only CI/action audit.
- Manual CRAN submissions and Studio Windows RC smoke remain outside this UI
  workflow batch.
