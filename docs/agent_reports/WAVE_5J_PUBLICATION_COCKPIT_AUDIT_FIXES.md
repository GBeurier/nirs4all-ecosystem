# Wave 5J - Publication cockpit audit fixes

Date: 2026-07-04

## Scope

- Read-only publication/cockpit audit from a Codex sidecar agent.
- Actionable fixes for the public cockpit and org/UI surfaces.

## Agent Report

- Agent: Fermat the 4th (`019f2d0e-2aeb-7b93-a6e2-af42a967f65c`).
- Mode: read-only.
- Main finding: the remaining cockpit blockers are external PyPI Trusted Publisher setup, Read the Docs activation for `nirs4all-repository`, and a UI canonical URL mismatch.

## Fixes Integrated

- `GBeurier/nirs4all-org`:
  - commit `30c3848` changes the two visible `nirs4all-ui` component/showcase links from `https://ui.nirs4all.org/` to the current GitHub Pages URL `https://gbeurier.github.io/nirs4all-ui/`;
  - live `https://nirs4all.org/?cachebust=30c3848` was verified to contain the GitHub Pages links.
- `GBeurier/nirs4all-ui`:
  - commit `3cb48dd` adds `"homepage": "https://gbeurier.github.io/nirs4all-ui/"` to package metadata;
  - CI and GitHub Pages were rerun and passed after a transient Pages deploy failure.
- `GBeurier/nirs4all-cockpit`:
  - commit `73f4af5` promotes `nirs4all-repository` Read the Docs from `planned` to `tracked`;
  - adds manual action `rtd-activate-repository`;
  - keeps PyPI Trusted Publisher blockers explicit and does not mark missing docs as green/planned.

## Verified Checks

- `nirs4all-org`:
  - `version-guard` on `30c3848` -> success;
  - `pages build and deployment` initially failed with GitHub Pages `Deployment failed, try again later`, then rerun -> success.
- `nirs4all-ui`:
  - local `PATH=$HOME/.nvm/versions/node/v24.16.0/bin:$PATH npm run ci` -> `59 passed` plus build/pack smoke;
  - local `PATH=$HOME/.nvm/versions/node/v24.16.0/bin:$PATH npm run site:build` -> success;
  - GitHub `CI` on `3cb48dd` -> success;
  - GitHub `Pages` initially failed with GitHub Pages `Deployment failed, try again later`, then rerun -> success;
  - live `https://gbeurier.github.io/nirs4all-ui/` returned HTTP 200 with `last-modified: Sat, 04 Jul 2026 12:26:35 GMT`.
- `nirs4all-cockpit`:
  - `. .venv/bin/activate && pytest -q tests/test_targets_topology.py tests/test_admin_workflows.py` -> `13 passed`;
  - `. .venv/bin/activate && pytest -q` -> `99 passed`;
  - `. .venv/bin/activate && ruff check .` -> pass;
  - `n4a-cockpit admin actions --md` shows `rtd-activate-repository` pending with `readthedocs:nirs4all-repository status=missing version=—`.

## Remaining Blockers

- PyPI Trusted Publisher must still be configured externally for:
  - `nirs4all-core`;
  - `nirs4all-providers`;
  - `nirs4all-tools`;
  - `nirs4all-benchmarks`;
  - `nirs4all-repository`.
- Read the Docs must be activated externally for `nirs4all-repository`.
- `nirs4all-core` remains stale in cockpit because the legacy `nirs4all-lite` PyPI alias is stale and `nirs4all-core` PyPI is missing; this is expected until the PyPI Trusted Publisher is configured.

## Decisions

- Keep `ui.nirs4all.org` unclaimed/unpublished for now, per user instruction.
- Use `https://gbeurier.github.io/nirs4all-ui/` as the current canonical component showcase.
- Do not downgrade missing docs/publications to planned when the repo-side publication config is already present.
