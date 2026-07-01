# Wave 2H Control Board

Date: 2026-07-01

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Preserved External Sessions

These processes were detected and intentionally left untouched:

| Process | PID | CWD | Notes |
| --- | ---: | --- | --- |
| Claude CLI | 208304 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`, attached to `/dev/pts/10`. |
| Claude CLI | 208423 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`, attached to `/dev/pts/7`. |

Two orphan `claude-code-mcp` node processes (`205809`, `206845`) were also observed at high CPU.
They were not killed because they may belong to the external Claude sessions.

## Active Codex Agents

The internal agent limit allowed six concurrent workers. These are the live implementation agents:

| Wave | Agent ID | Nickname | Target | Status |
| --- | --- | --- | --- | --- |
| W62 | `019f1bc4-fcb7-7061-a5d4-0b879d83ea2c` | Bernoulli | `branch_dup_three_way_merge_predictions` | running |
| W63 | `019f1bc5-7c62-7c71-b642-362f3fb8acfe` | Singer | `branch_dup_named_with_metamodel` | blocked; report merged |
| W64 | `019f1bc5-dc42-7c73-aca0-f1160c2ed19e` | Kuhn | `branch_dup_merge_all` | green; report committed |
| W65 | `019f1bc6-50b1-7533-bc68-166724671ea7` | Raman | `multi_source_by_source_branch_distinct_preproc` | running |
| W66 | `019f1bc7-19cf-7b02-8a43-262eca47cfa7` | Mencius | `multi_source_per_source_models_stacking` | running |
| W67 | `019f1bc7-ab90-7122-998e-20486fd007e6` | Ptolemy | `multi_source_sources_concat_then_rf` | green; report committed; core staged/uncommitted |

## Queued Agents

Launch these when one or more active agents finish and are closed:

| Wave | Role | Target |
| --- | --- | --- |
| W68 | worker | Stack/OOF/refit contract audit for W62/W63/W66 across `dag-ml` and `nirs4all`. |
| W69 | worker | Source-layout contract audit for W65/W67 across `dag-ml-data`, `dag-ml`, and `nirs4all`. |
| W70 | worker | Coverage gates/readiness update once any fallback is removed. |
| W71 | reviewer | Integration review of W62-W67 patches before merging into `refactor/integration-nirs4all`. |

## Completed / Blocked Outcomes

| Wave | Outcome |
| --- | --- |
| W63 | Blocked intentionally. The case is not equivalent to simple collect-all stacking: legacy runs a branch-local `Ridge_MetaModel`, then a structured per-branch best-by-RMSE prediction selector into features, then final `Ridge`. `EXPECTED_FALLBACK` remains unchanged. Report: `W63_BRANCH_DUP_NAMED_METAMODEL.md`. |
| W68 | Complete. dag-ml already had the OOF/refit contract; nirs4all should emit `stacking_oof_refit_contract={"policy": "require_full_coverage"}` for full-coverage stacking meta nodes. W63 remains blocked because metadata alone does not implement branch-local MetaModel or structured selectors. Report: `W68_STACKING_OOF_CONTRACT_AUDIT.md`. |
| W64 | Green in its worktree. `branch_dup_merge_all` was removed from `EXPECTED_FALLBACK`; coverage meter reported `fallback=5, target=0`. Core commit: `7f6aa4a3`; report: `W64_BRANCH_DUP_MERGE_ALL.md`. |
| W67 | Green by targeted tests. `multi_source_sources_concat_then_rf` native path passed targeted conformance, selector, py_compile, and ruff. Core hunks were left staged/uncommitted in the shared `nirs4all` working branch and need integration review/extraction before landing. Report: `W67_MULTISOURCE_SOURCES_CONCAT_RF.md`. |

## Queued / Running Support Agents

| Wave | Status |
| --- | --- |
| W69 | complete; source-layout emitted in nirs4all working branch and report committed. |

## Coordination Rules

1. Direct code is authoritative; CodeGraph may be useful but must not override the checked-out source.
2. A fallback leaves `EXPECTED_FALLBACK` only when its targeted dual-engine parity is green and the fallback boundary/coverage meter remain green.
3. Do not change tolerances to hide drift.
4. Do not merge or delete the external Claude sessions' work.
5. Each implementation agent must write a report in this directory and commit green changes in its own workspace.

## Current Blocker

`B-010-FALLBACK-ZERO` remains blocked until the nirs4all fallback meter reaches `fallback=0`.
The last audited baseline was `fallback=6, target=0`.
