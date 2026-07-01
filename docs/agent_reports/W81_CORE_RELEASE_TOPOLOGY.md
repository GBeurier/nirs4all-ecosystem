# W81 Core Release Topology

## Status

Implemented and committed a bounded `nirs4all-lite` package/facade/release
topology improvement.

## Scope

Worktree: `/home/delete/nirs4all/_worktrees/W81-core-release-topology`

Only the `nirs4all-lite` worktree was edited and committed. This report is
written in `nirs4all-ecosystem` as required and must remain uncommitted there.

## Change

- Added `nirs4all_lite._topology` with a JSON-serializable
  `release_topology_manifest()`.
- The manifest records that the current Python distribution remains
  `nirs4all-lite`, the future `nirs4all-core` distribution name is
  release-gated, and upstream install distributions remain explicit
  (`nirs4all-methods`, `nirs4all-formats`, `nirs4all-io`,
  `nirs4all-datasets`, `dag-ml`, `dag-ml-data`, and non-Python `nirs4all`).
- Added machine-checkable core facade constants:
  `CORE_FACADE_EXPORTS`, `EXECUTION_ENGINE_EXPORTS`, `TOPOLOGY_EXPORTS`,
  `core_facade_exports()`, `execution_engine_exports()`, and
  `validate_core_facade()`.
- Kept `n4a` as the full additive aggregate facade, now dynamically mirroring
  `nirs4all_lite.__all__` to avoid drift.
- Narrowed `nirs4all_core.__all__` to the no-engine core contract
  (inspect/validate/capability/release-topology/facade). Legacy execution
  helpers such as `run_portable_pipeline` remain reachable through passthrough,
  so existing explicit imports are not broken.
- Updated Python facade tests and added release-topology tests that check the
  manifest against `pyproject.toml`, verify no top-level Python `nirs4all`
  package is shipped, and assert that `nirs4all_core` advertises no execution
  exports.
- Updated `docs/NAMING.md`, `docs/BINDINGS.md`, `docs/RELEASE.md`, and the
  Python README to document the split between `n4a` and `nirs4all_core`.

## Design Notes

- No distribution rename was performed.
- No execution engine, parser, numerical method, dataset loader, or DAG
  coordinator was added to lite/core.
- `nirs4all_core` still has compatibility passthrough to the shipped aggregate
  while the rename is release-gated, but execution helpers are excluded from
  its advertised public surface.
- Ecosystem release-manifest/docs follow-up: if a central ecosystem manifest is
  created later, it should consume or mirror the lite
  `release_topology_manifest()` fields rather than re-deriving the Python
  facade boundary.

## Gates

- `git diff --check` -> passed
- `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests` -> passed (`30 tests`, `1 skipped`)
- `python3 -m build bindings/python --outdir dist/python` -> passed

## Commit

`4127f5f2fcd10aabde27846b20ccf4d90a91d696`
(`feat(release): codify core facade topology`)
