# RC-I Cluster Scheduler Report

Date: 2026-07-02

Worker: Codex RC-I cluster worker

Worktree: `/home/delete/nirs4all/_worktrees/RC-v1-cluster`

## Scope Audited

- Client/server scheduler and queue behavior.
- DAG-shaped request metadata and whole-run scheduling boundary.
- Worker lease, slot, retry, cancellation and load-routing behavior.
- Rights/RX boundary for submitter, viewer, executor, admin credentials.
- Minimal client/core contract for `nirs4all.run` submission.

## Files Modified

- `nirs4all_cluster/server/app.py`
  - Made scheduler metadata shape server-authoritative via `JobRequest.inferred_scheduler_contract()`.
  - Client-supplied `scheduler.shape` can no longer down-label a matrix or DAG-looking request as `atomic`.
- `tests/test_scheduler.py`
  - Added regression coverage that an ineligible high-priority GPU task does not block a CPU worker from leasing lower-priority eligible work.
- `tests/test_rbac.py`
  - Added regression coverage that client-declared scheduler rights/shape are normalized by the server for DAG-shaped jobs.
- `docs/agent_reports/RC_I_CLUSTER_SCHEDULER.md`
  - This report.

## Tests Run

- `uv run --extra dev pytest tests/test_scheduler.py tests/test_rbac.py tests/test_server_api.py tests/test_core_adapter.py -q`
  - Result: `69 passed, 1 warning`.
- `uv run --extra dev ruff check .`
  - Result: passed.
- `uv run --extra dev mypy nirs4all_cluster`
  - Result: passed, `Success: no issues found in 22 source files`.
- `uv run --extra dev pytest -q`
  - Result: `137 passed, 1 skipped, 3 warnings`.
- `uv run --extra dev pytest tests/test_integration_nirs4all.py -q -rs`
  - Result: `1 skipped`; reason: `could not import 'nirs4all': No module named 'nirs4all'`.
- Static import guard:
  - Result: no forbidden `nirs4all` imports outside `nirs4all_cluster/runners/nirs4all_run.py`.

Warnings observed are dependency deprecations from Starlette/httpx and websockets/uvicorn, not failures.

## Decisions

- Keep V1 cluster scheduling at whole `nirs4all.run` task granularity.
- Treat DAG-shaped inline pipelines as `dag_shaped_whole_run` metadata only; no fold, variant, subtree, or graph-node execution is claimed.
- Keep queue policy simple: priority order, eligibility scan, slot caps, lease TTL, retry, and worker capability/package/GPU filtering. No fairness, quotas, preemption, or Ray/Dask-class scheduler was added.
- Keep rights credential-derived:
  - `submitter`: submit/read/cancel.
  - `executor`: read/execute.
  - `viewer`: read.
  - `admin`: wildcard.
- Keep the minimal core-facing client contract as the existing `build_nirs4all_run_request()` adapter plus `DistributedRunParity`/`DagSchedulerContract` metadata. It records `n_jobs -> inner_n_jobs`, omits local `workspace_path`, and explicitly defers fine-grained DAG parity.

## Risks And Remaining Gaps

- Fine-grained DAG execution remains blocked on core/dag-ml execution-unit, data-view, artifact-provider, selection/refit, and parity contracts. The cluster can carry DAG-shaped whole-run jobs but should not distribute folds or subtrees yet.
- `worker_local` behaves like `shared_path`; true locality routing still needs an explicit dataset placement/provider contract.
- `catalog` datasets remain unimplemented in the beta worker.
- Load balancing is eligibility and slot based only. There is no fairness, project quota, duration estimate, preemption, or data-locality optimizer.
- Executor identity is principal-bound, not per-worker cryptographic identity. This is acceptable for the documented trusted-LAN beta, but not for open or multi-tenant deployment.
- The optional integration test requires a venv with `nirs4all` installed; it skipped in the cluster-only dev environment used for this audit.

## Follow-Up Commands

When a sibling `nirs4all` environment and data fixtures are available:

```bash
/home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/test_integration_nirs4all.py -q
/home/delete/nirs4all/nirs4all/.venv/bin/python scripts/validation.py
```

Those commands are still the right proof for actual runner parity/recovery, but this RC-I change did not touch the runner.
