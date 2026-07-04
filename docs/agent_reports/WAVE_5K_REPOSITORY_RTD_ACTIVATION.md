# Wave 5K - Repository Read the Docs activation

Date: 2026-07-04

## Scope

- Activate the public Read the Docs project for `GBeurier/nirs4all-repository`.
- Resolve the cockpit manual action and keep the release/distribution matrix honest.
- Keep PyPI Trusted Publisher blockers explicit; no production-sensitive release was changed.

## Changes Integrated

- `GBeurier/nirs4all-cockpit`:
  - commit `c5ec1fb` removes the completed `rtd-activate-repository` manual action;
  - updates the `nirs4all-repository` Read the Docs target reason to "active and builds from .readthedocs.yaml";
  - updates `tests/test_targets_topology.py` so the guard now asserts that RTD is tracked without a pending activation action;
  - collect commit `cf1dfad` refreshes `data/current.json` after the target/action cleanup.

## External Activation

- Read the Docs API authenticated with the local `rtd_token` file; token value was not printed.
- Project created: `nirs4all-repository`.
- Versions synchronized; `latest` is active.
- Build `33438943` for version `latest` finished successfully at commit `560ad83aa0aab0d6e6cf0d0f7711603927703747`.
- Public docs verified: `https://nirs4all-repository.readthedocs.io/en/latest/` returned HTTP 200.

## Verified Checks

- `nirs4all-cockpit`:
  - `. .venv/bin/activate && pytest -q tests/test_targets_topology.py tests/test_admin_workflows.py` -> `13 passed`;
  - `. .venv/bin/activate && ruff check .` -> pass;
  - `. .venv/bin/activate && pytest -q` -> `99 passed`;
  - `version-guard` on `c5ec1fb` -> success;
  - `collect` on `c5ec1fb` -> success, producing `cf1dfad`;
  - `pages` on `cf1dfad` -> success;
  - live `https://cockpit.nirs4all.org/data/current.json?cachebust=cf1dfad` reports `readthedocs:nirs4all-repository status=green`.

## Current Cockpit State

- Live summary after `cf1dfad`:
  - `green: 79`;
  - `stale: 3`;
  - `pending: 5`;
  - `missing: 12`;
  - `broken: 0`;
  - `unknown: 0`;
  - `excluded: 0`.
- `nirs4all-repository` targets:
  - GitHub Release: green;
  - Pages: green;
  - Read the Docs: green;
  - PyPI: missing because Trusted Publisher remains absent for the existing `v0.1.3` release.

## Remaining Blockers

- PyPI Trusted Publisher still needs external configuration for:
  - `nirs4all-core`;
  - `nirs4all-providers`;
  - `nirs4all-tools`;
  - `nirs4all-benchmarks`;
  - `nirs4all-repository`.
- No `pypi_token` is available in the workspace, so these cannot be completed through the current local token set.
- CRAN/manual distribution gaps remain outside this RTD-focused wave.

## Decisions

- Do not mark missing PyPI publications as planned or green.
- Keep `nirs4all` Python and `nirs4all-studio` outside release publication until the dedicated parity/manual validation gates are complete.
- No full parity run was launched in this wave; this was a distribution/cockpit correction, and parity-heavy runs remain reserved for larger integration batches.
