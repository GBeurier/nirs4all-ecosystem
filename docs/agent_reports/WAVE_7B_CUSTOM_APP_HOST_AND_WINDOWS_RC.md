# Wave 7B — Custom App Host + Windows RC Prep

Date: 2026-07-06

## Scope

- Consolidated the new cross-language scenario `e2e-core-ui-custom-app-host`.
- Validated the reusable `nirs4all-core` + `nirs4all-ui` custom app host path in `nirs4all-web`.
- Reviewed the `nirs4all-core` WASM package-name compatibility patch.
- Reviewed the `nirs4all-studio` local Windows RC installer helper.

## Files Changed

- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-web/studio-lite/src/app/custom-app-host.contract.test.ts`
- `nirs4all-web/studio-lite/package.json`
- `nirs4all-web/studio-lite/vendor/nirs4all/package.json`
- `nirs4all-web/studio-lite/vendor/nirs4all/src/index.js`
- `nirs4all-core/bindings/wasm/src/index.js`
- `nirs4all-core/bindings/wasm/package.json`
- `nirs4all-core/bindings/wasm/package-lock.json`
- `nirs4all-core/bindings/wasm/tests/index.test.js`
- `nirs4all-core/docs/BINDINGS.md`
- `nirs4all-studio/scripts/build-local-windows-rc.cjs`
- `nirs4all-studio/scripts/build-test.cjs`
- `nirs4all-studio/package.json`
- `nirs4all-studio/docs/PACKAGING.md`
- `nirs4all-studio/docs/RELEASE_CHECKLIST.md`

## Validation

- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py coverage --json`
- `nirs4all-ecosystem`: `python3 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-custom-host run e2e-core-ui-custom-app-host --execute`
- `nirs4all-core`: `npm run test:js --prefix bindings/wasm`
- `nirs4all-core`: `npm run test:v1-surface --prefix bindings/wasm` reached the Node tests, then hit local `tsc: Permission denied`
- `nirs4all-core`: `node bindings/wasm/node_modules/typescript/bin/tsc --project bindings/wasm/tsconfig.typecheck.json`
- `nirs4all-web/studio-lite`: `npm run smoke:custom-app-host`
- `nirs4all-web/studio-lite`: `ARTIFACTS_DIR=/tmp/n4a-custom-host npm run smoke:custom-app-host`
- `nirs4all-web/studio-lite`: `npm run check:ui-shim`
- `nirs4all-web/studio-lite`: `npm run check:core-shim`
- `nirs4all-web/studio-lite`: `npm run typecheck`
- `nirs4all-web/studio-lite`: `npm test`
- `nirs4all-web/studio-lite`: `npm run validate:catalog`
- `nirs4all-web/studio-lite`: `npm run build`
- `nirs4all-web/studio-lite`: `npm run build:single`
- `nirs4all-studio`: `npm run release:smoke`
- `nirs4all-studio`: `node scripts/build-local-windows-rc.cjs --version 1.0.0-rc.1` fails intentionally on Linux/WSL
- `nirs4all-studio`: direct Node unit checks for `parseArgs`, SemVer, and WSL UNC detection

## Decisions

- Kept one custom-host scenario instead of creating a duplicate.
- The scenario is structural plus strict core-vs-Python-oracle prediction parity; the R part records binding surface participation, not full numeric R parity.
- Web remains client-side-only: the custom host test runs in Vitest against core/ui artifacts and does not start Studio or a backend.
- Studio Windows RC packaging is prepared as a local Windows command; no Linux/WSL native build artifact is produced.

## Risks

- The full cross-language E2E `run-ready --execute` gate was not run in this batch.
- Full Python-reference parity remains a later large-batch gate.
- The native Windows installer must be produced and manually inspected from a real Windows checkout.
