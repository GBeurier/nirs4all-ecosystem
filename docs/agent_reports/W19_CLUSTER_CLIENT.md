# W19 - Cluster Client / Worker Transport

Status: salvaged after max-turns, verified, and committed.

## Scope

W19 covered the client-facing cluster slice: make the submitter client and the
worker-side control-plane client rights-aware, typed, and reusable by core /
Studio without importing `nirs4all`.

## Changes

- Added `client_errors.py` with a typed exception hierarchy:
  - 401 -> `ClusterAuthError`;
  - 403 -> `ClusterPermissionError` with parsed principal and missing rights;
  - 404/409/413/422/4xx/5xx -> specific client/server errors;
  - transport failures -> `ClusterConnectionError`;
  - protocol 426 keeps `ClusterVersionError`.
- Added shared `client_transport.py` for bearer headers, version headers,
  version-drift warnings, and typed HTTP response mapping.
- Refactored `ClusterClient` onto that transport and added `server_info()`.
- Added `WorkerClient` for executor-side registration, heartbeat, lease, task
  lifecycle, and artifact transfer.
- Exported the new public client/error symbols from `nirs4all_cluster`.
- CLI now maps typed auth/permission/connection/protocol errors to clear exit
  messages and return codes.

## Verification

From `_worktrees/W19-cluster-client` using the main cluster venv:

```bash
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m pytest -q tests/test_client_errors.py
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/ruff check \
  nirs4all_cluster/client.py \
  nirs4all_cluster/client_errors.py \
  nirs4all_cluster/client_transport.py \
  nirs4all_cluster/client_worker.py \
  nirs4all_cluster/cli.py \
  nirs4all_cluster/__init__.py \
  tests/test_client_errors.py \
  tests/conftest.py
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m pytest -q
/home/delete/nirs4all/nirs4all-cluster/.venv/bin/python -m mypy \
  nirs4all_cluster/client.py \
  nirs4all_cluster/client_errors.py \
  nirs4all_cluster/client_transport.py \
  nirs4all_cluster/client_worker.py \
  nirs4all_cluster/cli.py \
  nirs4all_cluster/__init__.py
```

Results:

- Error tests: `18 passed`.
- Ruff: clean.
- Full pytest: `116 passed, 1 skipped, 1 warning`.
- Mypy: success on 6 source files.

## Commit

`7a8d48f feat(cluster): add typed client and worker transport errors`
