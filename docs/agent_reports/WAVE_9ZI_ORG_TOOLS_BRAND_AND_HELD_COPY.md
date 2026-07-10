# Wave 9ZI - Org tools brand asset and held-copy cleanup

Date: 2026-07-10

## Scope

- Closed the remaining public-site audit items for `nirs4all-org` after the UI/core/provider branding wave.
- Added a dedicated `nirs4all-tools` brand kit to the deployed static site assets.
- Removed the remaining public wording that described Studio RC artifacts as "held" while keeping the production-vs-RC separation explicit.
- Updated the ecosystem submodule pin for `nirs4all-org`.

## Files / repos changed

- `nirs4all-org`
  - Commit: `958d9eb docs(site): add nirs4all-tools brand asset`
  - Added `assets/brand/nirs4all-tools/` with icon, raster, favicon, horizontal, stacked, dark, and OG assets.
  - Updated `index.html` ecosystem logo mapping for `nirs4all-tools`.
  - Updated `open-source-nirs-tools.html` to use the dedicated tools icon.
  - Updated `assets/brand/README.md` and `assets/_chart/Logos.txt` with the `n4t` tools brand entry.
- `nirs4all-ecosystem`
  - Updated `nirs4all-org` submodule to `958d9eb`.
  - Added this coordination report.

## Validation

- `nirs4all-org`
  - `git diff --check`
  - Static asset reference check for `index.html` and `open-source-nirs-tools.html`.
  - Public wording check confirmed absence of `release line stays held`, `held Studio`, `production held`, `held outside`, and `Release bundles`.
  - Local version-guard equivalent: `package.json` version `1.0.5` is not ahead of latest tag `v1.0.5`.
  - Visual inspection of `assets/brand/nirs4all-tools/og.png`.
  - GitHub `version-guard`: success on `958d9eb`.
  - GitHub Pages deployment: success after the push.
  - Public checks:
    - `https://nirs4all.org/` contains `assets/brand/nirs4all-tools/icon.svg` and no old held-copy wording.
    - `https://nirs4all.org/open-source-nirs-tools.html` contains `assets/brand/nirs4all-tools/icon.svg` and no old held-copy wording.
    - `https://nirs4all.org/assets/brand/nirs4all-tools/icon.svg` returns the slate tools mark.

## Decisions

- Used a neutral slate tools color `#475569` with stacked mark `n4t`, distinct from existing `nirs4all-core`, `nirs4all-ui`, and `nirs4all-providers` colors.
- Kept production Studio downloads visible, but described final V1 RC app artifacts as separate from the aggregate publication batch instead of "held".
- Did not force the local `assets/_chart/build/` generator into Git; that directory is intentionally ignored in `nirs4all-org`. The generated deployable brand assets are committed.

## Risks / follow-up

- This wave does not run long full parity gates; it is site/brand/documentation scoped.
