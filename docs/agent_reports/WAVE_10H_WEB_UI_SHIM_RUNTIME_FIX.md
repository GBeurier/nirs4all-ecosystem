# Wave 10H - Web UI shim runtime fix

Date: 2026-07-09

## Scope

- Fix the first fresh runtime E2E failure after dispatching `Cross-language E2E scenarios` with `execute=true`.
- Keep the Web app client-side-only while synchronizing its vendored `nirs4all-ui` shim with the published/shared UI source.
- Repin the ecosystem `nirs4all-web` submodule after Web CI and Pages passed.

## Root cause

Runtime E2E run `29004421709` failed in scenario `e2e-python-reopen-paper-repository-refit` during the Web/WASM import step:

```text
[sync-ui-shim] drift detected; run `npm run vendor:ui` from studio-lite.
FAILED e2e-python-reopen-paper-repository-refit.web-import-repository-best-pipeline
```

The failure was not numerical parity. It was a Web vendoring drift between `nirs4all-web/studio-lite/vendor/nirs4all-ui` and the current `nirs4all-ui` package.

## Files changed

- `nirs4all-web` submodule pointer
- `docs/agent_reports/WAVE_10H_WEB_UI_SHIM_RUNTIME_FIX.md`

## Upstream Web fix

- `GBeurier/nirs4all-web@4c9a8237086191490f55aebfd830e399609aec2c`
- Commit: `chore(studio-lite): sync vendored ui shim`
- Changed only vendored `nirs4all-ui` files in Web.
- Did not modify `nirs4all-ui` itself.

## Tests and checks

Local Web:

- `npm run check:ui-shim`
- `npm run typecheck`
- `npm run test`
- `npm run build`
- `npm run build:single`

GitHub Web:

- `version-guard` on `4c9a823`: success.
- `web-ci` on `4c9a823`: success, including client-side-only contract, typecheck, tests, catalog validation, UI/core shim checks, builds, and browser smoke.
- `Deploy nirs4all-web to GitHub Pages` on `4c9a823`: success.

## Remaining action

- Re-run the ecosystem E2E runtime dispatch on the ecosystem commit that includes this submodule repin and the runtime ledger artifact upload fix.

