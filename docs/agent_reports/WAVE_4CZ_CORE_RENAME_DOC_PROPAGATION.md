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
| `nirs4all-io` | `1cea4cb` | `docs/index.md`, `.github/workflows/ci.yml` |
| `nirs4all-formats` | `fd3fcdc` | `docs/index.md` |
| `nirs4all-methods` | `60641219` | `bindings/matlab/README.md`, `docs/about.md`, `bindings/js/README.md`, `bindings/js/INPUT_CONTRACT.md` |
| `dag-ml` | `e6ee688` on `refactor/L20-lockstep` | `AGENTS.md`, `docs/index.md`, `docs/SUPPORTED.md`, `crates/dag-ml-wasm/README.md` |
| `dag-ml-data` | `0850a71` on `rc/v1-full-refactor` | `docs/index.md` |
| `nirs4all-web` | `9829e7e` | `CLAUDE.md` |

The `nirs4all-ecosystem` submodule pins were advanced to those heads.

`nirs4all-io` received a follow-up CI-only fix after GitHub Actions exposed that
the ecosystem E2E test expects the `nirs4all-datasets` sibling repository on the
runner. The workflow now checks out that sibling instead of skipping or weakening
the E2E test.

## Tests and checks

- `git diff --check` passed in each touched repo.
- `python3.11 -m pytest -q tests/e2e/test_formats_io_datasets_methods.py`
  passed in `nirs4all-io` (`1 passed`) after installing the repo with
  `python3.11 -m pip install -e ".[parquet,excel]" scipy pytest ruff mypy`.
- `.github/workflows/ci.yml` YAML parsed successfully with `python3.11` /
  `yaml.safe_load`.
- Targeted stale-doc search passed for the corrected files:
  `grid-item-card} nirs4all-lite`, `nirs4all-lite.readthedocs`,
  stale `nirs4all-web` topology wording, stale MATLAB parity wording,
  stale `dag-ml` downstream-chain wording, and stale JS methods aggregation
  wording.
- GitHub Actions were triggered on the pushed repos. At commit time several
  full CI runs were still queued/in progress; the `nirs4all-io` follow-up is
  CI-only and supersedes the earlier failed run where the datasets sibling was
  absent.

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
- The `nirs4all-io` failure was fixed by making the runner match the intended
  multi-repo E2E workspace layout, not by reducing coverage.

## Risks

- Sphinx site builds were not run locally for every repo; only formatting and
  targeted text checks were run. GitHub Actions / Pages jobs remain the final
  docs build signal for this lightweight documentation batch.
- `dag-ml-data` is pinned from `rc/v1-full-refactor`, not `main`, matching its
  current local release-candidate lane.
- `dag-ml` is pinned from `refactor/L20-lockstep`, matching its current local
  release-candidate lane.
