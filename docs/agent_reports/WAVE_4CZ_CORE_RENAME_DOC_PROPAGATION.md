# Wave 4CZ - Core Rename Doc Propagation

Date: 2026-07-04

## Scope

Propagate the `nirs4all-lite` -> `nirs4all-core` V1 RC topology across public,
non-production-sensitive documentation surfaces discovered by the Claude Code
topology audit. Runtime compatibility names, legacy persistence keys, schema
fixture names, and the full Python `nirs4all` / `nirs4all-studio` production
hold were left untouched.

## Modified repos

| Repo | Commit | Files modified |
| --- | --- | --- |
| `nirs4all-datasets` | `2c414bda` | `docs/index.md` |
| `nirs4all-io` | `2e5e2a5` | `docs/index.md`, `.github/workflows/ci.yml`, `tests/e2e/test_formats_io_datasets_methods.py` |
| `nirs4all-formats` | `fd3fcdc` | `docs/index.md` |
| `nirs4all-methods` | `60641219` | `bindings/matlab/README.md`, `docs/about.md`, `bindings/js/README.md`, `bindings/js/INPUT_CONTRACT.md` |
| `dag-ml` | `222a1c3` on `refactor/L20-lockstep` | `AGENTS.md`, `Cargo.lock`, `docs/index.md`, `docs/SUPPORTED.md`, `docs/migration-nirs4all/README.md`, `crates/dag-ml-wasm/README.md` |
| `dag-ml-data` | `0850a71` on `rc/v1-full-refactor` | `docs/index.md` |
| `nirs4all-web` | `9829e7e` | `CLAUDE.md` |

The `nirs4all-ecosystem` submodule pins were advanced to those heads.

`nirs4all-io` received follow-up E2E fixes after GitHub Actions exposed that the
ecosystem test was accidentally relying on local, untracked canonical dataset
bytes. The workflow still checks out the `nirs4all-datasets` sibling source, but
the test now generates two deterministic schema-2.0 leaves and canonicalizes
them through the real `nirs4all-datasets.bootstrap` + `organize` APIs before
validating the `NirsDataset -> nirs4all-io DatasetPackage` bridge. This keeps
coverage active without depending on private/local canonical data.

## Tests and checks

- `git diff --check` passed in each touched repo.
- `python3.11 -m pytest -q tests/e2e/test_formats_io_datasets_methods.py`
  passed in `nirs4all-io` (`1 passed`) after installing the repo with
  `python3.11 -m pip install -e ".[parquet,excel]" scipy pytest ruff mypy`.
- The same targeted test passed after adding the CI install dependencies for
  `nirs4all-datasets` source imports (`pydantic`, `python-dotenv`, `matplotlib`,
  `requests`, `typer`).
- `nirs4all-io`: `python3.11 -m pytest -q tests/e2e/test_formats_io_datasets_methods.py`
  passed after replacing local canonical dataset assumptions with generated
  canonical bridge fixtures (`1 passed`).
- `nirs4all-io`: `python3.11 -m ruff check .` passed.
- `nirs4all-io`: `python3.11 -m mypy .` passed.
- `nirs4all-io`: `python3.11 -m pytest -q -m "not parity"` passed
  (`233 passed, 3 skipped`).
- `dag-ml`: `cargo test --workspace` passed (`575 passed, 2 ignored`).
- `dag-ml`: `cargo audit --deny warnings` passed after updating `anyhow` from
  `1.0.102` to `1.0.103`.
- `dag-ml`: `sphinx-build -W --keep-going -b html docs docs/_build/html`
  passed in a clean temporary worktree with the pending patch applied. The fix
  includes the committed migration docs in the site toctree and keeps local-only
  docs as literal paths.
- `.github/workflows/ci.yml` YAML parsed successfully with `python3.11` /
  `yaml.safe_load`.
- Targeted stale-doc search passed for the corrected files:
  `grid-item-card} nirs4all-lite`, `nirs4all-lite.readthedocs`,
  stale `nirs4all-web` topology wording, stale MATLAB parity wording,
  stale `dag-ml` downstream-chain wording, and stale JS methods aggregation
  wording.
- GitHub Actions were triggered on the pushed repos. At commit time several
  full CI runs were still queued/in progress; the `nirs4all-io` follow-up is
  CI-only and supersedes the earlier failed runs where the datasets sibling and
  then its source-import dependencies were absent.

## Review notes

- The cockpit snapshot already models `nirs4all-core` correctly:
  PyPI `nirs4all` remains the full Python library, PyPI `nirs4all-core` is the
  aggregate target, PyPI `nirs4all-lite` is the legacy alias, and bare
  `nirs4all` on crates/npm/CRAN belongs to the aggregate bindings.
- Remaining `nirs4all-lite` strings in code, fixtures, legacy local-storage
  keys, schema names, and compatibility shims were intentionally preserved.
- `nirs4all-studio` docs were not edited in this batch because the user asked
  to hold the production-sensitive Studio repo outside the release path, except
  for the Windows RC installer.
- The `nirs4all-io` failure was fixed by removing dependence on untracked local
  canonical data and exercising the actual datasets canonicalization bridge in
  the E2E test, not by reducing coverage.

## Risks

- Sphinx site builds were not run locally for every repo; only formatting and
  targeted text checks were run. GitHub Actions / Pages jobs remain the final
  docs build signal for this lightweight documentation batch.
- `dag-ml-data` is pinned from `rc/v1-full-refactor`, not `main`, matching its
  current local release-candidate lane.
- `dag-ml` is pinned from `refactor/L20-lockstep`, matching its current local
  release-candidate lane.
