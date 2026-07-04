# Wave 5S - E2E strictness gate hardening

Date: 2026-07-04

## Scope

- Hardened `scripts/n4a_e2e_scenarios.py` so a scenario with `evidence_level: "strict"` cannot contain any `v1_refactor_contract` phase with `status: "gap"`.
- Reclassified the two remaining falsely strict scenarios as `hybrid`:
  - `e2e-converter-legacy-save-predictions-web`
  - `e2e-cluster-dag-rights-client-core`
- Added regression coverage in `tests/test_e2e_scenarios.py` with an explicit injected gap phase, so the test does not depend on the current manifest keeping gaps forever.

## Review

- Claude Code read-only review inspected the local diff and confirmed the central contract issue: every current scenario still has at least one V1 gap, so no scenario should currently be globally strict.
- Codex subagent review (`Arendt`) found no blocking issue. Non-blocking feedback about test fragility was addressed by forcing an explicit gap in the regression fixture.

## Tests

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 -m pytest -q tests/test_e2e_scenarios.py` (`41 passed`)
- `python3 scripts/n4a_e2e_scenarios.py plan --json`
- `git diff --check`

## Current E2E Contract State

- Scenarios: 10
- Scenario evidence levels: all `hybrid`
- Strict scenario count: 0
- V1 gap phases across all scenario contracts: 30

This is intentional: strict parity checks still exist inside scenarios, but the scenario-level label now stays honest until every required V1 phase is non-gap.

## Risks

- No full parity or multi-language execution was run for this guardrail-only batch. Those remain reserved for the next larger implementation batch.
- The manifest now exposes the remaining implementation debt more clearly; it does not implement the missing runtime/papers/repository/Web phases.
