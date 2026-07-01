# W2L Lane K Final Review

## Agent

Codex Lane K final reviewer / parity auditor post-reset.

## Lane

Lane K: read-only final review across post-reset W2L control evidence. No Claude
tools used. `nirs4all-drafts` and `nirs4all-lab` were not read or touched.

## Findings

### BLOCKER 1 - Core parity/native lane is not review-complete, but the live `nirs4all` checkout is dirty and changes the fallback contract.

Evidence:

- `nirs4all-ecosystem/docs/agent_reports/WAVE_2L_POST_RESET_CONTROL.md:89-108`
  names the dirty `nirs4all/` and `dag-ml-data/` diffs and explicitly says the
  `nirs4all` diff "needs parity review before integration".
- `WAVE_2L_POST_RESET_CONTROL.md:124-132` says the parity/native agent must audit
  the dirty `nirs4all` diff before integration.
- `rg --files nirs4all-ecosystem/docs/agent_reports | rg 'W2L|LANE_B|LANE_C|LANE_F|PYREF|NATIVE'`
  found no W2L Lane B/C/F final report.
- `git -C nirs4all status --short --branch` shows five modified files:
  `docs/compatibility.json`, `detect.py`, `run_backend.py`, `run_paths.py`, and
  `test_conformance_dual_engine.py`.
- `git -C nirs4all diff --stat` reports `5 files changed, 783 insertions(+), 8 deletions(-)`.
- Current `docs/compatibility.json:386-395` records `fallback: 9`, `native: 78`,
  and `expected_fallback_target: 0`; `tests/integration/parity/test_conformance_dual_engine.py:310-324`
  no longer allowlists `multi_source_sources_concat_then_rf`.
- The diff wires a new source-concat path at
  `nirs4all/pipeline/dagml/run_backend.py:582` and `:669-671`, implemented in
  `nirs4all/pipeline/dagml/run_paths.py:466-535`.
- The same dirty diff adds `_run_by_source_stacking_branch()` at
  `nirs4all/pipeline/dagml/run_paths.py:1890-2142`, but `rg` finds no dispatch or
  call site beyond the definition. That is dead-code risk in a parity-critical path.

Impact: integration must not treat the current fallback reduction from 10 to 9 as
accepted evidence until Lane B/C/F or an equivalent reviewer signs it with targeted
and full parity gates. The current `nirs4all` branch also diverges from
`_worktrees/INT-nirs4all`: both ancestry checks returned `1`, and
`git -C nirs4all diff --shortstat HEAD..17ed929e...` reports
`45 files changed, 7028 insertions(+), 554 deletions(-)`.

### BLOCKER 2 - The central aggregation lock is stale and cannot be validated from the current workspace.

Evidence:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  failed with `error: lockfile is stale or inconsistent`.
- The manifest has lockstep and verification requirements at
  `docs/contracts/release/aggregation-manifest.n4a.json:14-32`.
- The manifest now requires `lite_release_topology_manifest` and a git-head
  `release_topology_manifest` artifact at
  `aggregation-manifest.n4a.json:486-530`.
- The checked-in lock still has old pins: `dag_ml` `f58d7bf...`
  at `aggregation-lock.n4a.lock.json:171-175`, `dag_ml_data` `347c15f...`
  at `:308-312`, `io` `84ab189...` at `:519-523`, `lite` `c14dcca...`
  at `:589-593`, and `methods` `7602eb...` at `:679-683`.
- The same lock has `lite` `contract_artifacts: []` at
  `aggregation-lock.n4a.lock.json:551`, contradicting the current manifest's
  topology artifact requirement.
- Lane A's W2K candidate pins are listed in
  `WAVE_2L_POST_RESET_CONTROL.md:159-167`, but the final selected clean root has
  not been materialized into the checked-in lock.

Impact: final release evidence cannot come from the checked-in lock. It also must
not be regenerated from the dirty current workspace: `dag-ml-data/` still has a
modified generated `_dag_ml_data.abi3.so`, and `nirs4all-lite/` now has a dirty
Lane D/E code fix.

### BLOCKER 3 - Several current checkouts are reset behind the reviewed integration heads, so `main` is not final V1 evidence.

Evidence:

- Studio: `git -C nirs4all-studio diff --shortstat HEAD..83aab1c...` reports
  `76 files changed, 5126 insertions(+), 484 deletions(-)`. `rg` for
  `allow_fallback|engine_requested|fallback_policy|RuntimeEngineBadge|buildRuntimeEngineStatus`
  under current `api src tests` returned `exit=1`.
- Web: `git -C nirs4all-web diff --shortstat HEAD..ee8ea7a...` reports
  `27 files changed, 2349 insertions(+), 24 deletions(-)`. `rg` for
  `allowFallback|RtError|rt-result|schedulerFallback|runtimeErrors` under current
  `studio-lite/src studio-lite/tests` returned `exit=1`.
- The W2L control summarizes the same Studio/Web gap at
  `WAVE_2L_POST_RESET_CONTROL.md:175-190`; Lane H says current reset mains are
  mostly pre-runtime-contract and full INT chains should be reviewed as stacks.
- IO: `git -C nirs4all-io diff --shortstat HEAD..e52eecd...` reports
  `12 files changed, 2166 insertions(+), 8 deletions(-)`. `rg` for
  `to_dataset_package|target=.*dataset_package|DatasetPackage|to_io_spec` in
  current `nirs4all-io/src tests` returned `exit=1`, while the same search in
  `_worktrees/INT-io` finds the public DatasetPackage API and tests.
- `WAVE_2L_POST_RESET_CONTROL.md:136-148` also warns not to generate final
  release-lock pins from stale `nirs4all-io/` at `5651da5`.

Impact: any integration script or release lock that reads the reset `main`
checkouts instead of the reviewed `INT-*` heads will miss strict runtime fallback,
runtime envelopes, and the IO DatasetPackage bridge.

### HIGH 1 - The old Claude worktree and Claude-related processes remain external, stale state.

Evidence:

- `git -C nirs4all/.claude/worktrees/agent-a5af0970d430760ab status --short --branch`
  reports untracked `tests/integration/parity/conformance/` and
  `tests/integration/parity/test_dual_engine_conformance.py`.
- `git -C nirs4all/.claude/worktrees/agent-a5af0970d430760ab rev-parse HEAD`
  is `4e9dfe1ca0c0fc4be308f29a17b5d4e8493eb532`; `git -C nirs4all branch --contains 4e9dfe1ca0c0`
  shows that head is already contained by `main`, `refactor/L17-pyref`, and
  `refactor/integration-nirs4all`.
- `ps -eo pid,ppid,comm,args | rg -i 'claude|claude-code|app-server'` still shows
  multiple `claude-code-mcp` processes and an old Codex app-server broker under
  `/home/delete/nirs4all/nirs4all`.
- `WAVE_2L_POST_RESET_CONTROL.md:73-87` already states this Claude work is not a
  trusted merge source and that the untracked parity harness is stale.

Impact: the worktree should remain excluded from integration. If cleanup is wanted,
it needs explicit coordinator/user approval, not an implicit reset.

### HIGH 2 - Lane D/E completed after reset with a real `nirs4all-lite` code change, but the checkout is dirty and the lock still points at the old lite commit.

Evidence:

- `WAVE_2L_POST_RESET_CONTROL.md:205-230` now records Lane D/E complete and one
  bounded code change in `nirs4all-lite`.
- `git -C nirs4all-lite status --short --branch` reports
  `M bindings/python/src/nirs4all_core/__init__.py`.
- Current `nirs4all-lite/bindings/python/src/nirs4all_core/__init__.py:31-44`
  dynamically mirrors `CORE_FACADE_EXPORTS + TOPOLOGY_EXPORTS` from
  `nirs4all_lite`.
- `git -C nirs4all-lite diff --stat` reports
  `1 file changed, 6 insertions(+), 26 deletions(-)`.

Impact: this may be a valid lint/topology fix, but final locking must either
commit/select it intentionally or exclude it. The release lock's stale lite pin
`c14dcca...` predates both W94 and this D/E fix.

### HIGH 3 - Some release-blocking gates are still documented as gaps, not passed evidence.

Evidence:

- `nirs4all/docs/compatibility.json:348-377` marks `n4a_cross_engine`,
  `workspace_cross_engine`, `error_refusal_parity`, and `studio_oracle` as `gap`.
- `nirs4all-ecosystem/docs/REFACTORING_ROADMAP_CRITICAL_REVIEW.md:311-318`
  requires cross-engine `.n4a`, workspace-schema, methods-installed CI,
  `.so` freshness, `EXPECTED_FALLBACK == empty`, native export coverage, and one
  auditable command before treating parity/drop as done.
- `nirs4all-ecosystem/docs/PARALLEL_REFACTORING_ROADMAP.md:1008-1010`
  makes `.so` freshness, cross-engine bundle/workspace, default dag-ml suite, and
  migration-tool availability mandatory for backend/cutover changes.
- Lane H did not run Studio Playwright because of the port-8000 contamination
  risk (`W2L_LANE_H_STUDIO_WEB_RUNTIME.md:84-88`).
- Lane D/E did not run R or Octave gates because binaries were unavailable
  (`W2L_LANE_DE_TOOLS_LITE_NAMESPACES.md:120-123`).

Impact: W2L can choose integration heads, but V1 release/drop claims still need
these gates before public proof.

### MEDIUM 1 - Agent reports and this control evidence live under ignored `docs/`.

Evidence:

- `nirs4all-ecosystem/.gitignore:8-9` ignores `/docs/`.
- `git -C nirs4all-ecosystem ls-files docs/agent_reports/...` returned no tracked
  files for W2L reports.
- `git -C nirs4all-ecosystem check-ignore -v docs/agent_reports/WAVE_2L_POST_RESET_CONTROL.md`
  reports `.gitignore:9:/docs/`.
- Lane A and Lane G also note that report paths will need `git add -f` if the
  coordinator wants them tracked.

Impact: reports are useful local evidence, but they are not durable release
evidence until force-added or moved to a tracked path.

### MEDIUM 2 - The release distribution matrix path is still unresolved.

Evidence:

- `WAVE_2L_POST_RESET_CONTROL.md:34-39` says
  `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md` is absent and the
  nearest local substitute is `/home/delete/nirs4all/RELEASE_DISTRIBUTION_INVENTORY.md`.
- `W2L_LANE_A_RELEASE_LOCK.md:71-73` reports the same absence.

Impact: future release agents can drift by using different matrix/inventory paths.
Add a tracked pointer or rename by decision before more release-topology work.

## Open questions

- Which heads are the final release roots: the clean W2K `INT-*` heads, the current
  reset checkouts, or a new integration branch that merges selected W2L patches?
- Should the dirty `nirs4all` source-concat fallback reduction be integrated,
  reworked, or discarded? Who owns the review of the unreferenced by-source stacking
  code added in the same diff?
- Should `nirs4all-studio/main` and `nirs4all-web/main` be fast-forwarded/rebased to
  the full W2K runtime chains, or should the reset mains stay pre-contract for now?
- Should primary `nirs4all-io/` be moved to `e52eecd`, or should release tooling
  explicitly read `_worktrees/INT-io`?
- How should the dirty `dag-ml-data` generated binary and dirty `nirs4all-lite`
  facade fix be cleaned, committed, or excluded before lock generation?
- Should ignored W2L reports be force-added as release audit evidence?
- Should the old Claude worktree/process tree be cleaned up after explicit approval?

## Required gates

- Clean selected worktree roots for all release members, then regenerate and validate
  `docs/contracts/release/aggregation-lock.n4a.lock.json`; rerun
  `pytest -q tests/test_release_lock.py`.
- Lane B/C/F or equivalent: review the dirty `nirs4all` diff; run targeted parity
  for `multi_source_sources_concat_then_rf`, `test_native_fallback_boundary`, full
  `tests/integration/parity`, coverage meter, `.so` freshness, `ruff`, `mypy`, and
  `git diff --check`.
- `dag-ml` / `dag-ml-data`: run paired `validate_contracts.py` with sibling roots
  and ensure no stale generated `.abi3.so` is carried into release evidence.
- IO/datasets/formats: run full final-pin gates, not only focused bridge tests.
- Studio/Web: integrate or deliberately reject the full INT runtime chains; rerun
  the W102 backend/Vitest/Web build gates, then Studio Playwright after fixing the
  port-8000 environment.
- Tools/lite: commit or discard the `nirs4all_core` facade fix; rerun lite topology,
  Python/Rust/WASM gates; run R and Octave gates in CI or document them as release
  exceptions.
- Final release audit: all selected repos clean, no ignored/untracked evidence used
  as proof unless force-added, no Claude worktree files in the integration source.

## Risks

- A release lock generated from `/home/delete/nirs4all` as-is would mix stale
  checkouts and dirty local state.
- Current Studio/Web mains do not enforce the strict fallback/runtime contract; any
  V1 UI/runtime claim based on those mains is stale.
- Current `nirs4all-io/` lacks the DatasetPackage bridge required by datasets main.
- The dirty `nirs4all` diff reduces fallback count without a final parity report and
  adds apparent dead code in a critical runtime file.
- Claude-related external processes remain able to mutate workspace state if reused.
- Ignored reports can disappear from release evidence unless intentionally tracked.

## No-code confirmation

I made no code changes and did not use Claude or Claude tools. I did not touch
`nirs4all-drafts` or `nirs4all-lab`. The only file written by this Lane K review is
`nirs4all-ecosystem/docs/agent_reports/W2L_LANE_K_FINAL_REVIEW.md`.
