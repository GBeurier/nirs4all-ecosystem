# WAVE 10AQ - Web UI shim sync

Date: 2026-07-09

## Scope

- Fix the executed cross-language E2E failure in
  `e2e-python-reopen-paper-repository-refit.web-import-repository-best-pipeline`.
- Keep the fix in `nirs4all-web`, then advance the `nirs4all-ecosystem`
  submodule pointer to the published head.

## Files changed

- `nirs4all-web/studio-lite/vendor/nirs4all-ui/package.json`
- `nirs4all-web/studio-lite/package-lock.json`
- `nirs4all-ecosystem/nirs4all-web` submodule pointer

## Decision

The failing CI step was not a runtime parity regression. Python reopen,
papers export, and repository refit passed; the Web/WASM smoke stopped on
`npm run check:ui-shim` because the vendored `nirs4all-ui` package metadata
missed the upstream `@types/node` dev dependency. The first Web push exposed the
paired CI issue: `studio-lite/package-lock.json` also had to be regenerated so
GitHub `npm ci` installs the same dependency graph. The vendor shim and clean
install remain the gates: no skip, no xfail, no fallback was added.

## Tests run

- `cd nirs4all-web/studio-lite && npm run check:ui-shim`
- `cd nirs4all-web/studio-lite && npm ci --ignore-scripts`
- `cd nirs4all-web/studio-lite && npm run smoke:shared-ui-contract`
- `cd nirs4all-web/studio-lite && npm run typecheck`
- `cd nirs4all-web/studio-lite && npm run test`
- `cd nirs4all-web/studio-lite && NIRS4ALL_METHODS_ABI_REQUIRED=1 NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1 npm run validate:catalog`
- `cd nirs4all-web/studio-lite && NIRS4ALL_UI_SHIM_REQUIRED=1 npm run check:ui-shim`
- `cd nirs4all-web/studio-lite && NIRS4ALL_CORE_SHIM_REQUIRED=1 npm run check:core-shim`
- `cd nirs4all-web/studio-lite && npm run build:single`
- `cd nirs4all-web/studio-lite && npm run build`
- `cd nirs4all-web/studio-lite && npm run smoke -- rt-fallback`
- `cd nirs4all-web/studio-lite && npm run smoke:repository-best-pipeline`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py run e2e-python-reopen-paper-repository-refit --execute`

## Risk

- Low. The code change is one vendored package metadata line. The targeted
  Web/WASM repository smoke proves the scenario still imports the repository
  descriptor, uploads the 130 x 2151 dataset, executes in browser, and matches
  the Python oracle within numerical tolerance.
