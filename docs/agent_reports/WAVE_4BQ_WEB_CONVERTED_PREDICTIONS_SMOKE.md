# Wave 4BQ - Web Converted Predictions Smoke

## Scope

- Closed the Web half of `e2e-converter-legacy-save-predictions-web`.
- Kept `web.nirs4all.org` client-side only: the smoke uses the static Vite preview, reads the converted `predictions.rt_result.json`, validates the V1 result envelope, and renders browser-side result panels inside the served SPA.

## Commits Integrated

- `nirs4all-web`: `f288952 test(web): render converted prediction artifacts`
- `nirs4all-ecosystem`: this report and `cross-language-scenarios.n4a.json`.

## Manifest Changes

- `e2e-converter-legacy-save-predictions-web`
  - `convert-legacy-save` remains the `nirs4all-tools` producer of `converted-workspace.n4a.json` and `predictions.rt_result.json`.
  - `web-open-predictions` now calls `npm run build` and `npm run smoke:converted-predictions`.
  - The scenario now declares both `web-results-panels.json` and `web-results.png` as produced artifacts.

## Tests

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run build`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH ARTIFACTS_DIR=/tmp/n4a-shape-check npm run smoke:converted-predictions`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-converter-web-4bq run e2e-converter-legacy-save-predictions-web --execute`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH node --check tests/converted-predictions-render-smoke.mjs`
- `git diff --check`

## Artifacts

- `/tmp/n4a-e2e-converter-web-4bq/legacy-converter/converted-workspace.n4a.json`
- `/tmp/n4a-e2e-converter-web-4bq/legacy-converter/predictions.rt_result.json`
- `/tmp/n4a-e2e-converter-web-4bq/legacy-converter/web-results-panels.json`
- `/tmp/n4a-e2e-converter-web-4bq/legacy-converter/web-results.png`

## Risks

- The smoke validates and renders the converted result contract in a browser context, but it is not yet a full product import workflow for arbitrary saved prediction files.
- Converter parity still reports legacy replay parity as `not_run`; this lane proves deterministic migration/lowering plus Web contract rendering, not full Python replay parity.
