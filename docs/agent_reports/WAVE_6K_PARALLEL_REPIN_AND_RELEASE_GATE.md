# Wave 6K - parallel repin and release gate

Date: 2026-07-06

## Scope

- Increase parallel Codex/Claude review capacity for the V1 refactor release gate.
- Integrate only reviewed ecosystem repins and targeted E2E/submodule guards.
- Keep `nirs4all` Python production and `nirs4all-studio` production releases out of scope.
- Do not touch `nirs4all-drafts`, `nirs4all-lab`, root token files, or the historical aggregation lock.

## Parallel agents

Codex agents launched in this wave:

- `019f3718-8cd7-7af2-af10-a655474eb840` - `nirs4all-methods` release watcher.
- `019f3718-8eaa-7200-a10a-8e78dd1c8123` - `nirs4all-cockpit` / `nirs4all-org` readiness.
- `019f3718-90fc-7662-8a22-0313b03fa720` - `nirs4all-ecosystem` E2E and submodule repins.
- `019f3718-939c-7df1-8411-33af3d16e159` - read-only UI/Web/Studio shared-component audit.
- `019f3718-95f2-7bb1-85a4-5d528cd2b50c` - read-only release blocker matrix.
- `019f3718-9830-7011-8cdc-8ab0bb0122f3` - read-only cluster secret alert audit.
- `019f371b-db94-7253-be02-12524733b8f5` - read-only core naming/package audit.
- `019f371b-dd40-7662-b62d-afc97308211d` - read-only bindings/language audit.

Claude Code sessions launched read-only with explicit allowed tools:

- `c77c3c5b-69d5-4904-bb6a-17dcb03a847f` - fable requested, provider fell back to Opus; global V1 reviewer.
- `0446bff5-c041-4007-926c-582046f75916` - Opus/max release and cockpit audit.

## Integrated ecosystem changes

- Added a cross-language E2E guard ensuring every step runs in a declared scenario repo and every required path stays on a declared public surface unless it is an allowed public data blocker.
- Added `scripts/n4a_submodule_repin.py` to plan/apply fast-forward submodule repins without regenerating `aggregation-lock.n4a.lock.json`.
- Added tests for repin planning, lock protection, JSON output, and gitlink-only apply behavior.
- Repinned reviewed fast-forward gitlinks to the currently published/reviewed heads:
  `nirs4all-benchmarks`, `nirs4all-cockpit`, `nirs4all-core`, `nirs4all-methods`, `nirs4all-org`, `nirs4all-providers`, `nirs4all-repository`, `nirs4all-studio`, `nirs4all-ui`, and `nirs4all-web`.

## Manual-review pins

The repin plan intentionally leaves these unchanged:

- `dag-ml` - diverged from `origin/main`.
- `dag-ml-data` - current gitlink is ahead of `origin/main`.
- `nirs4all` - current gitlink is ahead of `origin/main`; production Python remains outside this release batch.

## Release gate status

- `nirs4all-methods v1.0.5` is green for GitHub release, npm `@nirs4all/methods-wasm`, `pls4all` PyPI, R workflow, MATLAB workflow, and source workflow.
- PyPI `nirs4all-methods` still reports `1.0.3`; the full wheel workflow is therefore not yet a completed publication gate.
- `nirs4all-core`, `nirs4all-providers`, `nirs4all-repository`, and `nirs4all-benchmarks` PyPI publication remain blocked by Trusted Publisher configuration, not by local code.
- `nirs4all-web` is confirmed client-side-only and consumes the shared `nirs4all-ui` package/shim, but it is not yet a full Studio clone.
- The cluster GitGuardian alert is clean in the current tree and guarded by CI/pre-commit; historical secret-shaped examples remain reachable in published history.

## Tests run

- `python3 -m pytest tests/test_e2e_scenarios.py tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py tests/test_release_lock.py -q` -> `90 passed`.
- `python3 scripts/n4a_submodule_repin.py plan --json` -> protected lock `clean`, `17` up to date, `3` manual review, `0` dirty.

## Decisions and risks

- Do not regenerate `docs/contracts/release/aggregation-lock.n4a.lock.json` in this wave.
- Do not update `nirs4all-org` or `nirs4all-cockpit` to claim PyPI `nirs4all-methods 1.0.5` until PyPI confirms that package.
- Keep full parity deferred until this release/repin batch is stable.
- If the historical cluster values were ever real credentials, token rotation and GitGuardian resolution are owner actions.
