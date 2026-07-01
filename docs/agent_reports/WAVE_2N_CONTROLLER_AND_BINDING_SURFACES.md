# Wave 2N Controller And Binding Surfaces

Date: 2026-07-01T13:37:15+02:00

## Scope

Follow-up batch after W2M. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

## Starting State

- W2M integrated `dag-ml` binding-facing controller manifest derivation through
  `a428926cf8b4`.
- W2M integrated an opt-in `n4m` SNV route in `_worktrees/INT-nirs4all` through
  `06b574cf6239`.
- The selected release root validates the aggregation lock.
- Full Python-reference parity is intentionally deferred until a larger
  core/runtime/native batch.
- The public roadmap now requires `nirs4all` V1 release accounting for Python,
  R, and WASM/browser surfaces, not Python only.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| B/H | `019f1d77-ddeb-7de2-a8fe-07a130ab5652` / Pauli | `_worktrees/INT-nirs4all` only | Integrated: `799f789c feat(runtime): derive controller manifests through dagml` |
| E/R/WASM | `019f1d77-fc4a-72a2-81e4-e65596419e00` / Bernoulli | `nirs4all-lite` only | Integrated: `8fa133b test(release): gate v1 python r wasm surfaces` |

## Review Criteria

Lane B/H must not weaken the existing kind-level manifest output. It should keep
`nirs4all.runtime.list_controller_manifests()` as the Studio-facing accessor and
must remain compatible with environments where the new `dag_ml` helper is not
importable.

Lane E/R/WASM must not add parser, methods, dataset, or orchestration logic to
`nirs4all-lite`. It may only improve release-surface visibility, tests, or docs
for Python/R/WASM aggregate bindings.

## Expected Gates

- No full parity in this batch.
- Targeted `nirs4all` runtime/manifest tests and Studio operator manifest tests.
- Targeted Python/R/WASM `nirs4all-lite` checks matching touched files.
- Release lock regeneration only if a release member commit changes.

## Integration Gate

After integrating Pauli and Bernoulli and regenerating the release lock:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - passed
- `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`
  - passed

`pyref_oracle_full` was intentionally skipped for this batch and remains due
after the next larger parity batch.

## Agent Reports

### Pauli - Lane B/H

Files modified:
- `nirs4all/pipeline/dagml_bridge.py`
- `tests/unit/pipeline/test_rt_envelopes.py`

Decision:
- The public accessor remains `nirs4all.runtime.list_controller_manifests()`.
- When the local `dag_ml` exposes `HostControllerSpec` and
  `derive_controller_manifests`, `nirs4all` now validates real host specs and
  derives controller manifests through that public helper.
- When the helper is absent or partial, the accessor returns the exact legacy
  static manifest list, not host-spec payloads.

Review notes:
- Initial agent diff passed fake-module tests but passed full
  `ControllerManifest` payloads as `HostControllerSpec`; real `dag_ml` rejected
  `capabilities`/`supported_phases` as unknown fields. Integration fixed the
  spec shape before commit.
- Real helper output intentionally adds dag-ml template enrichments such as
  derived `data_requirements`; fallback output stays unchanged.

Tests run:
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:. /home/delete/miniconda3/bin/python -m pytest -q tests/unit/pipeline/test_rt_envelopes.py`
  - `18 passed`
- `ruff check nirs4all/pipeline/dagml_bridge.py tests/unit/pipeline/test_rt_envelopes.py`
- `mypy --follow-imports=skip nirs4all/pipeline/dagml_bridge.py tests/unit/pipeline/test_rt_envelopes.py`
- `/home/delete/miniconda3/bin/python -m py_compile nirs4all/pipeline/dagml_bridge.py tests/unit/pipeline/test_rt_envelopes.py`
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/INT-dmd/crates/dag-ml-data-py/python:. PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH /home/delete/miniconda3/bin/python -m pytest -q tests/integration/parity/test_dagml_bridge_spike.py`
  - `6 passed`
- `PYTHONPATH=/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/INT-dmd/crates/dag-ml-data-py/python:. PATH=/home/delete/nirs4all/dag-ml/target/release:$PATH /home/delete/miniconda3/bin/python -m pytest -q tests/integration/parity/test_dagml_dataplane.py tests/integration/parity/test_dagml_run_selector.py`
  - `34 passed`
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-nirs4all:/home/delete/nirs4all/dag-ml/crates/dag-ml-py/python:. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest -q tests/test_operators_manifests.py`
  - `3 passed, 2 skipped`

Risks:
- The helper-derived manifest surface is richer than the legacy fallback for
  data requirements; downstream code must treat the accessor as contract JSON,
  not a snapshot of the fallback dicts.
- Full Python-reference parity was not rerun in this batch.

### Bernoulli - Lane E/R/WASM

Files modified:
- `Makefile`
- `README.md`
- `bindings/python/src/nirs4all_lite/_topology.py`
- `bindings/python/tests/test_release_topology.py`
- `docs/RELEASE.md`

Decision:
- The aggregate release topology now explicitly gates the V1 public `nirs4all`
  surfaces for Python, R, and WASM/browser distribution.
- R checks are wired as an availability-aware gate: they run when R is installed
  and report a skip otherwise.

Tests run:
- `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests`
  - `35 tests, 1 skipped`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm test --prefix bindings/wasm`
  - `12 passed`
- `make test-r-if-available`
  - skipped because R is not installed locally
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH PYTHONPATH=bindings/python/src make test-v1-surfaces`
  - Python and WASM gates passed; R skipped because unavailable
- `git diff --check`

Risks:
- No local R runtime is installed, so the R surface is topology-gated and
  scripted but not executed on this machine.
- The `nirs4all-lite` commit changes a release-lock member and therefore needs a
  release lock refresh.
