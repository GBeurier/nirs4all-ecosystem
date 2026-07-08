# Wave 9F - Strict Numeric Proof Guard

Date: 2026-07-08

Owner: Codex coordinator

Parallel review:

- Claude Opus/max read-only audit on `nirs4all-core` native multisource replay.
- Claude Opus/max read-only audit on ecosystem strict-proof validator reached its turn budget without a usable report.

Scope:

- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

Changes:

- Added a validator guard: new strict parity checks must have numeric evidence requirements unless explicitly listed as current strict non-numeric debt.
- Added coverage JSON/Markdown fields for `strict_non_numeric_checks`.
- Added tests locking the current four strict non-numeric exceptions and rejecting new unlisted strict boolean/structural checks.
- Updated E2E docs to remove stale `v1_gap_phases` wording and document strict numeric exceptions.

Tests:

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-coverage-numeric.json --markdown-out /tmp/n4a-e2e-coverage-numeric.md`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`

Decisions:

- Did not promote multisource native vector parity to strict yet.
- Core audit found that `nirs4all-core/scripts/e2e/run_multisource_stacking_replay.py` can re-key existing vector parity fields, but the native meta-model prediction vector is not currently emitted (`arrays_present=false`, `array_rows=0`), so `compared_rows > 0` would red-gate honestly.
- Kept the current four structural strict checks visible as debt instead of weakening tests or inflating tolerance.

Risks:

- Coverage now reports `strict_non_numeric_checks=4`; this is an exposed debt metric, not a regression.
- Closing the multisource item requires upstream native/dag-ml result emission work before the ecosystem contract can require `prediction_vector_parity.compared_rows > 0`.
