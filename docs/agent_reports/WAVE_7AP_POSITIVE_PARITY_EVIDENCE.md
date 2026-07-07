# Wave 7AP - Positive parity evidence gate

Date: 2026-07-07

Scope:
- `nirs4all-ecosystem`: tightened cross-language E2E artifact validation.
- `nirs4all-tools`: added positive parity fields to the legacy converter runtime-result E2E artifact.
- `nirs4all`: added positive parity fields to the multisource stacking OOF ledger E2E artifact on `refactor/L17-pyref`.

Files changed:
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-tools/tests/e2e/test_legacy_save_predictions_web.py`
- `nirs4all/tests/e2e/test_multisource_stacking_replay.py`

Decisions:
- A JSON artifact referenced by `parity_checks[].artifacts` must now contain a recognized positive signal: passing status/result/verdict, true evidence booleans, positive row/count fields, or a finite delta within tolerance.
- Structural JSON artifacts such as pipeline descriptors, IO specs, repository indexes, and workspace manifests remain valid without adding artificial `status` fields, unless they are explicitly cited as parity evidence.
- Producer-side artifacts were fixed rather than weakening the ecosystem validator.

Validation:
- `nirs4all-ecosystem`: `python3 -m pytest -q tests/test_e2e_scenarios.py` -> 111 passed.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --json` -> 11 verified scenarios, 49 artifacts, 0 failures.
- `nirs4all-tools`: `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_legacy_save_predictions_web.py::test_convert_legacy_save --artifacts-dir=/home/delete/nirs4all/nirs4all-ecosystem/.n4a-e2e-artifacts/legacy-converter` -> 1 passed.
- `nirs4all`: `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/e2e/test_multisource_stacking_replay.py --artifacts-dir=/home/delete/nirs4all/nirs4all-ecosystem/.n4a-e2e-artifacts/multisource-stacking` -> 1 passed.
- Freshness check: `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --max-age-seconds 14400` still fails because most local artifacts are older than 4 hours; this was not bypassed.

Risks:
- Real full-run producers not exercised in this batch may still need small schema additions if they later cite structural files as parity evidence.
- `nirs4all` changes are test/evidence only and remain on the refactor branch; do not release the Python package from this branch without the separate prod validation gate.
