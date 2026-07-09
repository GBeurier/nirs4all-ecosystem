# Wave 10AB - E2E ledger runtime guard

Date: 2026-07-09

Lane: C / K, strict cross-language runtime evidence ledger.

## Scope

- Reviewed the strict E2E ledger check after the Web UI shim install fix.
- Confirmed a latent CI blocker: `evidence-ledger --check --max-age-seconds 14400`
  regenerated a ledger that differed from the committed ledger solely because
  `evidence.max_age_seconds` changed from `null` to the runtime guard value.
- Made `max_age_seconds` an execution-time freshness guard, not a committed-ledger
  drift source.

## Files changed

- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Tests run

- `python3.11 -m pytest -q tests/test_e2e_scenarios.py::test_cross_language_e2e_evidence_ledger_check_treats_max_age_as_runtime_guard`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_gitmodules_topology.py`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --check --max-age-seconds 999999999 --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`

## Results

- Targeted ledger guard test passed.
- E2E/topology tests passed: 134 tests.
- Runtime evidence ledger check passed with a non-null freshness threshold.
- Full strict coverage remained green: 11/11 scenarios ready, 0 blocked.

## Decisions

- Kept byte-for-byte strict ledger comparison for all committed evidence fields.
- Normalized only `evidence.max_age_seconds` during `--check`, taking the value
  from the committed ledger before comparison.
- Left the artifact freshness validation itself unchanged; stale artifacts still
  fail through the generated evidence summary.

## Risks

- The currently running GitHub dispatch started before this fix and may still fail
  on the old ledger comparison. A new dispatch is required after this commit.
