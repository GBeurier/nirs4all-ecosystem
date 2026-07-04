# WAVE 4BI - Cluster/Core handoff E2E

Date: 2026-07-04

## Scope

- Converted `e2e-cluster-dag-rights-client-core` from half-ready to executable.
- Added the missing Core-side verifier in `nirs4all-core`.
- Updated the scenario wording so it does not claim full numerical prediction
  parity; this gate verifies scheduler rights, routing, artifact handoff, and
  local recomputation of the cluster aggregate.

## Integrated commit

- `nirs4all-core`: `d487afbbe6eb84ec0175a42810e5dd969520aabc`
  - `test(e2e): verify cluster handoff artifacts`

## Files changed

### nirs4all-core

- `scripts/e2e/verify_cluster_handoff.py`

### nirs4all-ecosystem

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`

## Tests run

- `nirs4all-cluster`
  - `PYTHONPATH=src python3.11 -m pytest -q tests/e2e/test_cluster_dag_rights_core_client.py --artifacts-dir=/tmp/n4a-cluster-e2e`
- `nirs4all-core`
  - `python3.11 scripts/e2e/verify_cluster_handoff.py --artifacts-dir /tmp/n4a-cluster-e2e`
  - `python3.11 -m py_compile scripts/e2e/verify_cluster_handoff.py`
  - `python3.11 -m ruff check scripts/e2e/verify_cluster_handoff.py`
- `nirs4all-ecosystem`
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 scripts/n4a_e2e_scenarios.py plan --scenario e2e-cluster-dag-rights-client-core`
  - `python3.11 scripts/n4a_e2e_scenarios.py run e2e-cluster-dag-rights-client-core --execute`
  - `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
  - `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`

## Decisions

- The scenario now uses the existing cluster E2E test and `PYTHONPATH=src` so a
  local checkout works without an installed wheel.
- Core verifies the produced `scheduler-run.json`, rights checks, blocked-worker
  routing, best-model handoff, and recomputes `best_task_id` / `best_metric`
  from task results.
- The output `local-vs-cluster-parity.json` explicitly marks scope as
  `control_plane_metric_recompute`.

## Risks

- This is not the final cluster numerical parity gate. It does not run a real
  `nirs4all.run()` prediction pipeline; the cluster test still completes tasks
  with synthetic metrics.
- A future stronger gate should plug the worker subprocess runner into a small
  real pipeline once the production switch path is ready.
