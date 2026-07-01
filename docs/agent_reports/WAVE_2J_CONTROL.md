# Wave 2J Control Board

Date: 2026-07-01

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Purpose

Wave 2J moves from the Wave 2I drain/adoption state to the V1 cutover hardening
state. The key premise verified before launch is that
`refactor/integration-nirs4all` has `coverage_meter OK (fallback=0, target=0)`,
but the code still contains V1-blocking implicit legacy behavior:

- `nirs4all/pipeline/engine.py` still defaults to `legacy`.
- `nirs4all/api/run.py` still permits transparent legacy fallback by default for
  caught dag-ml unsupported/unavailable signals.
- `nirs4all/api/result.py` still contains dag-ml export paths that can rerun the
  pipeline through `engine="legacy"` as a bridge.

## Preserved External Sessions

These sessions were detected and intentionally left untouched:

| Process | PID | CWD | Notes |
| --- | ---: | --- | --- |
| Claude CLI | 208304 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`. |
| Claude CLI | 208423 | `/home/delete/nirs4all` | External interactive Claude session, `--dangerously-skip-permissions`. |
| claude-code-mcp | 205809 | `/home/delete/nirs4all` | High CPU; presumed owned by external Claude. |
| claude-code-mcp | 206845 | `/home/delete/nirs4all` | High CPU; presumed owned by external Claude. |

External Claude worktree preserved:
`/home/delete/nirs4all/nirs4all/.claude/worktrees/agent-a5af0970d430760ab`.

## Integration Bases

| Repo | Branch | Head at audit |
| --- | --- | --- |
| `nirs4all` | `refactor/integration-nirs4all` | `77c5afb1` |
| `nirs4all-studio` | `refactor/integration-studio` | `96f9239` |
| `nirs4all-web` | `refactor/integration-web` | `b498159` |
| `nirs4all-tools` | `main` | `3f8c34f` |
| `nirs4all-cluster` | `refactor/integration-cluster` | `ffad507` |
| `nirs4all-providers` | `refactor/integration-providers` | `a9fb457` |

The dirty main checkout `nirs4all/` is not an integration base.

## Agents

| Wave | Engine | Agent/session | Worktree | Target | Report |
| --- | --- | --- | --- | --- | --- |
| W82 | Codex worker | pending | `_worktrees/W82-nirs4all-cutover-strict` | Legacy-DROP cutover branch: default dag-ml, explicit fallback only. | `W82_LEGACY_DROP_CUTOVER.md` |
| W83 | Codex worker | pending | `_worktrees/W83-nirs4all-export-no-legacy` | Remove implicit dag-ml export legacy refit bridge from V1 path. | `W83_EXPORT_NO_LEGACY_REFIT.md` |
| W84 | Codex worker | pending | `_worktrees/W84-tools-legacy-converter` | Harden standalone converter for old predictions/pipelines/workspaces. | `W84_TOOLS_LEGACY_CONVERTER.md` |
| W85 | Codex worker | pending | `_worktrees/W85-studio-runtime-v1` | Studio backend runtime envelope as source of truth. | `W85_STUDIO_RUNTIME_V1.md` |
| W86 | Codex worker | pending | `_worktrees/W86-studio-ui-runtime` | Studio reusable runtime UI components. | `W86_STUDIO_UI_RUNTIME_COMPONENTS.md` |
| W87 | Codex worker | pending | `_worktrees/W87-web-runtime-v1` | Web runtime V1 cutover, no silent fallback diagnostics. | `W87_WEB_RUNTIME_V1.md` |
| W88 | Codex worker | pending | `_worktrees/W88-cluster-v1-dag` | Cluster V1 DAG scheduling, rights and worker-loss semantics. | `W88_CLUSTER_V1_DAG.md` |
| W89 | Codex worker | pending | `_worktrees/W89-providers-pipeline-services` | Repository/benchmarks pipeline service contracts. | `W89_PROVIDERS_PIPELINE_SERVICES.md` |

## Coordination Rules

1. W82 and W83 both edit `nirs4all`, but have disjoint primary files:
   `engine.py`/`run.py` versus `result.py`.
2. W85 and W86 both edit Studio, but backend and frontend ownership are split.
3. W84 must keep converter behavior standalone; it must not add legacy readers to
   V1 runtime packages.
4. W89 must not invent repository upload support; the clarified model is
   read-side `get_pipeline_list` / `get_pipeline`.
5. The coordinator integrates only scoped, committed, green changes and records
   test evidence here after agents finish.
