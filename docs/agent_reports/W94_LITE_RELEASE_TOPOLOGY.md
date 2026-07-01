# W94 Lite Release Topology

## Status

Completed the `nirs4all-lite` release topology consumer-readiness slice.

## Scope

- Worktree: `/home/delete/nirs4all/_worktrees/W94-lite-release-topology`
- Branch: `refactor/W94-release-topology-consumer`
- Commit: `d9d92d7` (`feat(release): harden lite topology manifest`)
- Ecosystem central release docs were not edited.

## Change

- Hardened `nirs4all_lite.release_topology_manifest()` with additive,
  machine-readable consumer fields:
  - `aggregate` identity for current `nirs4all-lite` and release-gated
    `nirs4all-core`.
  - `namespace_facades` for Python canonical/additive facades and non-Python
    aggregate namespaces.
  - Per-registry `install_distributions` rows for Python, Rust, npm, R,
    MATLAB/Octave, source/SBOM release artifacts, and explicit upstream Python
    distributions.
  - `upstream_components` with owner boundaries, default inclusion,
    optional/private flags, Python extras, and host package names.
  - `release_pointers` for the license expression/files, source/SBOM
    provenance workflow, and the upstream-owned `nirs4all-methods` C ABI
    pointer.
- Expanded Python binding tests around the release topology manifest:
  install distributions, namespace/facade names, optional upstream policy,
  license/provenance pointers, C ABI pointers, and deepcopy stability.
- Added a short lite-side `docs/RELEASE.md` note that central release tooling
  should consume the topology manifest instead of re-deriving it from prose.

## Verification

- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py -v`
  - Passed: 8 tests.
- `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests`
  - Passed: 34 tests, 1 skipped.
- `python3 -m ruff check bindings/python/src/nirs4all_lite/_topology.py bindings/python/tests/test_release_topology.py`
  - Passed.
- `python3 -m py_compile bindings/python/src/nirs4all_lite/_topology.py bindings/python/tests/test_release_topology.py`
  - Passed.
- `scripts/bump_version.sh --check`
  - Passed: all manifests in sync with Rust crate version `0.2.0`.
- `git diff --check`
  - Passed before commit.

## Notes

- The public Python distribution remains `nirs4all-lite`; no premature
  `nirs4all-core` rename was performed.
- No Rust, npm, R, or MATLAB package manifests were edited, so no additional
  non-Python package tests were required for this slice.
