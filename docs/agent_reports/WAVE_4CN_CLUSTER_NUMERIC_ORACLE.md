# Wave 4CN - Cluster numeric oracle

Date: 2026-07-04

## Scope

Lane I / cross-language E2E: upgrade the cluster DAG rights/core-client handoff from a pure control-plane aggregate recompute to an optional real numeric oracle against the current Python `nirs4all` reference.

## Files changed

- `nirs4all-cluster/tests/e2e/test_cluster_dag_rights_core_client.py`
  - Always writes `local-vs-cluster-numeric.json`.
  - Default status is `not_requested`.
  - With `N4A_CLUSTER_NUMERIC_ORACLE=1`, submits a real `nirs4all.run` job through the cluster worker subprocess and compares `best_rmse` with a local Python-reference `nirs4all.run`.
- `nirs4all-core/scripts/e2e/verify_cluster_handoff.py`
  - Validates the numeric oracle sidecar and embedded scheduler evidence.
  - Extends `local-vs-cluster-parity.json` with `numeric_oracle_valid`.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Documents the new sidecar artifact and opt-in parity check for `e2e-cluster-dag-rights-client-core`.

## Tests run

- `cd nirs4all-cluster && python3.11 -m ruff check tests/e2e/test_cluster_dag_rights_core_client.py`
- `cd nirs4all-cluster && PYTHONPATH=src python3.11 -m pytest -q tests/e2e/test_cluster_dag_rights_core_client.py --artifacts-dir=/tmp/n4a-cluster-handoff-default`
- `cd nirs4all-cluster && PYTHONPATH=/home/delete/nirs4all/nirs4all-cluster:/home/delete/nirs4all/nirs4all N4A_CLUSTER_NUMERIC_ORACLE=1 python3.11 -m pytest -q tests/e2e/test_cluster_dag_rights_core_client.py --artifacts-dir=/tmp/n4a-cluster-handoff-numeric`
- `cd nirs4all-core && python3.11 -m py_compile scripts/e2e/verify_cluster_handoff.py`
- `cd nirs4all-core && python3.11 scripts/e2e/verify_cluster_handoff.py --artifacts-dir /tmp/n4a-cluster-handoff-default`
- `cd nirs4all-core && python3.11 scripts/e2e/verify_cluster_handoff.py --artifacts-dir /tmp/n4a-cluster-handoff-numeric`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `cd nirs4all-ecosystem && PYTHONPATH=/home/delete/nirs4all/nirs4all-cluster:/home/delete/nirs4all/nirs4all N4A_CLUSTER_NUMERIC_ORACLE=1 PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-cluster-e2e-numeric run e2e-cluster-dag-rights-client-core --execute`

## Decisions

- Keep the numeric oracle opt-in so normal CI remains fast and dependency-light.
- The default artifact is still explicit (`status: not_requested`) so the absence of numeric parity cannot be confused with a pass.
- Use the Python package as the oracle, in line with the V1 parity rule.

## Risks / follow-up

- Numeric oracle execution requires a local Python reference checkout and the GRAPEVINE fixture dataset.
- This covers the cluster worker path for `best_rmse`; it is not a substitute for the broader full parity suite.
