# Custom App Host E2E Audit

Date: 2026-07-07

## Scope

Audit and tighten the `nirs4all-ecosystem` cross-language/custom-app-host E2E planning and evidence contracts without running full parity.

## Audit result

- The ecosystem manifest still defines 11 complex scenarios and `coverage --json` reports all 11 as ready.
- Requested suite coverage is present across the current scenario set:
  - custom app host mixing `nirs4all-core` + `nirs4all-ui` + `nirs4all-web`: `e2e-core-ui-custom-app-host`
  - R/Python/WASM/Web custom-host path: `e2e-core-ui-custom-app-host`
  - repository + papers + workspace-save provenance: `e2e-python-reopen-paper-repository-refit`
  - datasets/IO/repository handoff: `e2e-dataset-provider-repository-roundtrip`
  - multimodal: `e2e-multimodal-python-r-wasm-roundtrip`
  - multisource: `e2e-multisource-branching-stacking-replay`
  - save/predictions/web rendering: `e2e-converter-legacy-save-predictions-web`

## Files changed

- `scripts/n4a_e2e_scenarios.py`
  - Added a custom validator for `e2e-core-ui-custom-app-host`.
  - The validator now rejects regressions where the scenario drops:
    - the required custom-host artifact set,
    - the expected three-step host flow,
    - strict prediction parity evidence,
    - strict runtime-contract evidence for `serialized_model_predict_surfaces` / `predictPortablePipeline`,
    - shared `nirs4all-ui` render evidence,
    - or the intended custom-host V1 phase statuses.
- `tests/test_e2e_scenarios.py`
  - Extended the positive custom-host audit to assert the runtime-contract artifact/check.
  - Added focused negative tests for missing runtime-contract evidence, missing shared-UI evidence, and weakened custom-host parity phase.

## Tests run

- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json`

## Decisions

- Kept the existing 11-scenario manifest unchanged; the gap was in contract enforcement, not scenario count.
- Tightened only ecosystem-side planning/evidence validation. No parity workloads or sibling repos were touched.

## Risks

- The custom-host validator is intentionally opinionated about the current artifact names, step ids, and phase statuses. If the scenario is redesigned later, the validator and its tests will need to be updated together.
- Existing suite debt is unchanged: multimodal still has no strict parity check, and several V1 phases remain `contract`/`gap` by design.
