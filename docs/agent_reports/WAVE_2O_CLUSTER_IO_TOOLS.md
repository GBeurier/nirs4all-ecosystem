# Wave 2O Cluster IO Tools

Date: 2026-07-01T14:05:00+02:00

## Scope

Follow-up after W2N. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

Full Python-reference parity is intentionally deferred until a larger core /
runtime / native batch.

## Starting State

- W2N integrated `INT-nirs4all` controller-manifest derivation through
  `799f789c`.
- W2N integrated `nirs4all-lite` Python/R/WASM public-surface gates through
  `8fa133b`.
- W2N refreshed and validated the release lock through ecosystem commit
  `6e96c24`.
- Non-full cutover gates passed with `pyref_oracle_full` skipped.
- Disk audit still shows many historical `W*` worktrees plus a Claude-era
  `.claude/worktrees/agent-*` under `nirs4all`. They are not integration roots
  for this wave and must not be merged without a fresh audit. The selected roots
  remain the `INT-*` worktrees plus explicit primary repos such as
  `nirs4all-tools` and `nirs4all-lite`.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| I | `019f1d8f-268f-7310-876f-a718c2e1e963` / Halley | `_worktrees/INT-cluster` only | Integrated: `dc29840 test(rbac): cover read-only cluster rights` |
| D | `019f1d8f-48db-7111-8e71-63eeebd7dc4c` / Huygens | `nirs4all-tools` only | Integrated: `fd51610 test(legacy): lock preserved prediction arrays golden` |
| G | `019f1d8f-7f2f-7392-906c-bdd3f2fab145` / Goodall | `_worktrees/INT-io` only | Integrated: `b958a29 docs(io): align dagml data bridge status` |

## Review Criteria

- Lane I must preserve the cluster boundary: only
  `nirs4all_cluster/runners/nirs4all_run.py` may import `nirs4all`.
- Lane D must not weaken converter tests or hide failures behind xfail/skip.
- Lane G must keep dataset assembly in `nirs4all-io`, not move parser or dataset
  catalog logic across repo boundaries.
- No lane may touch `nirs4all-drafts` or `nirs4all-lab`.

## Expected Gates

- Targeted tests for each changed repo.
- No full parity in this wave.
- Release lock regeneration only if a release member commit changes.

## Integration Gate

After integrating Halley, Huygens, and Goodall:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - passed
- `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`
  - passed

`pyref_oracle_full` was intentionally skipped for this wave and remains due
after a larger parity batch.

## Agent Reports

### Halley - Lane I

Files modified:
- `tests/test_rbac.py`
- `tests/test_cli.py`

Decision:
- No auth model or wire contract change. The lane strengthens tests for the
  existing credential-bound RBAC surface: viewer/read-only keeps read routes but
  cannot submit, cancel, upload artifacts, register workers, heartbeat, lease, or
  mutate task lifecycle routes.
- CLI forbidden output is pinned to include the principal and missing right.

Review notes:
- Confirmed no new `nirs4all` import outside
  `nirs4all_cluster/runners/nirs4all_run.py`.

Tests run:
- `/home/delete/nirs4all/_worktrees/INT-cluster/.venv/bin/python -m pytest -q tests/test_rbac.py tests/test_cli.py tests/test_client_errors.py tests/test_core_adapter.py::test_only_subprocess_runner_imports_nirs4all`
  - `42 passed`
- `/home/delete/nirs4all/_worktrees/INT-cluster/.venv/bin/python -m ruff check tests/test_rbac.py tests/test_cli.py`

Risks:
- Targeted RBAC/CLI coverage only; no cluster end-to-end validation script in
  this wave.

### Huygens - Lane D

Files modified:
- `tests/test_real_golden_fixtures.py`

Decision:
- No converter/schema change. The SQLite legacy-arrays golden now pins exact
  preserved JSONL order/content, per-record checksums, preserved file checksum,
  and the `preserved_opaque` record.

Tests run:
- `PYTHONPATH=src pytest tests/test_real_golden_fixtures.py::test_golden_sqlite_legacy_arrays_lowers_metadata_and_preserves_rows -q`
- `PYTHONPATH=src pytest tests/test_real_golden_fixtures.py -q`
  - `5 passed`
- `ruff check tests/test_real_golden_fixtures.py`

Risks:
- The hardcoded checksums intentionally fail on any future JSONL shape change,
  including intended migrations that must update the golden deliberately.

### Goodall - Lane G

Files modified:
- `README.md`
- `COMPAT.md`
- `bindings/SPEC.md`
- `docs/API.md`
- `docs/DATASET_CONFIGURATIONS.md`
- `docs/PHASE2_GATE.md`
- `docs/ROADMAP.md`
- `docs/STATUS.md`
- `CLAUDE.md`
- `pyproject.toml`
- `src/nirs4all_io/api.py`
- `src/nirs4all_io/materialize/assemble.py`
- `src/nirs4all_io/spec/json_schema.py`
- `crates/nirs4all-io-cli/src/main.rs`
- `tests/test_dataset_package.py`

Decision:
- No Python `dag-ml-data` load target was invented. Python continues to reject
  `load(..., target="dag-ml-data")`, but now points callers to the implemented
  Rust bridge crate `crates/nirs4all-io-dagml` (`to_dag_ml_data`, `emit-dagml`).
- `DatasetPackage` is documented and tested as the Python target-agnostic
  package surface via `load(..., target="dataset_package"|"package")` and
  `to_dataset_package`.
- User-facing docs and binding docs no longer describe the bridge as future,
  stubbed, or gated.

Review notes:
- The initial agent diff left a stale CLI help string and a few residual
  "future/gated" mentions; integration corrected those before commit.
- The change is documentation/status plus public error-message/test coverage. It
  does not move dataset assembly out of `nirs4all-io` and does not touch
  `nirs4all-datasets`.

Tests run:
- `PYTHONPATH=src /home/delete/nirs4all/nirs4all-io/.venv/bin/python -m pytest tests/test_dataset_package.py -q`
  - `6 passed`
- `ruff check src/nirs4all_io/api.py src/nirs4all_io/materialize/assemble.py src/nirs4all_io/spec/json_schema.py tests/test_dataset_package.py`
- `cargo fmt --all --check`
- `cargo test -p nirs4all-io-cli emit_dag_ml_data_points_to_ecosystem_crate`
  - `1 passed`

Risks:
- Cross-CLI dag-ml/dag-ml-data conformance was not rerun in this wave; this wave
  only aligns docs/status and the Python rejection path with the already-built
  Rust bridge.
