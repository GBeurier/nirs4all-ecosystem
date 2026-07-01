# W98 To Post-W2P Delta Ledger

Date: 2026-07-01T15:03:46+02:00

## Scope

This ledger records the evidence delta from the W98 full Python-reference parity
gate through the post-W2P release proof state.

It is intentionally a ledger, not a new parity proof. The full
`pyref_oracle_full` gate was not rerun for W2M, W2N, W2O, W2P, or this report.
All W2M-W2P results below are targeted gates and must not be read as equivalent
to the W98 full parity run.

Source inputs read for this ledger:

- `AGENTS.md`
- `docs/PARALLEL_REFACTORING_ROADMAP.md`
- `docs/agent_reports/W98_FULL_PYREF_PARITY.md`
- `docs/agent_reports/WAVE_2M_CURRENT_STATUS.md`
- `docs/agent_reports/WAVE_2N_CONTROLLER_AND_BINDING_SURFACES.md`
- `docs/agent_reports/WAVE_2O_CLUSTER_IO_TOOLS.md`
- `docs/agent_reports/WAVE_2P_RELEASE_PROOF_AND_PARITY.md`
- `docs/contracts/release/public-v1-surface-matrix.n4a.json`

## W98 Baseline

Last full Python-reference parity proof:

| Field | W98 evidence |
| --- | --- |
| Worker worktree | `_worktrees/W98-nirs4all-full-parity` |
| Worker branch | `refactor/W98-full-parity-gate` |
| Worker commit | `23155948 test(parity): gate strict dag-ml cutover surfaces` |
| Integration merge | `17ed929e Merge branch 'refactor/W98-full-parity-gate' into refactor/integration-nirs4all` |
| Full command | `PYTHONPATH=/home/delete/nirs4all/_worktrees/W98-nirs4all-full-parity /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -q -ra` |
| Full result | `804 passed, 32 skipped, 11 xfailed` |
| Runtime | `1885.90s` |
| Log | `/tmp/w98_full_parity.log` |
| Fallback accounting | `coverage_meter --check`: `fallback=0, target=0` |

Known W98 outcome buckets:

- Pass: `804` full parity tests passed.
- Skip: `32` documented skips remained in the parity suite.
- Xfail: `11` strict xfails remained from the existing parity ledger.
- Fallback: `0` expected fallback paths; W98 recorded `fallback=0`.

W98 also added or tightened targeted coverage for structured example refusals,
named-dict stacking execution, fallback diagnostics in `RtResult`, and
no-partial-bundle behavior for native export refusals.

## Post-W98 Targeted Gates

### W2M

Proof commits and pins:

- `8b226bed0b6c feat(bindings): expose controller manifest derivation`
- `a428926cf8b4 build(py): refresh dag ml extension binary`
- `06b574cf6239 feat(dagml): add opt-in methods SNV route`
- ecosystem follow-up evidence includes `c785efc chore(release): update dagml lock pin`
  and `9be4c18 docs(release): record wave 2m implementation batch`

Targeted gates recorded:

- Selected-root release-lock validation passed for
  `/home/delete/nirs4all/_release_roots/W2L-selected`.
- Non-full cutover gates passed with `--skip pyref_oracle_full`.
- `dag-ml` controller derivation gates passed:
  `cargo test -p dag-ml-core controller_adapter`, PyO3 derivation tests,
  WASM derivation tests, `cargo fmt`, `cargo clippy`, contract validation with
  and without `DAG_ML_DATA_REPO`, `.so` freshness, Python import smoke, and
  `git diff --check`.
- `nirs4all` opt-in methods SNV route gates passed:
  operator routing unit tests, ruff, mypy, `git diff --check`, and selected
  dag-ml dataplane/run-selector integration tests.

Limits carried forward:

- `pyref_oracle_full` was intentionally skipped.
- `tests/unit/operators/methods/test_n4m_ops.py -m methods` skipped locally
  because `n4m` was not installed/loadable.
- The new methods route is opt-in SNV only; PLS auto-routing was explicitly
  deferred.
- Current-root release-lock validation was still not clean because the selected
  integration roots differed from the primary current checkouts, and
  `dag-ml-data` had a preexisting dirty generated binary.

### W2N

Proof commits:

- `799f789c feat(runtime): derive controller manifests through dagml`
- `8fa133b test(release): gate v1 python r wasm surfaces`
- `6e96c24 chore(release): record wave 2n integration`

Targeted gates recorded:

- Selected-root release-lock validation passed.
- Non-full cutover gates passed with `--skip pyref_oracle_full`.
- `nirs4all` controller-manifest gates passed, including runtime/unit tests,
  parity-adjacent dag-ml bridge/dataplane/run-selector tests, ruff, mypy,
  py_compile, and Studio operator manifest tests.
- `nirs4all-lite` Python and WASM release-surface gates passed.
- R gate was availability-aware and skipped because R was not installed locally.

Limits carried forward:

- `pyref_oracle_full` remained due.
- R topology was gated, but local R execution was not proven.
- Helper-derived controller manifests can be richer than legacy fallback dicts;
  downstream consumers must treat the accessor as contract JSON.

### W2O

Proof commits:

- `dc29840 test(rbac): cover read-only cluster rights`
- `fd51610 test(legacy): lock preserved prediction arrays golden`
- `b958a29 docs(io): align dagml data bridge status`
- `27a6190 chore(release): record wave 2o integration`

Targeted gates recorded:

- Selected-root release-lock validation passed.
- Non-full cutover gates passed with `--skip pyref_oracle_full`.
- Cluster RBAC/CLI targeted pytest passed: `42 passed`; ruff passed.
- Tools legacy golden targeted tests passed: full file `5 passed`; ruff passed.
- IO DatasetPackage/status gates passed: `tests/test_dataset_package.py`
  `6 passed`, ruff passed, `cargo fmt --all --check` passed, and targeted
  `nirs4all-io-cli` cargo test passed.

Limits carried forward:

- No cluster end-to-end validation script ran in W2O.
- Cross-CLI `dag-ml` / `dag-ml-data` / IO conformance was not rerun in W2O; it
  was added and run later in W2P.
- The IO change aligned docs/status and rejection-path tests; it did not move
  dataset assembly out of `nirs4all-io` or add a Python `dag-ml-data` load
  target.

### W2P

Proof commits:

- `e1aeb50 docs(release): add public v1 surface matrix`
- `eae8263 test(io): add strict dag-ml-data conformance command`
- `00ca8467 test(python): add installed n4m load smoke`
- `17dfe69 test(e2e): isolate Studio runtime ports`
- `021f33d chore(release): record wave 2p integration`

Targeted gates recorded:

- Release lock regenerated from
  `/home/delete/nirs4all/_release_roots/W2L-selected`:
  `io` moved `b958a290` -> `eae8263`; `methods` moved `46912485` -> `00ca8467`.
- Selected-root release-lock validation passed.
- Public V1 surface matrix validation passed.
- Ecosystem release-surface tests passed:
  `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q`
  -> `9 passed`.
- Non-full cutover gates passed with `--skip pyref_oracle_full`.
- Strict IO cross-CLI conformance command passed for `train_test` and
  `x_y_separate`; Rust bridge tests passed: `8 passed`.
- Methods installed-wheel smoke passed through `make test-python-install`;
  targeted methods metadata/context pytest passed: `2 passed`.
- Studio targeted gate passed with Linux Node path:
  `npm run lint:tsc` and Playwright web-chromium `63 passed`; isolated ports
  were free after teardown.

Limits carried forward:

- `pyref_oracle_full` remained intentionally skipped.
- W2P changed release accounting, IO conformance proof, methods binding
  loadability, and Studio e2e isolation; it did not change or fully reprove
  `nirs4all` core prediction/pipeline behavior.
- IO `single_combined` remains covered by in-process Rust tests, not the
  convention CLI emit path.
- Methods loadability proof does not route PLS from `nirs4all` and does not
  change the opt-in status of the SNV methods route.
- Studio Playwright assertions passed, but optional backend dependencies still
  produced expected logged 500s in some pages.

## Release Surface Boundaries

The public V1 surface matrix makes the release boundary explicit:

- The aggregation lock covers seven aggregate members:
  `dag_ml`, `dag_ml_data`, `methods`, `formats`, `io`, `lite`, `datasets`.
- The aggregation lock is not the complete public V1 product matrix.
- The Python historical/oracle package `nirs4all` is outside the aggregation
  lock; its full parity remains a separate gate.
- The R aggregate package is covered by the locked `lite` member, but missing
  local R runtime is a recorded risk, not green proof.
- Browser/WASM aggregate and scoped WASM packages are covered by locked members
  where declared, but browser/runtime parity and product e2e remain separate
  gates.
- Studio, Web, tools, and cluster are public/product/support surfaces outside
  the aggregation lock and require their own environment gates when their
  release claims change.

## Remaining Risks

- Full parity due: the last full Python-reference parity result remains W98
  (`804 passed, 32 skipped, 11 xfailed`, `fallback=0`). W2M-W2P targeted gates
  are not release-equivalent.
- R skipped: R release topology is represented and gated, but local execution
  skipped because R was unavailable. This is not a green R release proof.
- Current-root mismatch: the valid release proof root is the selected root
  `/home/delete/nirs4all/_release_roots/W2L-selected`, not the current workspace
  root. Primary branch identities and dirty/generated state can still diverge
  from selected pins.
- Python oracle checkout mismatch: `nirs4all/refactor/L17-pyref` is not the V1
  proof branch. The W98/W2N proof path is through `_worktrees/INT-nirs4all`.
- Methods route: `nirs4all` has opt-in SNV routing only. PLS is not routed from
  `nirs4all`, and methods/kernel parity is not a substitute for full pipeline
  parity.
- Provider execution: `nirs4all-providers` has a soft-import provider layer for
  metadata/planning/export, but reproducible execution and numerical
  portability are not proven.
- Product/environment gates: cluster e2e, Web/product browser gates, and broader
  Studio runtime/product gates remain scoped environment proofs, not implied by
  the aggregation lock.

## Decisions

- Treat W98 as the current full Python-reference parity baseline until a new
  full gate is run.
- Treat W2M-W2P as targeted release delta evidence only.
- Use selected-root validation for release-lock proof; do not infer proof from
  the current workspace root.
- Do not mark R, provider execution, PLS routing, browser product parity, or
  final `LOCK-DROP` as green from the W2M-W2P targeted gates.
- Do not modify the release lock from this ledger.
