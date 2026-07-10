# Wave 9ZH - Web UI 0.1.11 vendor sync and custom-host evidence

Date: 2026-07-10

## Scope

- Synchronized `nirs4all-web/studio-lite` with the published `nirs4all-ui@0.1.11` package.
- Updated the custom-host E2E contract to require `nirs4all-ui` `0.1.11` for published-package smoke evidence.
- Re-executed the focused `e2e-core-ui-custom-app-host` runtime scenario instead of the full long parity batch.
- Regenerated the committed runtime evidence ledger after the scenario manifest hash changed.

## Files / repos changed

- `nirs4all-web`
  - Commit: `b62d408 chore(web): sync ui vendor to 0.1.11`
  - Updated `studio-lite/vendor/nirs4all-ui` from `0.1.10` to `0.1.11`.
  - Added the vendored `nirs4all-quality` brand assets and brand registry surface.
  - Updated `studio-lite/scripts/smoke-published-custom-host.mjs` default published UI version to `0.1.11`.
- `nirs4all-ecosystem`
  - Updated `docs/contracts/e2e/cross-language-scenarios.n4a.json` custom-host published package command to `N4A_PUBLISHED_NIRS4ALL_UI_VERSION=0.1.11`.
  - Updated `scripts/n4a_e2e_scenarios.py` and `tests/test_e2e_scenarios.py` required evidence fields for `published-custom-host.json`.
  - Regenerated `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`.
  - Updated the `nirs4all-web` submodule pointer.

## Validation

- `nirs4all-web/studio-lite`
  - `npm run check:ui-shim`
  - `npm run smoke:shared-ui-contract`
  - `npm run test:client-only`
  - `npm run typecheck`
  - `npm test`: 24 files / 149 tests passed.
  - `NIRS4ALL_METHODS_ABI_REQUIRED=1 NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1 npm run validate:catalog`
  - `npm run build`
  - `npm run build:single`
- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py run e2e-core-ui-custom-app-host --execute`
  - `python3 scripts/n4a_e2e_scenarios.py evidence --scenario e2e-core-ui-custom-app-host --max-age-seconds 14400`
  - `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_e2e_scenarios.py`
  - `python3 scripts/n4a_e2e_scenarios.py validate`
  - `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  - `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Runtime evidence refreshed

- `e2e-core-ui-custom-app-host`: verified fresh with 9 artifacts and 0 failures.
- `published-custom-host.json`: `status=passed`, `nirs4all_version=0.3.9`, `nirs4all_ui_version=0.1.11`, `nirs4all_methods_version=1.0.9`.
- The committed ledger still covers 11/11 scenarios and 71 artifacts; only the custom-host proof hash and manifest hash changed.

## Decisions

- Did not run the full parity batch; this wave intentionally refreshes the core+UI custom-host runtime evidence requested by the goal.
- Kept `nirs4all-web` package version at `0.1.6`; this repo already tracks Pages as the deployed runtime surface and had commits ahead of the latest GitHub release before this sync. Version guard still accepts this posture.

## Risks / follow-up

- The full fresh runtime evidence gate remains incomplete: only the scheduled cluster smoke and this custom-host scenario are fresh under the 4-hour evidence window.
- The broader full Python/reference parity batch remains deferred until a larger batch, per maintainer instruction.
