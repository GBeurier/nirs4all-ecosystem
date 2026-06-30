# A1 preflight report - local evidence audit

Date: 2026-06-30
Workspace: `/home/delete/nirs4all`
Mode: read-only audit; only this dedicated report file was updated.

## Summary

All requested critical claims are verified against local code. No implementation code was modified. `PARALLEL_REFACTORING_SYNC.md` was not edited.

## Repo heads and status

| Repo | Branch | Upstream | HEAD | Status |
| --- | --- | --- | --- | --- |
| `nirs4all` | `main` | `origin/main` | `e41362b4` | clean |
| `dag-ml` | `main` | `origin/main` | `f58d7bf` | clean |
| `dag-ml-data` | `main` | `origin/main` | `347c15f` | clean |
| `nirs4all-studio` | `main` | `origin/main` | `2ccbf68` | clean |
| `nirs4all-web` | `main` | `origin/main` | `745eef8` | clean |
| `nirs4all-cluster` | `main` | `origin/main` | `dcced30` | clean |
| `nirs4all-io` | `main` | `origin/main` | `84ab189` | clean |
| `nirs4all-methods` | `main` | `origin/main` | `7602eb08` | clean |

Note: `nirs4all-ecosystem` had pre-existing added/modified docs/scripts before this A1 report update, including `docs/PARALLEL_REFACTORING_SYNC.md`. A1 did not touch the sync board.

## Claim status

| Claim | Status | Local evidence |
| --- | --- | --- |
| `nirs4all` defaults to legacy and `dag-ml` remains selectable | verified | `nirs4all/nirs4all/pipeline/engine.py:27` defines `Engine = Literal["legacy", "dag-ml", "dual"]`; `:29` sets `DEFAULT_ENGINE = "legacy"`; `:30` sets `N4A_ENGINE`; `:53-61` resolves explicit/env/default and rejects only `dual`. `nirs4all/tests/unit/pipeline/test_engine_selector.py:10-36` pins default legacy, env selection, explicit override, and dag-ml resolution. |
| Parity oracle, `EXPECTED_FALLBACK`, and `KNOWN_DIVERGENCES` exist | verified | `nirs4all/tests/integration/parity/_oracle.py:1-18` describes gold-baseline capture and legacy oracle; `:66-93` implements `compare()`. `nirs4all/tests/integration/parity/test_conformance_dual_engine.py:78-150` defines documented `KNOWN_DIVERGENCES`; `:303-326` defines `EXPECTED_FALLBACK`; `:372-403` enforces fallback boundary exactly. |
| `dag-ml` has `ControllerManifest`, `NodeTask`, `NodeResult`, and `validate_contracts` | verified | `dag-ml/crates/dag-ml-core/src/controller.rs:117-138` defines `ControllerManifest`. `dag-ml/crates/dag-ml-core/src/runtime/task.rs:60-87` defines `NodeTask`; `:378-404` defines `NodeResult`. Schemas exist under `dag-ml/docs/contracts/{controller_manifest,node_task,node_result}.schema.json`. `dag-ml/scripts/validate_contracts.py:34-56` registers those schema paths; `:1441-1462`, `:2277-2331`, and `:2333-2350` validate the three contracts. |
| Studio has `NativeResultsAdapter` and `/api/runs/execution-backends` | verified | `nirs4all-studio/api/native_results_adapter.py:570-625` defines a read-only native results adapter over native run dirs. `nirs4all-studio/api/runs.py:121` sets the runs router prefix to `/runs`; `nirs4all-studio/main.py:349` mounts it under `/api`; `nirs4all-studio/api/runs.py:1543-1551` defines `GET /execution-backends`, yielding `/api/runs/execution-backends`. `nirs4all-studio/api/execution_driver.py:13` defines typed backends and `:378-396` lists capabilities for `local-python`, `cluster`, and `wasm-local`. |
| Cluster client/server/lease/versioning exists | verified | `nirs4all-cluster/nirs4all_cluster/versioning.py:26-43` defines protocol `API_VERSION` and `X-N4C-*` headers. `nirs4all-cluster/nirs4all_cluster/client.py:68-112` defines `ClusterClient`, request headers, response version handling, and submit; `:171-221` covers job reads, workers, and cancel. `nirs4all-cluster/nirs4all_cluster/server/app.py:131-166` enforces version handshake; `:418-469` covers worker register/heartbeat/lease. `nirs4all-cluster/nirs4all_cluster/server/db.py:374-414` atomically leases tasks; `:604-624` renews leases on heartbeat. |
| `migration.py` exists in `nirs4all` | verified | `nirs4all/nirs4all/pipeline/storage/migration.py:1-17` documents workspace storage migration utilities and CLI module usage. File exists at `nirs4all/nirs4all/pipeline/storage/migration.py`. |

## Evidence files

- `nirs4all/nirs4all/pipeline/engine.py`
- `nirs4all/tests/unit/pipeline/test_engine_selector.py`
- `nirs4all/tests/integration/parity/_oracle.py`
- `nirs4all/tests/integration/parity/test_conformance_dual_engine.py`
- `nirs4all/nirs4all/pipeline/storage/migration.py`
- `dag-ml/crates/dag-ml-core/src/controller.rs`
- `dag-ml/crates/dag-ml-core/src/runtime/task.rs`
- `dag-ml/docs/contracts/controller_manifest.schema.json`
- `dag-ml/docs/contracts/node_task.schema.json`
- `dag-ml/docs/contracts/node_result.schema.json`
- `dag-ml/scripts/validate_contracts.py`
- `dag-ml/crates/dag-ml-capi/include/dag_ml.h`
- `nirs4all-studio/api/native_results_adapter.py`
- `nirs4all-studio/api/runs.py`
- `nirs4all-studio/api/execution_driver.py`
- `nirs4all-studio/main.py`
- `nirs4all-cluster/nirs4all_cluster/versioning.py`
- `nirs4all-cluster/nirs4all_cluster/client.py`
- `nirs4all-cluster/nirs4all_cluster/server/app.py`
- `nirs4all-cluster/nirs4all_cluster/server/db.py`
- `nirs4all-cluster/nirs4all_cluster/schemas.py`

## Commands run

- CodeGraph explorations for `nirs4all`, `dag-ml`, `nirs4all-studio`, and `nirs4all-cluster`.
- Direct verification with `rg`, `sed`/`nl`, and `git`.
- No build or test gates were executed in this preflight pass.

## Gates to ratify PRE-1/PRE-2/PRE-3

Recommended ratification gates:

1. Repo/head hygiene:
   - Re-run `git status --short --branch` and `git rev-parse --short HEAD` for the eight target repos.
2. Python core and parity boundary:
   - `cd nirs4all && pytest tests/unit/pipeline/test_engine_selector.py -q`
   - `cd nirs4all && pytest tests/integration/parity/test_parity_baseline.py -m parity -q`
   - `cd nirs4all && pytest tests/integration/parity/test_conformance_dual_engine.py -m "parity and slow" -q`
3. DAG-ML contracts:
   - `cd dag-ml && DAG_ML_DATA_REPO=../dag-ml-data python3 scripts/validate_contracts.py`
   - `cd dag-ml && cargo fmt --all --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`
4. Studio adapter/backend API:
   - `cd nirs4all-studio && python -m pytest tests/test_runs_execution_backend.py tests/test_execution_driver.py tests/test_native_results_adapter_identity.py tests/integration/test_native_results_format.py -q`
   - `cd nirs4all-studio && npm run lint:parallel && npm run test:parallel`
5. Cluster client/server/lease/versioning:
   - `cd nirs4all-cluster && ruff check . && mypy nirs4all_cluster && pytest -q`

## Blockers

None for this audit. The only caution is process-related: the ecosystem sync board already had pre-existing local modifications, so A1 left it untouched per multi-CLI mode and wrote this report for A0 integration.
