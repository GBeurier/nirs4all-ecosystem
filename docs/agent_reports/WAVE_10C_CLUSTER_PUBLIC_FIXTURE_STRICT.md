# Wave 10C - Cluster Public Fixture Strict Parity

## Scope

Promoted `e2e-cluster-dag-rights-client-core` from hybrid to strict by replacing the old non-public `nirs4all-data` dependency with the checked-in public `nirs4all/examples/sample_datasets/F01_regression` fixture.

## Files Modified

- `.github/workflows/cross-language-e2e.yml`
- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `tests/test_e2e_scenarios.py`

## Tests Run

- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-cluster-public run --execute e2e-cluster-dag-rights-client-core`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-cluster-public evidence --scenario e2e-cluster-dag-rights-client-core`

## Result

- Cluster E2E passed with the public fixture.
- Evidence verification passed with 4 artifacts.
- Local-vs-cluster numeric parity: `cluster_best_rmse == local_best_rmse == 2.332317732925242`, `abs_diff=0.0`.
- E2E coverage moves to 7 strict scenarios and 4 hybrid scenarios.

## Risks

- The cluster scenario still declares papers, repository forced-refit, and Web/WASM reuse as not applicable by design; this report does not expand the cluster lane beyond scheduler/client/core parity.

## Decision

Remove the cluster public-checkout data blocker allowlist entry. The public fixture is now explicit in the scenario manifest and CI command.
