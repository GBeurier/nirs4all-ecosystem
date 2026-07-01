# Wave-2F agent prompts

**Date:** 2026-07-01
**Supervisor:** Codex API session
**Base state:** Wave-2E is integrated. `EXPECTED_FALLBACK == 6` on
`nirs4all/refactor/integration-nirs4all`. External interactive Claude CLI PIDs
`208304` and `208423` exist at the workspace root and must be left untouched.

Agents must not edit `PARALLEL_REFACTORING_SYNC.md` or
`AGENT_RUN_SUPERVISION.md`. Each agent writes exactly one report under
`nirs4all-ecosystem/docs/agent_reports/` and may commit only in its assigned
worktree/repo when its gates pass. No agent may push.

All agents must inspect current files directly before editing. CodeGraph may be
used as an accelerator, but current files and test output are authoritative.
If an assigned change cannot be implemented safely, leave code unchanged, write
the precise blocker, and still produce the report.

## Integration bases

| Repo | Branch / worktree | Tip at launch |
|---|---|---|
| `nirs4all` | `_worktrees/INT-nirs4all` / `refactor/integration-nirs4all` | `e6299d52` |
| `dag-ml` | `_worktrees/INT-dagml` / `refactor/integration-dagml` | `35e9e00` |
| `dag-ml-data` | `_worktrees/INT-dmd` / `refactor/integration-dmd` | `9131cdf` |
| `nirs4all-studio` | `_worktrees/INT-studio` / `refactor/integration-studio` | `64b43c7` |
| `nirs4all-web` | `_worktrees/INT-web` / `refactor/integration-web` | `94ccc66` |
| `nirs4all-cluster` | `_worktrees/INT-cluster` / `refactor/integration-cluster` | `afacc0e` |
| `nirs4all-io` | `_worktrees/INT-io` / `refactor/integration-io` | `ccfea29` |
| `nirs4all-providers` | `_worktrees/INT-providers` / `refactor/integration-providers` | `6b9324a` |
| `nirs4all-lite` | `_worktrees/INT-lite` / `refactor/integration-lite` | `2f379ef` |
| `nirs4all-tools` | `main` | `b76458d` |
| `nirs4all-ecosystem` | `main` | `f126547` |

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

## W41 - Final fallback drain slice

**CWD:** `/home/delete/nirs4all/_worktrees/W41-nirs4all-fallback-final`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W41-fallback-final`
**Report:** `docs/agent_reports/W41_FALLBACK_FINAL.md`

Goal: materially reduce the remaining six `EXPECTED_FALLBACK` cases, without
lying about parity. Current remaining cases are:

- `branch_dup_three_way_merge_predictions`
- `branch_dup_named_with_metamodel`
- `branch_dup_merge_all`
- `multi_source_by_source_branch_distinct_preproc`
- `multi_source_per_source_models_stacking`
- `multi_source_sources_concat_then_rf`

Owned areas: `nirs4all/pipeline/dagml/detect.py`,
`nirs4all/pipeline/dagml/run_paths.py`,
`nirs4all/pipeline/dagml/run_backend.py`,
`tests/integration/parity/test_conformance_dual_engine.py`,
`tests/integration/parity/test_native_fallback_boundary.py`,
`tests/integration/parity/coverage_meter.py`, and compatibility-ledger entries
for cases that truly become native.

Do not touch `.n4a` export implementation, runtime envelopes, Studio, Web, or
Rust. If a case needs a dag-ml core contract, document the missing contract and
leave it in fallback.

Gate: targeted parity for changed cases, `test_native_fallback_boundary.py`,
`test_compatibility_ledger.py`, `coverage_meter --check`, `py_compile`, Ruff if
available.

## W42 - Native export coverage expansion

**CWD:** `/home/delete/nirs4all/_worktrees/W42-nirs4all-native-export2`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W42-native-export2`
**Report:** `docs/agent_reports/W42_NATIVE_EXPORT2.md`

Goal: advance B-011 by extending true native `.n4a` export beyond the W33
fusion subset, or by pinning precise xfail/blocker tests for shapes whose
native artifacts are still insufficient. Prioritize stacking and by-source
native artifacts that already run natively.

Owned areas: `nirs4all/api/result.py`,
`nirs4all/pipeline/dagml/native_results.py`,
`tests/integration/parity/test_dagml_native_n4a_bundle.py`,
`tests/integration/parity/test_conformance_n4a_cross_engine.py`, and focused
export tests.

Do not drain `EXPECTED_FALLBACK` and do not touch host-bridge detection/run
paths unless an export test proves a very small metadata fix is required.

Gate: native bundle tests, cross-engine `.n4a` tests, targeted `py_compile`,
Ruff if available.

## W43 - Python runtime goldens

**CWD:** `/home/delete/nirs4all/_worktrees/W43-nirs4all-rt-goldens`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W43-rt-goldens`
**Report:** `docs/agent_reports/W43_PY_RT_GOLDENS.md`

Goal: advance B-018 by adding Python-side `RtResult`/`RtError` golden fixtures
that match Web W37 semantics and current schemas. Prefer fixture-based tests
that can later be consumed by Studio/Web rather than broad runtime refactors.

Owned areas: `nirs4all/pipeline/dagml/rt.py`,
`nirs4all/pipeline/dagml/result.py`,
`tests/integration/parity/test_rt_*`,
new fixtures under `tests/integration/parity/fixtures/` or `docs/contracts/`
only if already consistent with existing conventions.

Do not change numerical parity or export behavior.

Gate: targeted RT tests, `test_rt_fallback_strict.py`,
`test_compatibility_ledger.py`, `py_compile`, Ruff if available.

## W44 - Studio compute push-down slice 3

**CWD:** `/home/delete/nirs4all/_worktrees/W44-studio-compute3`
**Base:** `refactor/integration-studio`
**Branch:** `refactor/W44-compute-pushdown3`
**Report:** `docs/agent_reports/W44_STUDIO_COMPUTE_PUSHDOWN3.md`

Goal: continue B-017 by removing one more duplicated Studio backend compute
path. Prioritize analysis metrics, preprocessing summaries, playground result
metrics, or chart transforms where a library/runtime helper exists or can be
called cleanly.

Owned areas: `api/analysis.py`, `api/preprocessing.py`, `api/playground/*`,
`api/shared/*`, `api/spectra.py`, and focused backend tests.

Do not touch runtime route metadata or frontend components.

Gate: targeted backend tests in `.venv` if available, compileall, Ruff.

## W45 - Studio UI runtime/result components

**CWD:** `/home/delete/nirs4all/_worktrees/W45-studio-ui-runtime`
**Base:** `refactor/integration-studio`
**Branch:** `refactor/W45-ui-runtime`
**Report:** `docs/agent_reports/W45_STUDIO_UI_RUNTIME.md`

Goal: continue the UI extraction requirement by adding a small reusable,
pure UI/view-model slice for runtime/result status display. Keep it internal to
Studio for now, consistent with the existing `src/ui/score` pattern.

Owned areas: `src/ui/*`, result/runtime view-model helpers, focused React/Vitest
tests. You may update importers that consume the extracted component, but do
not change backend APIs.

Do not redesign pages broadly. Do not add landing/marketing surfaces.

Gate: targeted Vitest/TS checks if Node is available; otherwise document the
missing Node environment and run static checks that are available.

## W46 - Web cross-runtime fixtures

**CWD:** `/home/delete/nirs4all/_worktrees/W46-web-cross-rt`
**Base:** `refactor/integration-web`
**Branch:** `refactor/W46-cross-rt`
**Report:** `docs/agent_reports/W46_WEB_CROSS_RT.md`

Goal: continue B-018 by making Web runtime fixtures consumable as a
cross-language contract. Extend W37 goldens so they can compare against the
Python runtime fixture shape and catch drift in `RtResult`/`RtError` fields.

Owned areas: `studio-lite/src/engine/rt-result.ts`,
`studio-lite/src/engine/fixtures/runtime/*`, runtime contract tests, and smoke
helpers. Avoid broad UI/product changes.

Gate: targeted Vitest, typecheck, build if Node is available.

## W47 - Cluster real DAG parity

**CWD:** `/home/delete/nirs4all/_worktrees/W47-cluster-real-dag`
**Base:** `refactor/integration-cluster`
**Branch:** `refactor/W47-real-dag-parity`
**Report:** `docs/agent_reports/W47_CLUSTER_REAL_DAG.md`

Goal: advance cluster parity from W38's fake deterministic backend toward a
real nirs4all DAG job. Add a narrow integration harness that exercises the
existing core adapter/server/worker flow with a real or minimal nirs4all
pipeline when dependencies are available, and degrades with explicit skip
reason when they are not.

Owned areas: `tests/test_distributed_parity.py`, core adapter tests, test
fixtures, and narrow adapter glue only if needed.

Do not redesign the scheduler or RBAC model.

Gate: targeted parity tests, full cluster pytest if feasible, Ruff, mypy.

## W48 - Provider services/adapters hardening

**CWD:** `/home/delete/nirs4all/_worktrees/W48-providers-services`
**Base:** `refactor/integration-providers`
**Branch:** `refactor/W48-provider-services`
**Report:** `docs/agent_reports/W48_PROVIDER_SERVICES.md`

Goal: advance DEC-PROV-001 without adding write-back. Harden repository and
benchmarks pipeline-provider adapters around `list_pipelines`/`get_pipeline`,
service-style data, health/capability reporting, and conformance tests using
real APIs or hermetic fakes.

Owned areas: `nirs4all-providers/src/nirs4all_providers/*` and tests only.
Do not edit backing repos unless a direct API bug is proven and small.

Gate: provider pytest, Ruff, mypy if available.

## W49 - Tools runtime-readable result lowering

**CWD:** `/home/delete/nirs4all/_worktrees/W49-tools-results-lowering`
**Base:** `nirs4all-tools/main`
**Branch:** `refactor/W49-results-lowering`
**Report:** `docs/agent_reports/W49_TOOLS_RESULTS_LOWERING.md`

Goal: advance LOCK-MIG by converting one preserved opaque result payload into a
runtime-readable workspace-v2 artifact instead of only copying it. Prefer
`prediction_arrays` lowering or native-results-v1 metadata lowering, whichever
is safer with current schemas. Strict mode must still refuse before output when
lossless conversion is not possible.

Owned areas: `src/nirs4all_tools/*`, tests, contracts under the tools repo.
Do not add legacy readers to runtime repos.

Gate: tools pytest, compileall, Ruff, CLI migrate/verify smoke, mypy if
available.

## W50 - Cutover gate CI integration

**CWD:** `/home/delete/nirs4all/_worktrees/W50-ecosystem-cutover-ci`
**Base:** `nirs4all-ecosystem/main`
**Branch:** `refactor/W50-cutover-ci`
**Report:** `docs/agent_reports/W50_CUTOVER_CI.md`

Goal: make W40's non-mutating cutover gate runner CI-ready without flipping
defaults. Add or harden a workflow/script/docs path that validates the gate
contract and runs safe non-mutating checks when sibling repos are present. The
gate must remain advisory/failing only for explicit cutover jobs until
`EXPECTED_FALLBACK == empty`.

Owned areas: `scripts/n4a_cutover_gates.py`, `docs/contracts/cutover/*`,
`docs/CUTOVER_GATE_RUNNER.md`, and ecosystem CI workflow files.

Do not edit product repos. Do not flip `DEFAULT_ENGINE`.

Gate: runner `validate`/`list`, JSON validation, py_compile, Ruff if available,
and workflow YAML parse if Python tooling is available.
