# WAVE 9W - R contract no legacy alias gate

Date: 2026-07-08

## Scope

Post-review cleanup after the R strict-numeric gate.

## Files Modified

- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`

## Decision

- Removed the explicit `requires_paths` gate for `nirs4all-methods/bindings/python/src/pls4all` from the R dataset scenario.
- Kept the canonical `n4m` path requirement.
- Did not remove the underlying Python `pls4all.sklearn` backend during this patch; that is a methods/core implementation migration, not a contract gate cleanup.

## Validation

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 -m pytest tests/test_e2e_scenarios.py -q`

## Risks

- Full removal of `pls4all` implementation aliases still needs a coordinated `nirs4all-methods` and `nirs4all-core` backend migration.
