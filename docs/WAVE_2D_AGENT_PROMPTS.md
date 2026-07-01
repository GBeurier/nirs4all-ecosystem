# Wave-2D agent prompts

**Date:** 2026-07-01
**Supervisor:** Codex API session
**Base state:** Wave-2C successful commits merged into tested integration
branches. External interactive Claude CLI PIDs `208304` and `208423` exist at
the workspace root and must be left untouched.

Agents must not edit `PARALLEL_REFACTORING_SYNC.md` or
`AGENT_RUN_SUPERVISION.md`. Each agent writes exactly one report under
`nirs4all-ecosystem/docs/agent_reports/` and may commit only in its assigned
worktree/repo when its gates pass. No agent may push.

All agents must inspect current files directly before editing. CodeGraph may be
used as an accelerator, but current files and test output are authoritative.
If an assigned change cannot be implemented safely, the agent must leave code
unchanged, write the precise blocker, and still produce the report.

## Integration bases

| Repo | Branch / worktree | Tip at launch |
|---|---|---|
| `nirs4all` | `_worktrees/INT-nirs4all` / `refactor/integration-nirs4all` | `1cecf6a5` |
| `nirs4all-studio` | `_worktrees/INT-studio` / `refactor/integration-studio` | `fb6f413` |
| `nirs4all-web` | `_worktrees/INT-web` / `refactor/integration-web` | `1a1bdba` |
| `nirs4all-io` | `_worktrees/INT-io` / `refactor/integration-io` | `0a06943` |
| `nirs4all-providers` | `_worktrees/INT-providers` / `refactor/integration-providers` | `2411568` |
| `nirs4all-cluster` | `_worktrees/INT-cluster` / `refactor/integration-cluster` | `7a8d48f` |
| `dag-ml` | `_worktrees/INT-dagml` / `refactor/integration-dagml` | `806a459` |
| `dag-ml-data` | `_worktrees/INT-dmd` / `refactor/integration-dmd` | `e64e6a2` |
| `nirs4all-tools` | `main` | `93f7050` |

## Shared report template

Each report must include:

```text
# Wxx report - <scope>

Summary:
Code changed:
Files touched:
Commits:
Tests run:
Tests not run and why:
Blockers:
Impact on blockers/locks:
Next action:
Sync doc updated: no
```

## W21 - B-010 fallback drain audit + safe lowering

**CWD:** `/home/delete/nirs4all/_worktrees/W21-nirs4all-fallback`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W21-fallback-drain`
**Report:** `docs/agent_reports/W21_FALLBACK_DRAIN.md`

Goal: materially reduce `EXPECTED_FALLBACK` if safe, or produce a precise
code-backed blocker map for every remaining fallback case. Do not claim a case
is native unless the parity tests prove it.

Owned areas: `nirs4all/pipeline/dagml/detect.py`,
`nirs4all/pipeline/dagml/run_paths.py`,
`nirs4all/pipeline/dagml/run_backend.py`,
`tests/integration/parity/coverage_meter.py`,
`tests/integration/parity/test_native_fallback_boundary.py`,
`tests/integration/parity/test_conformance_dual_engine.py`,
and the `EXPECTED_FALLBACK` / compatibility-ledger entries directly tied to
implemented lowering.

Do not edit export, runtime envelope, Studio, Web, or Rust code. If native
lowering needs a Rust scheduler/core feature, document the missing contract
instead of implementing cross-repo changes here.

Gate: targeted parity for changed fallback cases,
`test_native_fallback_boundary.py`, `test_compatibility_ledger.py`,
`py_compile`, Ruff if available.

## W22 - B-011 workspace/artifact `.n4a` parity

**CWD:** `/home/delete/nirs4all/_worktrees/W22-nirs4all-artifacts`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W22-artifact-parity`
**Report:** `docs/agent_reports/W22_ARTIFACT_PARITY.md`

Goal: close the workspace/artifact half of B-011 by adding real cross-engine
round-trip coverage for `.n4a` bundles, workspaces, selected chain/source
artifacts, and native-result provenance. Fix narrow Python-side issues found by
those tests.

Owned areas: `tests/integration/parity/test_conformance_n4a_cross_engine.py`,
`tests/integration/parity/test_conformance_workspace_cross_engine.py`,
`tests/integration/parity/test_conformance_n4a_bundle_parity.py`,
`tests/integration/parity/test_cross_engine_export_surface.py`,
`nirs4all/pipeline/dagml/native_results.py`, and export helpers in
`nirs4all/pipeline/` only when required by tests.

Do not drain fallback cases or touch Studio/Web. If native bundle support is
missing below Python, document the exact missing interface and add an xfail with
an explicit blocker ID rather than a silent skip.

Gate: targeted cross-engine export/workspace tests, native bundle tests,
`py_compile`, Ruff if available.

## W23 - B-011/B-018 error and refusal parity

**CWD:** `/home/delete/nirs4all/_worktrees/W23-nirs4all-errors`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W23-error-parity`
**Report:** `docs/agent_reports/W23_ERROR_PARITY.md`

Goal: make legacy vs dag-ml failure behavior explicit and catchable for
unsupported operators, invalid workspaces, `allowFallback=false`, native backend
unavailable, invalid dataset/spec, and export refusals. Prefer shared
`RtError`/native error mapping over ad hoc exception strings.

Owned areas: `nirs4all/pipeline/dagml/errors.py`,
`nirs4all/pipeline/dagml/rt.py`, `nirs4all/pipeline/dagml/result.py`,
`nirs4all/pipeline/dagml/envelope.py`,
`tests/integration/parity/test_rt_fallback_strict.py`,
`tests/integration/parity/test_cross_engine_export_surface.py`, and new focused
parity tests under `tests/integration/parity/`.

Do not change successful numerical behavior. Do not flip the default engine.
If Rust-native errors need new stable codes, report the exact proposed codes
and leave Rust edits to W29.

Gate: targeted error/refusal tests, runtime-envelope tests,
`test_compatibility_ledger.py`, `py_compile`, Ruff if available.

## W24 - Studio runtime route adoption

**CWD:** `/home/delete/nirs4all/_worktrees/W24-studio-runtime`
**Base:** `refactor/integration-studio`
**Branch:** `refactor/W24-runtime-routes`
**Report:** `docs/agent_reports/W24_STUDIO_RUNTIME_ROUTES.md`

Goal: continue B-017/B-018 by routing more Studio backend endpoints through the
runtime/library contract and preserving requested engine, actual engine,
fallback diagnostics, and `RtError` shape. Prioritize routes that still bypass
runtime despite W14/W15.

Owned areas: `api/runs.py`, `api/runtime_engine.py`, `api/execution_driver.py`,
`api/operators.py`, route tests in `tests/test_runs_engine_routing.py`,
`tests/test_runtime_engine.py`, `tests/test_runs_execution_backend.py`, and
`tests/test_operators_manifests.py`.

Do not do metric/math push-down here; W25 owns compute duplication. Do not
change frontend UI.

Gate: targeted backend tests; if environment is incomplete, run
`python -m compileall` and Ruff on touched files and report missing packages
precisely.

## W25 - Studio compute push-down slice 2

**CWD:** `/home/delete/nirs4all/_worktrees/W25-studio-compute2`
**Base:** `refactor/integration-studio`
**Branch:** `refactor/W25-compute-pushdown2`
**Report:** `docs/agent_reports/W25_STUDIO_COMPUTE_PUSHDOWN2.md`

Goal: reduce duplicated Studio backend computation after W15. Prioritize one
production path among analysis metrics, playground result metrics, spectra
statistics, dataset preprocessing summaries, or chart transforms where a
library/runtime helper already exists or can be called cleanly.

Owned areas: `api/shared/metrics_computer.py`, `api/predict.py`,
`api/analysis.py`, `api/playground/*`, `api/spectra.py`,
`api/preprocessing.py`, and focused tests such as `tests/test_predict_metrics.py`,
`tests/test_analysis_results_repository.py`, `tests/test_playground.py`, or
`tests/test_spectra_perf.py`.

Do not touch engine-recording or route-envelope behavior owned by W24. Do not
move broad UI components.

Gate: targeted backend tests; compileall/Ruff if full test env is incomplete.
Report exactly which compute duplication remains after the slice.

## W26 - Web runtime adoption and served failure smokes

**CWD:** `/home/delete/nirs4all/_worktrees/W26-web-runtime`
**Base:** `refactor/integration-web`
**Branch:** `refactor/W26-runtime-adoption`
**Report:** `docs/agent_reports/W26_WEB_RUNTIME_ADOPTION.md`

Goal: continue B-018 by making Web runtime/fallback semantics harder to regress:
add or improve served browser coverage for forced scheduler/runtime failure,
`RtError` diagnostics, and `allowFallback=false` behavior.

Owned areas: `studio-lite/src/engine/dagml-engine.ts`,
`studio-lite/src/engine/dagml.ts`,
`studio-lite/src/engine/dagml-engine.rt-fallback.test.ts`,
`studio-lite/tests/rt-fallback-smoke.mjs`,
`studio-lite/scripts/run-smokes.mjs`, and focused fixtures.

Do not do visual/product redesign. Do not touch Python Studio.

Gate: `npm ci` if needed, typecheck, Vitest targeted/full, build, and served
smokes. If Node/npm is missing, document the exact environment failure and keep
tests runnable.

## W27 - DatasetPackage public API and provider bridge

**CWD:** `/home/delete/nirs4all`
**Worktrees:** `_worktrees/W27-io-dataset-api`,
`_worktrees/W27-providers-dataset-api`
**Bases:** `refactor/integration-io`, `refactor/integration-providers`
**Branches:** `refactor/W27-dataset-api` in both repos
**Report:** `docs/agent_reports/W27_DATASET_PROVIDER_BRIDGE.md`

Goal: make W17's `DatasetPackage` practically consumable: expose a stable
Python/public API in `nirs4all-io` and add a read-only optional provider bridge
in `nirs4all-providers` that can return/describe packages without duplicating
IO assembly and without adding ecosystem write-back.

Owned areas in `nirs4all-io`: `src/nirs4all_io/spec/*`,
`src/nirs4all_io/materialize/*`, package exports, schema/tests.
Owned areas in `nirs4all-providers`: provider base/adapters, registry,
conformance tests, soft imports.

Do not modify datasets/repository/benchmarks/papers repositories. Do not add
upload/write APIs. If a provider cannot produce a package yet, expose a typed
capability/refusal instead of a fake package.

Gate: `nirs4all-io` fmt/test/clippy according to touched code;
`nirs4all-providers` ruff, mypy, pytest. Report both repos separately.

## W28 - Cluster client/core adapter and distributed parity scaffold

**CWD:** `/home/delete/nirs4all/_worktrees/W28-cluster-core-client`
**Base:** `refactor/integration-cluster`
**Branch:** `refactor/W28-core-client`
**Report:** `docs/agent_reports/W28_CLUSTER_CORE_CLIENT.md`

Goal: build on W19's typed client by adding the first core/CLI-facing adapter
and tests that encode local-vs-distributed parity expectations for nirs4all DAG
jobs. The slice may be a scaffold if execution parity requires W21/W29, but it
must have concrete contracts and tests.

Owned areas: `nirs4all_cluster/client.py`,
`nirs4all_cluster/client_worker.py`, `nirs4all_cluster/runners/nirs4all_run.py`,
`nirs4all_cluster/cli.py`, schemas, docs, and client/worker/server tests.

Do not redesign RBAC or server scheduling internals unless a narrow fix is
required by the adapter tests.

Gate: targeted client/worker tests, full pytest if feasible, Ruff, mypy.

## W29 - dag-ml/dag-ml-data data requirements consumption

**CWD:** `/home/delete/nirs4all`
**Worktrees:** `_worktrees/W29-dagml-datareq`,
`_worktrees/W29-dmd-datareq`
**Bases:** `refactor/integration-dagml`, `refactor/integration-dmd`
**Branches:** `refactor/W29-datareq-consumption` in both repos
**Report:** `docs/agent_reports/W29_DATAREQ_LOCKSTEP.md`

Goal: turn the existing controller/data-requirements contracts into a consumed
surface. Wire representation/data requirement metadata through at least one
real CLI, PyO3/C API, or validation path, and keep dag-ml / dag-ml-data
lockstep validation green.

Owned areas in `dag-ml`: `crates/dag-ml-core/src/controller_adapter.rs`,
`crates/dag-ml-core/src/controller_registry.rs`,
`crates/dag-ml-core/src/runtime/*`, `crates/dag-ml-cli/src/main.rs`,
`crates/dag-ml-py/src/*`, tests.
Owned areas in `dag-ml-data`: representation registry/provider crates,
Python provider bindings, tests, and lockstep conformance pack.

Do not modify nirs4all Python fallback lists here. If new stable error codes or
schema fields are needed, add them with tests and document downstream consumers.

Gate: Rust fmt/clippy/tests for touched crates, Python provider tests if
touched, and both `scripts/validate_contracts.py` lockstep checks.

## W30 - nirs4all-tools legacy converter first real transform

**CWD:** `/home/delete/nirs4all/_worktrees/W30-tools-migration`
**Base:** `nirs4all-tools/main`
**Branch:** `refactor/W30-legacy-converter`
**Report:** `docs/agent_reports/W30_TOOLS_MIGRATION.md`

Goal: move `nirs4all-tools` beyond scaffold by implementing the first real
offline, one-way, no-in-place legacy conversion transform. Target a small
fixture-backed legacy pipeline/workspace/prediction artifact and emit a V1
workspace/package-compatible output plus manifest/report/checksum/id-map.

Owned areas: `src/nirs4all_tools/*`, tests/fixtures under `tests/`, README or
CLI help if behavior changes.

Do not add runtime legacy readers to `nirs4all`. Do not mutate source inputs.
If the exact legacy format is not discoverable, implement a strict detector and
write the missing fixture/spec blocker rather than guessing.

Gate: full `pytest`, Ruff, mypy if configured, and a CLI dry-run/copy-only/
verify smoke using the new fixture.
