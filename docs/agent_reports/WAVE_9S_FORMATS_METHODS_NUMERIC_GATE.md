# WAVE 9S - Formats/IO/Datasets/Methods numeric gate

Date: 2026-07-08

## Scope

- Tightened `e2e-formats-io-datasets-methods-language-bindings` artifact validation.
- Kept the scenario hybrid: native/Python/R/WASM methods parity is strict over the shared methods orchestrator ledger; Web/core pipeline import over the assembled formats/IO dataset ledger is still contract-only; Rust remains archived/non-release evidence.
- Did not touch `nirs4all-ui`, `nirs4all-datasets` web work, `nirs4all-drafts`, or `nirs4all-lab`.

## Files Modified

- `nirs4all-methods/scripts/e2e/cross_binding_methods_parity.py`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/agent_reports/WAVE_9S_FORMATS_METHODS_NUMERIC_GATE.md`

## Decisions

- Added top-level numeric summaries to methods E2E JSON so ecosystem gates can assert real parity fields instead of only non-empty arrays.
- Rejected non-standard JSON `NaN` by writing artifacts with `allow_nan=False`; external reference `NaN` cells are normalized to `null`.
- Required C++/Python/R prediction payload hashes to match, plus finite WASM RMSE metrics below the declared tolerance.
- Removed the stale strict-numeric-proof exemption for this scenario after review found it no longer applied.

## Review

- Claude Code read-only review was launched twice. It identified the stale formats/methods exemption as a concrete issue before hitting/approaching turn limits; Codex fixed and revalidated it.
- No `nirs4all-lite` alias was introduced in touched files.

## Tests

- `python3.11 -m py_compile scripts/e2e/cross_binding_methods_parity.py` in `nirs4all-methods`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py` in `nirs4all-ecosystem` -> 128 passed
- `python3.11 scripts/n4a_e2e_scenarios.py validate` in `nirs4all-ecosystem` -> OK, 11 scenarios
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-coverage-formats-after.json --markdown-out /tmp/n4a-e2e-coverage-formats-after.md` -> 11/11 ready, strict non-numeric checks 3
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-formats-methods-next run --execute e2e-formats-io-datasets-methods-language-bindings`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-formats-methods-next evidence --scenario e2e-formats-io-datasets-methods-language-bindings --json` -> verified

## Risks

- WASM methods parity now uses the orchestrator ledger fixture, but it is still not a Web UI import/rerun gate; the scenario's `strictness_gaps` states that explicitly.
- The Rust binding remains archived and is only audited as non-release evidence.
