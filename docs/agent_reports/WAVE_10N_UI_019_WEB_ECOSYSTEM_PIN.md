# WAVE 10N - UI 0.1.9 Web/Ecosystem Pin

Date: 2026-07-08

## Scope

Propagate the published `nirs4all-ui@0.1.9` asset/component package into the
client-side custom-host evidence train:

- `nirs4all-web` now vendors the `0.1.9` UI shim and runs the published
  custom-host smoke against `nirs4all-ui@0.1.9`;
- `nirs4all-ecosystem` pins `nirs4all-ui@9b60bb0` and
  `nirs4all-web@4539f31`;
- the cross-language scenario contract expects the new published UI package.

## Files Modified

- `nirs4all-web/studio-lite/vendor/nirs4all-ui/**`
- `nirs4all-web/studio-lite/package-lock.json`
- `nirs4all-web/studio-lite/scripts/smoke-published-custom-host.mjs`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/nirs4all-ui` submodule
- `nirs4all-ecosystem/nirs4all-web` submodule

## Tests Run

- `nirs4all-web/studio-lite`: `npm run check:ui-shim`
- `nirs4all-web/studio-lite`: `npm run smoke:custom-app-host`
- `nirs4all-web/studio-lite`: `npm run smoke:custom-app-host-template`
- `nirs4all-web/studio-lite`: `npm run smoke:shared-ui-contract`
- `nirs4all-web/studio-lite`: `npm run smoke:published-custom-host`
- `nirs4all-web/studio-lite`: `npm run typecheck`
- `nirs4all-web/studio-lite`: `npm run test`
- `nirs4all-web/studio-lite`: `npm run build`

## Decisions

- Keep `nirs4all-web` on the vendored UI shim for its static GitHub Pages app,
  but require the downstream published-package smoke to prove the same custom
  host can consume public `nirs4all` and `nirs4all-ui` packages.
- Treat historical `0.1.8` wave reports as immutable evidence and update only
  live contracts, tests, scripts and pins.

## Risks / Follow-Up

- The full browser smoke suite and full cross-language `run-ready --execute`
  gate remain deferred until the next larger batch.
- The cockpit must still be refreshed after this web/ecosystem propagation so
  the public dashboard no longer reports the UI `0.1.8` train.
