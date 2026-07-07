# Wave 7AU - E2E coverage debt board

Date: 2026-07-07

## Scope

- Publish the cross-language E2E hybrid-vs-strict debt as CI artifacts on every
  `Cross-language E2E scenarios` run.
- Keep full runtime parity execution manual after large integration batches.
- Do not touch the concurrent `nirs4all-ui` / `nirs4all-quality` work.

## Files changed

- `.github/workflows/cross-language-e2e.yml`
- `docs/CROSS_LANGUAGE_E2E.md`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `docs/agent_reports/WAVE_7AU_E2E_COVERAGE_DEBT_BOARD.md`

## Implementation

- Added `coverage --markdown-out <path>` to render the E2E coverage report as a
  human audit board.
- The board includes scenario readiness, evidence levels, strictness gaps,
  V1 strict/contract/gap phase counts, per-scenario debt, and required
  language/tag coverage.
- The GitHub Actions workflow now writes and uploads:
  - `.n4a-e2e-artifacts/coverage/coverage-summary.json`
  - `.n4a-e2e-artifacts/coverage/coverage-debt.md`
- Runtime scenario execution remains explicit via `workflow_dispatch
  execute=true`.

## Agent reviews

### E2E audit agent

- Mode: Claude Code read-only.
- Files modified: none.
- Main finding: the suite covers the requested surfaces at contract level, but
  the important residual debt is the strict-vs-contract ratio and the lack of a
  default CI gate that executes full runtime parity.
- Local verification corrected one stale observation from the audit: the current
  manifest has `11` scenarios `ready` and `0` blocked.

### UI / quality boundary audit agent

- Mode: Claude Code read-only.
- Files modified: none.
- Main finding: `nirs4all-ui` has valuable in-flight lab/assets work, but it is
  dirty, behind `origin/main`, and overlaps the active `nirs4all-quality` work.
- Decision: do not edit or normalize `nirs4all-ui` in this batch. Reconcile it
  later on a dedicated branch/worktree, preserving the quality-owned components.

## Tests run

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-coverage-summary-current.json --markdown-out /tmp/n4a-coverage-debt-current.md`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `git diff --check`

Result: `117 passed`.

## Current coverage debt snapshot

- Scenarios: `11/11`
- Ready: `11`
- Blocked: `0`
- Evidence levels: `hybrid=11`
- Strictness gaps: `12`
- V1 contract phases: `10`
- V1 gap phases: `31`

## Risks

- This does not claim full parity. It makes the remaining hybrid/contract debt
  visible and reviewable on every E2E workflow run.
- Full runtime parity remains long-running and should still be launched after
  large batches or selected release heads.
- `nirs4all-ui` remains intentionally unmodified because another agent is
  working there and the brand/style systems need a controlled reconciliation.
