# Wave 4U - Parity resolver, neutral datasets, perf gate, and core pins

Date: 2026-07-02
Coordinator: Codex

## Scope

Close the post-reset RC drift found by parallel reviewers, then launch the full
parity suite once the batch is integrated:

- make Python parity tests resolve the selected RC `dag-ml` CLI instead of an
  absent local checkout path;
- make datasets/providers explain the non-Python path through neutral contracts
  rather than a full-Python provider dependency;
- add a lightweight Studio runtime overhead gate comparing legacy and `dag-ml`
  modes;
- align core strict-parity pins with the selected methods RC head;
- re-check the cluster GitGuardian alert against current branch, tag, and hidden
  PR refs;
- regenerate and validate the aggregate release lock.

## Published Code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all` Python surface | `rc/v1-full-refactor-python` | `884a196` / `n4a-v1-rc1-2026.07-refactor` | RC-aware `dag-ml` CLI resolver for parity/runtime tests |
| `nirs4all-datasets` | `rc/v1-full-refactor` | `59b34f5` / `n4a-v1-rc1-2026.07-refactor` | neutral descriptor exposed from native resolve, docs/tests/lock |
| `nirs4all-providers` | `rc/v1-full-refactor` | `bb87f35` / `n4a-v1-rc1-2026.07-refactor` | docs/tests pointing datasets consumers to neutral contracts |
| `nirs4all-studio` | `rc/v1-full-refactor` | `bd7de4b` / `n4a-v1-rc1-2026.07-refactor` | runtime performance gate and Python launcher preference |
| `nirs4all-lite` / `nirs4all-core` | `rc/v1-full-refactor-core` | `5067cab` / `n4a-v1-rc1-2026.07-refactor` | strict-parity methods pin alignment |
| `nirs4all-methods` | `rc/v1-full-refactor` | `6f6a3fa` / `n4a-v1-rc1-2026.07-refactor` | tag realigned to selected methods head |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | aggregation lock, board/security reports, this report |

## Local Gates

Python parity/runtime targeted gates:

- `python3.11 -m pytest -q tests/integration/parity/test_dagml_run_selector.py tests/integration/parity/test_rt_fallback_strict.py tests/integration/parity/test_marker_audit.py tests/integration/parity/test_native_fallback_boundary.py`
  -> `49 passed`.
- `python3.11 -m pytest -q tests/integration/parity/test_dagml_native_results.py`
  -> `30 passed`.
- `python3.11 -m pytest -q tests/integration/parity/test_dagml_native_export_model.py`
  -> `6 passed`.
- `python3.11 -m pytest -q tests/integration/parity/test_dagml_native_n4a_bundle.py`
  -> `8 passed`.
- Selected `test_dagml_cli_runner.py` cases -> `6 passed`.
- `python3.11 -m tests.integration.parity.coverage_meter --check`
  -> `coverage_meter OK (fallback=0, target=0)`.
- `python3.11 -m ruff check` on the touched parity/runtime files -> passed.

Python full parity after the integrated batch:

- Slow parity segment:
  `N4A_DAGML_CLI=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug/dag-ml-cli python3.11 -m pytest -q -m slow tests/integration/parity`
  -> `443 passed, 444 deselected, 1305 warnings` in `1776.75s`.
- Non-slow parity segment in the base interpreter:
  `N4A_DAGML_CLI=... python3.11 -m pytest -q -m "parity and not slow" tests/integration/parity`
  -> `316 passed, 1 skipped, 570 deselected, 503 warnings` in `470.31s`.
  The single skip was `test_dagml_node_runner.py::test_fit_cv_uses_methods_snv_when_env_enabled`,
  caused by `n4m` not being installed in the base interpreter.
- The skip was not accepted as green. The installed-methods proof harness built
  `nirs4all_methods-1.0.1-cp311-cp311-linux_x86_64.whl` from `RC-v1-methods`,
  installed it in a proof venv with `NIRS4ALL_REQUIRE_N4M=1`, verified ABI
  `2.0.0`, and verified identical SHA-256 for the source, staged, wheel, and
  proof-venv `libn4m.so.2.0.0`:
  `b70ce16fa9cac12fd670b6643e375f09f801842185fb3783524675d4ce45cc81`.
- The same non-slow parity pytest args were rerun through that proof harness and
  returned `status: OK`. This closes the methods skip as an environment setup
  issue, not accepted test debt.

Datasets/providers:

- Datasets Rust gates: `cargo fmt --all --check`; targeted
  `cargo test -p nirs4all-datasets-core ...`; locked targeted tests; and
  `cargo clippy -p nirs4all-datasets-core --all-targets -- -D warnings`.
- Datasets Python gates:
  `PYTHONPATH=src python3.11 -m pytest -q tests/test_index.py tests/test_acquire.py`
  -> `17 passed`; `python3.11 -m ruff check src tests scripts` -> passed.
- Providers gates:
  `python3.11 -m ruff check src tests scripts`; `PYTHONPATH=src python3.11 -m pytest -q tests/test_contracts.py`
  -> `21 passed`; `PYTHONPATH=src python3.11 scripts/validate_contracts.py`
  -> `provider contracts gate: PASS (5 schemas, 5 fixtures)`.

Studio:

- `python3.11 -m ruff check scripts/perf_runtime_gate.py tests/test_perf_runtime_gate.py`
  -> passed.
- `python3.11 -m pytest tests/test_perf_runtime_gate.py -q`
  -> `1 passed`.
- `npm run perf:runtime -- --iterations 8 --warmup 1 --no-write` with Linux
  Node `v24.16.0` -> PASS. The gate measured Studio wrapper overhead under
  0.1 ms in both legacy and `dag-ml` modes on the synthetic `nirs4all.run`-shaped
  runner. This is an overhead gate, not the full numerical performance suite.

Core/methods:

- `PYTHONPATH=bindings/python/src python3.11 -m unittest bindings/python/tests/test_release_topology.py -v`
  -> `12 tests OK`.
- Methods branch and RC tag both point to `6f6a3fa0dace421925502d4c8d5cab5102f56944`.

Ecosystem:

- `python3 scripts/n4a_release_lock.py ... validate` -> validated.
- `python3 scripts/n4a_release_lock.py ... audit-fetchability` ->
  `fetchability: 7/7 member commits checked out (0 unfetchable)`.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> validated.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`
  -> selected gates OK.
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py`
  -> `20 passed`.

## Parallel Review Inputs

- Codex Python worker confirmed `KNOWN_DIVERGENCES=0`, `EXPECTED_FALLBACK=0`.
  The coordinator then launched the full parity gate after the batch and closed
  the only realized methods skip with an installed-wheel proof.
- Codex datasets/providers worker confirmed the cross-language datasets contract
  is the neutral catalog/index/descriptor plus IO/materialization surfaces, not
  a mandatory Python provider package.
- Codex Studio worker added the focused runtime overhead gate without widening
  Studio backend or Playwright scope.
- Codex read-only reviewer found the stale methods pin in core strict parity CI;
  the coordinator fixed the pin to the selected methods RC head.
- Claude Code reviewer agreed the target separation is coherent but warned that
  R and native datasets/providers are not yet RC-backed as full pipeline
  consumers. Treat R as a portable methods-subset preview until a `dag-ml` R
  coordinator binding and `DatasetPackage` materialization path exist.

## Security Follow-up

The repeated GitGuardian alert for `GBeurier/nirs4all-cluster` was rechecked
after fetching current branch, tag, and hidden PR refs. Current selected refs are:

- `origin/main` -> `97b2b38`;
- `origin/rc/v1-full-refactor` -> `9d6ab34`;
- `n4a-v1-rc1-2026.07-refactor` -> `9d6ab34`.

No literal CLI secret-option values were found in the selected branch or tag
refs. Hidden PR refs #1/#2 still contain only documentation placeholders such as
`--token dev` / `TOKEN`; they are not selected release refs and GitHub does not
allow deleting `refs/pull/*/head`. If GitGuardian shows any value other than a
placeholder, rotate that credential before treating the alert as closed.

## Remaining Risk

- Full Python-reference parity on `884a196` passed in split form. The only
  realized skip in the base interpreter was the missing local `n4m` install, and
  it is covered by a strict installed-methods proof. Future release runners
  should run the non-slow parity segment in a methods-installed environment to
  keep skip count at zero.
- Studio full backend pytest and Playwright were not rerun in this wave; the new
  Studio evidence is the focused runtime overhead gate.
- R, MATLAB/Octave, and methods JS/WASM execution remain environment gates until
  their toolchains are present in CI or local release runners.
- Native R/WASM datasets consumption still needs materialization gates:
  byte-fetch/descriptor resolution is not the same thing as a full
  `DatasetPackage` provider feeding a `dag-ml-data` vtable.
- Public wording must avoid claiming full R pipeline parity. Current RC evidence
  supports R as a methods portable subset/preview, not a full `dag-ml`
  coordinator surface.
