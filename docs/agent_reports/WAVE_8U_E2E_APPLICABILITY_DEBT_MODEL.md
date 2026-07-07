# Wave 8U - E2E Applicability Debt Model

Date: 2026-07-07

## Scope

- Clarify the cross-language E2E debt board by separating real implementation
  gaps from V1 phases that are deliberately outside a scenario lane.
- Keep the 11-scenario orchestration unchanged and do not run the long full
  parity suite in this small cockpit/e2e bookkeeping batch.
- Do not touch `nirs4all-ui`, which still has concurrent uncommitted quality
  work in the sibling checkout.

## Files Modified

- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Decisions

- Added a V1 phase status `not_applicable`.
- `gap` now means missing evidence that belongs to the scenario objective.
- `not_applicable` requires an `applicability` explanation, cannot carry a
  `gap`, and cannot carry artifacts.
- The debt board now reports `v1_not_applicable_phases` separately from true
  `v1_gap_phases`.
- Web and papers surfaces cannot mark their required phases as
  `not_applicable`: `web`/`web_results` requires applicable `wasm_web_reuse`,
  and `papers` requires non-gap coverage for `papers_export`.

## Result

- Scenario count remains `11/11`.
- Readiness remains `ready=11`, `blocked=0`.
- Strictness gaps remain `12`.
- V1 contract phases remain `10`.
- True V1 gap phases drop from `31` to `6`.
- V1 not-applicable phases are now explicit at `25`.

## Tests Run

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-coverage-na.json --markdown-out /tmp/n4a-e2e-coverage-na.md`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 -m pytest -q tests/test_release_lock.py tests/test_e2e_scenarios.py tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py`
- `python3.11 -m pytest -q`
- `git diff --check`

## Risks

- This is a reporting/contract precision change, not new runtime parity
  execution.
- The six remaining V1 gaps are still real missing evidence and must not be
  described as solved.
- The manifest JSON was regenerated in normalized multi-line form, making the
  diff larger than the semantic change.

## Review

- Codex explorer `Pauli`: found that `not_applicable` could bypass required
  Web/papers phase checks. Fixed before commit with explicit validator checks
  and mutation tests.
