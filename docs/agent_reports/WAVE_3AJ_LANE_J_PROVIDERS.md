# Wave 3AJ - Lane J Providers/Plugins

Date: 2026-07-01

## Scope

Lane J follow-up for repository/benchmarks/papers as providers/plugins of
pipelines and reproducible exports.

Pre-existing state was audited before coding:

- `nirs4all-repository`, `nirs4all-benchmarks`, and `nirs4all-papers` were clean
  and each behind `origin/main` by one site/SEO commit.
- Those commits were reviewed as local SEO/crawl metadata changes, then
  fast-forwarded before feature work.
- Old worktrees under `_worktrees/` were not merged.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Kierkegaard the 2nd | `nirs4all-papers` read-only gap audit | done | Recommended a thin first-party provider/export facade only. |
| Gauss the 2nd | `nirs4all-benchmarks` repository consumer bridge | integrated | Commit `90ef79f feat(ingestion): register repository pipeline recipes`. |
| Kant the 2nd | benchmarks bridge review | GO | Confirmed consumer-only boundary, lazy optional dependency, planning-only tests. |
| Mill the 2nd | `nirs4all-papers` provider/export facade | integrated | Commit `f7ee141 feat(provider): add papers export facade`. |
| Dalton the 2nd | papers facade review | GO | Confirmed archive boundary, no runtime execution or writeback, focused tests. |

## Integrated Changes

### `nirs4all-benchmarks`

- Added `nirs4all_benchmarks.ingestion.repository`.
- Added `register_repository_pipeline()`:
  - lazy-imports `nirs4all_repository`;
  - resolves `get(name, with_artifacts=False)`;
  - consumes `Pipeline.recipe()`;
  - delegates to existing `register_pipeline`;
  - creates `planned_runs` only, with source `nirs4all-repository:<name>`.
- Added `list_repository_pipelines()` as a read-only helper over
  `nirs4all_repository.list(...)`.
- Added `tests/test_repository_bridge.py`.

### `nirs4all-papers`

- Added `nirs4all_papers.provider` facade:
  - `provider_capabilities`;
  - `list_papers`;
  - `load_paper_bundle`;
  - `inspect_bundle`;
  - `build_methods_section`;
  - `build_repro_page`;
  - `export_sidecars`.
- Exposed `write_paper_sidecars(view, out)` from `nirs4all_papers.site`.
- Kept sidecar writes bounded to explicit local output under `out/paper/<slug>/`.
- Added `tests/test_provider_api.py`.

## Validation

Fast-forward validation:

- `nirs4all-repository`: `PYTHONPATH=src python3.11 -m pytest tests/test_api.py -q -p no:cacheprovider` -> 7 passed.
- `nirs4all-benchmarks`: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_site_build.py -q -p no:cacheprovider` -> 1 passed.
- `nirs4all-papers`: `python3.11 -m pytest tests -q -p no:cacheprovider` -> 36 passed, 2 skipped.

Post-integration validation:

- `nirs4all-benchmarks`: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_repository_bridge.py tests/test_upload_indexing.py tests/test_site_build.py -q -p no:cacheprovider` -> 17 passed.
- `nirs4all-benchmarks`: `PYTHONPATH=src .venv/bin/python -m ruff check src/nirs4all_benchmarks/ingestion/repository.py src/nirs4all_benchmarks/ingestion/__init__.py tests/test_repository_bridge.py` -> passed.
- `nirs4all-benchmarks`: `PYTHONPATH=src .venv/bin/python -m mypy src/nirs4all_benchmarks/ingestion/repository.py` -> passed.
- `nirs4all-papers`: `PYTHONPATH=src python3 -m pytest tests/test_provider_api.py tests/test_build.py tests/test_provenance.py -q -p no:cacheprovider` -> 16 passed.
- `nirs4all-papers`: `ruff check src/nirs4all_papers/provider.py src/nirs4all_papers/site/__init__.py tests/test_provider_api.py` -> passed.
- `nirs4all-papers`: `mypy src/nirs4all_papers` -> passed.
- `git diff --check HEAD~1..HEAD` -> passed in both integrated repos.

## Gate Policy

- Full Python-reference parity was intentionally not run in this small Lane J
  batch; no runtime, prediction, save/load, converter, or native binding behavior
  changed.
- `nirs4all-repository` remains the provider of pipeline list/get pipeline.
- `nirs4all-benchmarks` consumes repository recipes and plans runs without writing
  into the repository or executing pipelines.
- `nirs4all-papers` remains an archive/export surface; the new facade writes only
  caller-selected local sidecar output.

## Risks

- `nirs4all-benchmarks` does not add a packaging extra for
  `nirs4all-repository`; callers must install the optional provider package.
- Repository lookup can fetch remotely according to `nirs4all-repository.get`
  semantics if no local/bundled pipeline is available; tests monkeypatch the
  provider to stay offline.
- `write_paper_sidecars` overwrites its five sidecar filenames if the caller
  points it at an existing output tree, but it does not delete directories and is
  bounded to explicit local output.
