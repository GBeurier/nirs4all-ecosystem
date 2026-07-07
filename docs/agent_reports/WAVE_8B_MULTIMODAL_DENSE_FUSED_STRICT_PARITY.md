# Wave 8B - Multimodal Dense-Fused Strict Parity

Date: 2026-07-07

## Scope

- Repository: `nirs4all-ecosystem`
- Files changed:
  - `docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - `docs/CROSS_LANGUAGE_E2E.md`
  - `tests/test_e2e_scenarios.py`
  - `docs/agent_reports/WAVE_8B_MULTIMODAL_DENSE_FUSED_STRICT_PARITY.md`

## Decision

Promoted `e2e-multimodal-python-r-wasm-roundtrip` from contract-only parity evidence to strict parity for the existing portable dense-fused contract.

This does not claim native source-aware multimodal runtime parity. The scenario remains `hybrid`, and the existing strictness gap for native multimodal runtime plus Web/Studio roundtrip remains visible.

## Rationale

`nirs4all-core/scripts/e2e/run_multimodal_roundtrip.py` already compares Python oracle output against R and JavaScript/WASM outputs for:

- split indices
- targets
- variant count and component count
- RMSE deltas
- prediction vector max absolute deltas
- selected component identity

The comparison is emitted in JSON artifacts, including `core-roundtrip-evidence.json` and `wasm-predictions.json`, so the E2E manifest can require strict numeric parity for the current dense-fused representation without weakening the native multimodal gap.

## Tests

Targeted tests to run after integration:

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json`
- `python3.11 -m pytest tests/test_e2e_scenarios.py`

Executed locally:

- `python3.11 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json` -> OK, 11 ready, 0 blocked, no scenario without strict parity
- `python3.11 scripts/n4a_e2e_scenarios.py coverage` -> OK
- `python3.11 -m pytest tests/test_e2e_scenarios.py` -> 114 passed
- `git diff --check -- docs/CROSS_LANGUAGE_E2E.md docs/contracts/e2e/cross-language-scenarios.n4a.json tests/test_e2e_scenarios.py` -> OK

No full parity batch was launched in this lane.

## Risks

- The scenario still does not exercise source-aware native multimodal execution.
- The scenario still does not include a Web/Studio UI roundtrip.
- R/WASM execution remains dependent on local runtime availability when the scenario is executed, not merely validated.
