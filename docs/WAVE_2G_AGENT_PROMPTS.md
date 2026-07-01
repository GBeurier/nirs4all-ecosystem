# Wave-2G agent prompts

**Date:** 2026-07-01
**Supervisor:** Codex API session
**Base state:** Wave-2F is integrated. `EXPECTED_FALLBACK == 6` on
`nirs4all/refactor/integration-nirs4all`. External interactive Claude CLI PIDs
`208304` and `208423` exist at the workspace root and must be left untouched.

Agents must inspect current files directly before editing. CodeGraph may be used
only as an accelerator; direct files and test output are authoritative. Agents
must not edit `PARALLEL_REFACTORING_SYNC.md` or `AGENT_RUN_SUPERVISION.md`.
Each agent writes one report under `nirs4all-ecosystem/docs/agent_reports/` and
may commit only on its assigned branch/worktree when its gates pass. No agent may
push.

If a task cannot be implemented safely, leave code unchanged, write the precise
contract blocker, and still produce the report. Do not drop fallback allowlist
entries unless the relevant parity test is green.

## Integration bases

| Repo | Branch / worktree | Tip at launch |
|---|---|---|
| `nirs4all` | `_worktrees/INT-nirs4all` / `refactor/integration-nirs4all` | `c12fea5d` |
| `dag-ml` | `_worktrees/INT-dagml` / `refactor/integration-dagml` | `35e9e00` |
| `dag-ml-data` | `_worktrees/INT-dmd` / `refactor/integration-dmd` | `9131cdf` |
| `nirs4all-studio` | `_worktrees/INT-studio` / `refactor/integration-studio` | `609f756` |
| `nirs4all-web` | `_worktrees/INT-web` / `refactor/integration-web` | `1adc71c` |
| `nirs4all-cluster` | `_worktrees/INT-cluster` / `refactor/integration-cluster` | `297aec1` |
| `nirs4all-providers` | `_worktrees/INT-providers` / `refactor/integration-providers` | `818fbd0` |
| `nirs4all-tools` | `main` | `a9fd589` |
| `nirs4all-ecosystem` | `main` | `abfdfd7` |

## Shared report template

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

## W51 - dag-ml stacking OOF/refit contract

**CWD:** `/home/delete/nirs4all/_worktrees/W51-dagml-stacking-oof`
**Base:** `refactor/integration-dagml`
**Branch:** `refactor/W51-stacking-oof-contract`
**Report:** `docs/agent_reports/W51_DAGML_STACKING_OOF.md`

Goal: unblock the remaining stacking fallbacks by making dag-ml's OOF/refit
semantics explicit. W41 proved that widening native detection fails with
`OOF predictions do not cover the refit sample universe`. Add a narrow contract,
validator, diagnostic, or test fixture that distinguishes:

- full-coverage stacking that may refit the meta-model;
- incomplete OOF stacking that must be CV-only, skip refit, or carry an explicit
  coverage policy;
- invalid stacking that must remain rejected with a stable error cause.

Owned areas: dag-ml planner/validation/runtime contract code, schema docs, and
tests. Do not edit `nirs4all`.

Gate: targeted Rust tests for the new/changed contract, fmt, clippy if feasible,
and cross-repo contract validation if the conformance pack changes.

## W52 - nirs4all native stacking replay manifest

**CWD:** `/home/delete/nirs4all/_worktrees/W52-nirs4all-stacking-replay`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W52-stacking-replay-manifest`
**Report:** `docs/agent_reports/W52_STACKING_REPLAY_MANIFEST.md`

Goal: advance B-011 by persisting enough native result metadata to replay
stacking `.n4a` bundles from raw X without the legacy bridge. W42 pins the
current blocker: native artifacts contain base and meta REFIT models, but no
replay graph / column-order manifest for base-prediction meta-feature
construction.

Owned areas: `nirs4all/pipeline/dagml/native_results.py`,
`nirs4all/api/result.py`, native result tests, and native `.n4a` bundle tests.
Avoid `detect.py`/`run_paths.py` fallback lowering.

Gate: native bundle tests, focused native-results artifact tests, xfail updated
only if the blocker is made more precise, py_compile, Ruff.

## W53 - dag-ml-data by-source feature layout contract

**CWD:** `/home/delete/nirs4all/_worktrees/W53-dmd-source-layout`
**Base:** `refactor/integration-dmd`
**Branch:** `refactor/W53-source-layout-contract`
**Report:** `docs/agent_reports/W53_DMD_SOURCE_LAYOUT.md`

Goal: define the data-side contract needed for the by-source fallbacks. W41
shows native parity fails when reconstructing legacy by-source dict layouts and
source-concat RF flows. Add an explicit representation/layout contract or
conformance fixture for source blocks, source order, per-source preprocessing
output, and concat layout preservation.

Owned areas: dag-ml-data representation/data-requirements contract code,
schemas, conformance-pack artifacts, and tests. Do not edit `nirs4all`.

Gate: fmt, targeted Rust tests, clippy if feasible, byte-identical manifest
regeneration if a contract artifact changes.

## W54 - nirs4all by-source layout parity probe

**CWD:** `/home/delete/nirs4all/_worktrees/W54-nirs4all-source-layout`
**Base:** `refactor/integration-nirs4all`
**Branch:** `refactor/W54-source-layout-parity`
**Report:** `docs/agent_reports/W54_NIRS4ALL_SOURCE_LAYOUT.md`

Goal: turn W41's by-source failures into either a safe native lowering or a
smaller executable contract test. Prioritize
`multi_source_by_source_branch_distinct_preproc` and
`multi_source_sources_concat_then_rf`; do not touch stacking. If exact parity
requires W53's contract first, add a failing/xfail contract test that names the
missing source-layout field and keep fallback entries unchanged.

Owned areas: `nirs4all/pipeline/dagml/detect.py`,
`nirs4all/pipeline/dagml/run_paths.py`, source-layout helpers if needed, and
focused parity tests. Do not edit export/native-results files.

Gate: targeted dual-engine parity for changed cases, fallback boundary tests,
compatibility ledger, coverage meter, py_compile, Ruff.

## W55 - Studio route-bypass parity gate

**CWD:** `/home/delete/nirs4all/_worktrees/W55-studio-bypass-parity`
**Base:** `refactor/integration-studio`
**Branch:** `refactor/W55-studio-bypass-parity`
**Report:** `docs/agent_reports/W55_STUDIO_BYPASS_PARITY.md`

Goal: advance B-011/B-017 by proving Studio routes do not bypass runtime/core
semantics for one important run/result path. Add a focused backend test or small
adapter fix showing `engine`, runtime fallback diagnostics, and result retrieval
stay consistent with the Python runtime envelope.

Owned areas: Studio backend route tests, route adapters, and shared runtime
helpers. Avoid frontend UI refactors.

Gate: targeted backend pytest, compileall, Ruff.

## W56 - Web runtime adoption gate

**CWD:** `/home/delete/nirs4all/_worktrees/W56-web-runtime-adoption`
**Base:** `refactor/integration-web`
**Branch:** `refactor/W56-runtime-adoption`
**Report:** `docs/agent_reports/W56_WEB_RUNTIME_ADOPTION.md`

Goal: advance B-018 by turning the Web RT fixtures into a stricter adoption
gate. Prefer a served/offline smoke or test that ensures runtime results and
errors keep the Python-compatible fields through the browser worker path, not
only static fixture parsing.

Owned areas: `studio-lite/src/engine/*`, runtime fixture tests, smoke helpers.
Avoid broad UI changes.

Gate: targeted Vitest, typecheck, build, and served/offline smoke if Node is
available; otherwise document the missing Node environment precisely.

## W57 - Providers real-service read adapter bridge

**CWD:** `/home/delete/nirs4all/_worktrees/W57-providers-real-bridge`
**Base:** `refactor/integration-providers`
**Branch:** `refactor/W57-real-service-bridge`
**Report:** `docs/agent_reports/W57_PROVIDER_REAL_BRIDGE.md`

Goal: advance DEC-PROV-001 by bridging at least one provider adapter to a real
local backing API/service shape without adding ecosystem write-back. Good
targets: repository pipeline list/get, benchmarks get-by-hash, or datasets
retrieve/list. Keep adapters dependency-light and hermetic-testable.

Owned areas: `src/nirs4all_providers/*`, provider tests, README. Do not edit
backing repos unless a tiny API bug is proven and isolated.

Gate: full provider pytest, Ruff, mypy.

## W58 - Cluster scheduler DAG rights and result contract

**CWD:** `/home/delete/nirs4all/_worktrees/W58-cluster-dag-rights`
**Base:** `refactor/integration-cluster`
**Branch:** `refactor/W58-dag-rights-contract`
**Report:** `docs/agent_reports/W58_CLUSTER_DAG_RIGHTS.md`

Goal: advance L15 after W47 by tightening cluster DAG job behavior around
rights, worker execution, and result envelope preservation. Add a focused test
or small scheduler/client change proving a registered worker/client can execute
or submit a DAG-shaped job only with the intended rights and that the result
shape remains stable.

Owned areas: cluster runner/client/server tests and narrow scheduler/client
glue. Do not redesign RBAC or the queue.

Gate: targeted parity/RBAC tests, full pytest if feasible, Ruff, mypy.

## W59 - Tools native-results semantic lowering preview

**CWD:** `/home/delete/nirs4all/_worktrees/W59-tools-native-results-lowering`
**Base:** `nirs4all-tools/main`
**Branch:** `refactor/W59-native-results-lowering`
**Report:** `docs/agent_reports/W59_TOOLS_NATIVE_RESULTS_LOWERING.md`

Goal: advance LOCK-MIG beyond W49 by converting one currently opaque
native-results-v1 payload into runtime-readable workspace-v2 metadata, or by
adding a strict preflight/schema gate that makes the remaining semantic blocker
machine-checkable. Do not add legacy readers to runtime repos.

Owned areas: `src/nirs4all_tools/*`, tests, README/contracts in the tools repo.

Gate: full tools pytest, Ruff, mypy, py_compile, CLI migrate/verify smoke.

## W60 - Cutover readiness matrix

**CWD:** `/home/delete/nirs4all/_worktrees/W60-ecosystem-cutover-matrix`
**Base:** `nirs4all-ecosystem/main`
**Branch:** `refactor/W60-cutover-matrix`
**Report:** `docs/agent_reports/W60_CUTOVER_MATRIX.md`

Goal: make the cutover blockers executable/readable after Wave-2F. Add a
machine-readable cutover readiness matrix or update the gate docs so each
remaining blocker maps to one owning repo, one command, expected evidence, and
the exact missing contract. This is documentation/tooling only; do not flip
`DEFAULT_ENGINE`.

Owned areas: `docs/contracts/cutover/*`, `docs/CUTOVER_GATE_RUNNER.md`,
`scripts/n4a_cutover_gates.py`, and report docs.

Gate: gate-runner validate/list, py_compile, JSON validation, Ruff, diff-check.
