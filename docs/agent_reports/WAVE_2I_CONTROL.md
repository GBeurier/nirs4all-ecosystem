# Wave 2I Control Board

Date: 2026-07-01

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Purpose

Wave 2I starts the next ten-agent batch toward the full refactoring goal after the
Wave 2H integration baseline:

- `nirs4all` integration head: `63976243`
- `nirs4all-studio` integration head: `b427a22`
- `nirs4all-web` integration head: `f87a969`
- `nirs4all-cluster` integration head: `51ee2a6`
- `nirs4all-providers` integration head: `8476a3f`
- `nirs4all-lite` integration head: `2f379ef`
- current fallback meter target: `fallback=3 -> 0`

## Preserved External Sessions

These external interactive sessions were detected and intentionally left
untouched:

| Process | PID | CWD | Notes |
| --- | ---: | --- | --- |
| Claude CLI | 208304 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`. |
| Claude CLI | 208423 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`. |

Two orphan-looking `claude-code-mcp` node processes (`205809`, `206845`) are
still high-CPU. They were not killed because they may belong to the external
Claude sessions.

## Agents

| Wave | Engine | Agent/session | Worktree | Target | Report |
| --- | --- | --- | --- | --- | --- |
| W72 | Codex worker | `019f1c27-d4f4-7ad1-9373-1626adc11454` / Herschel | `_worktrees/W72-nirs4all-branchdup-three-way-v2` | Drain or re-block `branch_dup_three_way_merge_predictions` under W68 full-coverage policy. | `W72_BRANCH_DUP_THREE_WAY_V2.md` |
| W73 | Codex worker | `019f1c27-d607-7252-90ec-fd6b73fad683` / Euclid | `_worktrees/W73-nirs4all-branchdup-named-metamodel` | Drain or re-block `branch_dup_named_with_metamodel`. | `W73_BRANCH_DUP_NAMED_METAMODEL.md` |
| W74 | Codex worker | `019f1c27-d737-74a2-b258-62b5bce984b1` / McClintock | `_worktrees/W74-nirs4all-multisource-stacking` | Drain or re-block `multi_source_per_source_models_stacking`. | `W74_MULTISOURCE_PER_SOURCE_STACKING.md` |
| W75 | Codex worker | `019f1c27-d89a-7543-aeac-bda7ba51ee80` / Sartre | `_worktrees/W75-nirs4all-artifact-error-parity` | Advance B-011 artifact/workspace/error parity. | `W75_ARTIFACT_ERROR_PARITY.md` |
| W76 | Codex worker | `019f1c27-d9b6-7d92-b2ae-6a8aee92d630` / Dirac | `_worktrees/W76-studio-runtime-bypass` | Advance Studio runtime/bypass parity. | `W76_STUDIO_RUNTIME_BYPASS.md` |
| W77 | Codex CLI | exec `64309`, Codex `019f1c30-9fe1-7f93-9624-fee77c9897e1` | `_worktrees/W77-web-runtime-cutover` | Advance Web runtime/RtResult/RtError adoption. | `W77_WEB_RUNTIME_CUTOVER.md` |
| W78 | Codex CLI | exec `66194`, Codex `019f1c31-5291-7ae0-80f9-110431d32474` | `_worktrees/W78-tools-migration-complete` | Advance `nirs4all-tools` migration completeness. | `W78_TOOLS_MIGRATION_COMPLETE.md` |
| W79 | Codex CLI | exec `83733`, Codex `019f1c31-52d1-7d52-88dd-1cb434fa2b0b` | `_worktrees/W79-cluster-scheduler-dag` | Advance cluster real-DAG scheduler/RBAC behavior. | `W79_CLUSTER_SCHEDULER_DAG.md` |
| W80 | Codex CLI | exec `78950`, Codex `019f1c31-5371-7513-8690-2b06020270ab` | `_worktrees/W80-providers-real-services` | Advance provider real service contracts. | `W80_PROVIDERS_REAL_SERVICES.md` |
| W81 | Codex CLI | exec `73940`, Codex `019f1c31-53a8-7243-a4c4-abbd330c7774` | `_worktrees/W81-core-release-topology` | Advance core/release topology and additive facades. | `W81_CORE_RELEASE_TOPOLOGY.md` |

Claude Code sessions were attempted for W77-W81 first, but each hit the weekly
Claude limit (`resets Jul 3, 7am Europe/Paris`). Those tasks were relaunched as
controlled Codex CLI sessions instead.

## Integrated During Wave

| Wave | Status | Evidence |
| --- | --- | --- |
| W76 | integrated into `refactor/integration-studio` | commit `96f9239`; `tests/test_runtime_engine.py` 12 passed; Ruff passed; `tests/test_runs_engine_routing.py` 14 passed |

## Integration Rules

1. Agents write code only in their assigned worktree.
2. Agents write a report in `docs/agent_reports/` but do not commit
   `nirs4all-ecosystem`.
3. Green code changes must be committed in the assigned worktree only.
4. The coordinator integrates reports and cherry-picks only green, scoped commits.
5. Fallback entries leave `EXPECTED_FALLBACK` only when targeted dual-engine
   parity, `native_fallback_boundary`, and `coverage_meter` are green.
6. No agent may touch `nirs4all-drafts` or `nirs4all-lab`.

## Current Expected Outcomes

| Outcome | Requirement |
| --- | --- |
| Fallback drain | W72/W73/W74 may reduce `EXPECTED_FALLBACK` from 3 to 0 only with parity proof. |
| PYREF unblock | W75 should either land a concrete B-011 slice or produce exact remaining blockers. |
| Runtime/product adoption | W76/W77 should move Studio/Web away from backend-specific interpretation toward runtime contracts. |
| Migration safety | W78 should improve standalone conversion/verification without adding runtime legacy readers. |
| Ecosystem services | W79/W80/W81 should advance cluster/providers/core-release topology without breaking existing imports/APIs. |
