# Wave 5C - Publication and E2E follow-up

Date: 2026-07-04
Coordinator: Codex

## Scope

Follow-up after the Wave 5A/5B publication batch. This wave fixes the
cross-language E2E CI topology, attaches fallback GitHub Release artifacts for
Python packages whose PyPI Trusted Publisher is missing, and repairs the
`nirs4all-repository` Pages artifact.

`nirs4all` Python and `nirs4all-studio` production release remain out of scope.
`nirs4all-drafts`, `nirs4all-lab`, and token files were not touched.

## Parallel reviews

- Claude publication/Pages reviewer: diagnosed `tools`, `repository`,
  `benchmarks`, `providers`, and `core` PyPI failures as missing external PyPI
  Trusted Publisher configuration (`invalid-publisher` with `environment=pypi`);
  diagnosed Pages failures as deploy-time/backend failures after successful
  artifact upload.
- Claude E2E reviewer: confirmed the 10-scenario harness is honest about
  strict/contract/gap evidence, and identified that the CI workflow was using
  unpinned default branch checkouts instead of the ecosystem submodule lock.
- Claude core/ui/providers reviewer: confirmed `nirs4all-core` is the active
  canonical aggregate and `nirs4all-lite` is a legacy blocked publishing line;
  follow-up org/cockpit review remains needed.

## Changes integrated

- `nirs4all-ecosystem`
  - `tests/test_e2e_scenarios.py`: the workspace readiness assertion now accepts
    only explicitly declared public-checkout data blockers (`nirs4all-data` and
    the missing heavy catalog dataset), while still rejecting missing tools,
    env vars, or undeclared paths.
  - `.github/workflows/cross-language-e2e.yml`: switched from unpinned per-repo
    checkouts to a single `nirs4all-ecosystem` checkout with
    `submodules: recursive`; `N4A_WORKSPACE_ROOT` now points to the checked-out
    submodule workspace.
  - `nirs4all-repository` submodule updated to `de2f8a5e7bdef1972373ebb89e205e646e4830f0`
    for the Pages workflow fix.
- `nirs4all-repository`
  - `.github/workflows/deploy-pages.yml`: added `site/CNAME` and `.nojekyll`
    before uploading the Pages artifact, matching the working `papers` pattern.
  - Commit: `de2f8a5e7bdef1972373ebb89e205e646e4830f0`
    (`ci(pages): preserve repository custom domain`).

## GitHub Release artifact fallback

The following non-prod Python releases now have verified wheel + sdist assets
attached to GitHub Releases, regardless of PyPI status:

- `nirs4all-aom v0.10.3`
- `nirs4all-benchmarks v0.1.3`
- `nirs4all-cluster v0.1.2`
- `nirs4all-papers v0.2.2`
- `nirs4all-providers v0.2.3`
- `nirs4all-repository v0.1.3`
- `nirs4all-tools v0.0.2`

All attached artifacts were locally built and passed `twine check` before
upload.

## Checks run

- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 10 scenarios.
  - `N4A_WORKSPACE_ROOT=/home/delete/nirs4all/nirs4all-ecosystem python3 -m pytest -q tests/test_e2e_scenarios.py` -> `34 passed`.
  - `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py` -> `24 passed`.
  - `git diff --check` -> clean.
- `nirs4all-repository`
  - `python3.11 -m build`
  - `python3.11 -m twine check dist/nirs4all_repository-0.1.3*`
  - `python3.11 -m pip install -e .`
  - `n4a-repository site --out /tmp/n4a-repository-site`
  - verified generated `index.html`, `CNAME`, and `.nojekyll`.

## Remote status snapshot

Green after polling:

- `nirs4all-papers v0.2.2`: CI, Content Check, PyPI publish, Pages, and
  version guard are green after rerun.
- `nirs4all-aom v0.10.3`: PyPI publish and version guard green.
- `nirs4all-cluster v0.1.2`: CI, Release, version guard green.
- `nirs4all-datasets v0.3.3`: Python/npm/crates/R/MATLAB/source release jobs
  and core checks green.
- `nirs4all-methods v1.0.2`: docs, parity, coverage, ABI, sanitizers, and
  cross-binding parity green.
- `nirs4all-ui v0.1.2` and `nirs4all-web v0.1.2`: CI/Pages/package checks
  green.

Still external-blocked at this snapshot:

- `nirs4all-core release-python v0.2.4`: PyPI Trusted Publisher
  `invalid-publisher` for repo `GBeurier/nirs4all-core`, workflow
  `release-python.yml`, environment `pypi`.
- `nirs4all-benchmarks v0.1.3`: PyPI Trusted Publisher `invalid-publisher`.
- `nirs4all-providers v0.2.3`: PyPI Trusted Publisher `invalid-publisher`.
- `nirs4all-repository v0.1.3`: PyPI Trusted Publisher `invalid-publisher`.
- `nirs4all-tools v0.0.2`: PyPI Trusted Publisher `invalid-publisher`.

Still running/needs polling:

- `nirs4all-ecosystem@6d651f0`: cross-language E2E CI rerun after workflow
  correction.
- `nirs4all-repository@de2f8a5e`: Pages/CI/docs/CodeQL rerun after artifact
  chrome fix.

## Decisions

- Do not create new package tags for workflow-only Pages fixes.
- Keep the old `nirs4all-lite` repo as a legacy blocked publishing line; do not
  merge old lite worktrees/branches into `nirs4all-core`.
- Treat GitHub Release assets as public fallback distribution for PyPI-blocked
  packages, but do not claim PyPI completion until the external Trusted
  Publisher entries are created and failed publish jobs rerun successfully.
