# Wave 8C - nirs4all-ui Pages Custom Host Boundary

Date: 2026-07-07

## Scope

- Repository: `nirs4all-ui`
- Commit: `5ce32e1` (`docs(site): show custom host integration`)
- Files changed:
  - `site/src/App.tsx`
  - `site/src/styles.css`
  - `site/src/App.test.tsx`
  - `site/vite.config.ts`

## Decision

Updated the `nirs4all-ui` GitHub Pages showcase to expose the reusable `nirs4all-core -> nirs4all-ui -> custom app host` boundary.

The lane deliberately avoided the paths currently used by `nirs4all-quality`:

- `src/lab/**`
- `assets/theme.css`
- `assets/brand/nirs4all/**`
- `assets/brand/quali/**`
- the already-dirty `package.json` and `src/index.ts`

The Pages build now copies only direct files from `assets/brand` into `site/dist/assets/brand/nirs4all-ui`, so the quality-specific brand subdirectories are not embedded in the UI Pages artifact.

## Tests

Executed locally in `nirs4all-ui`:

- `PATH="/home/delete/emsdk/node/22.16.0_64bit/bin:$PATH" npm test -- site/src/App.test.tsx` -> 2 passed
- `PATH="/home/delete/emsdk/node/22.16.0_64bit/bin:$PATH" npm run site:build` -> OK
- `git diff --check -- site/src/App.tsx site/src/styles.css site/src/App.test.tsx site/vite.config.ts` -> OK
- `find site/dist/assets/brand/nirs4all-ui -maxdepth 2` -> direct asset files only, no `nirs4all/` or `quali/` subdirectories

GitHub Actions after push:

- `nirs4all-ui` CI for `5ce32e1`: success
- `nirs4all-ui` GitHub Pages for `5ce32e1`: pending at report creation

## Parallel Review Notes

Claude review identified the next custom-host gap:

- Studio still uses the full Python `nirs4all` library rather than `nirs4all-core`.
- Web uses vendored `nirs4all-ui` and vendored core bindings rather than a published-package install path.
- There is no standalone custom-host template yet; the existing contract test is in-repo and imports app-internal paths.

Those gaps were not mixed into the Pages showcase commit.

## Risks

- The dirty `nirs4all-ui` and `nirs4all-quality` worktree state belongs to another lane and remains uncommitted.
- The new Pages section documents the intended boundary, but it is not yet a reusable template package.
