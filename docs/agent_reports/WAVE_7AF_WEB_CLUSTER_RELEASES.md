# WAVE 7AF - Web and cluster releases

Date: 2026-07-07

## Scope

- Repositories: `nirs4all-web`, `nirs4all-cluster`, `nirs4all-org`,
  `nirs4all-cockpit`, `nirs4all-ecosystem`
- Lane: public release/status surfaces outside the core aggregation lock
- Constraint: no changes to `nirs4all-ui`, `nirs4all-quality`, `nirs4all`
  Python production, or `nirs4all-studio`

## Released heads

- `nirs4all-web` `v0.1.4`: `14f3d769f5d56e88cc76d64a4a5c38541fb1d448`
- `nirs4all-cluster` `v0.1.4`: `25529480a26b0e1a21be2d05aa2639acb9f6651e`
- `nirs4all-org` public site refresh:
  `af6a7953bd44e31e6595aa5d21ffa575a687f71c`
- `nirs4all-cockpit` post-release collect snapshot:
  `8329cb8fb87ff340f471529e17be10d47af40b58`

## Files modified

- `nirs4all-web` submodule pointer
- `nirs4all-cluster` submodule pointer
- `nirs4all-org` submodule pointer
- `nirs4all-cockpit` submodule pointer
- `docs/agent_reports/WAVE_7AF_WEB_CLUSTER_RELEASES.md`

## Publication status

- `nirs4all-web` GitHub Release `v0.1.4` published.
- `nirs4all-web` `web-ci`, `version-guard`, and Pages deployment passed.
- `nirs4all-cluster` GitHub Release `v0.1.4` published.
- `nirs4all-cluster` CI, `version-guard`, and PyPI Trusted Publishing passed.
- PyPI confirms `nirs4all-cluster` `0.1.4` with two distribution files.
- `nirs4all-org` version guard and Pages deployment passed.
- `nirs4all-cockpit` collect and Pages deployment passed; snapshot reports:
  - `nirs4all-cluster`: source `0.1.4`, PyPI `green 0.1.4`, RTD `green latest`
  - `nirs4all-web`: source `0.1.4`, Pages `green`

## Tests run

In `nirs4all-web/studio-lite`:

- `npm run typecheck`
- `npm run test -- --run src/app/client-side-only.test.ts src/engine/nirs4all-core.test.ts src/app/custom-app-host.contract.test.ts`
- `npm run check:core-shim`
- `npm run build:single`
- `npm run build`

In `nirs4all-cluster`:

- `uv run ruff check .`
- `uv run mypy nirs4all_cluster`
- `uv run pytest -q`
- `git ls-files -z | xargs -0 uvx --from detect-secrets detect-secrets-hook --baseline .secrets.baseline`
- `python3 scripts/secret_shape_guard.py`
- `uv build`
- `uvx twine check --strict dist/*`

In `nirs4all-cockpit`:

- `.venv/bin/python -m pytest -q`
- `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml`
- `.venv/bin/ruff check .`

## Decisions

- `nirs4all-web` remains client-side-only; the release is a Pages/GitHub release
  surface, not a server/backend package.
- `nirs4all-cluster` stays scoped as trusted-LAN beta, not public multi-tenant
  production infrastructure.
- These repositories are not members of the core aggregation lock, so the lock
  was not regenerated for this wave.

## Risks

- GitGuardian may still show historical alerts for old token-shaped examples in
  `nirs4all-cluster` history, but the current tree passes both detect-secrets and
  the custom secret-shape guard.
- The broader full-parity debt remains tracked in the ecosystem E2E coverage
  board; no full parity run was launched in this wave.
