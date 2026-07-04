# Wave 4BO - UI and Org Showcase Integration

## Scope

- Reviewed and integrated the parallel `nirs4all-ui` / `nirs4all-org` agent lane.
- Kept write ownership limited to those two repositories.
- Did not touch `nirs4all-web`, `nirs4all-studio`, `nirs4all-drafts`, or `nirs4all-lab`.

## Commits

- `nirs4all-ui`: `67e482f docs(site): expand component showcase`
- `nirs4all-org`: `401122b docs(org): surface ui core provider brands`

## Files Modified

- `nirs4all-ui/README.md`
- `nirs4all-ui/site/index.html`
- `nirs4all-ui/site/src/App.tsx`
- `nirs4all-ui/site/src/styles.css`
- `nirs4all-org/README.md`
- `nirs4all-org/index.html`

## Review Notes

- `nirs4all-ui` now exposes a visible reusable component catalogue before runtime helper demos.
- `nirs4all-ui` remains presentational: no Studio/Web imports, routing, API calls, execution, browser storage, or app-owned state.
- `nirs4all-org` links the UI Components page and uses existing brand assets for `nirs4all-ui`, `nirs4all-core`, and `nirs4all-providers`.
- Existing brand assets were reused; no generated bitmap/logo changes were needed.

## Tests

- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run typecheck`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm test`
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run site:build`
- `python3.11` static `nirs4all-org/index.html` parse plus local image asset existence check
- `git diff --check` in both repositories

## Risks

- GitHub Pages publication was validated locally through the Vite build; the public GitHub Pages URL was not fetched after push.
- `nirs4all-org` remains a single static HTML file, so future content changes still need manual SEO/sitemap discipline.
