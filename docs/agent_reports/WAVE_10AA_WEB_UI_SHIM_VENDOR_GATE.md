# Wave 10AA - Web UI shim vendor gate

Date: 2026-07-09

Lane: H / J, `nirs4all-web` Studio-lite client-side app consuming the shared `nirs4all-ui` package.

## Scope

- Investigated the strict cross-language E2E failure after the methods runtime gate passed.
- Confirmed the failure was limited to `nirs4all-web/studio-lite` reporting `vendor/nirs4all-ui` drift.
- Regenerated the vendored `nirs4all-ui` shim from the clean sibling `nirs4all-ui` HEAD `a12ae9d`.
- Pushed initial `nirs4all-web` commit `1e7d53f65d58cfe86df3103481ef0bce89f8110d`.
- The follow-up GitHub strict E2E reproduced an install-time blocker: the vendored
  `nirs4all-ui` `prepare` lifecycle ran during `npm ci` without the full UI build config.
- Normalized the Web vendored UI package lifecycle back to `prepack`, keeping upstream
  `nirs4all-ui` unchanged while preserving an installable client-side shim.
- Pushed follow-up `nirs4all-web` commit `c087789d92fe72f85482b80ab6701e4cc5ca356c`.
- Repinned `nirs4all-ecosystem` to that `nirs4all-web` commit.

## Files changed upstream

- `nirs4all-web/studio-lite/vendor/nirs4all-ui/package.json`
- `nirs4all-web/studio-lite/scripts/sync-ui-shim.mjs`

## Tests run

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run check:ui-shim`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm ci --no-audit --no-fund`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run typecheck`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run validate:catalog`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run test`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:/home/delete/.cargo/bin:$PATH npm run build:single`
- `git diff --check`

## Results

- `check:ui-shim` passed after vendoring.
- `npm ci --no-audit --no-fund` passed locally after normalizing the vendored lifecycle.
- TypeScript typecheck passed.
- Catalog validation passed: 64 symbols referenced, 702 exported upstream; 5 Studio flow/operator ids in sync.
- Vitest passed: 24 files, 149 tests.
- Served static build passed.
- Single-file offline build passed.

## Decisions

- Kept the change strictly to the vendored UI package metadata consumed by Web.
- Kept `nirs4all-ui` upstream `prepare` intact for real local consumers.
- Converted `prepare` to `prepack` only inside the Web shim because Web vendors `dist/`
  and must not rebuild the shared UI package during app dependency installation.
- Did not edit `nirs4all-ui` components or assets; this preserves the concurrent quality-agent work boundary.
- Preserved the client-side-only `nirs4all-web` model.

## Risks

- Browser smoke tests were not rerun locally for this metadata-only vendor sync.
- The GitHub strict E2E remains the authoritative gate because it reproduces the exact ecosystem checkout and scenario execution order.
