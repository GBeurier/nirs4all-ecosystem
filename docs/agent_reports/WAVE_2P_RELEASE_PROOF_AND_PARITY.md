# Wave 2P Release Proof And Parity

Date: 2026-07-01T14:25:46+02:00

## Scope

Follow-up after W2O and Faraday read-only audit. Claude is not used.
`nirs4all-drafts` and `nirs4all-lab` remain out of scope.

Full Python-reference parity is still deferred until this wave has produced a
larger batch of release-scope, conformance, methods, and runtime fixes. Do not
treat targeted W2M/W2N/W2O gates as release-equivalent to W98 full parity.

## Starting State

- Selected release root: `/home/delete/nirs4all/_release_roots/W2L-selected`.
- The selected root validates the aggregation lock after W2O.
- The current workspace root is not the proof root: primary `dag-ml`,
  `dag-ml-data`, and `nirs4all-io` states diverge from the selected pins.
- `nirs4all/refactor/L17-pyref` is not the V1 proof branch. The current
  integration proof branch is `_worktrees/INT-nirs4all` at `799f789c`.
- Historical `W*` worktrees and the Claude-era `.claude/worktrees/agent-*` tree
  are audit inputs only. They are not merge sources for this wave.
- The roadmap requirement is explicit: public `nirs4all` V1 accounting covers
  the Python oracle package, the aggregate R package, and browser/WASM
  distribution surfaces. A Python-only check cannot close `nirs4all`.

## Faraday Audit Summary

Read-only reviewer: `019f1d9d-bbfb-7d73-a424-73057432eca6`.

Findings carried into W2P:

- Release proof root must be unique. Use selected-root for gates, not the dirty
  current workspace root.
- Full Python-reference parity has not been rerun since W98
  (`804 passed, 32 skipped, 11 xfailed`, `fallback=0`).
- The release matrix is currently a pointer to the draft inventory; the
  aggregate lock covers seven components, not every public V1 product surface.
- R surface is topology-gated but skipped locally because R is unavailable.
- IO W2O did not rerun cross-CLI `dag-ml` / `dag-ml-data` conformance.
- Methods/native binding parity remains weak: SNV is opt-in, PLS is not routed,
  and installed `n4m` is not loadable locally.
- Studio Playwright and cluster e2e remain environment gates, not green proof.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| A/K | `019f1da6-05b9-7f63-8391-16c453f5ec51` / Meitner | `nirs4all-ecosystem` release docs/scripts only | Integrated: `e1aeb50 docs(release): add public v1 surface matrix` |
| G | `019f1da6-066e-7e23-aa33-619def5fb4e4` / Sartre | `_worktrees/INT-io` only | Integrated: `eae8263 test(io): add strict dag-ml-data conformance command` |
| F | `019f1da6-06f3-7853-9f7a-144f743d1d53` / Ohm | `nirs4all-methods` only | Integrated: `00ca8467 test(python): add installed n4m load smoke` |
| H | `019f1da6-8cf5-7e82-af72-80fcb4c3e11f` / Curie | `_worktrees/INT-studio` only | Integrated: `17dfe69 test(e2e): isolate Studio runtime ports` |
| J | `019f1da6-8d87-7dd0-8e28-d7887657874c` / Lorentz | read-only | Audited repo/benchmarks/papers/provider plugin gaps; no files modified. |

## Review Criteria

- Agents must read the local `AGENTS.md` / `CLAUDE.md` for their touched repo
  before editing.
- No agent may touch `nirs4all-drafts` or `nirs4all-lab`.
- No agent may merge or cherry-pick historical `W*` worktrees without a fresh
  diff audit and explicit integration review.
- Any pipeline, prediction, save/export, converter, runtime, or binding change
  must preserve or test parity with the current Python `nirs4all` oracle.
- R skipped because missing runtime is recorded as risk, not as a green gate.
- No tests may be reduced, xfailed, or hidden behind broad fallbacks to obtain a
  green result.

## Expected Gates

- Targeted tests for each changed repo.
- Release lock validation if a lock member changes.
- Cross-CLI `dag-ml` / `dag-ml-data` / IO conformance if Lane G changes code or
  test contracts.
- No full `pyref_oracle_full` until this wave accumulates a substantial batch.

## Integration Log

### Release Scope - Meitner

Files modified:

- `docs/RELEASE_DISTRIBUTION_MATRIX.md`
- `docs/contracts/release/public-v1-surface-matrix.n4a.json`
- `scripts/n4a_release_surface_matrix.py`
- `tests/test_release_surface_matrix.py`

Decision:

- The aggregation lock remains bounded to seven aggregate members:
  `dag_ml`, `dag_ml_data`, `methods`, `formats`, `io`, `lite`, `datasets`.
- Public V1 release accounting is now represented separately in
  `public-v1-surface-matrix.n4a.json`.
- `nirs4all` V1 is explicitly non-Python-only:
  - Python historical/oracle package `nirs4all`, outside the aggregation lock.
  - R aggregate package `nirs4all`, covered by locked member `lite`.
  - Browser/WASM aggregate `nirs4all` and scoped `@nirs4all/*` packages, covered
    by locked members where declared.

Tests run:

- `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q`
  - `9 passed`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_release_surface_matrix.py report`
- `python3 -m json.tool docs/contracts/release/public-v1-surface-matrix.n4a.json >/dev/null`
- `git diff --check`

Risks:

- This matrix is release accounting, not parity proof. R/WASM/product gates
  remain separate and must not be inferred green from the aggregation lock.

### IO Conformance - Sartre

Files modified:

- `.github/workflows/dag-ml-data-conformance.yml`
- `scripts/dag_ml_data_conformance.sh`
- `tests/dag_ml_data/README.md`

Decision:

- Added a strict release-proof command for IO -> `dag-ml-data` cross-CLI
  conformance. It sets `NIRS4ALL_REQUIRE_DAGML_SIBLINGS=1`, so missing sibling
  CLIs are a hard failure rather than a green skip.
- No Python `dag-ml-data` target was added. Python remains on the
  `DatasetPackage` surface; the bridge remains Rust/CLI.

Tests run:

- `scripts/dag_ml_data_conformance.sh`
  - passed for `train_test` and `x_y_separate` through both
    `dag-ml-data-cli validate-envelope` and
    `dag-ml-cli validate-data-binding`
- `cargo test --manifest-path crates/nirs4all-io-dagml/Cargo.toml --config "patch.crates-io.dag-ml-data.path='/home/delete/nirs4all/_worktrees/INT-dmd/crates/dag-ml-data'"`
  - `8 passed`
- `bash -n scripts/dag_ml_data_conformance.sh tests/dag_ml_data/verify_cross_cli.sh`
- `git diff --check`

Risks:

- `single_combined` remains covered by in-process Rust tests, not the convention
  CLI emit path.

### Methods Loadability - Ohm

Files modified:

- `Makefile`
- `bindings/python/scripts/smoke_installed_nirs4all_methods.py`

Decision:

- Added `make test-python-install` as a real installed-wheel smoke for
  `nirs4all-methods` / import `n4m`.
- The smoke generates the package, stages an ABI-compatible `libn4m`, builds a
  wheel with `python -m build`, installs it into a venv, and verifies `n4m`,
  `SNV`, `PLS`, ABI `2.0.0`, and a mini SNV -> PLS execution from the installed
  package.

Tests run:

- `python3 -m py_compile bindings/python/scripts/smoke_installed_nirs4all_methods.py`
- `python3 -m ruff check bindings/python/scripts/smoke_installed_nirs4all_methods.py`
- `python3 -m ruff format --check bindings/python/scripts/smoke_installed_nirs4all_methods.py`
- `make test-python-install`
- `N4M_LIB_PATH=/home/delete/nirs4all/nirs4all-methods/build/dev-release/cpp/src/libn4m.so.2.0.0 PYTHONPATH=bindings/python/src python3 -m pytest bindings/python/tests/test_release_surface_metadata.py bindings/python/tests/test_n4m_context.py -q`
  - `2 passed`
- `git diff --check`

Risks:

- This proves installed binding loadability. It does not route PLS from
  `nirs4all`, and it does not change the opt-in status of the SNV methods route.

### Studio E2E - Curie

Files modified:

- `e2e/fixtures/e2e-env.ts`
- `e2e/fixtures/global-setup.ts`
- `e2e/pages/runs.page.ts`
- `e2e/tests/smoke.spec.ts`
- `playwright.config.ts`
- `vite.config.ts`

Decision:

- Studio Playwright now defaults to isolated e2e ports:
  backend `127.0.0.1:8765`, frontend `127.0.0.1:5174`.
- Reusing an existing server is now explicit via `NIRS4ALL_E2E_REUSE_SERVER`,
  preventing silent contamination by an unrelated process on the old default
  ports.
- Vite proxy targets and backend health checks are derived from the same e2e
  runtime config.

Tests run:

- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm run lint:tsc`
- `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npx playwright test --project=web-chromium --reporter=list`
  - `63 passed`
- Verified ports `8765` and `5174` were free after teardown.
- `git diff --check`

Risks:

- The first validation attempt without the Linux Node path resolved to a Windows
  `npm` / `cmd.exe` and failed on a UNC WSL path. The repo gate is valid with the
  Linux Node path used elsewhere in the release gates.
- Some backend pages still log expected 500s when optional `nirs4all`
  workspace/store dependencies are absent; the Playwright assertions pass.

### Providers / Repo / Benchmarks / Papers - Lorentz

Read-only result:

- `nirs4all-providers` now exists and provides a soft-import
  `ProviderPlugin` layer with `PipelineProvider`, `BenchmarkProvider`, and
  `PaperExportProvider`. The old B12 review statement that these interfaces were
  absent is partially superseded.
- The provider layer is still a read slice: it serves/plans/exports metadata but
  does not prove reproducible execution or numerical portability.

Gaps carried forward:

- Benchmarks queue/evaluate is not an execution runner; runtime/cluster still
  owns execution.
- Papers replay is still browser JS approximate, not `libn4m` WASM parity.
- Native `.n4a` / workspace cross-engine parity remains the shared blocker.
- `nirs4all-providers` needs an explicit release decision: public package vs
  absorbed core/lite surface.

## Integration Gate

After integrating W2P lanes:

- Release lock regenerated from
  `/home/delete/nirs4all/_release_roots/W2L-selected`.
  - `io`: `b958a290` -> `eae8263`
  - `methods`: `46912485` -> `00ca8467`
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - passed
- `python3 scripts/n4a_release_surface_matrix.py validate`
  - passed
- `python3 -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py -q`
  - `9 passed`
- `N4A_RELEASE_WORKSPACE_ROOT=/home/delete/nirs4all/_release_roots/W2L-selected python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --skip pyref_oracle_full --json`
  - passed

`pyref_oracle_full` remains intentionally skipped for W2P. W2P changed release
accounting, IO conformance proof, methods binding loadability, and Studio e2e
isolation; it did not change `nirs4all` core prediction/pipeline behavior. Full
Python-reference parity remains due for the next large core/native cutover or
final `LOCK-DROP` proof.
