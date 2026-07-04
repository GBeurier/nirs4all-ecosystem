# Wave 5F - nirs4all-ui Pages and cockpit refresh

Date: 2026-07-04

## Scope

- Lane H / public UI surface: make the `nirs4all-ui` showcase a GitHub Pages project page for now, without activating a custom subdomain.
- Lane A / cockpit: refresh the public cockpit snapshot after the UI Pages deployment.

## Changes Integrated

- `GBeurier/nirs4all-ui` commit `610b118`:
  - removed the active `site/public/CNAME` for `ui.nirs4all.org`;
  - set the default Vite Pages base to `/nirs4all-ui/`;
  - updated canonical, Open Graph, Twitter, robots, sitemap, and manifest metadata to `https://gbeurier.github.io/nirs4all-ui/`;
  - added a Vite build plugin that copies the package brand kit to `site/dist/assets/brand/nirs4all-ui/`;
  - listed the stable Pages brand URLs in the single-page showcase;
  - documented the distinction between namespaced Pages URLs and npm package exports under `assets/brand`.
- `GBeurier/nirs4all-cockpit` bot commit `32a0a07`:
  - refreshed `data/current.json` after the UI deployment.

## Review

- Claude Code review session `86d1e958-d111-44ce-94f7-7156213e206d` reviewed the `nirs4all-ui` diff.
- Findings fixed before commit:
  - the build plugin now derives the target directory from Vite `configResolved().build.outDir`;
  - UI copy and README now avoid implying that the namespaced Pages URL is an npm package import path.
- Remaining accepted notes:
  - site-only behavior is covered by `site:build` and HTTP preview checks, not by Vitest;
  - `site:dev` does not synthesize the copied Pages brand URLs;
  - the build copies the complete brand kit, not only the three SVGs referenced by the showcase.

## Tests and Checks

- `nirs4all-ui`:
  - `npm run ci` with Node 24.16.0: passed (`59 passed`);
  - `npm run site:build`: passed;
  - local `vite preview` at `/nirs4all-ui/`: page 200, `assets/brand/nirs4all-ui/icon.svg` 200, `robots.txt` 200;
  - GitHub Actions for `610b118`: `CI` success, `GitHub Pages` success;
  - live checks:
    - `https://gbeurier.github.io/nirs4all-ui/` 200;
    - `https://gbeurier.github.io/nirs4all-ui/assets/brand/nirs4all-ui/icon.svg` 200;
    - `https://gbeurier.github.io/nirs4all-ui/CNAME` 404.
- `nirs4all-cockpit`:
  - `collect` workflow `28704680242`: success, generated `2026-07-04T11:25:58.408272+00:00`;
  - `pages` workflow `28704762711`: success;
  - live `https://cockpit.nirs4all.org/data/current.json` contains `nirs4all-ui` commit `610b118` and URL `https://gbeurier.github.io/nirs4all-ui/`.

## Current Public Blockers Still Visible in Cockpit

- PyPI `nirs4all-core`: missing; manual action `pypi-publisher-core` remains pending.
- PyPI `nirs4all-providers`: missing; manual action `pypi-publisher-providers` remains pending.
- R-universe `nirs4all`: still stale at `0.2.0` and still reports the old `nirs4all-lite` source while the config repo points to `nirs4all-core`; manual action `runiverse-core-rebuild` remains pending.

## Decisions

- No production release was made for `nirs4all` Python or `nirs4all-studio`.
- The UI showcase is served from GitHub Pages project path until the dedicated subdomain is intentionally enabled later.
