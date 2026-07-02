# Wave 3AO - Lite V1 Surfaces, IO Dag-ML Bridge Pointer, Benchmark Read-Only Pipelines

Date: 2026-07-02

## Scope

This batch integrated three independent lanes from the Codex-only refactoring
run:

- Lane E/Lite: audit and re-run the V1 public surface gates for Python, R, and
  browser/WASM aggregate bindings.
- Lane G/IO: align the Python MVP and CLI documentation/messages with the
  current Rust `nirs4all-io-dagml` bridge ownership.
- Lane J/Benchmarks/Repository: keep repository as the provider of pipeline
  presets and add read-only catalogue coverage in benchmarks.

No old worktree or superseded branch was merged wholesale. Full Python-reference
parity and the long dag-ml/native parity gates were intentionally deferred for a
larger batch.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Gibbs the 2nd | `nirs4all-lite` V1 public surfaces | no-op, verified | Confirmed Python/R/JS-WASM surfaces are already explicit in the topology manifest. |
| Locke the 2nd | `nirs4all-io` implementation | integrated | Commit `1642c5d` (`docs(dagml): point io target to rust bridge`). |
| Harvey the 2nd | `nirs4all-io` review | GO | Confirmed Python MVP stays non-duplicative and points to the Rust bridge. |
| Ohm the 2nd | `nirs4all-repository`/`nirs4all-benchmarks` implementation | partially integrated | No repository change; benchmarks tests were added and then strengthened. |
| Newton the 2nd | `nirs4all-benchmarks` review | NO-GO then GO | Initial read-only proof was too weak; re-review accepted snapshot and sentinel coverage. |
| Coordinator | `nirs4all-benchmarks` fix/integration | integrated | Commit `1a32b38` (`test(pipelines): enforce read-only catalogue queries`). |

## Integrated Changes

### `nirs4all-lite`

- No source change was needed.
- Reconfirmed `release_topology_manifest()` accounts for:
  - Python `nirs4all` oracle surface;
  - R `nirs4all` aggregate surface;
  - browser/WASM `nirs4all` aggregate surface.
- Local gate rerun covered Python and JS/WASM; R remains an environment skip
  because `R`/`Rscript` are not installed.

### `nirs4all-io`

- Updated docs, package metadata text, Python API messages, and CLI messages so
  `target="dag-ml-data"` points users to the Rust `nirs4all-io-dagml` bridge.
- Kept the Python MVP fail-loud: it does not implement or duplicate dag-ml-data
  emission.
- Added Python coverage proving `load(target="dag-ml-data")` reports the Rust
  bridge as the owner.
- The CLI `emit-dag-ml-data` path remains a pointer to the bridge crate, not an
  emitter in the generic CLI.

### `nirs4all-benchmarks`

- Added read-only catalogue coverage for `Queries.pipelines()`:
  - public `ArenaStore` mutators are forbidden during the call;
  - `sqlite3.Connection.total_changes` must remain unchanged;
  - SQLite dump, schema `user_version`, and store file hashes are unchanged.
- Added equivalent `/api/pipelines` endpoint coverage:
  - `ArenaStore` mutators are blocked at class level;
  - `nirs4all_repository` imports are guarded during the request;
  - store snapshot is unchanged before and after the request.
- Kept `nirs4all-repository` unchanged. It remains the preset/pipeline provider;
  benchmarks only consume the seeded benchmark store.

## Validation

`nirs4all-lite`:

- `make test-v1-surfaces` -> Python surface tests: 38 passed; JS/WASM Node
  tests: 14 passed; TypeScript typecheck passed.
- `make test-r-v1-surfaces-if-available` -> skipped with explicit risk because
  `R`/`Rscript` are not installed.

`nirs4all-io`:

- `PYTHONPATH=src rtk pytest tests/test_load_e2e.py::test_load_dag_ml_data_target_points_to_rust_bridge -q` -> 1 passed.
- `rtk cargo test -p nirs4all-io-cli emit_dag_ml_data_points_to_ecosystem_crate` -> 1 passed.
- Reviewer also ran `rtk run "PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider tests/test_load_e2e.py::test_load_dag_ml_data_target_points_to_rust_bridge"` -> 1 passed.
- `git diff --check` -> passed.

`nirs4all-repository`:

- Worker reran `PYTHONPATH=src pytest tests/test_api.py` -> 7 passed.
- No files changed.

`nirs4all-benchmarks`:

- `/tmp/n4a-bench-tests/bin/python -m pytest tests/test_queries.py::test_pipelines_catalogue_is_read_only tests/test_service_api.py::test_pipelines_endpoint_is_read_only -q -p no:cacheprovider` -> 2 passed.
- `/tmp/n4a-bench-tests/bin/python -m pytest tests/test_queries.py tests/test_service_api.py tests/test_repository_bridge.py -q -p no:cacheprovider` -> 27 passed.
- `/tmp/n4a-bench-tests/bin/python -m ruff check tests/test_queries.py tests/test_service_api.py` -> passed.
- `git diff --check` -> passed.
- Reviewer re-check: `git diff --check` -> passed; reviewer test execution was
  blocked by an environment-local old `jsonschema` without
  `Draft202012Validator`, so coordinator verification used an isolated venv
  with current dependencies.

## Release Surface Accounting

The release surface matrix explicitly includes the required `nirs4all` V1
surfaces:

- `nirs4all.python.oracle`: Python `nirs4all`, outside aggregation lock.
- `nirs4all.r.aggregate`: R `nirs4all`, covered by locked `lite`.
- `nirs4all.browser_wasm.aggregate`: browser/WASM `nirs4all`, covered by locked
  `lite`.
- `nirs4all.browser_wasm.methods_scoped`: methods WASM surface.
- `nirs4all.browser_wasm.datasets_scoped`: datasets WASM surface.

## Gate Policy

- Full Python-reference parity and dag-ml/native parity were not run in this
  batch because they are long and reserved for larger batches.
- No tests were reduced, xfailed, or weakened.
- No superseded Claude worktree or branch was merged blindly.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Risks

- `nirs4all-lite`: R public-surface runtime checks remain unexecuted in this
  environment because R is unavailable.
- `nirs4all-io`: the change is documentation/message alignment plus targeted
  tests; it does not exercise a full bridge emission round trip.
- `nirs4all-benchmarks`: endpoint import guards cover imports during the
  request, not hypothetical top-level imports already executed before the test.
  SQLite `*-shm` files are intentionally ignored as transient lock metadata.
