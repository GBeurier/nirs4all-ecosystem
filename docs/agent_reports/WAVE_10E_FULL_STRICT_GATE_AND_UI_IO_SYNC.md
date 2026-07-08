# Wave 10E - Full Strict Gate And UI/IO Sync

Date: 2026-07-08

## Scope

- Accepted the integrated `nirs4all-ui` head `90cf1d6` as pushed and published.
- Accepted the `nirs4all-io` head `9de9b42` as pushed, with the delivered change scoped to the web demo component.
- Audited the then-current three remaining hybrid E2E scenarios with parallel read-only agents.
- Added an explicit full-strict coverage gate to avoid treating ready hybrid scenarios as full parity release evidence.
- Superseded note: the formats/IO/datasets/methods scenario was later promoted to strict by adding a real nirs4all-core client-side WASM import over the assembled dataset ledger. The remaining full-strict blockers are now multimodal and multisource only.

## Agent Reviews

Three parallel agents reviewed disjoint strictness gaps:

- Multimodal: current evidence is strict only for a dense fused-matrix proxy. A strict claim still requires native source-aware multimodal runtime evidence and Web/Studio reuse over the same multimodal hashes.
- Multisource: current evidence is strict for deterministic duplication-branch stacking. A strict claim still requires native `by_source + merge: predictions + meta-model`, byte-pinned external multisource catalog evidence, and non-Python replay evidence.
- Formats/IO/datasets/methods: current native/Python/R/WASM parity is strict for the deterministic fixture/oracle. At this point in the wave, a strict claim still required WASM/core/web consumption of the same assembled dataset ledger; Rust remained archive-only and not a release target. This specific gap is now closed by `web-core-pipeline-import.json`.

Decision at the time: do not promote any of the three scenarios to `strict` until those structural gaps are implemented. A label-only promotion would be false release evidence. Later work implemented the formats/IO/core-WASM evidence rather than relabeling it.

## Changes

- `scripts/n4a_e2e_scenarios.py`
  - Added `debt_summary.full_strict_ready`.
  - Added `debt_summary.full_strict_blockers`.
  - Added `debt_summary.non_strict_scenarios`.
  - Added `coverage --require-full-strict`, which exits non-zero while hybrid evidence, strictness gaps, V1 contract phases, V1 gap phases, non-numeric strict checks, or missing strict parity checks remain.
  - Added a "Full Strict Gate" section to the generated markdown coverage board.
- `tests/test_e2e_scenarios.py`
  - Initially locked the expected state as `full_strict_ready=false`, `hybrid:3`, `strictness_gaps=3`, `v1_contract_phases=2`; later updated to `hybrid:2`, `strictness_gaps=2`, `v1_contract_phases=1` after the formats/IO/core-WASM artifact landed.
  - Added a regression test that `coverage --require-full-strict` fails in the current state.

## Validation

- `python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - Result: `129 passed`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
  - Result: `11/11 scenarios; ready=11 blocked=0`
  - Full strict gate: `false`
  - Current blockers after the formats/IO/core-WASM promotion: `non_strict_evidence_levels=hybrid:2`, `strictness_gaps=2`, `v1_contract_phases=1`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  - Expected failure: exit code `1`

## Remaining Risk

The gate does not implement the remaining native multimodal and multisource `by_source` work. It makes the remaining debt explicit and machine-enforceable so a release candidate cannot accidentally claim full strict parity while these gaps remain.
