# WAVE 10AZ — E2E GitHub Auth Refresh

## Scope

- Keep the cross-language E2E evidence refresh runnable after unauthenticated
  GitHub REST rate limits.
- Refresh the ready runtime evidence batch without running the full parity suite.

## Files Changed

- `scripts/e2e/verify_core_matlab_octave_release_gate.py`

## Changes

- The MATLAB/Octave release-gate verifier now accepts `GH_TOKEN` as a fallback
  to `GITHUB_TOKEN` for GitHub REST calls.
- No runtime contracts, package manifests, release locks, or published artifacts
  were changed.

## Validation

- `python3 -m py_compile scripts/e2e/verify_core_matlab_octave_release_gate.py scripts/n4a_e2e_scenarios.py`
- `GITHUB_TOKEN="$(gh auth token)" python3 scripts/n4a_e2e_scenarios.py run e2e-formats-io-datasets-methods-language-bindings --execute`
- `python3 scripts/n4a_e2e_scenarios.py evidence --max-age-seconds 14400 --json-out .n4a-e2e-artifacts/evidence-summary.json`
- `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict --json-out .n4a-e2e-artifacts/coverage/coverage-summary.json --markdown-out .n4a-e2e-artifacts/coverage/coverage-debt.md`
- `python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_quality_custom_host_smoke.py`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Results

- Runtime evidence: 11/11 scenarios verified, 70 artifacts, 0 failures.
- Coverage gate: 11/11 ready, 0 blocked, full strict ready.
- Orchestrator tests: 140 passed.

## Risks

- The verifier still depends on the GitHub API being reachable. CI/local callers
  should provide `GITHUB_TOKEN` or `GH_TOKEN` to avoid unauthenticated rate limits.
