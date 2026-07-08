# WAVE 10X — E2E CI Strict Runtime Prep

Date: 2026-07-09

## Scope

- Lane C/K: cross-language strict E2E parity execution and CI evidence diagnostics.
- Reproduced the `e2e-multimodal-python-r-wasm-roundtrip` failure path from GitHub Actions run `28981986806`.
- Kept the scenario strict: no skip, xfail, fallback success, or relaxed parity threshold.

## Files Modified

- `nirs4all-core/scripts/e2e/run_multimodal_roundtrip.py`
  - Adds blocker/failure runtime reasons to the final JSON summary so CI logs expose the exact missing runtime artifact.
- `nirs4all-ecosystem/.github/workflows/cross-language-e2e.yml`
  - Builds the strict `nirs4all-methods` native `libn4m` and JS/WASM artifacts before executing R/WASM parity.
  - Installs strict R dependencies used by the core R runner.
  - Enables runtime evidence upload from the hidden `.n4a-e2e-artifacts/` directory.
- `nirs4all-ecosystem/nirs4all-core`
  - Repinned to `6e06a61 test(e2e): expose multimodal runtime blockers`.

## Tests Run

- `python3.11 -m py_compile scripts/e2e/run_multimodal_roundtrip.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 -m pytest -q nirs4all/tests/e2e/test_multimodal_roundtrip.py::test_generate_oracle --artifacts-dir /tmp/...`
- `python3.11 nirs4all-core/scripts/e2e/run_multimodal_roundtrip.py --workspace-root /home/delete/nirs4all --artifacts-dir /tmp/...`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-ecosystem-selected-multimodal run e2e-multimodal-python-r-wasm-roundtrip --execute`
- `git diff --check`

## Result

- Local selected scenario now passes end to end with fresh artifacts:
  - Python oracle: passed.
  - `nirs4all-core` Python: passed.
  - R runtime: passed.
  - JavaScript/WASM runtime: passed.
  - `web-core-import.json`: passed.

## Risks / Follow-Up

- The full GitHub `cross-language-e2e` workflow must be rerun because the prior run failed before strict runtime prep existed.
- The CI runtime prep increases execution time; this is intentional for strict parity and should stay behind `execute=true`.
- Full parity remains deferred until this batch is pushed and the selected strict E2E is green on Actions.
