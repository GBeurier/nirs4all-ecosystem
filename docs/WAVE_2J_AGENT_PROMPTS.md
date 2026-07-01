# Wave 2J Agent Prompts

Date: 2026-07-01

Coordinator cwd: `/home/delete/nirs4all`

Wave 2J treats the two still-running external Claude CLI sessions as reserved
slots. The coordinator launches eight controlled Codex workers, W82-W89, for ten
total active lanes. Workers must not touch `nirs4all-drafts`, `nirs4all-lab`, or
the external Claude worktree
`/home/delete/nirs4all/nirs4all/.claude/worktrees/agent-a5af0970d430760ab`.

General rules for every worker:

- You are not alone in the workspace. Do not revert edits made by other workers
  or the user. If a file changed under you, inspect it and adapt.
- Use direct code inspection, not only CodeGraph. CodeGraph may be stale.
- Read the nearest `AGENTS.md` / `CLAUDE.md` in any repo you edit.
- Create or reuse only your assigned worktree and branch. Do not edit the dirty
  main checkout `nirs4all/`; use `_worktrees/INT-*` as integration bases.
- Commit code changes in the edited repo when green.
- Write exactly one report in
  `nirs4all-ecosystem/docs/agent_reports/Wxx_*.md`. Do not edit the control
  board or another worker report.
- The report must include changed files, commits, tests run, failures, and exact
  blockers.

## W82 - nirs4all Legacy-DROP Cutover Branch

Base repo/worktree: `nirs4all`, base branch `refactor/integration-nirs4all`,
new worktree `_worktrees/W82-nirs4all-cutover-strict`, branch
`refactor/W82-cutover-strict`.

Ownership:

- `nirs4all/pipeline/engine.py`
- `nirs4all/api/run.py`
- new or focused tests under `tests/integration/parity/` for cutover behavior
- compatibility docs only if needed for the cutover gate

Task:

Implement the V1 cutover posture on a branch: default execution resolves to
`dag-ml`, explicit `engine="legacy"` remains available only as an explicit
compatibility path, and `engine="dag-ml"` must not silently degrade to legacy
unless an explicit opt-in policy is passed. Use the existing `allow_fallback`
contract if it is sufficient; otherwise add the smallest clear option/env gate
needed. Preserve structured `RtError` diagnostics for refusal cases. Do not
touch export code in `api/result.py`; that belongs to W83.

Required verification:

- `test_native_fallback_boundary.py`
- focused cutover tests you add
- at least one representative dual-engine conformance selector proving the new
  default reaches dag-ml
- Ruff on touched Python files

Report: `W82_LEGACY_DROP_CUTOVER.md`.

## W83 - nirs4all Export Without Implicit Legacy Refit

Base repo/worktree: `nirs4all`, base branch `refactor/integration-nirs4all`,
new worktree `_worktrees/W83-nirs4all-export-no-legacy`, branch
`refactor/W83-export-no-legacy`.

Ownership:

- `nirs4all/api/result.py`
- export/native-results tests under `tests/integration/parity/`
- small helper files only if directly needed by `result.py`

Task:

Remove the V1-blocking implicit legacy refit path for dag-ml exports. A dag-ml
result should either export from captured native artifacts or refuse with a
stable structured error/message that points to `nirs4all-tools` conversion or an
explicit compatibility command. Do not re-run the pipeline through
`engine="legacy"` from `RunResult.export()` / `export_model()` in the default V1
path. Keep any compatibility behavior behind an explicit, named opt-in if the
existing tests still need it.

Required verification:

- existing native `.n4a` / export-model tests
- existing cross-engine export tests, adapted only where the V1 contract changes
- new regression proving dag-ml export refusal does not call legacy when native
  artifacts are absent or unreadable
- Ruff on touched Python files

Report: `W83_EXPORT_NO_LEGACY_REFIT.md`.

## W84 - nirs4all-tools Legacy Converter Hardening

Base repo/worktree: `nirs4all-tools`, base branch `main`, new worktree
`_worktrees/W84-tools-legacy-converter`, branch
`refactor/W84-legacy-converter-hardening`.

Ownership:

- `src/nirs4all_tools/*`
- `tests/test_*`
- `README.md` only for command/support notes

Task:

Harden the standalone converter so old predictions/pipelines/workspaces can be
preserved without keeping runtime legacy readers in V1. Extend verify/dry-run
coverage around legacy workspace inputs and native-results sidecars. The tool
must never mutate source data in place by default, must preserve opaque payloads
with checksums when not lowerable, and must emit a machine-readable unsupported
report.

Required verification:

- focused pytest for converter commands and checksum/tamper paths
- Ruff on `src` and `tests`
- if mypy is configured and practical, run it

Report: `W84_TOOLS_LEGACY_CONVERTER.md`.

## W85 - Studio Runtime Contract Finalization

Base repo/worktree: `nirs4all-studio`, base branch
`refactor/integration-studio`, new worktree `_worktrees/W85-studio-runtime-v1`,
branch `refactor/W85-studio-runtime-v1`.

Ownership:

- backend runtime/runs routing modules and tests
- do not edit reusable UI component files; W86 owns UI extraction

Task:

Move Studio's run/predict/analysis backend behavior to the runtime envelope as
the source of truth. Remove or quarantine warning-string engine heuristics where
structured `RtResult` / `RtError` is available. Ensure run records preserve
engine, diagnostics, fallback/refusal policy, and native result references.

Required verification:

- focused Python tests for runtime engine/runs routing
- existing route/runtime tests touched by W76/W55
- Ruff on touched backend Python
- TypeScript tests only if you touch TS indirectly

Report: `W85_STUDIO_RUNTIME_V1.md`.

## W86 - Studio Reusable UI Runtime Components

Base repo/worktree: `nirs4all-studio`, base branch
`refactor/integration-studio`, new worktree `_worktrees/W86-studio-ui-runtime`,
branch `refactor/W86-studio-ui-runtime`.

Ownership:

- Studio frontend reusable UI components/hooks for runtime status/results
- frontend tests/story fixtures if present
- do not edit backend routing modules; W85 owns backend runtime behavior

Task:

Extract a small, concrete set of reusable UI primitives around runtime results:
engine badge/status, diagnostics list, native-results/export action affordance,
and run state presentation. Keep the extraction grounded in existing Studio
screens, not a speculative design system. Preserve current visuals unless the
componentization needs minor cleanup.

Required verification:

- TypeScript typecheck
- focused Vitest/component tests if the repo has them for the touched area
- lint/format command used by Studio for frontend changes

Report: `W86_STUDIO_UI_RUNTIME_COMPONENTS.md`.

## W87 - Web Runtime V1 Cutover

Base repo/worktree: `nirs4all-web`, base branch `refactor/integration-web`,
new worktree `_worktrees/W87-web-runtime-v1`, branch
`refactor/W87-web-runtime-v1`.

Ownership:

- `studio-lite/src/engine/*`
- runtime fixtures/tests under `studio-lite/src/engine` and Web smoke scripts

Task:

Finalize Web/Studio-lite runtime adoption for V1: runtime fixtures and worker
results should treat explicit `RtResult` / `RtError` as the contract, not a
backend-specific fallback. Add a regression for "no silent legacy fallback" in
the browser/WASM path and keep unsupported-shape diagnostics schema-compatible
with Python.

Required verification:

- `npm run typecheck` with the WSL Node path if needed
- focused Vitest runtime tests
- browser smoke if a local preview is practical

Report: `W87_WEB_RUNTIME_V1.md`.

## W88 - Cluster Scheduler V1 DAG Semantics

Base repo/worktree: `nirs4all-cluster`, base branch
`refactor/integration-cluster`, new worktree `_worktrees/W88-cluster-v1-dag`,
branch `refactor/W88-cluster-v1-dag`.

Ownership:

- scheduler/client/server RBAC and DAG execution modules
- cluster tests

Task:

Advance the cluster from rights-aware scheduling toward the V1 load-balancer
contract: server can assign executable DAG jobs to registered clients based on
rights/capabilities, clients can submit jobs to the server, and cancellation or
worker loss is deterministic. Keep this as a local trusted-LAN scheduler slice;
do not add broad auth/security features beyond existing RBAC.

Required verification:

- scheduler/RBAC pytest suites
- mypy and Ruff if configured
- add a focused distributed-local parity or worker-loss test if missing

Report: `W88_CLUSTER_V1_DAG.md`.

## W89 - Providers Repository/Benchmarks Pipeline Services

Base repo/worktree: `nirs4all-providers`, base branch
`refactor/integration-providers`, new worktree
`_worktrees/W89-providers-pipeline-services`, branch
`refactor/W89-pipeline-services`.

Ownership:

- `src/nirs4all_providers/*`
- provider tests
- do not edit private `drafts`/`lab`; edit repository/benchmarks repos only if
  the provider tests require a tiny local fixture and it is explicitly scoped

Task:

Make the provider layer reflect the clarified ecosystem model: repository is a
read-side provider of preset/pipeline lists and pipeline payloads; benchmarks can
provide `get_pipeline` and local queue/test planning against datasets; papers is
a potential export plugin over methods docs/UI and must not be treated as a
write-side repository. Add contract tests for `get_pipeline_list` /
`get_pipeline` and for benchmarks local planning.

Required verification:

- provider pytest suite
- Ruff and mypy if configured
- report any required service-repo follow-up without inventing upload support

Report: `W89_PROVIDERS_PIPELINE_SERVICES.md`.
