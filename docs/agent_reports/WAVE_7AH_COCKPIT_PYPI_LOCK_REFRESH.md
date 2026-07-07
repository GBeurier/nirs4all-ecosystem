# Wave 7AH - Cockpit, PyPI Blockers, and Lock Refresh

Date: 2026-07-07 06:15 CEST

## Scope

- Did not touch `nirs4all-ui` or `nirs4all-quality`; another agent owns that work.
- Kept `nirs4all` Python and `nirs4all-studio` production releases out of scope.
- Focused on publication evidence, cockpit accuracy, release-lock freshness, and public site
  version drift.

## Changes Integrated

- Uploaded fallback Python artifacts to GitHub Releases while PyPI Trusted Publisher setup is
  pending:
  - `nirs4all-core v0.2.12`: `nirs4all_core-0.2.12-py3-none-any.whl`,
    `nirs4all_core-0.2.12.tar.gz`.
  - `nirs4all-providers v0.2.6`: `nirs4all_providers-0.2.6-py3-none-any.whl`,
    `nirs4all_providers-0.2.6.tar.gz`.
- Added explicit PyPI Trusted Publisher tuple validation to:
  - `nirs4all-providers` commit `e1bad9b`.
  - `nirs4all-tools` commit `4a82d7b`.
  - `nirs4all-benchmarks` commit `64b7e46`.
- Updated `nirs4all-cockpit` targets/manual actions/tests:
  - `ec42572`: records current `invalid-publisher` blockers and fallback release assets.
  - `fd4f249`: refreshed `data/current.json` through the collect workflow.
- Updated `nirs4all-org`:
  - `77c6250`: refreshed hardcoded release versions for `io 0.1.7`, `datasets 0.3.5`,
    `benchmarks 0.1.5`, and `tools 0.0.3`.
- Regenerated the aggregation release lock so locked members now record:
  - `io` at `d275a7b` / `v0.1.7`.
  - `datasets` at `ed168751` / `v0.3.5`.

## Validation

- `nirs4all-providers`: `python3.11 -m pytest -q`, `python3.11 -m build`,
  `python3.11 -m twine check dist/*`.
- `nirs4all-core`: `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests`,
  `python3.11 -m build bindings/python --outdir dist/python-release`,
  `python3.11 -m twine check dist/python-release/*`.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`,
  `python3.11 -m pytest -q`, `python3.11 -m ruff check .`.
- `nirs4all-org`: HTML parser smoke for `index.html` and `open-source-nirs-tools.html`,
  `git diff --check`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-refresh-20260707 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`,
  `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py`.

## Parallel Review Inputs

- Pasteur audited PyPI failures and confirmed the current failures are external Trusted
  Publisher configuration gaps, not build failures.
- Aristotle audited E2E coverage and confirmed `11` ready scenarios with `48` evidence
  artifacts, while identifying remaining semantic strictness debt.
- Planck audited cockpit/org/ecosystem consistency and identified the stale public site
  versions plus the stale `io`/`datasets` lock members addressed here.

## Remaining Risks

- PyPI still needs Trusted Publisher setup for `nirs4all-core`, `nirs4all-providers`,
  `nirs4all-tools`, and `nirs4all-benchmarks`; no PyPI token is available in the workspace.
- R-universe is still allowed to lag GitHub/PyPI/npm/crates publication status.
- E2E scenarios are evidence-green but still have strictness debt: `strictness_gaps=12` and no
  full strict multimodal parity scenario yet.
