# Wave 4V - Studio/Web/Core/Methods/Org RC Gates And Security Refresh

Date: 2026-07-03

Coordinator: Codex parent session.

## Scope

This wave integrated the post-4U review batch from the Studio/Web/Core/Methods/Org
lanes, refreshed the aggregate release lock after retagging selected heads, and
rechecked the GitGuardian cluster alert against published refs and hidden GitHub
PR refs.

## Integrated Heads

| Repo | Branch | Commit | Tag |
| --- | --- | --- | --- |
| `nirs4all-studio` | `rc/v1-full-refactor` | `e9fa4cf` | `n4a-v1-rc1-2026.07-refactor` |
| `nirs4all-web` | `rc/v1-full-refactor` | `85dcd79` | `n4a-v1-rc1-2026.07-refactor` |
| `nirs4all-lite` / `nirs4all-core` target | `rc/v1-full-refactor-core` | `8dcf2af` | `n4a-v1-rc1-2026.07-refactor` |
| `nirs4all-methods` | `rc/v1-full-refactor` | `a24b06b` | `n4a-v1-rc1-2026.07-refactor` |
| `nirs4all-org` | `rc/v1-full-refactor` | `fd4634d` | `n4a-v1-rc1-2026.07-refactor` |

The ecosystem lock was regenerated after retagging. The lock boundary moved only
the aggregate members `nirs4all-core` and `nirs4all-methods`; Studio/Web/Org are
tracked by the surface matrix and this coordination report rather than by the
aggregate lock.

## Files Modified

- `nirs4all-studio`: `api/venv_manager.py`, `scripts/run-python.cjs`,
  `tests/conftest.py`, `tests/test_venv_manager.py`,
  `e2e/pages/settings.page.ts`.
- `nirs4all-web`: `.github/actions/nirs4all-ui-sibling/action.yml`,
  `.github/workflows/deploy-pages.yml`, `.github/workflows/web-ci.yml`,
  `studio-lite/package.json`, `studio-lite/package-lock.json`.
- `nirs4all-lite` / core target: `README.md`, `docs/RELEASE.md`,
  `bindings/wasm/tests/execution.test.js`.
- `nirs4all-methods`: `bindings/js/test/run_smoke.mjs`.
- `nirs4all-org`: `README.md`, `index.html`.
- `nirs4all-ecosystem`: `docs/contracts/release/aggregation-lock.n4a.lock.json`,
  this report, and the control board update.

## Tests And Checks

- Studio:
  - Full Playwright e2e after settings locator fix: `63 passed (13.8m)`.
  - Settings focused e2e: `11 passed (5.2m)`.
  - Backend full pytest before the final pip-error-cache refinement:
    coordinator run `2325 passed, 6 skipped`; lane report after agent fixes
    `2327 passed, 6 skipped`.
  - Final targeted runtime/venv tests after the pip-error-cache refinement:
    `7 passed, 9 warnings`.
  - `npm run lint:parallel`: passed before the final refinement.
  - Final Ruff target: `All checks passed`.
  - `npm run perf:runtime`: PASS; legacy overhead `0.011768 ms`, dag-ml
    overhead `0.080063 ms`.
- Web:
  - `npm audit --audit-level=moderate --json`: zero vulnerabilities.
  - `NIRS4ALL_UI_SHIM_REQUIRED=1 npm run check:ui-shim`: passed.
  - `NIRS4ALL_LITE_SHIM_REQUIRED=1 npm run check:lite-shim`: passed.
  - Typecheck, Vitest, catalog validation, `build`, `build:single`, normal
    smoke, and offline single-file smoke passed in the lane batch.
- Core target:
  - Python V1 surface unittest batch: `53 tests OK`.
  - WASM npm gate after clean install: `13 passed, 2 skipped`; typecheck passed.
  - `git diff --check`: passed.
- Methods:
  - `git diff --check`: passed.
  - JS/WASM smoke is now strict on missing parity fixture, but local execution
    remains blocked because no Emscripten-built `n4m.js` exists locally and
    `emcc` is unavailable.
- Org:
  - `git diff --check`: passed.
  - JSON-LD parse check: `jsonld_ok 1`.
- Ecosystem:
  - `n4a_release_lock.py validate`: passed.
  - `n4a_release_surface_matrix.py validate`: passed.
  - `pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py`:
    `16 passed`.

## Decisions

- Studio system-runtime size calculation is skipped unless the runtime root looks
  app-owned. This avoids recursive scans of `/usr` in development/system Python
  sessions.
- Studio `pip list --outdated` failures now return stale cache when available
  and cache an empty result on the first nonzero pip exit. This prevents repeated
  stacktrace spam for Debian/Ubuntu package versions such as
  `2.22.1ubuntu1.2` while preserving runtime startup.
- Web RC CI now hard-gates the vendored `nirs4all-ui` shim in addition to the
  portable core shim.
- Core WASM methods parity can be made mandatory with
  `NIRS4ALL_LITE_REQUIRE_METHODS_PARITY=1`, and the methods JS smoke now fails
  if its Python-generated parity fixture is absent.
- Org wording now treats `nirs4all-core` as the V1 RC aggregate target and
  `nirs4all-lite` as the legacy/current artifact line until the cutover is
  published. R/MATLAB claims are intentionally narrowed to subset/preview
  surfaces.

## GitGuardian Cluster Alert

The July 2, 2026 GitGuardian alert for `GBeurier/nirs4all-cluster` was
rechecked against the current remote heads and hidden PR refs:

- Published heads remain clean: `origin/main` `97b2b38` and
  `origin/rc/v1-full-refactor` `9d6ab34`.
- Hidden merged PR refs #1 and #2 from June 4, 2026 still expose placeholder CLI
  examples such as `--token dev`.
- No non-placeholder secret value was found in the local/remote audit available
  from git refs.

Interpretation: the current release refs do not expose a real token-shaped
secret. If the GitGuardian UI shows an actual non-placeholder value, rotate that
credential out of band; otherwise this is a stale/placeholder PR-ref alert to
close in GitGuardian or with GitHub support because hidden PR refs cannot be
deleted by a normal push.

## Risks

- Full Python parity was not rerun in this wave by design; this wave is a
  focused post-4U integration batch. The next full parity run should happen
  after the next larger cross-repo batch.
- Studio backend still reports six optional/environment skips in the full gate.
  They are not operator-fixture debt, but they must stay classified in the
  skip/xfail audit.
- Core/Methods JS/WASM parity execution still needs an Emscripten methods build
  or a CI environment that provides it.
- R/Rscript, Octave, MATLAB, and full non-Python dataset materialization remain
  environment gates, not proven by this local wave.
