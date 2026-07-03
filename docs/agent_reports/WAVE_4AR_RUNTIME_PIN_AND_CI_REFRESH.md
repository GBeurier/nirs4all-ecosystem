# Wave 4AR Runtime Pin And CI Refresh

Date: 2026-07-03

## Scope

Refresh the selected RC heads after the first published CI sweep exposed two
release-blocking but narrow integration issues:

- `nirs4all` Windows CI failed on a transient parquet atomic replace lock.
- `dag-ml-data` Rust/MSRV CI checked out `dag-ml` default `main` instead of the
  paired RC branch.
- Studio release archive/Docker pins then needed to follow the refreshed Python
  and `dag-ml-data` heads.

No full Python parity run was launched in this wave. Per coordination policy,
that gate remains deferred until the next large integration batch.

## Files Modified

`nirs4all`:

- `nirs4all/pipeline/storage/array_store.py`
- `tests/unit/pipeline/storage/test_array_store.py`

`dag-ml-data`:

- `.github/workflows/ci.yml`

`nirs4all-studio`:

- `.github/workflows/release-unified.yml`
- `Dockerfile`

`nirs4all-ecosystem`:

- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
- `docs/agent_reports/WAVE_4AR_RUNTIME_PIN_AND_CI_REFRESH.md`

## Published Heads

- Python `nirs4all`: `bf242e4854693ccb048b7f0ffc5f3fdd2380315a`
- `dag-ml-data`: `616f3e5ff715667d537c089a9ba059832f8cc1c9`
- Studio: `15082420c4c91f089eddfcf299b733b96d0802f6`
- Cluster security guard remains selected at `96434605f5379ceda8eafea608a4a51c373f1fc4`

## Tests And Checks

`nirs4all` local targeted checks:

- `ruff check nirs4all/pipeline/storage/array_store.py tests/unit/pipeline/storage/test_array_store.py`
- `python3.11 -m pytest tests/unit/pipeline/storage/test_array_store.py::TestArrayStoreAppend::test_append_retries_transient_windows_replace_lock tests/unit/pipeline/storage/test_array_store.py::TestArrayStoreAppend::test_append_to_existing -q -p no:cacheprovider`
- `python3.11 -m pytest tests/integration/pipeline/test_separation_branch_generators.py::TestBySourceWithGenerators::test_by_source_with_or_generator -q -p no:cacheprovider`
- `python3.11 -m pytest tests/unit/pipeline/storage/test_array_store.py -q -p no:cacheprovider`

`dag-ml-data` local checks:

- workflow YAML parse
- `python3 scripts/validate_contracts.py --require-sibling --sibling-root ../RC-v1-dagml`
- `git diff --check`

`nirs4all-studio` local checks:

- workflow YAML parse
- stale branch/ref guard over `.github/workflows/release-unified.yml` and `Dockerfile`
- `git diff --check`

`nirs4all-ecosystem` local checks:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`

GitHub Actions:

- `dag-ml-data` `616f3e5`: `CI` and `version-guard` completed successfully.
- Python `bf242e48`: `version-guard` and `CodeQL` completed successfully; `CI`,
  `Documentation`, and `Docs Quality` were still running when this report was
  written.
- Studio `1508242`: `CI` and `Playwright E2E Tests` were still running when this
  report was written.

## Decisions

- The Windows atomic replace retry is scoped to `os.name == "nt"` and only wraps
  the final `os.replace`, so Linux/macOS semantics remain unchanged.
- `dag-ml-data` Rust/MSRV jobs now resolve the paired `dag-ml` branch the same
  way as the lockstep contract job. This prevents RC CI from accidentally testing
  against stale `dag-ml` main contracts.
- Studio release all-in-one/Docker runtime dependencies stay pinned to immutable
  commit archives, not moving `rc/**` branch tarballs.

## Risks

- Full Python parity still needs a fresh large-batch rerun on `bf242e48` or the
  eventual later selected head before RC promotion.
- Studio all-in-one/Docker release jobs remain release-environment proof, not
  fully exercised by this YAML/pin refresh.
- Python and Studio GitHub Actions were pending at report creation and must be
  checked before final RC sign-off.
