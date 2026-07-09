# WAVE 10AP - Contract parity closure

Date: 2026-07-09

## Scope

- Repository: `nirs4all-ecosystem`
- Lane: cross-language E2E parity gate
- Goal: remove the last `contract` parity checks without hiding non-release evidence or weakening runtime proof.

## Files changed

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `tests/test_e2e_scenarios.py`
- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/agent_reports/WAVE_10AO_E2E_GATE_SCOPE.md`

## Decisions

- Promoted the Web/WASM repository import check to `strict` because `pipeline-repository-smoke.json` already proves client-side execution and numeric prediction deltas within tolerance.
- Promoted the provider/repository Python-vs-JS/WASM loader check to `strict` because `cross-language-consumption.json` proves metadata identity plus numeric execution deltas within tolerance.
- Removed the archived Rust status from `parity_checks`; `release_target=false` and `gate=not_applicable` remain scenario evidence, but they are not a current runtime parity claim.
- Kept fresh runtime evidence as a separate cutover blocker through `LOCK-E2E-FRESH-001`.

## Validation

- `python3.11 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict` -> passed.
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json` -> 11/11 scenarios verified, 70 artifacts, 0 failures.
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py` -> 139 passed.
- `python3.11 -m pytest -q` -> 170 passed.

## Agent review

- Read-only Codex agent agreed with the split: promote the two JSON-ledger-backed runtime checks; keep archived Rust as non-release structural evidence outside parity.

## Risks

- This closes the manifest-level strict parity debt only. Fresh executed runtime parity still requires the long `execute=true` E2E batch and `evidence-ledger --check --max-age-seconds 14400`.
