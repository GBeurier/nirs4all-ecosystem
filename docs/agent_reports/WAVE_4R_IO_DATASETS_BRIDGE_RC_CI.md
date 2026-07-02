# Wave 4R - IO/datasets bridge and RC CI refresh

Date: 2026-07-02
Coordinator: Codex

## Scope

Close the concrete provider/datasets bridge gap found after the reset, refresh
normal RC branch gates where touched, and fold in the latest GitGuardian
read-only follow-up. Full Python parity was not rerun in this wave.

## Published Code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-io` | `rc/v1-full-refactor` | `dac4841` / `n4a-v1-rc1-2026.07-refactor` | `bindings/python/README.md`, `bindings/python/python/nirs4all_io/__init__.py`, `bindings/python/python/nirs4all_io/_package.py`, `bindings/python/python/nirs4all_io/materialize/__init__.py`, `bindings/python/tests/test_idiomatic.py` |
| `nirs4all-datasets` | `rc/v1-full-refactor` | `cac8742` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/{abi-check,ci,version-guard,version-sync}.yml`, `bindings/python/Cargo.lock`, `scripts/ensure_rust_deps.sh` |
| `nirs4all-studio` | `rc/v1-full-refactor` | `fd06d94` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/ci.yml`, `.github/workflows/playwright.yml` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | aggregation lock, surface matrix source list, control/security reports, this report |

## Changes

- The pyo3 `nirs4all-io` Python binding now exposes
  `to_dataset_package`, `describe_dataset_package`, and
  `load(..., target="dataset_package"|"package")`, plus
  `nirs4all_io.materialize` re-exports for `DatasetPackage`,
  `PayloadManifest`, `PayloadManifestEntry`, `PayloadStorageKind`,
  `RowPositionFallback`, and `repr_ids`.
- The binding package implementation was split out of top-level
  `__init__.py` into `_package.py` after review, uses the same canonical JSON
  form as the Python MVP/Rust core, includes the full representation-id set,
  hashes metadata with dtype labels, and keeps `load(package,
  target="assembled")` coherent with the package assembled view.
- `nirs4all-datasets/scripts/ensure_rust_deps.sh` now resolves `rc/**`
  sibling refs from `NIRS4ALL_SIBLING_REF`, GitHub branch env, or the local
  branch, and can clone from local `RC-v1-formats` / `RC-v1-io` worktrees
  where `.git` is a worktree file. This prevents the RC layout from silently
  falling back to stale default siblings.
- Datasets normal CI/version/ABI workflows now include `rc/**` branch filters.
- Datasets `bindings/python/Cargo.lock` was refreshed by the successful
  editable build against the selected IO RC dependency graph.
- Studio CI and Playwright workflows now run on `rc/**` branches and select the
  RC Python library checkout on RC branch runs.
- The aggregation lock now pins `nirs4all-io` `dac4841` and
  `nirs4all-datasets` `cac8742`.

## Local Gates

IO:

- `python3.11 -m py_compile bindings/python/python/nirs4all_io/__init__.py bindings/python/python/nirs4all_io/_package.py bindings/python/python/nirs4all_io/materialize/__init__.py bindings/python/tests/test_idiomatic.py`
- `python3.11 -m ruff check bindings/python/python/nirs4all_io bindings/python/tests/test_idiomatic.py`
  -> `All checks passed!`
- `git diff --check`
- `/tmp/n4a-io-binding-venv/bin/python -m pytest bindings/python/tests -q`
  -> `25 passed in 0.58s`

Datasets/providers bridge:

- `bash -n scripts/ensure_rust_deps.sh`
- YAML parse of `.github/workflows/*.yml`
- `git diff --check`
- `./scripts/ensure_rust_deps.sh` selected `rc/v1-full-refactor` siblings and
  refreshed the local canonical sibling clones.
- `/tmp/n4a-io-binding-venv/bin/python -m pip install -e RC-v1-datasets -e RC-v1-providers`
  -> successful editable install.
- Datasets bridge tests:
  `tests/test_dataset.py::test_to_dataset_package_delegates_to_nirs4all_io`,
  `tests/test_dataset.py::test_nirs4all_io_load_accepts_real_reference_dataset`,
  `tests/test_access.py::test_get_local_reference_dataset_loads_through_io_package_bridge`
  -> `3 passed in 0.35s`.
- Providers bridge tests:
  `tests/test_datasets_provider.py::test_dataset_package_capability_reports_available_bridge`,
  `tests/test_datasets_provider.py::test_to_dataset_package_forwards_verbatim_to_io_entrypoint`
  -> `2 passed`.

Ecosystem:

- `python3.11 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`

## Parallel Review Inputs

- Codex IO package reviewer found canonical JSON, metadata dtype, assembled
  target, and `repr_ids` drift risks in the first bridge slice. The published
  IO commit corrects those before publication.
- Codex CI reviewer found normal gates still missing `rc/**` across several
  repos. This wave fixes the touched datasets and previously published Studio
  gates; the remaining repo-wide CI branch filters are recorded as follow-up
  debt, not hidden.
- Codex security reviewer confirmed current cluster release branch/tag refs are
  clean for the checked CLI secret-option patterns. Old PR refs and superseded
  local/remote refactor refs may still contain placeholder-looking examples
  such as env-token, `dev`, or `T` values; treat continued GitGuardian alerts
  as rescan/support work unless the revealed value was a real credential.

## Remaining Risk

- Full Python-reference parity was not rerun in this wave by design; rerun only
  after the next substantial runtime batch or before production cutover.
- Providers still has only a Python implementation package. The cross-language
  contract is the neutral JSON schema/fixture set until R/WASM/native provider
  clients are implemented.
- Datasets non-Python acquisition surfaces still need their own environment
  gates. This wave only proves the Python datasets/providers bridge through the
  pyo3 IO binding and the RC sibling topology.
- Several other repos still have normal CI workflows filtered to `main` rather
  than `rc/**`; those should be patched in a separate broad CI branch-filter
  batch.
