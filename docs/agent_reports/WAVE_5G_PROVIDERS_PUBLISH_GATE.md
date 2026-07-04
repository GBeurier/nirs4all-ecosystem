# Wave 5G - nirs4all-providers publish gate repair

Date: 2026-07-04

## Scope

- Lane E / provider package publication readiness.
- Keep the PyPI publication gate honest: fix real CI failures before treating PyPI as the only blocker.

## Changes Integrated

- `GBeurier/nirs4all-providers`:
  - `e3dd19c` added the missing `nirs4all-formats` checkout to `.github/workflows/publish.yml`;
  - `f560073` added the missing `nirs4all-io` checkout to the same workflow;
  - `d3fb294` set `N4A_WORKSPACE_ROOT=${{ github.workspace }}` for `scripts/ci_gate.py`, so e2e provider tests resolve the sibling checkouts actually created by Actions.

## Root Cause

- The publish workflow installed `nirs4all-datasets` from a local checkout.
- Its Rust/Python build needs local path dependencies at `../nirs4all-formats` and `../nirs4all-io`; those siblings were absent in the workflow.
- After those were added, the e2e test still saw an empty dataset catalogue because the test defaulted to the parent of the provider checkout while Actions places sibling checkouts under `$GITHUB_WORKSPACE`.

## Tests and Checks

- Local reproduction:
  - Python 3.11 temp venv;
  - `pip install -e ".[dev]"`;
  - `pip install -e ../nirs4all-datasets -e ../nirs4all-repository -e ../nirs4all-benchmarks -e ../nirs4all-papers "nirs4all-io>=0.1.5"`;
  - `DatasetProvider(root=/home/delete/nirs4all/nirs4all-datasets).list_datasets()` returned 164 rows.
- GitHub Actions:
  - `Providers CI` on `d3fb294`: success.
  - `Publish to PyPI` dry-run on `d3fb294`: success, including build + artifact.
  - `Publish to PyPI` real run on `d3fb294`: build success, artifact created, publish failed only at PyPI OIDC.

## Remaining Blocker

- PyPI refuses `nirs4all-providers` with `invalid-publisher`.
- Current OIDC claims from the real publish run:
  - `sub`: `repo:GBeurier/nirs4all-providers:environment:pypi`;
  - `repository`: `GBeurier/nirs4all-providers`;
  - `workflow_ref`: `GBeurier/nirs4all-providers/.github/workflows/publish.yml@refs/heads/main`;
  - `environment`: `pypi`.
- The cockpit manual action `pypi-publisher-providers` remains valid: create/fix the PyPI Trusted Publisher, then rerun `publish.yml` with `dry_run=false`.

## Decisions

- No xfail, skip, or relaxed assertion was added.
- The failing provider e2e stayed active; the workflow environment was corrected instead.
