# Wave 2K Control Board

Date: 2026-07-01

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Purpose

Wave 2K follows Wave 2J, which integrated the first V1 cutover hardening:

- `nirs4all` integration head: default engine is now `dag-ml`.
- public `run()` fallback is strict by default (`allow_fallback=False`).
- dag-ml export no longer performs implicit legacy refit; the compatibility
  bridge is named explicitly.
- Studio/Web runtime envelopes and reusable UI primitives exist.
- `nirs4all-tools` carries the standalone legacy migration toolbox.
- cluster/provider V1 slices exist on their integration branches.

The remaining work is not another broad greenfield roadmap. It is a hardening
wave: sync stale control docs, pin lockstep contracts, verify packages/release
topology, remove remaining silent fallback defaults outside core, add realistic
migration/parity gates, and then review what is still missing.

## Preserved External Sessions

These processes were detected and intentionally left untouched:

| Process | PID | CWD | Notes |
| --- | ---: | --- | --- |
| Codex parent | 183569 | `/home/delete/nirs4all` | Current coordinator session. |
| Claude CLI | 208304 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`. |
| Claude CLI | 208423 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`. |
| claude-code-mcp | 205809 | `/home/delete/nirs4all` | High CPU; presumed owned by external Claude. |
| claude-code-mcp | 206845 | `/home/delete/nirs4all` | High CPU; presumed owned by external Claude. |
| Codex app-server from Claude plugin | 4054814 | `/home/delete/nirs4all/nirs4all` | Old Claude/Codex app-server with many MCP children; not treated as a W2K worker. |

The two active `claude` processes currently show no visible child worker
processes besides CodeGraph servers. The many older MCP children are preserved
as external state, not counted as managed W2K agents.

## Integration Bases At Wave Start

| Repo | Branch | Head at W2K audit |
| --- | --- | --- |
| `nirs4all` | `refactor/integration-nirs4all` | `f970bf0e` |
| `nirs4all-studio` | `refactor/integration-studio` | `1979b72` |
| `nirs4all-web` | `refactor/integration-web` | `60a0967` |
| `nirs4all-tools` | `main` | `44ce7a3` |
| `nirs4all-cluster` | `refactor/integration-cluster` | `eac4d0b` |
| `nirs4all-providers` | `refactor/integration-providers` | `1e289a9` |
| `dag-ml` | `refactor/integration-dagml` | `618ffb2` |
| `dag-ml-data` | current repo head | pending W91 audit |
| `nirs4all-io` | `refactor/integration-io` | `ccfea29` |
| `nirs4all-lite` | `refactor/integration-lite` | `0dad1c6` |

The dirty main checkout `nirs4all/` is not an integration base.

## Agents

| Wave | Engine | Agent/session | Worktree | Target | Report |
| --- | --- | --- | --- | --- | --- |
| W90 | Codex worker | `019f1c74-9911-7022-a1b4-f17d01efc6b6` / Meitner | ecosystem docs/scripts | Cutover state gate and stale roadmap sync. | `W90_CUTOVER_STATE_GATE.md` |
| W91 | Codex worker | `019f1c74-af0e-79a3-a222-c419b42e39d7` / Leibniz | `_worktrees/W91-dagml-lockstep` + `_worktrees/W91-dagml-data-lockstep` | dag-ml/dag-ml-data contract freshness and lockstep validation. | `W91_DAGML_LOCKSTEP_FRESHNESS.md` |
| W92 | Codex worker | `019f1c74-c574-73a1-ba33-5e3b3ea01b74` / Pasteur | `_worktrees/W92-methods-release-surface` | nirs4all-methods package/binding namespace and parity gate. | `W92_METHODS_RELEASE_SURFACE.md` |
| W93 | Codex worker | `019f1c74-dfc1-7040-ae9e-2c0f3bbbd9ec` / Darwin | `_worktrees/W93-io-datasets-bridge` + datasets/formats worktrees | Formats/IO/datasets reference dataset bridge. | `W93_IO_DATASETS_REFERENCE_BRIDGE.md` |
| W94 | Codex worker | `019f1c74-f4a6-7632-9ec2-645e02fa106b` / Fermat | `_worktrees/W94-lite-release-topology` | Lite/core release topology manifest consumer readiness. | `W94_LITE_RELEASE_TOPOLOGY.md` |
| W95 | Codex worker | `019f1c7e-83e6-78e2-b1d5-0f9c2ab838c4` / Bohr | `_worktrees/W95-studio-strict-runtime` | Studio strict fallback default. | `W95_STUDIO_STRICT_RUNTIME.md` |
| W96 | queued | pending | `_worktrees/W96-studio-runtime-e2e` + `_worktrees/W96-web-runtime-e2e` | Runtime UX/E2E smoke for Studio/Web. | `W96_RUNTIME_UX_E2E.md` |
| W97 | queued | pending | `_worktrees/W97-tools-real-goldens` | Real legacy converter golden fixtures. | `W97_TOOLS_REAL_GOLDENS.md` |
| W98 | queued | pending | `_worktrees/W98-nirs4all-full-parity` | Full Python-reference parity and cutover runner. | `W98_FULL_PYREF_PARITY.md` |
| W99 | queued | pending | ecosystem report only | Post-W2K integration review. | `W99_POST_W2K_REVIEW.md` |

## Launch Policy

The integrated agent backend normally accepts five concurrent workers. Launch
W90-W94 first. Launch W95-W99 only as slots open.

Do not launch W95 and W96 simultaneously if W95 needs frontend request-type
changes; otherwise their ownership is backend-vs-UX and can proceed in sequence.
Do not launch W99 until W90-W98 reports exist or have explicitly failed.

## Coordination Risks

- W90 and W94 can both be tempted to edit ecosystem release docs. W90 owns
  ecosystem status docs; W94 owns `nirs4all-lite` only.
- W95 and W96 both touch Studio. W95 owns backend strict fallback semantics;
  W96 owns UX/E2E verification.
- W91 must surface existing dag-ml schemas. It must not invent a parallel schema
  vocabulary in ecosystem docs.
- W98 must not paper over parity regressions with broad xfails.
- External Claude processes are preserved; if they modify files under an
  integration worktree, the coordinator must inspect and adapt before merging.

## Integrated During Wave

| Wave | Status | Evidence |
| --- | --- | --- |
| W90 | running | launched as Meitner (`019f1c74-9911-7022-a1b4-f17d01efc6b6`). |
| W91 | report complete | report commit `4afaad0`; paired dag-ml/dag-ml-data validation passed after aligning data side to integration head `818616e`; no new dag-ml commit. |
| W92 | running | launched as Pasteur (`019f1c74-c574-73a1-ba33-5e3b3ea01b74`). |
| W93 | running | launched as Darwin (`019f1c74-dfc1-7040-ae9e-2c0f3bbbd9ec`). |
| W94 | running | launched as Fermat (`019f1c74-f4a6-7632-9ec2-645e02fa106b`). |
| W95 | running | launched as Bohr (`019f1c7e-83e6-78e2-b1d5-0f9c2ab838c4`). |
| W96 | queued | - |
| W97 | queued | - |
| W98 | queued | - |
| W99 | queued | - |
