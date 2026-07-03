# Wave 4W - Strict dag-ml, WASM, Studio, Datasets Gates

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

Wave 4W integrates the post-reset review batch requested after the skip/xfail
and provider-role discussion. It does not run full Python parity; it closes
targeted strict dag-ml API gaps, removes locally coverable Studio skips, makes
Core WASM/Methods parity skips fail explicitly in strict mode, and pins a
non-Python Datasets-to-IO bridge contract.

## Agents And Reviews

- Claude Code read-only review session `7aecd5c4-6b84-4df2-b770-68b01ec4ced8`
  reviewed RC separation and called out the missing strict dag-ml proof, Studio
  skip accounting, Core/Methods WASM artifact gap, non-Python datasets bridge
  gap, and GitGuardian PR-ref residue.
- Codex agent `019f259d-145f-7182-968c-0891cb405d6f` owned Studio skip burn-down.
- Codex agent `019f259d-159f-7440-8a0e-46b5c9cac99f` owned Core/Methods WASM
  strict artifact preflight.
- Codex agent `019f259d-16ca-7c91-8bbf-154d77808a6e` owned Datasets non-Python
  bridge proof.
- Codex agent `019f259d-189a-74e2-9158-f2c5a4fd0395` reviewed Python strict
  dag-ml failures and identified the native `.n4a` explain gap.

## Integrated Heads

- `nirs4all` Python: `6a2c7200`
  - `3f89ff44 test(api): align strict dagml public API gates`
  - `6a2c7200 fix(api): support native dagml bundle explain`
- `nirs4all-core`: `f120c28`
  - `f120c28 test(core): preflight strict wasm methods parity`
- `nirs4all-studio`: `75f511b`
  - `75f511b test(studio): remove local skip gates`
- `nirs4all-datasets`: `259d1445`
  - `259d1445 test(datasets): pin non-python io bridge contract`
- `nirs4all-ecosystem`: aggregation lock regenerated after Core/Datasets moved.

The branches and tag `n4a-v1-rc1-2026.07-refactor` were pushed for Python,
Core, Studio, and Datasets after review.

## Tests Run

Python strict dag-ml targeted gates:

- `pytest tests/integration/api/test_dagml_native_retrain_roundtrip.py -q` with
  RC `dag-ml`/`dag-ml-data` paths: `2 passed`.
- `pytest tests/integration/api/test_module_api.py tests/integration/api/test_predict_explain_retrain_happy_path.py tests/integration/api/test_dagml_native_retrain_roundtrip.py -q`: `28 passed`.
- `ruff check nirs4all/pipeline/explainer.py tests/integration/api/test_dagml_native_retrain_roundtrip.py tests/integration/api/test_predict_explain_retrain_happy_path.py tests/integration/api/test_module_api.py`: passed.
- `git diff --check`: passed.

Core/WASM:

- `PYTHONPATH=bindings/python/src python3.11 -m unittest -v bindings/python/tests/test_release_topology.py`: `12 tests OK`.
- `npm test --prefix bindings/wasm` with Linux Node `v22.21.1`: `13 passed, 2 skipped`.
- `make check-wasm-methods-artifact NIRS4ALL_METHODS_ROOT=../RC-v1-methods`: expected strict failure; missing `index.js`, `n4m.js`, `n4m.wasm`.
- `git diff --check`: passed.

Studio:

- `pytest tests/test_env_coherence.py tests/test_operators_manifests.py tests/test_pipeline_canonical.py`: `65 passed`.
- `ruff check api/system.py tests/test_env_coherence.py tests/test_operators_manifests.py tests/test_pipeline_canonical.py`: passed.
- `eslint electron/portable-paths.test.ts`: passed.
- `vitest run electron/portable-paths.test.ts`: `4 passed`.
- Full backend: `2335 passed, 301 warnings`, `0 skipped`.

Datasets:

- `rtk pytest tests/test_index.py -q`: `11 passed`.
- `rtk cargo test -p nirs4all-datasets-core`: `32 passed`.
- `rtk cargo test --workspace`: `35 passed`.
- `rtk cargo clippy --workspace --all-targets -- -D warnings`: passed.
- `rtk cargo fmt --all --check`: passed.
- `rtk ruff check tests/test_index.py`: passed.
- R smoke not run: `Rscript` is not installed.
- WASM Node smoke not run: `bindings/wasm/pkg-node` build artifact is absent.

Ecosystem:

- `python3.11 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate ...`: regenerated lock.
- `python3.11 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate ...`: passed.
- `pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py`: `16 passed`.
- `python3.11 scripts/n4a_release_surface_matrix.py validate`: passed.

## Decisions

- Strict dag-ml public API no longer accepts legacy workspace/session semantics
  implicitly. Tests now pin `workspace_path` and `Session` as legacy-mode public
  API contracts, while strict native uses `results_path`.
- Native `.n4a` explain uses the exported composite `_DagmlExportedModel`
  directly. Replaying `minimal_pipeline` is cosmetic for native single-model
  bundles and cannot deserialize the underlying Python `PLSRegression` label.
- Core WASM parity remains skipped in normal local runs when Methods JS/WASM
  artifacts are absent, but strict release mode now fails before comparison
  with a build/stage instruction.
- Datasets non-Python consumers are contract consumers, not Python provider
  consumers: `catalog/index.json -> n4ds_resolve -> descriptor-rich resolved
  contract -> nirs4all-io DatasetSpec` is now golden-tested.
- Studio skips that can be simulated locally are removed. Windows-host behavior
  is still a real host gate, not claimed by Linux simulation.

## GitGuardian State

Current remote branch/tag heads for `nirs4all-cluster` remain clean:

- `origin/main`: `97b2b38`
- `origin/rc/v1-full-refactor`: `9d6ab34`
- `n4a-v1-rc1-2026.07-refactor`: `9d6ab34`

`refs/pull/1/head` and `refs/pull/2/head` are merged hidden GitHub PR refs and
still contain placeholder examples `--token dev`. Source branches are deleted
and normal branch/tag pushes do not control those generated refs. No real
token value was found locally; if the GitGuardian alert exposes a true value in
its UI, rotate it externally and close the alert there or via GitHub support.

## Risks

- Full Python reference parity was intentionally not rerun in this wave; run it
  after the next large batch.
- Core WASM/Methods strict parity still needs a built/staged Methods JS/WASM
  distribution.
- R, Octave/MATLAB, and end-to-end non-Python DatasetPackage materialization
  remain environment gates.
- Studio full backend has zero skips, but frontend full Vitest was not rerun in
  this wave; only skip candidates and prior Wave 4V e2e evidence were used.
