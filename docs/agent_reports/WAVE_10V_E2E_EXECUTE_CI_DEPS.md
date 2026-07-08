# WAVE 10V - E2E Execute CI Dependencies

Date: 2026-07-09

## Scope

Fix the first manual full `execute=true` GitHub E2E dispatch after the stable
runtime evidence ledger landed.

## Triggered Run

- Workflow: `Cross-language E2E scenarios`
- Run: `28980904951`
- Ref: `main` at `7ab912b`
- Inputs: `execute=true`, `allow_blocked=true`

## Finding

The run failed before parity execution could produce artifacts. The failing step
was `Execute ready scenarios`, and the first scenario command loaded
`nirs4all/tests/conftest.py`, which imports `matplotlib`. The workflow had only
installed `pytest`, so Python test collection failed with:

`ModuleNotFoundError: No module named 'matplotlib'`

This is an environment provisioning failure, not a parity failure.

## Files Modified

- `.github/workflows/cross-language-e2e.yml`
- `docs/agent_reports/WAVE_10V_E2E_EXECUTE_CI_DEPS.md`

## Decision

Keep push/PR checks lightweight, but install the editable Python E2E packages
and Web `node_modules` only when `workflow_dispatch execute=true`. This prepares
the long runtime scenarios without slowing normal contract validation.

## Follow-Up

Re-dispatch the full `execute=true` run after this workflow fix lands.
