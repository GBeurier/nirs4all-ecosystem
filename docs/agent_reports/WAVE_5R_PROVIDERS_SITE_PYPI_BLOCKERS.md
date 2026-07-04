# Wave 5R - Providers site and PyPI blocker audit

Date: 2026-07-04

## Scope

- Add the missing public site surface for `nirs4all-providers`.
- Track that site in the cockpit.
- Re-audit the PyPI publication blockers for `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-benchmarks`, and `nirs4all-repository`.

## Changes Integrated

- `GBeurier/nirs4all-providers`
  - `f7f667f` adds a static GitHub Pages site, `robots.txt`, `sitemap.xml`, web manifest, `.nojekyll`, and a Pages workflow.
  - `487e201` updates the Pages workflow to request Pages enablement.
  - Repository Pages was enabled through the GitHub API with `build_type=workflow` because the workflow `GITHUB_TOKEN` could not create the Pages site.
- `GBeurier/nirs4all-cockpit`
  - `df36033` adds `nirs4all-providers` as a tracked `pages` target and updates the topology test expectation.

## Verified Checks

- `nirs4all-providers`
  - static checks: HTML parse, JSON manifest parse, XML sitemap parse, and required brand assets present -> pass;
  - `git diff --check` -> pass;
  - `ruff check .` -> pass;
  - `python3.11 -m pytest -q` -> pass (`1 skipped`, dependency warning only);
  - GitHub `Providers CI` on `487e201` -> success;
  - GitHub `Pages` on `487e201` -> success after repository Pages enablement;
  - live page `https://gbeurier.github.io/nirs4all-providers/` -> HTTP 200;
  - live `robots.txt` and `sitemap.xml` -> HTTP 200.
- `nirs4all-cockpit`
  - `PYTHONDONTWRITEBYTECODE=1 .venv/bin/n4a-cockpit validate-targets ops/targets.yaml` -> pass (`21 packages`, `100 targets`);
  - `.venv/bin/pytest -q tests/test_targets_topology.py tests/test_stats.py` -> `23 passed`;
  - `.venv/bin/ruff check .` -> pass;
  - `git diff --check` -> pass.

## PyPI Publication Status

The following latest publish attempts all built artifacts successfully but failed in the publish job with `invalid-publisher`:

- `nirs4all-core`: `repo:GBeurier/nirs4all-core:environment:pypi`, workflow `release-python.yml`, ref `refs/tags/v0.2.4`;
- `nirs4all-providers`: `repo:GBeurier/nirs4all-providers:environment:pypi`, workflow `publish.yml`, ref `refs/heads/main`;
- `nirs4all-tools`: `repo:GBeurier/nirs4all-tools:environment:pypi`, workflow `publish.yml`, ref `refs/heads/main`;
- `nirs4all-benchmarks`: `repo:GBeurier/nirs4all-benchmarks:environment:pypi`, workflow `publish.yml`, ref `refs/heads/main`;
- `nirs4all-repository`: `repo:GBeurier/nirs4all-repository:environment:pypi`, workflow `publish.yml`, ref `refs/heads/main`.

This is not a code/build failure. PyPI refused the GitHub OIDC exchange because no matching Trusted Publisher exists for those claims.

## Decisions

- Do not publish from local API tokens as a workaround. These projects are configured for OIDC Trusted Publishing and should stay tokenless.
- Treat the five PyPI packages as externally blocked until the Trusted Publishers are created on PyPI.
- Treat `nirs4all-lite` as legacy/superseded. Its `main` explicitly blocks legacy publishing; the final alias release remains Phase R2 after `nirs4all-core` exists on PyPI.

## Remaining Actions

- Create PyPI Trusted Publishers for the five package/repo/workflow/environment tuples listed above, then rerun the existing publish workflows.
- Refresh cockpit after the providers Pages target is collected.
- Decide whether `nirs4all-lite` should remain tracked as stale until the alias release or be represented as a legacy target in cockpit.
