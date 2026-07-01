# W28 report - cluster core client

Status: completed and committed in the W28 worktree.

## Scope

W28 built on W19's typed client by adding the first core/CLI-facing adapter for
`nirs4all.run` jobs. The adapter still distributes only whole `nirs4all.run`
tasks (Level 0/1), but now records concrete local-vs-distributed parity
expectations in the submitted job contract.

## Changes

- Added `DistributedRunParity` to `schemas.py` and `JobRequest.parity` as
  stored traceability metadata.
- Added `build_nirs4all_run_request()` and `ClusterClient.submit_nirs4all_run()`.
  The adapter:
  - accepts local `nirs4all.run` vocabulary;
  - translates `n_jobs` to worker-local `inner_n_jobs`;
  - omits `workspace_path` because cluster tasks use isolated worker workspaces;
  - records that fine-grained DAG/variant/fold/subtree parity is deferred until
    core/dag-ml execution-unit and data-provider contracts exist.
- Kept `submit_run()` as a compatibility path by delegating it through the new
  adapter.
- Added `n4cluster run --pipeline ... --dataset ...` for file-free CLI
  submissions using the same adapter request builder.
- Updated SDK, CLI, and job-spec docs.
- Added focused tests for:
  - adapter request construction and parity metadata;
  - client method delegation;
  - CLI request construction and invalid input handling;
  - server persistence/decomposition of the adapter contract;
  - runner argument mapping (`workspace_path` isolation, `n_jobs` -> remote
    `n_jobs`);
  - the invariant that only `runners/nirs4all_run.py` imports `nirs4all`.

## Verification

From `/home/delete/nirs4all/_worktrees/W28-cluster-core-client` using
`/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python`:

```bash
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m pytest -q \
  tests/test_core_adapter.py tests/test_cli.py tests/test_worker.py
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m pytest -q \
  tests/test_server_api.py tests/test_versioning.py tests/test_client_errors.py tests/test_rbac.py
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/ruff check .
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m mypy nirs4all_cluster
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m pytest -q
```

Results:

- Focused adapter/CLI/worker tests: `16 passed`.
- Broader API/RBAC/versioning/client-error tests: `69 passed`.
- Ruff: clean.
- Mypy: success on 22 source files.
- Full pytest: `124 passed, 1 skipped, 1 warning`.

## Commit

`bd8ce70 feat(cluster): add core nirs4all run adapter`

## Notes

This slice intentionally does not redesign RBAC or server scheduling. It also
does not claim fine-grained DAG parity: the contract explicitly limits parity to
whole-run tasks and marks variant/fold/subtree distribution as deferred to
core/dag-ml/data-provider contracts.
