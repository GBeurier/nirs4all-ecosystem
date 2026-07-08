# WAVE 9T - Cluster Numeric Recompute Gate

Date: 2026-07-08

## Scope

Closed the strict-numeric proof gap for `e2e-cluster-dag-rights-client-core` without running the global full-parity suite.

## Files Modified

- `nirs4all-core/scripts/e2e/verify_cluster_handoff.py`
- `nirs4all-core/tests/test_verify_cluster_handoff.py`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `nirs4all-core` submodule pointer

## Decisions

- Kept `best_task_id` as exact categorical equality.
- Added measurable deltas to `local-vs-cluster-parity.json`:
  - `task_count_absolute_delta <= count_tolerance`
  - `succeeded_count_absolute_delta <= count_tolerance`
  - `best_metric_absolute_delta <= best_metric_tolerance`
- Removed the cluster entry from `STRICT_NUMERIC_PROOF_EXEMPTIONS`.
- Left full parity for a later large batch; this lane only ran the targeted cluster scenario and contract gates.

## Tests Run

- `cd nirs4all-core && python3.11 -m pytest tests/test_verify_cluster_handoff.py -q`
  - `2 passed`
- `cd nirs4all-ecosystem && python3.11 -m pytest tests/test_e2e_scenarios.py -q`
  - `128 passed`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
  - OK
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-cluster-next run --execute e2e-cluster-dag-rights-client-core`
  - `1 passed`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-cluster-next evidence --scenario e2e-cluster-dag-rights-client-core --json`
  - `verified_count: 1`, `failure_count: 0`

## Evidence

Real `local-vs-cluster-parity.json` now reports:

- `task_count_absolute_delta: 0`
- `succeeded_count_absolute_delta: 0`
- `best_metric_absolute_delta: 0.0`

Coverage debt now reports `strict_non_numeric_check_count: 2`; cluster contributes `0`.

## Risks

- The scenario still depends on the local `GRAPEVINE_LeafTraits` data path for execution.
- No global full-parity suite was launched in this batch by design.
