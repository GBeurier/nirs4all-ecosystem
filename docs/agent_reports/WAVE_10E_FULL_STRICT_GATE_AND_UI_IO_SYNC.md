# Wave 10E - Full Strict Gate And UI/IO Sync

Date: 2026-07-08

## Scope

- Accepted the integrated `nirs4all-ui` head `90cf1d6` as pushed and published.
- Accepted the `nirs4all-io` head `9de9b42` as pushed, with the delivered change scoped to the web demo component.
- Audited the three remaining hybrid E2E scenarios with parallel read-only agents.
- Added an explicit full-strict coverage gate to avoid treating ready hybrid scenarios as full parity release evidence.

## Agent Reviews

Three parallel agents reviewed disjoint strictness gaps:

- Multimodal: current evidence is strict only for a dense fused-matrix proxy. A strict claim still requires native source-aware multimodal runtime evidence and Web/Studio reuse over the same multimodal hashes.
- Multisource: current evidence is strict for deterministic duplication-branch stacking. A strict claim still requires native `by_source + merge: predictions + meta-model`, byte-pinned external multisource catalog evidence, and non-Python replay evidence.
- Formats/IO/datasets/methods: current native/Python/R/WASM parity is strict for the deterministic fixture/oracle. A strict claim still requires WASM/core/web consumption of the same assembled dataset ledger; Rust remains archive-only and not a release target.

Decision: do not promote any of the three scenarios to `strict` until those structural gaps are implemented. A label-only promotion would be false release evidence.

## Changes

- `scripts/n4a_e2e_scenarios.py`
  - Added `debt_summary.full_strict_ready`.
  - Added `debt_summary.full_strict_blockers`.
  - Added `debt_summary.non_strict_scenarios`.
  - Added `coverage --require-full-strict`, which exits non-zero while hybrid evidence, strictness gaps, V1 contract phases, V1 gap phases, non-numeric strict checks, or missing strict parity checks remain.
  - Added a "Full Strict Gate" section to the generated markdown coverage board.
- `tests/test_e2e_scenarios.py`
  - Locked the current expected state: `full_strict_ready=false`, `hybrid:3`, `strictness_gaps=3`, `v1_contract_phases=2`.
  - Added a regression test that `coverage --require-full-strict` fails in the current state.

## Validation

- `python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - Result: `129 passed`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
  - Result: `11/11 scenarios; ready=11 blocked=0`
  - Full strict gate: `false`
  - Blockers: `non_strict_evidence_levels=hybrid:3`, `strictness_gaps=3`, `v1_contract_phases=2`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  - Expected failure: exit code `1`

## Remaining Risk

The new gate does not implement the missing native/multimodal/multisource/WASM work. It makes the remaining debt explicit and machine-enforceable so a release candidate cannot accidentally claim full strict parity while these gaps remain.
