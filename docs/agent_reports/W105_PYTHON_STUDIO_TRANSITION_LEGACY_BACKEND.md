# W105 — Python/Studio transition legacy backend

Date: 2026-07-10

## Scope

Transition-release hardening for the two held production projects:

- `nirs4all` Python library: keep both `legacy` and `dag-ml` backends selectable, detect old workspace/save formats, warn with a concrete conversion command, and prevent accidental blank-store creation in old filesystem workspaces.
- `nirs4all-studio`: expose the same transition diagnosis in the workspace UI/API and provide a conversion action backed by `nirs4all-tools`.

## Decisions

- `nirs4all-tools` remains the canonical legacy reader/converter. The runtime does not duplicate full legacy readers.
- `nirs4all` gets an optional `transition` extra (`nirs4all-tools>=0.0.5`) and a CLI wrapper: `nirs4all workspace convert <input> --output <dir> --verify`.
- Existing DuckDB/SQLite legacy-array compatibility is preserved, but now emits a transition warning.
- Legacy filesystem `runs/*/*/manifest.yaml` workspaces are refused in-place by `WorkspaceStore` with a conversion command, because opening them as a new SQLite workspace would risk hiding old data behind a blank store.
- Studio conversion runs through a maintenance job and calls `python -m nirs4all_tools legacy migrate ... --target nirs4all-workspace-v2`.

## Files Modified

`nirs4all`:

- `nirs4all/workspace/compat.py`
- `nirs4all/pipeline/storage/workspace_store.py`
- `nirs4all/cli/commands/workspace.py`
- `pyproject.toml`
- `tests/unit/workspace/test_workspace_compat.py`
- `tests/unit/cli/test_main.py`

`nirs4all-studio`:

- `api/workspace/models.py`
- `api/workspace/services.py`
- `api/workspace/router_maintenance.py`
- `src/api/workspace.ts`
- `src/types/storage.ts`
- `src/components/settings/WorkspaceStats.tsx`
- `src/components/settings/WorkspaceStatsData.ts`
- `requirements.txt`
- `requirements-cpu.txt`
- `tests/test_workspace_transition.py`

## Tests Run

`nirs4all`:

- `.venv/bin/python -m ruff check nirs4all/workspace/compat.py nirs4all/cli/commands/workspace.py nirs4all/pipeline/storage/workspace_store.py tests/unit/workspace/test_workspace_compat.py tests/unit/cli/test_main.py`
- `.venv/bin/python -m pytest tests/unit/workspace/test_workspace_compat.py tests/unit/cli/test_main.py tests/unit/pipeline/test_engine_selector.py`
- Result: 39 passed.

`nirs4all-studio`:

- `ruff check api/workspace/models.py api/workspace/services.py api/workspace/router_maintenance.py tests/test_workspace_transition.py`
- `.venv/bin/python -m pytest tests/test_workspace_transition.py tests/test_runtime_engine.py tests/test_runs_engine_routing.py`
- Result: 37 passed, 7 expected warning-capture warnings from engine fallback tests.

## Risks / Follow-up

- Frontend Vitest/TypeScript was not runnable in this WSL shell because `node` is absent while `npm` resolves to a non-usable shim. Run `npm run lint:tsc` and `npm run test:frontend` in the configured Node environment before tagging Studio.
- Full parity is intentionally deferred until a larger batch, per project instruction.
- Studio UI conversion action is wired locally in Studio, not in shared `nirs4all-ui`, to avoid interfering with the concurrent quality work.
