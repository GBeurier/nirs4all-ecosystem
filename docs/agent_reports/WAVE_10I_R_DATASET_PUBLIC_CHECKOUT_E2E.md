# WAVE 10I - R dataset public-checkout E2E closure

## Scope

Closed the remaining `e2e-r-dataset-io-pipeline-save` public-checkout blocker without xfail, skip, or
green-only fallback.

## Files changed

- `nirs4all-core/scripts/e2e/prepare_r_dataset_io_pipeline.py`
- `nirs4all-ecosystem/.github/workflows/cross-language-e2e.yml`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/nirs4all-core` submodule pin

## Decisions

- Keep the real malaria catalog dataset as the preferred local source when canonical bytes are present.
- In public checkouts where dataset bytes are intentionally gitignored, generate a tiny deterministic
  public fixture registry through `nirs4all-datasets` bootstrap/organize, then consume it through
  `DatasetProvider` and `nirs4all-io`.
- Remove the workflow allowlist for the R/dataset scenario. `allow_blocked` remains as a generic CLI
  escape hatch, but no scenario is currently allowlisted in the workflow.

## Tests

- `python3.11 -m py_compile scripts/e2e/prepare_r_dataset_io_pipeline.py`
- `NIRS4ALL_CORE_E2E_FORCE_PUBLIC_FIXTURE=1 ... prepare_r_dataset_io_pipeline.py --out /tmp/n4a-r-prepare-fallback`
- `NIRS4ALL_CORE_E2E_FORCE_PUBLIC_FIXTURE=1 python3 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-r-scenario-fallback run e2e-r-dataset-io-pipeline-save --execute`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- `python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py` -> `141 passed`

## Risks

- The committed runtime evidence ledger was refreshed locally to unblock contract tests. A fresh GitHub
  runtime execution should still be run after this commit so the ledger can be replaced by CI-produced
  public-checkout evidence if any proof hashes differ by host/runtime path.
