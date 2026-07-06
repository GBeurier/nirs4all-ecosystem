# Wave 7R — DAG PyPI Workflows And Cockpit Refresh

Date: 2026-07-06

## Scope

Post-RC11 publication cleanup outside the protected production repos (`nirs4all`, `nirs4all-studio`) and without touching `nirs4all-ui` / `nirs4all-quality`.

## Agents / Reviews

- Codex main lane: implemented, published workflow changes, ran validation, refreshed cockpit.
- Codex reviewer `Confucius`: read-only cockpit/release blocker audit.
- Codex reviewer `Mencius`: read-only docs/actions/pages audit.
- Claude Code read-only reviewer: audited cockpit blockers and confirmed the PyPI/CRAN/R-universe gap classes. It did not edit files.
- Codex worker `Dewey`: read-only cockpit contract review for the new DAG PyPI surfaces.

## Repos / Files Changed

- `dag-ml`
  - `.github/workflows/release-python.yml`
  - Commits pushed to `main` and `rc/v1-full-refactor`:
    - `de5f552` — add PyPI release workflow.
    - `c41e94a` — use current macOS Intel runner.
    - `742e39b` — set up Python in publish job.
- `dag-ml-data`
  - `.github/workflows/release-python.yml`
  - Commits pushed to `main` and `rc/v1-full-refactor`:
    - `936f13e` — add PyPI release workflow.
    - `ca42edf` — use current macOS Intel runner.
    - `72be9d5` — set up Python in publish job.
- `nirs4all-cockpit`
  - `ops/targets.yaml`
  - `ops/manual-actions.yaml`
  - `tests/test_targets_topology.py`
  - `data/current.json`
  - Commits pushed to `main`:
    - `9581dbe` — track DAG PyPI release workflows.
    - `0bb3743` — refresh DAG release snapshot.
    - `b6f6d3f` — record DAG PyPI publisher blockers.
- `GBeurier/GBeurier.r-universe.dev`
  - `packages.json`
  - Commit pushed:
    - `217f163` — pin `dagmldata` to the main branch for R-universe rebuilds.

## Validation

- Local `dag-ml` Python release build:
  - `maturin build --release --manifest-path crates/dag-ml-py/Cargo.toml`
  - `scripts/smoke_python_wheel_metadata.py`
  - `scripts/smoke_python_bindings.py`
  - `maturin sdist`
  - `twine check`
- Local `dag-ml-data` Python release build:
  - `maturin build --release --manifest-path crates/dag-ml-data-py/Cargo.toml`
  - `scripts/smoke_python_wheel_metadata.py`
  - `scripts/smoke_python_bindings.py`
  - `maturin sdist`
  - `twine check`
- GitHub Actions:
  - `dag-ml` `main` and `rc/v1-full-refactor` CI/version-guard passed on `742e39b`.
  - `dag-ml-data` `main` and `rc/v1-full-refactor` CI/version-guard passed on `72be9d5`.
  - `dag-ml` `release-python` built all wheels/sdist successfully, then failed only at PyPI trusted publishing.
  - `dag-ml-data` `release-python` built all wheels/sdist successfully, then failed only at PyPI trusted publishing.
  - `nirs4all-cockpit` pages/version-guard passed on `0bb3743`; `b6f6d3f` run was pending at report creation.
- Cockpit:
  - `n4a-cockpit validate-targets ops/targets.yaml` OK.
  - `pytest -q` -> `109 passed`.
  - Fresh collect summary: `green=86 stale=2 pending=4 missing=7 broken=0 unknown=0 excluded=1`.
- R-universe:
  - `dagmldata` is published at `0.2.4` in `https://gbeurier.r-universe.dev/api/packages`.
  - Source package is present in `https://gbeurier.r-universe.dev/src/contrib/PACKAGES`.
  - R-universe overall run still reports failure because the optional R-for-WASM build failed, but Linux/macOS/Windows/source artifacts were deployed.

## Remaining Blockers

- PyPI Trusted Publisher must be created on pypi.org for:
  - `dag-ml`: owner `GBeurier`, repo `dag-ml`, workflow `release-python.yml`, environment `pypi`.
  - `dag-ml-data`: owner `GBeurier`, repo `dag-ml-data`, workflow `release-python.yml`, environment `pypi`.
  - Existing cockpit blockers still apply for `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-benchmarks`, and `nirs4all-repository`.
- CRAN manual/pending surfaces remain:
  - `n4m`, `pls4all`, `nirs4allio`, `nirs4all`.
- CRAN stale surface remains:
  - `nirs4alldatasets` is still `0.2.0` while cockpit expects `0.3.4`.

## Decisions

- Kept `nirs4all-ui` untouched because another agent is working there for `nirs4all-quality`.
- Kept `nirs4all` Python and `nirs4all-studio` production lines held.
- Did not move the RC11 aggregation tag for workflow-only changes; runtime/source parity lock stays on the previously selected RC11 heads.
- Treated `dagmldata` as green in cockpit because R-universe published source and regular platform binaries at `0.2.4`; the remaining R-for-WASM failure is tracked as external R-universe build noise, not as a package publication failure.
