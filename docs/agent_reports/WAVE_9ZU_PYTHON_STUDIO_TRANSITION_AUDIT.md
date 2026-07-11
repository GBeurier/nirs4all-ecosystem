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

Follow-up commit: `e32bfe5a`

Additional files changed:

- `tests/unit/workspace/test_workspace_compat.py`

Additional decisions:

- Added direct coverage for the legacy DuckDB workspace warning before migration.
- Verified that the warning gives the user the `nirs4all workspace convert` command before the compatibility path migrates to SQLite.

Additional validation:

- `.venv/bin/python -m pytest -q tests/unit/workspace/test_workspace_compat.py tests/unit/api/test_engine_transition.py tests/unit/pipeline/test_engine_selector.py` (`21 passed`)
- `.venv/bin/ruff check tests/unit/workspace/test_workspace_compat.py`
- No full Pre-Publish rerun for this test-only follow-up; reserve the long gate for the next larger parity batch.

Follow-up commit: `8b003429`

Additional files changed:

- `nirs4all/pipeline/engine.py`
- `tests/unit/api/test_engine_transition.py`

Additional decisions:

- Public helper APIs that are still legacy-only (`predict`, `explain`, `retrain`) now tolerate an inherited `N4A_ENGINE=dag-ml` environment variable.
- Explicit `engine="dag-ml"` on those helpers still fails fast with `NotImplementedError`, preserving the transition boundary.
- The inherited environment case now emits a `RuntimeWarning` and uses `engine="legacy"`, which keeps old scripts working under a process-wide dag-ml preference.

Additional validation:

- `.venv/bin/python -m pytest -q tests/unit/api/test_engine_transition.py tests/unit/pipeline/test_engine_selector.py` (`15 passed`)
- `.venv/bin/ruff check nirs4all/pipeline/engine.py tests/unit/api/test_engine_transition.py`
- GitHub `Pre-Publish Check` green on `8b003429`:
  - Ruff
  - mypy
  - docs strict build
  - package build and wheel install
  - user, developer and reference examples
  - full pytest + coverage on Windows 3.11, Windows 3.13, Ubuntu 3.11, Ubuntu 3.13 and macOS 3.13

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

Result:

- Local targeted validation green.
- GitHub `CI` green on `ae5b4eb`.
- GitHub `Playwright E2E Tests` green on `ae5b4eb` with `63 passed`.
- GitHub `version-guard` green on `ae5b4eb`.

Follow-up commit: `fc7925d297dcd628d8cffb6d81e3bd318d00aa0d`

Additional files changed:

- `api/workspace/models.py`
- `api/workspace/router_maintenance.py`
- `src/api/workspace.ts`
- `src/components/settings/WorkspaceStats.tsx`
- `src/components/settings/__tests__/WorkspaceStats.test.tsx`
- `src/types/storage.ts`
- `tests/test_workspace_transition.py`

Additional decisions:

- Legacy workspace conversion now links and activates the converted workspace after a successful conversion by default.
- Conversion remains successful if linking fails; the response records `link_error` so the UI can show the manual fallback.
- The frontend now requests `link_converted_workspace: true` from Workspace Statistics conversion.

Additional validation:

- `rtk pytest tests/test_workspace_transition.py -q` (`6 passed`)
- `rtk ruff check api/workspace/models.py api/workspace/router_maintenance.py tests/test_workspace_transition.py`
- Linux Node direct Vitest run for `src/components/settings/__tests__/WorkspaceStats.test.tsx` (`1 passed`)
- Linux Node direct `tsc --noEmit`
- Linux Node direct ESLint on touched frontend files
- GitHub `CI` green on `fc7925d`.
- GitHub `Playwright E2E Tests` green on `fc7925d` with `63 passed`.
- GitHub `version-guard` green on `fc7925d`.

Follow-up commit: `c88508e27376229101ea3a95e99d1f68f7fd0e7b`

Additional files changed:

- `src/lib/runtimeBackendPreference.ts`
- `src/lib/runtimeBackendPreference.test.ts`
- `src/components/settings/RuntimeBackendPreference.tsx`
- `src/pages/SettingsSections.tsx`
- `src/pages/NewExperiment.tsx`
- `src/components/pipeline-editor/PipelineExecutionDialog.tsx`

Additional decisions:

- Studio now exposes a global runtime backend preference in Settings.
- New experiments and pipeline-editor executions consume the same persisted preference.
- `dag-ml` fallback is persisted only when the selected backend is `dag-ml`; legacy/default selections cannot retain a stale fallback flag.

Additional validation:

- Linux Node direct Vitest run for `src/lib/runtimeBackendPreference.test.ts` and `src/components/runtime/RuntimeComponents.test.tsx` (`9 passed`)
- Linux Node direct `tsc --noEmit`
- Linux Node direct ESLint on touched frontend files
- GitHub `CI` green on `c88508e`.
- GitHub `Playwright E2E Tests` green on `c88508e` with `63 passed`.
- GitHub `version-guard` green on `c88508e`.

Follow-up commit: `c35b98207891da1beddff6ca26081d5d74173dc6`

Additional files changed:

- `scripts/python-runtime-config.cjs`
- `requirements.txt`
- `requirements-cpu.txt`
- `api/workspace/models.py`
- `api/workspace/router_maintenance.py`
- `api/workspace/services.py`
- `src/types/storage.ts`
- `src/components/settings/WorkspaceStats.tsx`
- `tests/test_workspace_transition.py`

Additional decisions:

- Studio runtime requirements now install `nirs4all-tools[duckdb,parquet]>=0.0.5`, matching the legacy workspace converter extras required for real DuckDB/Parquet inputs.
- A converter exit code `10` is treated as best-effort success, but Studio no longer auto-links or activates that output.
- The conversion response now reports `best_effort` and `activation_skipped`, so the UI can distinguish a clean conversion from a preserved/manual-review output.

Additional validation:

- `rtk pytest tests/test_workspace_transition.py -q` (`7 passed`)
- `rtk ruff check api/workspace/models.py api/workspace/router_maintenance.py api/workspace/services.py tests/test_workspace_transition.py`
- `node scripts/check-dep-sync.cjs`
- Linux Node direct `tsc --noEmit`
- Linux Node direct ESLint on touched frontend files
- Linux Node direct Vitest run for `src/components/settings/__tests__/WorkspaceStats.test.tsx` and `src/lib/runtimeBackendPreference.test.ts` (`5 passed`)
- GitHub `CI` green on `c35b982`.
- GitHub `Playwright E2E Tests` green on `c35b982` with `63 passed`.
- GitHub `version-guard` green on `c35b982`.

Follow-up commit: `08328d3640dd1274b0c16e6e6a46e41a813fffdd`

Additional files changed:

- `src/components/layout/AppLayout.tsx`
- `src/components/layout/LegacyWorkspaceBanner.tsx`
- `src/components/layout/__tests__/LegacyWorkspaceBanner.test.tsx`

Additional decisions:

- Studio now checks the active workspace transition status from the main layout.
- If a legacy workspace is active, Studio shows a top-level warning immediately after startup and links to `Settings > Workspaces` for conversion.
- V1 workspaces and unavailable transition-status calls keep the banner hidden.

Additional validation:

- Linux Node direct Vitest run for `src/components/layout/__tests__/LegacyWorkspaceBanner.test.tsx` (`2 passed`)
- Linux Node direct `tsc --noEmit`
- Linux Node direct ESLint on touched frontend files
- GitHub `CI` green on `08328d3`.
- GitHub `Playwright E2E Tests` green on `08328d3` with `63 passed`.
- GitHub `version-guard` green on `08328d3`.

Follow-up commit: `1970b885822368602e4fcd54b211a0b9b2a9d71b`

Additional files changed:

- `api/training.py`
- `tests/test_training_runtime_engine.py`

Additional decisions:

- The legacy `/training/start` Studio route now accepts `engine` and `allow_fallback`, persists them in the background job config, and forwards them to `nirs4all.run`.
- Training jobs now use the same `engine_run_kwargs`, `observe_engine`, and `fallback_policy_record` helpers as the main runs backend, so completed training results preserve requested/actual runtime metadata.
- This closes one secondary execution route that previously ignored the global backend preference and could silently run with the library default.

Additional validation:

- `rtk pytest tests/test_training_runtime_engine.py -q` (`3 passed`)
- `rtk pytest tests/test_training_runtime_engine.py tests/test_runtime_engine.py tests/test_runs_engine_routing.py -q` (`40 passed`)
- `rtk ruff check api/training.py tests/test_training_runtime_engine.py`
- GitHub `CI` green on `1970b88`.
- GitHub `Playwright E2E Tests` green on `1970b88` with `63 passed`.
- GitHub `version-guard` green on `1970b88`.

Follow-up commit: `514ebe171124c2d01417cb84b44ce770c9643b53`

Additional files changed:

- `api/automl.py`
- `api/execution_driver.py`
- `tests/test_analysis_execution_metadata.py`
- `tests/test_automl_runtime_engine.py`

Additional decisions:

- The legacy `/automl/start` Studio route now accepts `engine` and `allow_fallback`, records them in analysis execution metadata, and forwards them to `nirs4all.run`.
- Analysis execution metadata now exposes the same fallback policy envelope used by normal run execution requests.
- AutoML results now persist requested/actual runtime engine metadata, diagnostics source, fallback policy and native result references when available.

Additional validation:

- `rtk pytest tests/test_analysis_execution_metadata.py tests/test_automl_runtime_engine.py tests/test_runtime_engine.py -q` (`26 passed`)
- `rtk pytest tests/test_execution_driver.py tests/test_runs_execution_backend.py tests/test_training_runtime_engine.py tests/test_automl_runtime_engine.py tests/test_analysis_execution_metadata.py -q` (`59 passed`)
- `PYTHONPATH=/home/delete/nirs4all/nirs4all rtk pytest tests/test_runtime_engine.py tests/test_runs_engine_routing.py tests/test_training_runtime_engine.py tests/test_automl_runtime_engine.py tests/test_analysis_execution_metadata.py -q` (`50 passed`)
- `rtk ruff check api/automl.py api/execution_driver.py tests/test_analysis_execution_metadata.py tests/test_automl_runtime_engine.py`
- GitHub `CI` green on `514ebe1`.
- GitHub `Playwright E2E Tests` green on `514ebe1` with `63 passed`.
- GitHub `version-guard` green on `514ebe1`.

### `nirs4all-cockpit`

Commit: `7a78202`

Follow-up commit: `725ebcd`

Files changed:

- `data/current.json`
- `data/manual-actions.json`

Decisions:

- Refreshed public cockpit snapshot after the Python/Studio/ecosystem pushes.
- Refreshed public cockpit snapshot again after the Studio conversion-linking follow-up.

Validation:

- `n4a-cockpit collect`
- `pytest -q` (`146 passed`)
- `ruff check .`
- `n4a-cockpit validate-targets ops/targets.yaml`
- GitHub `ci` green on `725ebcd`.
- GitHub `pages` green on `725ebcd`.
- GitHub `version-guard` green on `725ebcd`.

Snapshot summary:

- `green=97`
- `stale=0`
- `pending=5`
- `broken=0`
- `excluded=1`

## Post-Batch Full Gates

Triggered after the Studio training and AutoML runtime-route hardening batch, with long-job monitoring left to completion.

- `nirs4all` Python `Pre-Publish Check` on `refactor/L17-pyref` / `8b003429`: GitHub run `29136909881`, green. Covered Ruff, mypy, strict docs build, package build/wheel install, user/developer/reference examples, and full pytest+coverage on Ubuntu 3.11/3.13, Windows 3.11/3.13 and macOS 3.13.
- `nirs4all-ecosystem` `Cross-language E2E scenarios` with `execute=true`, `allow_blocked=false`: GitHub run `29136909868`, green in 13m34s. Executed ready scenarios, verified ready artifacts, and checked the committed runtime evidence ledger.
- `nirs4all-ecosystem` `cutover-gates` in advisory mode with `timeout=1800`: GitHub run `29136909884`, green. Validated gate tooling and produced the advisory gate report artifact.

## Studio RC Installer Artifacts

Triggered a non-publishing Studio RC installer build after the latest Studio
transition hardening batch.

- `nirs4all-studio` `Release` workflow on `main` / `514ebe1` with manual
  input `tag=1.0.0-rc.2`, `skip_all_in_one=true`, `skip_docker=true`: GitHub
  run `29138360308`, green.
- Built and uploaded unsigned installer artifacts:
  - `installer-windows-x64` (250,862,344 bytes)
  - `installer-linux-x64` (277,582,596 bytes)
  - `installer-macos-x64` (158,203,036 bytes)
  - `installer-macos-arm64` (153,478,971 bytes)
- The workflow dispatch did not create a GitHub Release. The release job
  downloaded and prepared assets, but `Create GitHub Release` was skipped.
- All-in-one bundles and Docker images were intentionally skipped for this RC
  artifact gate.

### `nirs4all-ecosystem`

Commits:

- `70b6b46`
- `051a0e2`

Files changed:

- `docs/agent_reports/WAVE_9ZU_PYTHON_STUDIO_TRANSITION_AUDIT.md`

Validation:

- GitHub `version-guard` green.
- GitHub `Cross-language E2E scenarios` green for the report-only push.

## Remaining Risks / Follow-Up

- `nirs4all` still scopes explicit `engine="dag-ml"` to `run()`. `predict`, `explain`, `retrain`, session and generate APIs intentionally reject explicit non-legacy engines today, but inherited `N4A_ENGINE=dag-ml` no longer breaks those helpers.
- `nirs4all` still contains transition-era in-place DuckDB auto-migration in `WorkspaceStore`, while `nirs4all-tools` documents a no-in-place converter policy. This needs either a documented transition exception or a later removal with migration tests adjusted.
- Python docs now include the offline converter path, but the full release notes still need to state the exact transition policy and legacy-removal plan.
- Studio backend selection now has a global Settings preference for the new-experiment and pipeline-editor execution paths, and the legacy `/training/start` and `/automl/start` execution routes accept and record the same engine/fallback contract. Remaining secondary analysis routes were reviewed as legacy-only or non-`nirs4all.run` paths in this batch.
- Studio legacy warning is visible both in Settings / Workspace Statistics and as a workspace-open banner in the main layout.
- Studio conversion writes a sibling `*-workspace-v2` directory, links and activates clean conversions, and deliberately skips automatic activation for best-effort conversions.
- Studio packaged release metadata still pins the current Python library line until the held `nirs4all` transition release is cut.
- Fresh full Python Pre-Publish, cross-language executed E2E and cutover advisory gates are green after this batch. These are transition readiness gates, not a production switch for the held `nirs4all` and `nirs4all-studio` releases.
- Studio RC installers now build from current `main` in GitHub Actions, including
  Windows x64, but the Windows installer still needs manual smoke validation on
  a native Windows machine before any production Studio switch.
