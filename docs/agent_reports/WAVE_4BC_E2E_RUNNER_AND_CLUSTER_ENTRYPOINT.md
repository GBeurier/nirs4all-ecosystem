# Wave 4BC - E2E Runner Hardening and Cluster Entrypoint

Date: 2026-07-04

## Scope

Implemented the first executable cross-repo E2E entrypoint while keeping the
remaining scenario blocker explicit.

## Files changed

- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
  - `execute_plan()` now fails when a successful step does not create every
    declared `produces` artifact.
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
  - Added a regression test for the "command exits 0 but artifact is missing"
    false-green case.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Cluster scenario now uses `python3.11`, matching the repo's tested local
    environment.
  - `core-client-result.json` is now declared in the blocked core step's
    `produces`, so it cannot remain only a scenario-level artifact once the step
    becomes executable.
- `nirs4all-ecosystem/pytest.ini`
  - Restricts ecosystem pytest collection to `tests/`, so `pytest -q` does not
    recurse into tracked gitlinks such as the historical `nirs4all-cluster`
    pointer.
- `nirs4all-cluster/tests/conftest.py`
  - Added `--artifacts-dir` and an `artifacts_dir` fixture for ecosystem
    entrypoints.
- `nirs4all-cluster/tests/e2e/test_cluster_dag_rights_core_client.py`
  - New e2e entrypoint that exercises submit/read/execute rights, scheduler
    metadata, package/label routing, task leasing, task completion, model
    artifact linking, aggregate selection, event emission, and writes
    `scheduler-run.json`.

## Results

- `nirs4all-ecosystem`: `python3.11 -m pytest -q` -> 32 passed.
- `nirs4all-ecosystem`: `ruff check scripts tests` -> passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
  -> OK, 10 scenarios.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py run
  e2e-cluster-dag-rights-client-core --execute --allow-blocked` -> cluster
  step passed, final exit code 2 because `core-client-handoff` remains blocked.
- `nirs4all-cluster`: `python3.11 -m pytest tests/e2e/test_cluster_dag_rights_core_client.py
  -q --artifacts-dir=/tmp/n4a-cluster-e2e-verify` -> 1 passed.
- `nirs4all-cluster`: `python3.11 -m pytest -q` -> 147 passed, 1 skipped,
  1 deselected.
- `nirs4all-cluster`: `ruff check .` -> passed.
- `nirs4all-cluster`: `mypy nirs4all_cluster` -> passed.
- Claude Code Fable read-only review: verdict `SHIP`; it confirmed the
  produces guard, blocked-step exit semantics, and cluster no-`nirs4all` import
  invariant. Actionable follow-up folded back here: add `core-client-result.json`
  to the core step's `produces`.

## Decisions

- The cluster scenario is intentionally only partially executable today. The
  first step is real and produces an artifact; the second step stays blocked
  until `nirs4all-core/scripts/e2e/verify_cluster_handoff.py` exists.
- No skip/xfail was added. Missing runtime/entrypoint state remains represented
  as `blocked` by the ecosystem runner.
- The cluster entrypoint does not import `nirs4all`; it remains within the
  server/client/worker control plane, preserving the repo invariant.

## Risks

- The next step needs a real `nirs4all-core` handoff verifier, not a wrapper
  that only rereads `scheduler-run.json`.
- Other declared scenarios are still blocked by missing entrypoints or runtimes;
  the runner now prevents a green result if future stubs forget their declared
  outputs.
