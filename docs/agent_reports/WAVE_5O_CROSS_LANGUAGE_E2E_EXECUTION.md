# Wave 5O - Cross-language E2E execution

Date: 2026-07-04

## Scope

- Add the user's new requirement to the active goal: ecosystem-level orchestration of about 10 complex cross-language E2E scenarios.
- Execute the current 10-scenario E2E contract after the RTD/cockpit batch.
- Fix drift found by the E2E/Web gates without weakening tests or adding skips.
- Keep `nirs4all` Python and `nirs4all-studio` production releases untouched.

## Changes Integrated

- `GBeurier/nirs4all-web`:
  - commit `e1a4975` syncs the vendored `nirs4all-ui` shim from `nirs4all-ui`;
  - commit `361e6f8` syncs the vendored portable `nirs4all` shim from `nirs4all-core` (`0.2.3` -> `0.2.4`).

No changes were required in the E2E manifest during this wave: `docs/contracts/e2e/cross-language-scenarios.n4a.json` already declares the 10 requested complex scenarios and the runner validates exactly 10.

## Executed Scenarios

- `e2e-r-dataset-io-pipeline-save`
- `e2e-python-reopen-paper-repository-refit`
- `e2e-wasm-open-repo-pipeline-alt-dataset`
- `e2e-multimodal-python-r-wasm-roundtrip`
- `e2e-multisource-branching-stacking-replay`
- `e2e-converter-legacy-save-predictions-web`
- `e2e-dataset-provider-repository-roundtrip`
- `e2e-pipeline-generation-performance-compare`
- `e2e-cluster-dag-rights-client-core`
- `e2e-formats-io-datasets-methods-language-bindings`

## Verified Checks

- `python3 scripts/n4a_e2e_scenarios.py plan --json` -> all 10 scenarios ready locally.
- `python3 scripts/n4a_e2e_scenarios.py run-ready --execute` -> all 10 scenarios passed after the shim sync fixes.
- The integrated E2E run covered:
  - R dataset/IO reshape, R/native parity install, and saved pipeline workspace;
  - Python reopen/rerun parity plus papers/repository handoff export;
  - Web/WASM repository pipeline import, dag-ml-data materialization, CV predictions, `.n4a` roundtrip, and prediction rendering;
  - multimodal and multisource Python/native replay artifacts;
  - legacy save conversion and Web results rendering;
  - provider/repository/core descriptor roundtrip;
  - Python legacy vs dag-ml performance comparison with Web WASM execution;
  - cluster scheduler rights/core handoff;
  - formats/io/datasets/methods cross-binding parity.
- `nirs4all-web` local checks:
  - `npm run check:ui-shim` -> pass;
  - `npm run check:lite-shim` -> pass;
  - `npm run smoke:shared-ui-contract` -> `2 passed`;
  - E2E Web smokes under the ecosystem runner -> pass.
- `nirs4all-web` GitHub checks on `361e6f8`:
  - `version-guard` -> success;
  - `web-ci` -> success, including client-side-only contract, typecheck, tests, catalog validation, both shim checks, `build:single`, `build`, and browser smoke;
  - `Deploy nirs4all-web to GitHub Pages` -> success.
- Live deployment:
  - `https://web.nirs4all.org/` -> HTTP 200;
  - deployed page metadata states a single-page, in-browser/WASM app with no upload backend.

## Decisions

- The E2E goal is considered part of the active refactor objective, not a later calendar item.
- Shim drift is treated as a failing integration condition; the fix was to sync the vendored shims, not to relax checks.
- The execution did not run the full parity suite; it ran the focused cross-language E2E contract after a substantial batch, consistent with the long-runtime parity constraint.

## Risk Notes

- Several E2E scenarios are still `hybrid` and declare strictness gaps in the manifest; the E2E execution proves the current contract, not full Python-reference parity for every future production path.
- `nirs4all` Python remains on `refactor/L17-pyref` and was used as an oracle/runtime input only; no production release/tag was made for it.
- `nirs4all-studio` was not released or modified in this wave.
