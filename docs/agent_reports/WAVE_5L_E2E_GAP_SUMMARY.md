# Wave 5L - E2E gap summary hardening

Date: 2026-07-04

## Scope

- Make the ten complex cross-language E2E scenarios more auditable without claiming false strict parity.
- Keep hybrid/contractual gaps visible in CI plan output.

## Changes Integrated

- `GBeurier/nirs4all-ecosystem`:
  - commit `9cfd057` adds `v1_refactor_summary` to each E2E scenario plan;
  - exposes the same per-scenario summary in `run-ready` dry-run JSON;
  - replaces the unordered V1 phase set with a stable `V1_REFACTOR_PHASE_ORDER`;
  - adds tests asserting strict/contract/gap counters and representative gap phases.

## Verified Checks

- `python3 scripts/n4a_e2e_scenarios.py validate` -> `OK: 10 cross-language E2E scenarios`.
- `python3 scripts/n4a_e2e_scenarios.py plan --scenario e2e-wasm-open-repo-pipeline-alt-dataset --json` -> includes `v1_refactor_summary` with `strict: 2`, `contract: 1`, `gap: 3`.
- `python3 scripts/n4a_e2e_scenarios.py run-ready` dry-run -> `10 ready`, `0 blocked`, includes `v1_refactor_summary`.
- `pytest -q tests/test_e2e_scenarios.py` -> `40 passed`.
- `pytest -q` -> `64 passed`.
- GitHub `version-guard` on `9cfd057` -> success.
- GitHub `Cross-language E2E scenarios` on `9cfd057` -> success.

## Risk Notes

- This does not promote any hybrid scenario to strict.
- This does not launch the long full-parity batch.
- The summary is derived from the existing `v1_refactor_contract`; if a future scenario changes phase status, CI plan output will show the new count.

## Remaining Gaps

- Several scenarios still intentionally expose `gap` or `contract` phases, especially around repository forced best-refit, Python reopen/rerun over the exact same artifact, true external provider datasets, and Web/WASM reuse of selected candidate artifacts.
- Those gaps need implementation in the owning repos before the scenarios can become strict gates.
