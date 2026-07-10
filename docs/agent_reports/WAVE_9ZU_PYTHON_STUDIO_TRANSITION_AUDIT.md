# Wave 9ZU - Python/Studio transition audit and targeted hardening

Date: 2026-07-10

## Scope

Transition-release readiness for the two held projects:

- `nirs4all` Python library: dual-backend transition surface, legacy/new workspace conversion route, `.n4a` bundle guard.
- `nirs4all-studio`: backend selector and legacy workspace warning/conversion coverage.

No changes were made to `nirs4all-drafts`, `nirs4all-lab`, or `nirs4all-ui`.

## Agents

- Claude Code / Python audit: read-only audit of `nirs4all` backend and workspace transition. Result: substantially implemented; flagged `.n4a` forward-version guard, public fallback proof, and runtime auto-migration/documentation tension.
- Claude Code / Studio audit: read-only audit of `nirs4all-studio` transition UX/backend. Result: substantially implemented; flagged thin e2e coverage, per-run-only backend selection, warning discoverability, and untested legacy detection branches.
- Codex Hilbert / converter audit: read-only audit of `nirs4all-tools` and Python wrapper. Result: converter path is valid; `nirs4all[transition]` needed DuckDB/Parquet extras; docs still need reconciliation around in-place DuckDB migration.
- Codex Lovelace / e2e audit: read-only audit of ecosystem cross-language scenarios. Result: 11 executable scenarios and 70 artifacts exist, but runtime evidence was stale at audit time.

## Integrated Changes

### `nirs4all`

Commits:

- `102c20760efb7dab422004780a2678ff47729aea`
- `12bb829ee8e54e7dd050802328bf9c0d64a76f3e`

Files changed:

- `pyproject.toml`
- `nirs4all/pipeline/bundle/constants.py`
- `nirs4all/pipeline/bundle/generator.py`
- `nirs4all/pipeline/bundle/loader.py`
- `tests/unit/cli/test_main.py`
- `tests/unit/pipeline/bundle/test_bundle.py`
- `docs/source/migration/duckdb_to_sqlite.md`
- `docs/source/user_guide/troubleshooting/migration.md`

Decisions:

- `nirs4all[transition]` now installs `nirs4all-tools[duckdb,parquet]>=0.0.5`, so the documented converter command can handle real legacy workspace inputs.
- Bundle format version is centralized in `nirs4all.pipeline.bundle.constants`.
- `BundleLoader` now refuses future `.n4a` bundle format versions with an explicit upgrade error instead of loading silently.
- Migration docs now mention the non-mutating transition converter path while preserving the existing Python auto-migration behavior.

Validation:

- `.venv/bin/ruff check nirs4all/pipeline/bundle/constants.py nirs4all/pipeline/bundle/generator.py nirs4all/pipeline/bundle/loader.py tests/unit/pipeline/bundle/test_bundle.py tests/unit/cli/test_main.py`
- `.venv/bin/mypy nirs4all/pipeline/bundle/loader.py nirs4all/pipeline/bundle/generator.py`
- `.venv/bin/python -m pytest -q tests/unit/pipeline/bundle/test_bundle.py tests/unit/cli/test_main.py tests/unit/workspace/test_workspace_compat.py`
- `.venv/bin/python -m build --sdist --wheel --outdir /tmp/n4a-transition-build2`
- Wheel metadata checked: `Requires-Dist: nirs4all-tools[duckdb,parquet]>=0.0.5; extra == "transition"`
- Docs build attempted with `.venv/bin/python -m sphinx ...`; not run because Sphinx is not installed in this venv.

Result: local targeted validation green. The repository is clean after push. A new Pre-Publish workflow was not auto-triggered by this push; previous Pre-Publish was green on `1bc3dcad`.

### `nirs4all-studio`

Commit: `ae5b4eba15a8b48695498efac066f9971e12a75b`

Files changed:

- `tests/test_workspace_transition.py`

Decisions:

- Added backend tests for the two previously untested legacy transition branches:
  - `sqlite-workspace-legacy-arrays`
  - `fs-runs-legacy`
- No functional Studio code was changed in this batch.

Validation:

- `rtk pytest tests/test_workspace_transition.py -q`
- `rtk ruff check tests/test_workspace_transition.py`

Result: local targeted validation green. GitHub Studio checks were triggered on push and were still running at report creation.

## Remaining Risks / Follow-Up

- `nirs4all` still scopes `engine="dag-ml"` to `run()`. `predict`, `explain`, `retrain`, session and generate APIs intentionally reject non-legacy engines today.
- `nirs4all` still contains transition-era in-place DuckDB auto-migration in `WorkspaceStore`, while `nirs4all-tools` documents a no-in-place converter policy. This needs either a documented transition exception or a later removal with migration tests adjusted.
- Python docs now include the offline converter path, but the full release notes still need to state the exact transition policy and legacy-removal plan.
- Studio backend selection is per-run only. There is no global engine preference in Settings.
- Studio legacy warning is currently visible in Settings / Workspace Statistics, not as a workspace-open banner.
- Studio conversion writes a sibling `*-workspace-v2` directory and does not automatically re-link the active workspace.
- Full parity and fresh cross-language e2e evidence were not launched in this small batch; run them after the next larger stabilization batch.
