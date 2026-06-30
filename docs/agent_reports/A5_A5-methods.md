# A5 methods/n4m audit report

Date: 2026-06-30

Mode: read-only audit. No implementation code changed. Per session mode, I did
not edit `docs/PARALLEL_REFACTORING_SYNC.md`; A0 should integrate the sync
handoff at the end of this report.

## Executive summary

Recommendation: V1 should stay sklearn-host-controller first, with the existing
opt-in `nirs4all-methods` wrappers gated under a dedicated methods-installed CI
job. A direct n4m C ABI controller is feasible, but it is not the minimal V1:
it adds new controller manifests, model-artifact semantics, lib discovery,
matrix-view plumbing, and cross-repo CI. Do not modify n4m kernels without an
accepted ARB-003 decision.

Current state:

- `nirs4all-methods` has real sklearn/reference parity infrastructure and a
  PR gate for seven scikit-learn-oracle methods.
- `nirs4all` already has opt-in `MethodsSNV` and `MethodsPLS` wrappers that
  dispatch to the `n4m` Python binding.
- `nirs4all/pipeline/dagml` can execute those wrappers through the generic
  host-controller path. This is a Python host operator path, not a direct
  dag-ml-native n4m controller.
- `dag-ml` itself has generic `ControllerManifest`, process-adapter, artifact,
  and runtime-controller infrastructure, but no live `n4m` or
  `nirs4all-methods` source path in crates/examples/Cargo.

## methods/sklearn parity evidence

`nirs4all-methods` evidence:

- The cross-binding harness treats `benchmarks/parity_timing/registry.py` as
  the method source of truth and records canonical call paths, external
  references, tolerances, and benchmark cells
  (`benchmarks/cross_binding/README.md:8`).
- The orchestrator has internal n4m/pls4all rows plus external sklearn/R/MATLAB
  reference rows (`benchmarks/cross_binding/orchestrator.py:80`).
- PR CI has "External-reference parity gate (Gate 2 - n4m vs scikit-learn
  oracle)" for `pls`, `pcr`, `recursive_pls`, `ridge_pls`, `gpr_pls`,
  `bagging_pls`, and `random_subspace_pls`
  (`.github/workflows/cross-binding-parity.yml:69`).
- That gate fails the job if any n4m row has `reference_parity_ok is not True`
  (`.github/workflows/cross-binding-parity.yml:102`,
  `.github/workflows/cross-binding-parity.yml:108`).
- The full registry sweep exists as nightly/non-blocking evidence; it runs
  `--algorithms all --registry-cells --canonical-pls4all-only
  --reference-backends registry` but comments state `main()` always exits 0 and
  the CSV carries verdicts (`.github/workflows/nightly-parity.yml:68`).
- Historical README coverage says 568/568 internal cells and 143/143
  registry-declared external cells were OK, but explicitly marks those numbers
  as historical smoke evidence until dual-gate fixes land
  (`benchmarks/cross_binding/README.md:151`).
- The core parity-gate text says preprocessing/signal/baseline/augmenter/etc.
  fixtures are C++ ctest asserted, but PLS/SIMPLS/PCR/OPLS/CV/model fixtures
  are not yet asserted by in-tree C++ ctest and are currently covered by the
  per-PR sklearn-oracle and cross-binding harness
  (`.github/workflows/parity-gate.yml:157`).

Targeted verification run:

- Passed:
  `PYTHONPATH=bindings/python/src /home/delete/.local/bin/pytest bindings/python/tests/test_sklearn_regressors.py bindings/python/tests/test_sklearn_slice.py -q`
  -> `70 passed in 1.62s`.
- Local source binding smoke:
  `n4m import OK (2, 0, 0) .../bindings/python/src/n4m/lib/libn4m.so`;
  `pls4all import OK 0.99.0`.

## n4m execution-path audit in nirs4all

Existing opt-in operators:

- `nirs4all/operators/methods/n4m_ops.py` imports
  `n4m.transform.scatter.SNV` with an older-wheel fallback to
  `n4m.sklearn.preprocessing.SNV` (`n4m_ops.py:17`).
- It imports `n4m.estimators.regression.latent.PLS` with an older-wheel
  fallback to `n4m.sklearn.native_sweeps.NativePLSRegressor`
  (`n4m_ops.py:25`).
- `METHODS_AVAILABLE` is true only when both n4m-backed operators import
  (`n4m_ops.py:33`).
- `MethodsSNV` is a sklearn transformer wrapper around native SNV
  (`n4m_ops.py:41`).
- `MethodsPLS` is a sklearn regressor wrapper around native PLS
  (`n4m_ops.py:95`). It is currently single-target PLS1 and pins one candidate
  component count to match fixed-component sklearn PLS (`n4m_ops.py:128`).

Existing tests:

- `tests/unit/operators/methods/test_n4m_ops.py` declares coverage for
  packaging/import, SNV fixture parity, SNV->PLS parity vs sklearn, and
  dual-engine execution (`test_n4m_ops.py:1`).
- The test module skips if `n4m` is absent (`test_n4m_ops.py:25`), so current
  normal CI does not force methods-installed coverage.
- It checks import/lib resolution (`test_n4m_ops.py:56`), JSON-serializable
  params (`test_n4m_ops.py:76`), SNV fixture parity at `atol=1e-12`
  (`test_n4m_ops.py:109`), PLS prediction parity vs sklearn with
  `max_diff < 1e-9` (`test_n4m_ops.py:155`), and both `legacy` and `dag-ml`
  engines (`test_n4m_ops.py:207`).

dag-ml host path in nirs4all:

- `nirs4all/pipeline/dagml_bridge.py` emits generic controller manifests for
  `transform`, `y_transform`, `model`, `prediction_join`, and meta-model nodes.
  These bind by node kind and use empty selectors for catch-all transform/model
  execution (`dagml_bridge.py:1008`, `dagml_bridge.py:1016`).
- The generic model manifest emits prediction and artifact ports and declares
  `emits_predictions`, `emits_artifacts`, and `stateful`
  (`dagml_bridge.py:1057`).
- `operator_routing.py` imports fully qualified transform/y-transform classes
  and accepts either short allow-table model names or model FQNs
  (`operator_routing.py:38`, `operator_routing.py:68`).
- `node_runner.py` executes real nirs4all/sklearn operators over real
  `SpectroDataset` rows (`node_runner.py:1`).
- The top docstring is stale or over-conservative: it says cross-node feature
  chaining is unresolved (`node_runner.py:18`), but the current code reconstructs
  a linear upstream X chain (`node_runner.py:225`) and wraps upstream transforms
  plus model in an sklearn pipeline (`node_runner.py:365`).
- REFIT artifacts are currently stored as in-process sklearn/joblib estimator
  artifacts (`node_runner.py:492`), not n4m-native artifacts.

Targeted nirs4all verification:

- `.venv/bin/python -m pytest tests/unit/operators/methods/test_n4m_ops.py -q`
  was blocked by missing `matplotlib` in `tests/conftest.py`.
- Minimal import smoke in the nirs4all venv passed:
  `n4m import OK`, ABI `(1, 22, 0)`,
  `METHODS_AVAILABLE True`.
- Direct pipeline smoke outside pytest passed:
  `MethodsSNV -> MethodsPLS` on both engines.
  Results:
  - `legacy OK best_rmse 0.008704768967814898`
  - `dag-ml OK best_rmse 0.008704769005886844`

CI gap:

- `nirs4all` hard-depends on `dag-ml`/`dag-ml-data` (`pyproject.toml:93`) but
  does not depend on `nirs4all-methods` and has no optional extra for it in the
  inspected dependency section (`pyproject.toml:101`).
- `nirs4all` CI installs `requirements-test.txt` and then `pip install -e .
  --no-deps`; it does not install `nirs4all-methods`
  (`.github/workflows/CI.yaml:70`, `.github/workflows/CI.yaml:86`).

## dag-ml n4m source-path audit

No live direct n4m integration was found in `dag-ml` source:

- Command checked:
  `rg -n "\\bn4m\\b|pls4all|nirs4all-methods|nirs4all_methods" crates examples .github Cargo.toml Cargo.lock -g '!target/**'`
- Result: no matches.

What does exist in `dag-ml`:

- Generic `ControllerCapability`, including prediction/artifact/stateful and
  aggregation capabilities (`crates/dag-ml-core/src/controller.rs:18`).
- Generic `ArtifactPolicy` values: `serializable`, `host_only`,
  `content_addressed`, `replay_required` (`controller.rs:60`).
- Generic `ControllerManifest` with ports, selectors, fit scope, RNG policy,
  and artifact policy (`controller.rs:117`).
- A registry that resolves controllers by requested ID or selectors and fails
  on ambiguous controllers (`controller.rs:292`).
- CLI process runtime controllers that register one process adapter per
  controller manifest (`crates/dag-ml-cli/src/main.rs:3513`,
  `main.rs:4388`).

Conclusion: there is no dag-ml-native n4m controller today. The working n4m
path is `nirs4all` Python host operator -> generic dag-ml host controller.

## V1 n4m controller scope/cost

### Minimal V1: sklearn-only with methods-installed gate

Scope:

- Keep generic `controller:nirs4all.model` and `controller:nirs4all.transform`.
- Keep `MethodsSNV` and `MethodsPLS` as opt-in sklearn-contract operators.
- Add a dedicated CI job that installs or builds `nirs4all-methods`, then runs
  the methods operator tests without allowing skips.
- Document the operator path as "Python host controller using n4m binding", not
  "dag-ml-native n4m".

Estimated cost: 1-2 engineering days. Low contract risk.

### Minimal direct n4m controller

Scope:

- Add explicit manifests, for example `controller:n4m.transform.snv` and
  `controller:n4m.model.pls`, with non-empty selectors for the FQNs/refs. Avoid
  colliding with the generic catch-all nirs4all controller.
- Implement a host controller that translates `NodeTask` data views to
  `n4m_matrix_view_t` inputs. The C ABI supports row-major, column-major, and
  strided matrix views (`cpp/include/n4m/n4m.h:150`).
- Manage `n4m_context_t` lifecycle, thread counts, seeds, error propagation,
  and ABI checks.
- For models, call `n4m_model_predict`/`n4m_model_predict_alloc`
  (`n4m.h:754`).
- For artifacts, use `n4m_model_export_size`,
  `n4m_model_export_to_buffer`, and `n4m_model_import_from_buffer`
  (`n4m.h:796`). This means `artifact_policy=content_addressed` or
  `serializable` is viable for fitted n4m models. `host_only` is only a simpler
  temporary fallback.
- Add parity fixtures covering NodeTask -> n4m predictions and artifact
  replay, plus mismatch/error cases.

Estimated cost:

- Python-host n4m-specific controller over the existing `n4m` binding: 2-4 days.
- Rust/C direct controller over `libn4m`: 1-2 weeks for a narrow PLS/SNV slice,
  because it adds FFI build/link/discovery, memory ownership, artifact payload,
  and cross-platform CI concerns.
- Full methods catalog controller: larger program, not a V1 slice.

## Release gates for methods-installed

Recommended gates before advertising V1 methods integration:

1. `nirs4all-methods` existing gates:
   - CMake/CTest and ABI snapshots per repo guidelines.
   - `cross-binding-parity.yml` Gate 2 against scikit-learn oracle.
   - `PYTHONPATH=bindings/python/src ... pytest bindings/python/tests/test_sklearn_regressors.py bindings/python/tests/test_sklearn_slice.py -q`.

2. `nirs4all` new methods-installed gate:
   - Install `nirs4all-methods` wheel from the sibling build or PyPI candidate.
   - Preflight `python -c "import n4m; import nirs4all.operators.methods as m; assert m.METHODS_AVAILABLE"`.
   - Run `tests/unit/operators/methods/test_n4m_ops.py` with skip forbidden or
     a separate non-skipping smoke script.
   - Include one direct `legacy` and one `dag-ml` run over `MethodsSNV ->
     MethodsPLS`.

3. If a direct dag-ml n4m controller is added:
   - `cargo fmt --all --check`
   - `cargo clippy --workspace --all-targets -- -D warnings`
   - `cargo test --workspace`
   - `python3 scripts/validate_contracts.py`
   - Process-adapter or C-ABI conformance fixture for n4m fit/predict/artifact
     replay.

## Recommendation

Ship V1 as sklearn-only host-controller integration plus a required
methods-installed gate. This uses the current working path, validates the real
value proposition, and avoids new cross-repo controller contracts before
ARB-003 is accepted.

Treat direct n4m as V1.1 or V2:

- Start with PLS/SNV only.
- Use explicit manifests and selectors, not generic catch-all manifests.
- Use n4m serializable/content-addressed model buffers for artifacts.
- Keep Python-host and direct-C-ABI paths separated in reports and docs, so
  "uses n4m numerics" is not confused with "dag-ml owns native n4m execution".

## Sync-board handoff for A0

Suggested lane update:

- A5 methods/n4m: report complete. Recommendation is V1 sklearn-host path with
  mandatory methods-installed CI; direct n4m controller deferred until ARB-003
  and a narrow controller contract are accepted.

Suggested worklog entry:

- 2026-06-30 A5 audited nirs4all-methods parity gates, nirs4all opt-in n4m
  operators, nirs4all/pipeline/dagml host-controller execution, and dag-ml live
  source references. Verified methods Python sklearn tests (70 passed) and a
  direct nirs4all legacy/dag-ml methods pipeline smoke. Found no live direct
  n4m path in dag-ml crates/examples/Cargo. Report:
  `docs/agent_reports/A5_A5-methods.md`.

## Tests and commands run

- `PYTHONPATH=bindings/python/src /home/delete/.local/bin/pytest bindings/python/tests/test_sklearn_regressors.py bindings/python/tests/test_sklearn_slice.py -q`
  - Passed: `70 passed in 1.62s`.
- `.venv/bin/python -m pytest tests/unit/operators/methods/test_n4m_ops.py -q`
  - Blocked before collection: `ModuleNotFoundError: No module named 'matplotlib'`
    from `tests/conftest.py`.
- `.venv/bin/python` import smoke in `nirs4all`
  - Passed: `n4m import OK`, `METHODS_AVAILABLE True`.
- `.venv/bin/python` direct methods pipeline smoke in `nirs4all`
  - Passed for `legacy` and `dag-ml`.
- `rg` audit in `dag-ml` for live n4m/pls4all references
  - No matches in crates/examples/.github/Cargo files.

## Blockers

No blocker for the report. The only local test blocker was the incomplete
`nirs4all/.venv` test dependency set (`matplotlib` missing), worked around with
a direct smoke script.
