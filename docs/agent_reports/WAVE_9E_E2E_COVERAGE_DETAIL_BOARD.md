# Wave 9E - E2E Coverage Detail Board

Date: 2026-07-08

Owner: Codex coordinator

Scope:

- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

Changes:

- Added per-scenario coverage details to the E2E coverage JSON report.
- Added a Markdown strictness gap detail table so each hybrid scenario exposes its remaining non-strict evidence.
- Added regression tests for the multimodal scenario debt detail and generated Markdown output.
- Documented that `11/11 ready` means the scenario contracts are coherent and runnable, not full strict ecosystem parity.

Tests:

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-coverage-details.json --markdown-out /tmp/n4a-e2e-coverage-details.md`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`

Decisions:

- Kept all existing strictness gaps visible instead of promoting hybrid/contract evidence to strict parity without new runtime proof.
- Did not run the long full-parity suite in this small batch; it remains reserved for larger integration cuts.

Risks:

- The suite still reports `hybrid=11` and `strictness_gaps=12`; this is now more visible, not resolved.
- Runtime evidence still needs fresh execution on selected release heads before production cutover.
