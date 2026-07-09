# WAVE 10AO - E2E gate scope clarity

Date: 2026-07-09

## Scope

- Repository: `nirs4all-ecosystem`
- Lane: cross-language E2E orchestration and release-gate reporting
- Goal: make the E2E board explicit about the difference between manifest strictness and fresh runtime parity evidence, without launching the long full parity batch.

## Files changed

- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/contracts/cutover/readiness-matrix.n4a.json`
- `tests/test_cutover_state_gate.py`
- `docs/CROSS_LANGUAGE_E2E.md`

## Decisions

- Added `gate_scope` to the coverage JSON report.
- Kept `full_strict_ready` as a manifest/contract readiness signal.
- Made coverage text and Markdown say `runtime_evidence_checked=false`.
- Kept fresh runtime proof tied to `evidence` / `evidence-ledger`, optionally with `--max-age-seconds`.
- Made `full_strict_ready` fail on remaining `contract` parity checks.
- Promoted two runtime/descriptor checks to strict because their artefacts already carry numeric comparison ledgers.
- Moved the archived Rust wrapper status out of `parity_checks`; it remains non-release-target evidence through the scenario artefact requirements.
- Regenerated `latest-runtime-evidence-ledger.n4a.json` so it records `contract_parity_checks=0`.
- Added the required cutover gate `e2e_runtime_evidence_fresh`.
- Added the required readiness blocker `LOCK-E2E-FRESH-001` in `blocked` state until a fresh executed runtime batch exists.
- Did not run the long executed full parity batch in this wave.

## Validation

- `python3.11 -m pytest -q tests/test_e2e_scenarios.py` -> 134 passed.
- `python3.11 -m pytest -q tests/test_cutover_state_gate.py tests/test_e2e_scenarios.py` -> 139 passed.
- `python3.11 -m pytest -q` -> 170 passed.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage` -> 11/11 ready, explicit `gate scope`, `full_strict_ready=true`, `contract_parity_checks=0`.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict` -> passed.
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json` -> 11/11 scenarios verified, 70 artifacts, 0 failures.
- `python3.11 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all validate` -> passed.
- `python3.11 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all readiness` -> reports `LOCK-E2E-FRESH-001` as required/blocked.

## Agent review

- Cockpit read-only agent confirmed manual actions/blockers are rendered at the bottom of the dashboard and counters separate `blocker` from `important`.
- No cockpit patch was needed in this wave.

## Risks

- This change does not replace a fresh executed full parity run.
- No `parity_checks` entry remains at `contract` level.
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --check --max-age-seconds 14400 --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json` is expected to fail until the next executed batch refreshes the artifacts.
- Python `nirs4all` and Studio production remain held until fresh runtime evidence and manual Windows Studio smoke are complete.
