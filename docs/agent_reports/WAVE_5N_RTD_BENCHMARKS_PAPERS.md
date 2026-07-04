# Wave 5N - Benchmarks and papers RTD activation

Date: 2026-07-04

## Scope

- Activate Read the Docs for `nirs4all-benchmarks` and `nirs4all-papers`.
- Keep Python `nirs4all` and `nirs4all-studio` out of production release changes.
- Refresh `nirs4all-cockpit` so the public status reflects the new documentation targets.
- Carry forward the expanded goal: add about 10 complex cross-language E2E scenarios in `nirs4all-ecosystem` covering R/Python/WASM/Web, datasets/io, pipelines, repository, papers, saves, predictions, and multimodal workflows.

## Changes Integrated

- `GBeurier/nirs4all-benchmarks`:
  - commit `27b3abd` adds `.readthedocs.yaml`, Sphinx configuration, docs requirements, and an RTD index over the existing architecture/contract/API/CLI/deployment docs;
  - Read the Docs project `nirs4all-benchmarks` was created and built successfully.
- `GBeurier/nirs4all-papers`:
  - commit `878e597` adds `.readthedocs.yaml`, Sphinx configuration, docs requirements, and an RTD index over the reproducible publishing docs;
  - Read the Docs project `nirs4all-papers` was created and built successfully.
- `GBeurier/nirs4all-cockpit`:
  - commit `c1bcb16` marks the two RTD targets as active/tracked and strengthens the topology test for active RTD targets;
  - commit `89b1e87` refreshes `data/current.json` after collection.

## Verified Checks

- `nirs4all-benchmarks`:
  - `sphinx-build -W -b html docs docs/_build/html` -> pass;
  - `ruff check . && pytest -q` -> `88 passed`;
  - GitHub `CI`, `version-guard`, and `pages` on `27b3abd` -> success;
  - RTD build `33439217` on `27b3abd` -> success;
  - `https://nirs4all-benchmarks.readthedocs.io/en/latest/` -> HTTP 200.
- `nirs4all-papers`:
  - `sphinx-build -W -b html docs docs/_build/html` -> pass;
  - `ruff check . && pytest -q` -> `44 passed`, `2 skipped`;
  - GitHub `CI`, `version-guard`, `Site (GitHub Pages)`, and `Content Check` on `878e597` -> success;
  - RTD build `33439220` on `878e597` -> success;
  - `https://nirs4all-papers.readthedocs.io/en/latest/` -> HTTP 200.
- `nirs4all-cockpit`:
  - `pytest -q tests/test_targets_topology.py tests/test_admin_workflows.py` -> `13 passed`;
  - `ruff check .` -> pass;
  - `pytest -q` -> `99 passed`;
  - GitHub `version-guard` and `collect` -> success;
  - GitHub `pages` deployment for `89b1e87` -> success after rerun;
  - live cockpit summary -> `81 green`, `3 stale`, `5 pending`, `10 missing`, `0 broken`.

## Decisions

- The two new RTD projects are treated as active service targets, not planned/manual activation items.
- No full parity run was launched in this wave; that remains reserved for large integration batches.
- The new cross-language E2E requirement is now part of the active goal and must be implemented as ecosystem-level orchestration, not as isolated smoke tests.

## Risk Notes

- Remaining missing targets are mostly publication/account-level gates, especially PyPI Trusted Publisher setup for some repos.
- `nirs4all-papers` currently keeps `2 skipped` tests; they were not introduced by this wave and still need review in the wider no-skip parity cleanup.
- The upcoming E2E scenarios need carefully staged fixtures and should not depend on private `nirs4all-drafts` or `nirs4all-lab` data.
