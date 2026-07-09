# WAVE 10AC - core multimodal runtime dependency gate

Date: 2026-07-09

## Scope

Fix the strict cross-language E2E blocker from GitHub run `28985357809` for
`e2e-multimodal-python-r-wasm-roundtrip`.

## Files changed

- `nirs4all-core/scripts/e2e/run_multimodal_roundtrip.py`
- `nirs4all-core/tests/test_run_multimodal_roundtrip_env.py`
- `.github/workflows/cross-language-e2e.yml`
- `tests/test_e2e_scenarios.py`
- `nirs4all-core` submodule pin

## Decision

The public package manifests were already correct: R declares `jsonlite` and
`yaml`, and the WASM package declares `yaml`. The failure was an execution
environment issue:

- the multimodal runner isolated `R_LIBS`/`R_LIBS_USER` to the scenario library,
  hiding preinstalled CRAN imports during `R CMD INSTALL`;
- the ecosystem workflow did not run `npm ci` for
  `nirs4all-core/bindings/wasm` before importing the source binding in Node.

The fix keeps the scenario R library first while preserving pre-existing R
library paths, and prepares the core WASM package explicitly in the strict E2E
workflow.

## Validation

- `nirs4all-core`: `python3.11 -m pytest tests/test_run_multimodal_roundtrip_env.py -q` -> 5 passed.
- `nirs4all-core`: `npm --prefix bindings/wasm ci --no-audit --no-fund` -> OK.
- `nirs4all-core`: `npm --prefix bindings/wasm run test:js` -> 17 passed.
- `nirs4all-core`: `node bindings/wasm/node_modules/typescript/bin/tsc --project bindings/wasm/tsconfig.typecheck.json` -> OK.
- `nirs4all`: `pytest tests/e2e/test_multimodal_roundtrip.py::test_generate_oracle` -> passed.
- `nirs4all-core`: `scripts/e2e/run_multimodal_roundtrip.py --workspace-root /home/delete/nirs4all --artifacts-dir /tmp/n4a-e2e-multimodal-fix/multimodal-roundtrip` -> `status=passed`.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate` -> OK.
- `nirs4all-ecosystem`: `pytest tests/test_e2e_scenarios.py tests/test_gitmodules_topology.py` -> 134 passed.

## Risks

- The full ready-scenario GitHub run still needs to be relaunched on the new
  ecosystem head. Local targeted execution proves the previously failing
  multimodal R/WASM step.
- Local `npm test` through the shell `tsc` shim can fail on this WSL PATH with
  `Permission denied`; the equivalent `node .../typescript/bin/tsc` command
  passed.
