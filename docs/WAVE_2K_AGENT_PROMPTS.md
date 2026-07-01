# Wave 2K Agent Prompts

Date: 2026-07-01

Coordinator cwd: `/home/delete/nirs4all`

Wave 2K starts after Wave 2J integrated the V1 cutover hardening:
`nirs4all` now defaults to `dag-ml`, `allow_fallback=False` is the public
default, dag-ml export no longer performs an implicit legacy refit, Studio/Web
runtime envelopes are present, and `nirs4all-tools` has the standalone legacy
converter.

External Claude sessions are still running in the workspace. Treat them as
reserved external work. Do not kill them, do not reuse their terminals, and do
not edit their private worktrees.

General rules for every worker:

- You are not alone in the workspace. Do not revert edits made by other workers
  or the user. If a file changed under you, inspect it and adapt.
- Use direct code inspection, not only CodeGraph. CodeGraph may be stale.
- Read the nearest `AGENTS.md` / `CLAUDE.md` in any repo you edit.
- Create or reuse only your assigned worktree and branch. Do not edit the dirty
  main checkout `nirs4all/`; use `_worktrees/INT-*` integration branches as
  bases where they exist.
- Keep write scopes disjoint. If you discover an unavoidable overlap, stop and
  write it in your report instead of editing another worker's ownership area.
- Commit code changes in the edited repo when green.
- Write exactly one report in
  `nirs4all-ecosystem/docs/agent_reports/Wxx_*.md`. Do not edit the control
  board or another worker report.
- The report must include changed files, commits, tests run, failures, exact
  blockers, and whether follow-up coordinator integration is needed.

## W90 - Cutover State Gate And Roadmap Sync

Base repo/worktree: `nirs4all-ecosystem`, base branch `main`, direct checkout
is acceptable for docs/scripts. If code changes are easier in a worktree, create
`_worktrees/W90-ecosystem-cutover-gate`, branch
`refactor/W90-cutover-state-gate`.

Ownership:

- `nirs4all-ecosystem/scripts/*cutover*`
- `nirs4all-ecosystem/docs/CUTOVER_GATE_RUNNER.md`
- `nirs4all-ecosystem/docs/PARALLEL_REFACTORING_SYNC.md`
- `nirs4all-ecosystem/docs/agent_reports/W90_CUTOVER_STATE_GATE.md`
- Do not edit code in `nirs4all`, Studio, Web, tools, cluster, providers.

Task:

Fact-check the current post-W2J integration state directly in code, then make the
ecosystem docs/gates stop saying the pre-W2J truth. At minimum the gate must
assert:

- `nirs4all/pipeline/engine.py` declares `DEFAULT_ENGINE = "dag-ml"` on
  `refactor/integration-nirs4all`.
- `nirs4all.api.run.run` defaults to `allow_fallback=False`.
- fallback compatibility still exists only through explicit opt-in.
- `RunResult.export()` / `export_model()` do not implicitly legacy-refit; the
  bridge is only reachable through named `compatibility="legacy-refit"`.
- coverage meter still reports `fallback=0`.
- Studio/Web/tools/cluster/provider integration heads referenced by Wave 2J are
  current enough for L19 status accounting.

Update `PARALLEL_REFACTORING_SYNC.md` so `LOCK-DROP`/`L19` is no longer marked
blocked on `DEFAULT_ENGINE="legacy"`. If another blocker remains, name it
precisely; do not claim full V1 release readiness unless verified.

Required verification:

- Run the existing ecosystem cutover gate or add a focused dry-run command if it
  does not cover the above.
- Run any new unit tests for the gate.
- Run `git diff --check` in `nirs4all-ecosystem`.

Report: `W90_CUTOVER_STATE_GATE.md`.

## W91 - dag-ml / dag-ml-data Lockstep Freshness Gate

Base repos/worktrees:

- `dag-ml`, base branch from `_worktrees/INT-dagml`, new worktree
  `_worktrees/W91-dagml-lockstep`, branch `refactor/W91-lockstep-freshness`.
- `dag-ml-data`, base branch from current repo head, new worktree
  `_worktrees/W91-dagml-data-lockstep`, branch
  `refactor/W91-lockstep-freshness`.

Ownership:

- `dag-ml/docs/contracts/*`
- `dag-ml/scripts/validate_contracts.py` and focused contract tests
- `dag-ml-data/docs/contracts/*`
- `dag-ml-data` focused lockstep validation scripts/tests
- `nirs4all-ecosystem/docs/agent_reports/W91_DAGML_LOCKSTEP_FRESHNESS.md`

Task:

Verify that the existing frozen contract system is still current after Wave 2J:
controller manifests, runtime/result schemas, representation/data-requirements
contracts, conformance-pack hashes, and ABI snapshots must agree across
`dag-ml` and `dag-ml-data`. Do not re-author schemas unless drift requires a
versioned extension. If you find drift, fix the source of truth and update the
hash/manifest through the repo's intended tooling.

Pay special attention to the critical-review correction: the ecosystem should
surface existing dag-ml schemas, not invent a parallel CAP/CTRL/REL vocabulary.

Required verification:

- `dag-ml/scripts/validate_contracts.py` or the closest current equivalent.
- `dag-ml-data` contract validation tests/scripts.
- Rust/Python focused tests only where touched.
- `git diff --check` in both repos.

Report: `W91_DAGML_LOCKSTEP_FRESHNESS.md`.

## W92 - nirs4all-methods Package Surface, Bindings, And Parity Gate

Base repo/worktree: `nirs4all-methods`, base branch current main, new worktree
`_worktrees/W92-methods-release-surface`, branch
`refactor/W92-methods-release-surface`.

Ownership:

- `nirs4all-methods` build/package metadata
- C/C++ ABI tests and docs
- Python/R binding package docs if present in this repo
- `nirs4all-ecosystem/docs/agent_reports/W92_METHODS_RELEASE_SURFACE.md`

Task:

Audit and harden the `nirs4all-methods` release/binding surface for V1. The
install project name may be `nirs4all-methods`, but namespaces must be
comprehensible and technically simple. Verify whether exported symbols,
bindings, docs, and tests consistently communicate the intended split:
`nirs4all-methods` as the numerical/method engine, not `n4m` as an unexplained
public package. Do not rename public symbols broadly unless the repo already has
a migration pattern; prefer additive aliases/docs/tests if risk is high.

Also verify parity expectations against the Python reference where a local gate
exists. If no gate exists, add a narrow, low-risk smoke/parity test or a report
with exact missing test fixture requirements.

Required verification:

- Repo-prescribed build/test command from `AGENTS.md`/`CLAUDE.md`.
- Focused ABI/package tests for touched files.
- Formatting/linting for touched files.
- `git diff --check`.

Report: `W92_METHODS_RELEASE_SURFACE.md`.

## W93 - Formats / IO / Datasets Reference Dataset Bridge

Base repos/worktrees:

- `nirs4all-io`, base from `_worktrees/INT-io`, new worktree
  `_worktrees/W93-io-datasets-bridge`, branch
  `refactor/W93-datasets-bridge`.
- `nirs4all-datasets`, base current main, new worktree
  `_worktrees/W93-datasets-reference-bridge`, branch
  `refactor/W93-reference-bridge`.
- `nirs4all-formats`, base current main, new worktree
  `_worktrees/W93-formats-io-contract`, branch
  `refactor/W93-io-contract`.

Ownership:

- Dataset reference access API and docs.
- `nirs4all-io` DatasetPackage/reference dataset bridge.
- Format/IO contract tests only where needed.
- `nirs4all-ecosystem/docs/agent_reports/W93_IO_DATASETS_REFERENCE_BRIDGE.md`

Task:

Implement or verify the local path by which reference datasets can feed IO and,
through core, tests/pipelines. The user model is: datasets can nourish IO via
core; `nirs4all-datasets` is the catalog/source of reference datasets, while IO
assembles pipeline-ready datasets and formats owns readers. Keep write behavior
disconnected from repository/benchmarks providers.

If the bridge already exists, make it visible and tested. If it does not, add the
smallest adapter/facade with clear boundaries and no duplicated parsing logic.

Required verification:

- Focused pytest/cargo tests for touched repos.
- No network-only tests unless already marked/skippable.
- Formatting/linting for touched files.
- `git diff --check` in touched repos.

Report: `W93_IO_DATASETS_REFERENCE_BRIDGE.md`.

## W94 - Lite/Core Release Topology Manifest Consumer

Base repo/worktree: `nirs4all-lite`, base from `_worktrees/INT-lite`, new
worktree `_worktrees/W94-lite-release-topology`, branch
`refactor/W94-release-topology-consumer`.

Ownership:

- `nirs4all-lite` release topology manifest/tests.
- Optional small docs in `nirs4all-lite`.
- `nirs4all-ecosystem/docs/agent_reports/W94_LITE_RELEASE_TOPOLOGY.md`
- Do not edit ecosystem central release docs unless the coordinator explicitly
  asks; W90 owns ecosystem status docs in this wave.

Task:

Finish the `nirs4all-lite` side of the future `nirs4all-core` aggregate release
story. The current `release_topology_manifest()` already exposes
`nirs4all-lite` and target `nirs4all-core`; verify it is stable, tested, and
complete enough for a central ecosystem manifest to consume. Add missing tests
for install distributions, namespace/facade names, optional upstreams, and
license/ABI pointers. Do not prematurely rename the project.

Required verification:

- Python binding tests around `release_topology_manifest()`.
- Any Rust/package tests required by touched files.
- Formatting/linting for touched files.
- `git diff --check`.

Report: `W94_LITE_RELEASE_TOPOLOGY.md`.

## W95 - Studio Strict Runtime Fallback Default

Base repo/worktree: `nirs4all-studio`, base branch
`refactor/integration-studio`, new worktree `_worktrees/W95-studio-strict-runtime`,
branch `refactor/W95-studio-strict-runtime`.

Ownership:

- `api/runs.py`
- backend tests for run/quick-run/runtime fallback policy
- minimal frontend API type/default changes only if needed to keep requests
  coherent
- `nirs4all-ecosystem/docs/agent_reports/W95_STUDIO_STRICT_RUNTIME.md`

Task:

Studio still has `allow_fallback=True` defaults in request/config models after
core moved to strict-by-default. Make Studio V1 match the no-silent-fallback
policy: fallback may remain available, but it must be explicit and visible, not
the default for QuickRun/ExperimentConfig. Preserve existing structured
diagnostics and fallback records.

Required verification:

- Focused backend tests around `ExperimentConfig`, `QuickRunRequest`, execution
  fallback/refusal, and persisted `fallback_policy`.
- Typecheck/lint if frontend types are touched.
- Ruff on touched Python.

Report: `W95_STUDIO_STRICT_RUNTIME.md`.

## W96 - Studio/Web Runtime UX And E2E Smoke

Base repos/worktrees:

- `nirs4all-studio`, base `refactor/integration-studio`, new worktree
  `_worktrees/W96-studio-runtime-e2e`, branch `refactor/W96-runtime-e2e`.
- `nirs4all-web`, base `refactor/integration-web`, new worktree
  `_worktrees/W96-web-runtime-e2e`, branch `refactor/W96-runtime-e2e`.

Ownership:

- Runtime-result UI smoke tests and visual/E2E coverage.
- No backend model changes; W95 owns Studio fallback defaults.
- `nirs4all-ecosystem/docs/agent_reports/W96_RUNTIME_UX_E2E.md`

Task:

Verify the user-facing runtime surfaces after W85-W87: engine status, fallback
refusal diagnostics, native-results/export affordance, and Web worker `RtError`
rendering. Add focused E2E/smoke coverage where the existing test harness makes
it practical. Do not redesign the UI; this is a V1 verification slice.

Required verification:

- Studio focused Vitest/Playwright or existing E2E command for touched surface.
- Web typecheck/focused Vitest and browser smoke if practical.
- Screenshot/canvas checks only if the app already supports them.
- `git diff --check`.

Report: `W96_RUNTIME_UX_E2E.md`.

## W97 - Tools Legacy Converter Real Golden Fixtures

Base repo/worktree: `nirs4all-tools`, base branch `main`, new worktree
`_worktrees/W97-tools-real-goldens`, branch `refactor/W97-real-goldens`.

Ownership:

- `nirs4all-tools` converter fixtures/tests/docs.
- No runtime package changes.
- `nirs4all-ecosystem/docs/agent_reports/W97_TOOLS_REAL_GOLDENS.md`

Task:

Move the standalone migration tool from synthetic coverage toward real legacy
preservation confidence. Add or wire small golden fixtures representing old
predictions/pipelines/workspaces. The converter must remain offline, one-way,
no-in-place by default, and must preserve unsupported payloads with checksums
and machine-readable reports. Do not add legacy readers back into V1 runtime
packages.

Required verification:

- Converter pytest, including dry-run/verify/resume/unsupported reports.
- Ruff and mypy if configured.
- `git diff --check`.

Report: `W97_TOOLS_REAL_GOLDENS.md`.

## W98 - Full Python Reference Parity And Cutover Runner

Base repo/worktree: `nirs4all`, base branch `refactor/integration-nirs4all`,
new worktree `_worktrees/W98-nirs4all-full-parity`, branch
`refactor/W98-full-parity-gate`.

Ownership:

- parity gate runner/tests/scripts in `nirs4all`
- docs only if needed to explain exact command
- `nirs4all-ecosystem/docs/agent_reports/W98_FULL_PYREF_PARITY.md`

Task:

Run and, if necessary, stabilize the full Python-reference parity suite against
the V1 cutover posture. The current Python library is the reference: any current
Python pipeline using sklearn operators, whatever its complexity, must either
produce the same results on the final dag-ml path or fail with a documented
compatibility/refusal classification. Do not hide failures with broad xfails.

Required verification:

- Full or maximal practical `tests/integration/parity` run with the current
  `PYTHONPATH` including dag-ml-py.
- coverage meter `--check`.
- Focused reruns for any failures you fix.
- Ruff/mypy for touched files.

Report: `W98_FULL_PYREF_PARITY.md`.

## W99 - Post-W2K Integration Reviewer

Base repo/worktree: `nirs4all-ecosystem`, base branch `main`, no code worktree
required unless you prefer one.

Ownership:

- `nirs4all-ecosystem/docs/agent_reports/W99_POST_W2K_REVIEW.md`
- Read-only inspection across all repos.

Task:

Act as a strict reviewer after W90-W98 are available. Do not implement code.
Fact-check the reports and current integration heads directly in code. Produce a
ranked blocker list for V1 refactor completion, with file/line evidence and
exact next actions. Identify stale docs, risky unmerged worktrees, missing tests,
and any overlap/collision between workers.

Required verification:

- Direct code/git inspection; do not rely only on CodeGraph.
- No code changes except the report.

Report: `W99_POST_W2K_REVIEW.md`.
