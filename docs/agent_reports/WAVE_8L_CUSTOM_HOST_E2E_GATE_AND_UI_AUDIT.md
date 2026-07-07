# Wave 8L - Custom Host E2E Gate And UI Audit

Date: 2026-07-07

## Scope

- `nirs4all-ecosystem`: tightened the cross-language custom app host scenario
  so its shared UI/Web proof must explicitly cover the full
  dataset-to-pipeline-to-prediction-to-result-panel flow.
- `nirs4all-ui` / `nirs4all-quality`: read-only audit of the Wave 8K visual
  system against the paths consumed by the concurrent quality app work.

## Agent Reports

- Codex worker `Lovelace`: implemented the custom app host E2E contract
  tightening and reran the scenario/test gates.
- Codex explorer `Raman`: audited `nirs4all-ui` quality-consumed paths and
  confirmed Wave 8K did not touch `src/lab`, `assets/theme.css`, or
  `assets/brand/{nirs4all,quali}`.

## Files Modified

- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Decisions

- The `e2e-core-ui-custom-app-host` contract must not accept generic component
  rendering as enough shared-UI evidence. It now requires dataset, pipeline,
  prediction, result panel, engine label, and `nirs4all-ui` evidence.
- No V1 phase was promoted from `contract` or `gap` to `strict` because this
  wave did not produce new runtime/full-parity artifacts.
- No 12th scenario was added; the manifest and tests intentionally enforce the
  current 11-scenario contract.
- `nirs4all-ui` remains safe to evolve, but the active quality integration still
  requires coordinated reconciliation of the dirty `lab/theme` work with the
  published Wave 8K `brand/styles` exports.

## Tests

- `python3.11 scripts/n4a_e2e_scenarios.py validate` -> 11 scenarios OK.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage` -> 11/11 ready,
  `strictness_gaps=12`, `v1_contract_phases=10`, `v1_gap_phases=31`.
- `python3.11 -m pytest tests/test_e2e_scenarios.py -q` -> 115 passed.
- `git diff --check`.

## Risks

- This is a stricter declarative/evidence contract, not execution of the full
  Python-reference parity suite.
- The main `nirs4all-ui` checkout is still behind the published UI head and has
  concurrent uncommitted quality work; do not merge asset/style/lab changes
  casually.
- Quality still consumes UI from source aliases and absolute sibling paths; a
  later migration should publish `nirs4all-ui/lab` and move brand generation
  ownership into UI before changing quality consumption.
