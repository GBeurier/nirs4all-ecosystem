# Wave 4CW — Web/WASM Strict Smoke Evidence

Date: 2026-07-04

## Scope

- Lane H / C: Web/WASM artifact smoke evidence.
- Repos changed: `nirs4all-web`, `nirs4all-ecosystem`.
- Production hold respected: no `nirs4all-studio` release or production switch.

## Changes Integrated

- `nirs4all-web@73b9184`
  - `studio-lite/tests/smoke-evidence-helpers.mjs`
    - Shared helpers for SHA-256 artifacts, runtime/resource hashes, UI panel assertions, and prediction comparison.
  - `studio-lite/tests/pipeline-repository-smoke.mjs`
    - Records `status: passed`, console/fetch/dialog counts, pipeline artifact SHA-256, runtime resource hashes, and source-vs-imported prediction comparison.
  - `studio-lite/tests/n4a-roundtrip-smoke.mjs`
    - Records `.n4a` SHA-256, runtime evidence, prediction panel evidence before/after import, and displayed prediction comparison.
- `nirs4all-ecosystem`
  - `nirs4all-web` gitlink moved to `73b9184`.
  - `e2e-wasm-open-repo-pipeline-alt-dataset` upgraded from `contract_smoke` to `hybrid`.

## Verification

From `nirs4all-web/studio-lite`:

- `node --check tests/smoke-evidence-helpers.mjs tests/pipeline-repository-smoke.mjs tests/n4a-roundtrip-smoke.mjs` equivalent split commands — OK.
- `ARTIFACTS_DIR=/tmp/n4a-web-smoke-artifacts npm run smoke:artifacts` — 2/2 smokes passed.
- `npm run typecheck` — OK.
- `npm run test` — 22 files / 137 tests passed.
- `npm run build` — OK, existing chunk-size warnings only.

Artifact spot check:

- `pipeline-repository-smoke.json`: `status=passed`, `console_error_count=0`, `failed_request_count=0`, `unexpected_dialog_count=0`, `prediction_comparison.max_abs_delta=0`.
- `predict-artifact-smoke.json`: `status=passed`, `console_error_count=0`, `prediction_comparison.max_abs_delta=0`.

## Remaining Gaps

- This is now strict for source-vs-imported Web/WASM preservation.
- It still does not assert Python-vs-WASM numeric parity; that remains covered by the core/provider execution gate and future full parity batches.
