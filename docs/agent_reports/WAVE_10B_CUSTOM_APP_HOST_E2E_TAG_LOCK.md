# Wave 10B - Custom app host E2E tag lock

## Scope

- Promoted `custom_app_host` to an explicit required cross-language E2E tag.
- Added the tag to `e2e-core-ui-custom-app-host`.
- Regenerated the committed runtime evidence ledger from existing verified
  artifacts so the manifest hash and tag coverage remain consistent.

## Files Modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `docs/agent_reports/WAVE_10B_CUSTOM_APP_HOST_E2E_TAG_LOCK.md`

## Tests And Gates

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_quality_custom_host_smoke.py`
- `python3.11 -m pytest -q`
- `git diff --check`

## Decisions

- Did not rerun the full runtime scenarios. This wave tightens manifest coverage
  accounting and reuses the latest verified artifacts: `11/11` scenarios,
  `70` artifacts, `0` failures.
- Kept the runtime evidence freshness policy unchanged: run the expensive
  runtime job after large functional batches and before Python/Studio
  production switches.

## Risks / Follow-Up

- `custom_app_host` is now visible in coverage as `1` required tag. Future
  custom host regressions should fail the manifest or ledger checks instead of
  being hidden under generic `web_results`.
