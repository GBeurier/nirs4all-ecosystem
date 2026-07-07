# Wave 8Z - Multisource Python Rerun Parity

Date: 2026-07-08

Owner: Codex main agent

## Scope

- Promoted `e2e-multisource-branching-stacking-replay` `python_rerun_pipeline` from contract to strict.
- Added a Python reopen/rerun ledger over the persisted multisource stacking replay manifest.
- Kept `nirs4all-ui` and `nirs4all-io` untouched because both have active dirty work from other agents.

## Files Modified

- `nirs4all/tests/e2e/test_multisource_stacking_replay.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_8Z_MULTISOURCE_PYTHON_RERUN_PARITY.md`

## Tests Run

- `cd nirs4all && python3.11 -m ruff check tests/e2e/test_multisource_stacking_replay.py`
- `cd nirs4all && PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_multisource_stacking_replay.py --artifacts-dir=/tmp/n4a-multisource-rerun`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `cd nirs4all-ecosystem && python3.11 -m pytest tests/test_e2e_scenarios.py -q`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-multisource-rerun-evidence run e2e-multisource-branching-stacking-replay --execute`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-multisource-rerun-evidence evidence --scenario e2e-multisource-branching-stacking-replay --json`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q`

## Decisions

- The rerun ledger uses `schema_version=n4a.e2e.python_rerun_pipeline.v1`.
- It verifies manifest reopen, pipeline hash, branch hash, fold hash, finite predictions, prediction/target vector identity, and score deltas.
- The remaining multisource strictness gap is still native vector-level prediction parity; this lane does not claim to solve the existing native prediction-table schema/array coverage limitation.

## Risks

- This closes the Python rerun phase only. Native prediction vector parity remains a separate contract-level parity-check debt.
- Full parity was not launched; this was a targeted E2E batch consistent with the current full parity policy.
