# Wave 9ZM - Web app path rename and E2E sync

## Scope

Retire the visible `studio-lite/` app path in `nirs4all-web` and make the
ecosystem contracts use the canonical `web-app/` browser/WASM source tree.

## Files changed

- `nirs4all-web`
  - renamed tracked app source from `studio-lite/` to `web-app/`;
  - updated Web CI, Pages, version guard, docs, smoke helpers, and custom-host
    aliases to the new path;
  - bumped `nirs4all-web` to `0.1.7`;
  - published Git tag and GitHub Release `v0.1.7`.
- `nirs4all-cockpit`
  - changed the `nirs4all-web` source-of-truth path to
    `web-app/package.json`;
  - committed as `309b0fb`.
- `nirs4all-ecosystem`
  - repointed `nirs4all-web` submodule to `7eb1bb6`;
  - repointed `nirs4all-cockpit` submodule to `309b0fb`;
  - updated cross-language E2E scenario commands and references from
    `nirs4all-web/studio-lite` to `nirs4all-web/web-app`;
  - updated the committed runtime evidence ledger hash after the scenario
    manifest path-only change.

## Tests and checks

- `nirs4all-web/web-app`
  - `npm run test:client-only`
  - `npm run typecheck`
  - `npm run test` -> `24 passed`, `149 tests`
  - `NIRS4ALL_METHODS_ABI_REQUIRED=1 NIRS4ALL_STUDIO_REGISTRY_REQUIRED=1 npm run validate:catalog`
  - `npm run build:single`
  - `npm run build`
  - `npm run smoke -- rt-fallback`
- GitHub `nirs4all-web@7eb1bb6`
  - `version-guard`: success
  - `web-ci`: success
  - `Deploy nirs4all-web to GitHub Pages`: success
  - release `v0.1.7`: published, non-draft, non-prerelease
- `nirs4all-cockpit`
  - `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_targets_topology.py tests/test_reconcile.py`
    -> `51 passed`
  - `.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`
    -> `23 packages, 103 targets`
- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py validate`
    -> `OK: 11 cross-language E2E scenarios`
  - `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --max-age-seconds 14400`
    -> `11/11 scenarios verified; artifacts=71 failures=0`
  - `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
    -> `11/11 scenarios verified; artifacts=71 failures=0`
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_gitmodules_topology.py tests/test_release_surface_matrix.py tests/test_release_lock.py`
    -> `160 passed`
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_cutover_state_gate.py`
    -> `5 passed`
  - selected-member release lock validation via
    `/tmp/n4a-lock-selected-webapp.LCBKwn`
    -> `validated docs/contracts/release/aggregation-lock.n4a.lock.json`

## Decisions

- Kept negative tests that reject the retired `nirs4all-lite` session/model
  formats; those do not preserve an alias, they prove the old format is refused.
- Did not relaunch full parity; this was a path-only Web app rename and the
  web CI/Pages gate plus E2E ledger validation covered the affected surface.

## Risks

- Direct release-lock validation against `/home/delete/nirs4all` still reports
  the live workspace as inconsistent with the pinned selected-member lock, which
  is expected while several sibling worktrees are ahead of the lock. The
  selected-member validation remains the authoritative lock gate.
