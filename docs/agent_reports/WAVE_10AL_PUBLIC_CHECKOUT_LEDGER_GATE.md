# WAVE 10AL - public checkout ledger gate

Date: 2026-07-09

## Scope

Fix the strict GitHub run `28990976603`, where all executable scenarios passed
but the committed runtime evidence ledger check failed.

## Files changed

- `.github/workflows/cross-language-e2e.yml`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Decision

The workflow already allowlisted `e2e-r-dataset-io-pipeline-save` when a public
checkout lacks the private malaria dataset, but the later `evidence-ledger
--check` step did not receive the same allowlist. The ledger check now filters
only scenarios that are both explicitly allowlisted and actually blocked in the
current checkout.

The ledger proof hash also no longer includes host-variable numeric values. It
hashes the required constraint result instead, after the artifact validator has
already enforced the strict numeric and equality requirements. This keeps the
committed ledger stable across CI/local hosts without weakening the artifact
validation gate.

## Validation

- `nirs4all-ecosystem`: `python3.11 -m pytest -q` -> 170 passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py evidence --ready-only` -> `11/11 scenarios verified; artifacts=70 failures=0`.
- `nirs4all-ecosystem`: simulated public checkout with the malaria dataset removed plus the downloaded artifacts from run `28990976603`, then `evidence-ledger --check --allow-blocked ...` -> `10/10 scenarios verified; artifacts=59 failures=0`.

## Risks

- The GitHub strict workflow must be relaunched to prove the public-checkout
  ledger path on the real runner.
