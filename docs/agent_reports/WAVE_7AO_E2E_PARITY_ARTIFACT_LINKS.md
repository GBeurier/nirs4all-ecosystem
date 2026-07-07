# Wave 7AO - E2E parity artifact links

Date: 2026-07-07T07:29:03Z

## Scope

- Hardened `nirs4all-ecosystem` cross-language E2E contracts without touching `nirs4all-ui` or `nirs4all-quality`.
- Kept the suite at 11 hybrid scenarios; no strictness gap was hidden or promoted.
- Did not run full parity. This batch only validates contracts and existing artifact evidence.

## Changes

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Added explicit `artifacts` links to every `parity_checks` entry.
  - Strict checks now point only at JSON evidence ledgers, not screenshots or ZIPs.
- `scripts/n4a_e2e_scenarios.py`
  - Requires every parity check to declare artifact evidence.
  - Requires strict parity checks to use JSON evidence artifacts.
  - Verifies parity-check artifacts are declared scenario artifacts and are produced by a step.
- `tests/test_e2e_scenarios.py`
  - Added guard tests for missing strict artifacts, non-JSON strict artifacts, and parity artifacts outside the scenario artifact set.
  - Updated synthetic manifest tests for the stronger parity-check artifact contract.
- `docs/CROSS_LANGUAGE_E2E.md`
  - Documented the new parity-check artifact rule and its relation to `evidence` verification.

## Validation

- `python3 scripts/n4a_e2e_scenarios.py validate`
  - OK: 11 cross-language E2E scenarios.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json`
  - `scenario_count=11`, `ready_count=11`, `blocked_count=0`, `evidence_levels={"hybrid": 11}`.
  - Debt remains visible: `strictness_gap_count=12`, `parity_check_evidence_levels={"contract": 8, "strict": 16}`.
  - `e2e-multimodal-python-r-wasm-roundtrip` remains the only scenario without a strict parity check.
- `python3 -m pytest -q tests/test_e2e_scenarios.py`
  - 104 passed.
- `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --json`
  - 11 verified scenarios, 49 verified artifacts, 0 failures.
- `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --max-age-seconds 14400`
  - Expected stale-local-artifact failure: only `e2e-core-ui-custom-app-host` is fresh; other checked artifacts are around 65h old.
- `git diff --check`
  - OK.

## Risks / Remaining Work

- This is stronger contract/evidence validation, not a fresh execution of all long-running E2E commands.
- The suite remains hybrid. Full strict parity still requires reducing the 12 strictness gaps and promoting contract/gap V1 phases only after runtime evidence exists.
- The local artifact evidence was verified without a freshness window. The 4h freshness gate is currently stale for most scenarios; use `--max-age-seconds` only after a fresh `run-ready --execute` batch when cutting final release heads.
