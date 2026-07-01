# W2L Lane G IO/Datasets/Formats

Agent: Codex Lane G formats/io/datasets bridge post-reset

Lane: G - `nirs4all-io`, `nirs4all-datasets`, `nirs4all-formats`

## Files modified

- `nirs4all-ecosystem/docs/agent_reports/W2L_LANE_G_IO_DATASETS_FORMATS.md`

No code files were modified. Note: `nirs4all-ecosystem/.gitignore` ignores `/docs/`, so this local report file does not appear in `git status`.

## Evidence

- Read required instructions and references:
  - root `AGENTS.md`
  - root `CLAUDE.md`
  - `nirs4all-io/CLAUDE.md`
  - `nirs4all-datasets/AGENTS.md`
  - `nirs4all-datasets/CLAUDE.md`
  - `nirs4all-formats/AGENTS.md`
  - `nirs4all-formats/CLAUDE.md`
  - `nirs4all-ecosystem/docs/agent_reports/WAVE_2L_POST_RESET_CONTROL.md`
  - `nirs4all-ecosystem/docs/agent_reports/W93_IO_DATASETS_REFERENCE_BRIDGE.md`
  - `nirs4all-ecosystem/docs/agent_reports/W101_PACKAGE_RELEASE_REVIEW.md`
- Git state:
  - `nirs4all-io/`: `refactor/L7-io-dagml-sibling` at `5651da5`, clean. This checkout is stale relative to the W93 integration state and does not expose the W93 adapter/package API.
  - `_worktrees/INT-io`: `refactor/integration-io` at `e52eecd`, clean. This contains `ac7809d feat(io): accept reference dataset specs` plus the W27 DatasetPackage API.
  - `nirs4all-datasets/`: `main` at `ac455f32`, clean, ahead of `origin/main` by 3. This contains W93 (`20b41824`), its merge (`028fb1d7`), and the post-W101 cross-repo bridge test (`ac455f32`).
  - `nirs4all-formats/`: `main` at `89231b2`, clean. This is also `refactor/W93-io-contract`; W93 required no formats code change.
- Contract verification:
  - `_worktrees/INT-io/src/nirs4all_io/api.py` has duck-typed `_adapt_to_io_spec()`, wired from `to_spec()`, accepting objects with `to_io_spec()` without importing `nirs4all-datasets`.
  - `_worktrees/INT-io/src/nirs4all_io/api.py` exposes `load(..., target="dataset_package")` and `to_dataset_package()`.
  - `_worktrees/INT-io/src/nirs4all_io/__init__.py` exports `to_dataset_package`, `describe_dataset_package`, and `DatasetPackage`.
  - `nirs4all-datasets/src/nirs4all_datasets/dataset.py` has `NirsDataset.to_io_spec()` and `NirsDataset.to_dataset_package()`, with native split labels exposed as metadata, not applied partitions.
  - `nirs4all-datasets/tests/test_dataset.py` contains `test_nirs4all_io_load_accepts_real_reference_dataset`, covering the W101 missing test: a real `NirsDataset` passed directly to `nirs4all_io.load(ds, target="dataset_package")`.
  - `nirs4all-formats/main` remains the parser-layer contract head; no bridge logic was added there.

## Tests/gates run

- `_worktrees/INT-io`:
  - `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-io/src /home/delete/nirs4all/nirs4all-io/.venv/bin/python -m pytest -q tests/test_dataset_package.py`
  - Result: `4 passed`.
- `nirs4all-datasets`:
  - `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-io/src:/home/delete/nirs4all/nirs4all-datasets/src /home/delete/nirs4all/nirs4all-datasets/.venv/bin/python -m pytest -q tests/test_dataset.py -k "to_io_spec or to_dataset_package or nirs4all_io_load"`
  - Result: `4 passed, 13 deselected`.
- `nirs4all-formats`:
  - `cargo test -p nirs4all-formats-core --lib`
  - Result: `9 passed`.

## Risks

- The primary `nirs4all-io/` checkout is stale after reset. If an integration script or release lock reads `nirs4all-io/` instead of `_worktrees/INT-io`, it will miss the W93 bridge and the DatasetPackage public API.
- `nirs4all-datasets/main` now depends on an IO head that exposes `to_dataset_package()` and `load(..., target="dataset_package")`; pairing it with stale IO `5651da5` will fail the bridge path.
- I did not move or fast-forward the shared `nirs4all-io/` checkout because `_worktrees/INT-io` is the preserved reviewed integration head and concurrent agents may rely on current branch placement.

## Decisions needed

- Decide whether the final IO pin is `_worktrees/INT-io` at `e52eecd` or whether the primary `nirs4all-io/` checkout should be fast-forwarded/merged to that state before release-lock generation.
- Decide whether to run full green gates after selecting final pins. This lane ran targeted bridge gates only.

## Recommended integration steps

1. Pin or merge IO from `_worktrees/INT-io` at `e52eecd`, not stale `nirs4all-io/` at `5651da5`.
2. Pin datasets to `nirs4all-datasets/main` at `ac455f32`.
3. Pin formats to `nirs4all-formats/main` at `89231b2`.
4. Regenerate the ecosystem release lock only after the final IO head is selected.
5. Run the full per-repo gates for IO, datasets, and formats in the final pinned workspace.
