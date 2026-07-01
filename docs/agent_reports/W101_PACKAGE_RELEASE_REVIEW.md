# W101 Package And Release Integration Review

Date: 2026-07-01

Scope: read-only review of Wave 2K non-UI package/release work. I read the root
`AGENTS.md` plus W90, W91, W92, W93, W94, and W97 reports, then fact-checked the
named worktrees/branches directly.

## Direct Worktree State

Clean Wave worktrees:

- W92 methods: `_worktrees/W92-methods-release-surface`,
  `refactor/W92-methods-release-surface`, `d077ea5f`.
- W93 IO: `_worktrees/W93-io-datasets-bridge`,
  `refactor/W93-datasets-bridge`, `ac7809d`.
- W93 datasets: `_worktrees/W93-datasets-reference-bridge`,
  `refactor/W93-reference-bridge`, `20b41824`.
- W93 formats: `_worktrees/W93-formats-io-contract`,
  `refactor/W93-io-contract`, `89231b2`; no W93-specific code delta.
- W94 lite: `_worktrees/W94-lite-release-topology`,
  `refactor/W94-release-topology-consumer`, `d9d92d7`.
- W97 tools: `_worktrees/W97-tools-real-goldens`,
  `refactor/W97-real-goldens`, `c10934a`.
- W91 dag-ml: `_worktrees/W91-dagml-lockstep`,
  `refactor/W91-lockstep-freshness`, `618ffb2`.
- W91 dag-ml-data: `_worktrees/W91-dagml-data-lockstep`,
  `refactor/W91-lockstep-freshness`, `818616e`.

Dirty state:

- The main `dag-ml-data` checkout is still dirty at
  `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`, matching W91.
- The W91 dag-ml-data worktree itself is clean.
- The implementation repos touched by W92/W93/W94/W97 were not modified during
  this review.

Integration ancestry:

- W97 is already merged into `nirs4all-tools/main`
  (`0ff31c2 Merge branch 'refactor/W97-real-goldens'`).
- W92 is not in `nirs4all-methods/main`.
- W93 IO is not in `refactor/integration-io`; W93 datasets is not in
  `nirs4all-datasets/main`.
- W94 is not in `refactor/integration-lite`; it builds on the W81 facade work
  already present at `0dad1c6` in `refactor/integration-lite`.

## Findings

### Blocker: Central Release Lock Does Not Validate

`python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all
validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock
docs/contracts/release/aggregation-lock.n4a.lock.json` currently fails with:

`lockfile is stale or inconsistent; regenerate with n4a_release_lock.py generate ...`

This is a required W90 gate (`release_lock_validation`) in
`docs/contracts/cutover/drop-gates.n4a.json`. A temporary regenerated lock showed
the manifest digest is unchanged; the drift is member state:

- `dag_ml`: pinned `main@f58d7bf` -> workspace `refactor/L20-lockstep@4f0a3b5`.
- `dag_ml_data`: pinned `main@347c15f` -> workspace
  `refactor/L20-lockstep@2214f75`, dirty `False -> True`.
- `io`: pinned `main@84ab189` -> workspace
  `refactor/L7-io-dagml-sibling@5651da5`.

Impact: the release topology cannot be claimed green until final member heads are
selected, the dirty dag-ml-data artifact is resolved, and the aggregation lock is
regenerated from those heads.

### Blocker: Methods Release Lock Reads Ignored Generated Package Outputs

The central aggregation manifest version-checks
`bindings/python_nirs4all_methods/pyproject.toml` and
`bindings/python_pls4all/pyproject.toml` for `nirs4all-methods`, but those
directories are ignored by `.gitignore` in `nirs4all-methods`:

- `.gitignore`: `bindings/python_nirs4all_methods/`,
  `bindings/python_pls4all/`.
- Current main working tree has ignored generated files reporting version
  `1.0.0` and old `https://github.com/GBeurier/pls4all` URLs.
- W92 changed the source generator and `bindings/python/pyproject.toml` to
  version `1.0.1` / current `nirs4all-methods` URLs, but the W92 branch does not
  track generated package directories.

Impact: release-lock generation is not reproducible from tracked sources. A
clean checkout without ignored generated dirs can produce different lock content
than this workstation, while a dirty workstation can record stale generated
metadata. The lock should either consume tracked package metadata or generate
these package trees in a controlled temporary directory before reading them.

### Major: W94 Lite Topology Is Not Consumed By Central Release Contracts

W94 added `nirs4all_lite.release_topology_manifest()` with machine-readable
facades (`nirs4all_lite`, `n4a`, `nirs4all_core`), per-registry distribution
rows, upstream component policy, and release pointers. The central ecosystem
aggregation manifest still records the lite component as only:

- Python distribution `nirs4all-lite`.
- Python imports `["nirs4all_lite"]`.
- No contract artifact or generated assertion for `release_topology_manifest()`.

Impact: W94 improves the lite repo locally, but the ecosystem release lock still
does not enforce the new namespace/package clarity, future `nirs4all-core`
target, `n4a` facade, or release-pointer fields. Central tooling must consume the
W94 manifest before it can be release evidence.

### Major: Lite License Metadata Is Inconsistent Across Release Artifacts

W94's topology manifest declares one license expression,
`CeCILL-2.1 OR AGPL-3.0-or-later`, and tests it against the Python pyproject.
However `bindings/r/DESCRIPTION` in the same lite branch still declares
`License: MIT + file LICENSE`, and `bindings/r/LICENSE` is an MIT-style R
license file.

Impact: the W94 release pointer is not a cross-artifact license check. Publishing
Python/npm/R/source artifacts from the same release would present inconsistent
license metadata unless the R package metadata is fixed or explicitly justified.

### Major: W97 "Real Golden" Fixture Coverage Includes Placeholder Files

W97 adds useful end-to-end migration tests, but the mixed workspace fixtures are
not fully real binary fixtures:

- `tests/fixtures/legacy/old_workspace_mixed/store.duckdb` is ASCII text:
  `legacy duckdb workspace placeholder`.
- `tests/fixtures/legacy/old_workspace_mixed/sample.meta.parquet` starts with
  `PAR1` but is not valid Parquet; `pyarrow.parquet.read_table()` raises
  `ArrowInvalid: Parquet magic bytes not found in footer`.

The W97 tests only byte-preserve those files, so the placeholders are sufficient
for opaque preservation behavior, but they should not be described as real
DuckDB/Parquet goldens. The SQLite dump fixture is stronger: it materializes a
real SQLite workspace and tests lowered Parquet sidecars.

Impact: converter golden risk remains for loose legacy Parquet/DuckDB inputs.
Before release, either rename/document the placeholders as opaque sentinel
payloads or add valid reduced binary fixtures when parser/sidecar behavior is
part of the claim.

### Medium: W93 Lacks A True Cross-Repo Adapter Test

The W93 boundary is generally sound:

- IO uses a duck-typed `_adapt_to_io_spec()` and does not import
  `nirs4all-datasets`.
- Datasets imports `nirs4all_io` lazily only inside `to_dataset_package()`.
- Formats remains untouched for this bridge.

The integration test coverage is split, though:

- IO tests `nio.load(obj_with_to_io_spec)` using a local
  `ReferenceDatasetDouble`.
- Datasets tests `NirsDataset.to_dataset_package()`, not
  `nirs4all_io.load(real_NirsDataset, target="dataset_package")`.

Impact: a final package gate should add one combined-environment test that passes
a real `NirsDataset` instance directly to IO. This would lock the exact public
adapter path that W93 documents.

## Package/Namespace Notes

- W92 correctly clarifies the distribution/import split:
  `nirs4all-methods` is the Python distribution and `n4m` is the full import
  package; `pls4all` remains the slim PLS subset. No ABI symbol rename was made.
- W92 intentionally leaves broader generated docs with many old `n4m.sklearn`
  references; this is a docs debt, not an ABI/package blocker by itself.
- W94 correctly keeps `nirs4all-core` release-gated and additive, not a premature
  distribution rename.
- W93 keeps the IO/datasets direction one-way: catalog owns local canonical
  paths and roles; IO owns loading, joins, and package materialization; formats
  stays the parser layer.

## Required Before Release Claim

1. Select final release heads for W92, W93 IO/datasets, and W94, then merge or
   explicitly pin them.
2. Remove or resolve the dirty main `dag-ml-data` ABI artifact before running any
   lock gate.
3. Regenerate and commit the aggregation lock from the final clean workspace.
4. Fix release-lock handling of ignored generated methods package directories.
5. Wire W94's lite topology manifest into the central release contract.
6. Add the missing real `NirsDataset` -> `nirs4all_io.load()` integration test.
7. Document W97 placeholders as opaque sentinels or replace them with valid
   reduced binary fixtures.
