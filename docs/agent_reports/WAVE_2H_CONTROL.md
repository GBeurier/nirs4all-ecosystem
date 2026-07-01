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

## Wave 2H Agents

The internal agent limit allowed six concurrent workers. These are the implementation/review outcomes:

| Wave | Agent ID | Nickname | Target | Status |
| --- | --- | --- | --- | --- |
| W62 | `019f1bc4-fcb7-7061-a5d4-0b879d83ea2c` | Bernoulli | `branch_dup_three_way_merge_predictions` | partially integrated as list-branch stacking support; named-dict case remains fallback under W68 full-coverage policy |
| W63 | `019f1bc5-7c62-7c71-b642-362f3fb8acfe` | Singer | `branch_dup_named_with_metamodel` | blocked; report merged |
| W64 | `019f1bc5-dc42-7c73-aca0-f1160c2ed19e` | Kuhn | `branch_dup_merge_all` | integrated into `refactor/integration-nirs4all` |
| W65 | `019f1bc6-50b1-7533-bc68-166724671ea7` | Raman | `multi_source_by_source_branch_distinct_preproc` | integrated into `refactor/integration-nirs4all` |
| W66 | `019f1bc7-19cf-7b02-8a43-262eca47cfa7` | Mencius | `multi_source_per_source_models_stacking` | blocked; report committed |
| W67 | `019f1bc7-ab90-7122-998e-20486fd007e6` | Ptolemy | `multi_source_sources_concat_then_rf` | integrated into `refactor/integration-nirs4all` |

## Support Agents

| Wave | Role | Status |
| --- | --- | --- |
| W68 | Stack/OOF/refit contract audit for W62/W63/W66 | complete; integrated as commit `0aa2a674` |
| W69 | Source-layout contract audit for W65/W67 | complete; integrated as commit `362c2d79` |
| W70 | Coverage gates/readiness update once fallbacks are removed | superseded by integration commits and this control update |
| W71 | Integration review of W62-W67 patches | complete; report committed as `11b0f91` |

## Completed / Blocked Outcomes

| Wave | Outcome |
| --- | --- |
| W63 | Blocked intentionally. The case is not equivalent to simple collect-all stacking: legacy runs a branch-local `Ridge_MetaModel`, then a structured per-branch best-by-RMSE prediction selector into features, then final `Ridge`. `EXPECTED_FALLBACK` remains unchanged. Report: `W63_BRANCH_DUP_NAMED_METAMODEL.md`. |
| W68 | Complete. dag-ml already had the OOF/refit contract; nirs4all now emits `stacking_oof_refit_contract={"policy": "require_full_coverage"}` for full-coverage stacking meta nodes. Integrated commit: `0aa2a674`; report: `W68_STACKING_OOF_CONTRACT_AUDIT.md`. |
| W69 | Complete. nirs4all now emits the explicit multi-source `source_layout` contract consumed by W65/W67. Integrated commit: `362c2d79`; report: `W69_SOURCE_LAYOUT_CONTRACT_AUDIT.md`. |
| W65 | Green and integrated. `multi_source_by_source_branch_distinct_preproc` now runs native with source-layout keyed preprocessing. Integrated commit: `4ef0b3fe`; report: `W65_MULTISOURCE_DISTINCT_PREPROC.md`. |
| W62 | Adjusted during integration. The list-branch stacking path now runs native with full-coverage metadata (`bc0443f4`), but `branch_dup_three_way_merge_predictions` remains fallback because its named-dict branch shape makes legacy skip the refit surface that W68 requires native to validate. Report: `W62_BRANCH_DUP_THREE_WAY.md`. |
| W64 | Green and integrated. `branch_dup_merge_all` was removed from `EXPECTED_FALLBACK`. Integrated commit: `099da729`; report: `W64_BRANCH_DUP_MERGE_ALL.md`. |
| W67 | Green and integrated. `multi_source_sources_concat_then_rf` now runs native by preserving the legacy source-concat storage boundary. Integrated commit: `63976243`; report: `W67_MULTISOURCE_SOURCES_CONCAT_RF.md`. |
| W66 | Blocked intentionally. Boundary can run native, but parity fails because legacy Ridge fits on a cumulative `10755`-feature post-merge source layout, not a 3-column OOF matrix. Keep fallback. Report: `W66_MULTISOURCE_PER_SOURCE_STACKING.md`. |

## Coordination Rules

1. Direct code is authoritative; CodeGraph may be useful but must not override the checked-out source.
2. A fallback leaves `EXPECTED_FALLBACK` only when its targeted dual-engine parity is green and the fallback boundary/coverage meter remain green.
3. Do not change tolerances to hide drift.
4. Do not merge or delete the external Claude sessions' work.
5. Each implementation agent must write a report in this directory and commit green changes in its own workspace.

## Current Blocker

`B-010-FALLBACK-ZERO` remains blocked until the nirs4all fallback meter reaches `fallback=0`.
The current integrated baseline is `fallback=3, native=84, target=0`.

Remaining `EXPECTED_FALLBACK` entries:

- `branch_dup_three_way_merge_predictions`
- `branch_dup_named_with_metamodel`
- `multi_source_per_source_models_stacking`
