# WAVE 10BG - Scheduled cluster E2E runtime smoke

Date: 2026-07-09T20:20:00Z

Lane: cross-language E2E runtime evidence.

## Scope

Added a scheduled runtime smoke to the central cross-language E2E workflow
without changing the push/PR behavior or launching the full parity suite.

The scheduled lane executes only:

- `e2e-cluster-dag-rights-client-core`

This scenario was selected because it is currently ready, has strict JSON
artifact evidence, covers cluster scheduler rights plus core handoff, and avoids
the R/WASM/browser/toolchain surfaces that make the full suite expensive and
more runner-sensitive.

## Files changed

- `.github/workflows/cross-language-e2e.yml`
  - Added a weekly schedule.
  - Added schedule-only Python dependency installation for `nirs4all` and
    `nirs4all-cluster`.
  - Added schedule-only execution and evidence verification for the cluster
    smoke scenario.
  - Added a dedicated scheduled runtime evidence artifact upload.
- `docs/CROSS_LANGUAGE_E2E.md`
  - Documented the planning/runtime split and the new scheduled smoke.
- `tests/test_e2e_scenarios.py`
  - Locked the workflow contract so schedule stays single-scenario and does not
    run `run-ready` or the full evidence ledger gate.

## Decisions

- Push and pull-request runs remain manifest/contract planning gates.
- Scheduled runs skip the full-suite planning step and execute only the cluster
  smoke scenario.
- Full runtime execution remains manual via `workflow_dispatch execute=true`.
- Full evidence-ledger checking remains a manual full-suite gate after large
  integration batches.
- No full Python parity run was launched in this batch.

## Risks

- The scheduled smoke still installs the Python reference library and cluster
  dependencies, so it can catch dependency drift that contract-only CI cannot.
- It does not prove R/WASM/Web/papers/repository/save-converter parity; those
  remain covered by the existing manual full-suite scenarios and evidence
  ledger.
