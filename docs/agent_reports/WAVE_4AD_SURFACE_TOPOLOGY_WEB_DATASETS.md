# Wave 4AD - Surface Topology, Web, IO, Datasets

Date: 2026-07-03

Coordinator: Codex parent session in `/home/delete/nirs4all`.

## Scope

This batch closes review findings from parallel read-only agents and adds
release evidence without rerunning the long full Python parity oracle. The last
full Python-reference proof remains Python `6a2c720` with `887 passed`,
`0 skipped`, `0 xfailed`, and `0 failed`.

## Core Topology

Commit:

- `1b505e9 fix(release): declare rust and matlab v1 surfaces`

Files modified:

- `Makefile`
- `bindings/python/src/nirs4all_lite/_topology.py`
- `bindings/python/tests/test_release_topology.py`

Decisions:

- Core `v1_release_surfaces` now matches the public V1 language promise:
  Python, JavaScript/WASM, Rust, R, and MATLAB/Octave.
- `test-v1-surfaces` now includes Rust and a MATLAB/Octave parity target that
  emits an explicit `SKIP/RISK` only when Octave is unavailable.
- The aggregation lock was regenerated from the committed Core head, rather
  than edited by hand.

Tests:

- `PYTHONPATH=bindings/python/src python3.11 -m unittest -v bindings/python/tests/test_release_topology.py`
  -> `12` tests passed.
- `PYTHON=python3.11 make test-v1-surfaces
  NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods` with
  Node `v22.21.1` and R from `p4a-r` on `PATH` -> Rust `8` tests passed,
  Python V1 surfaces `53` tests passed, WASM V1 surfaces Node TAP `14` tests
  with `0` skipped, R V1 package surface scripts passed, and MATLAB/Octave was
  explicitly skipped in that PATH.
- `conda run -n pls4all_r bash -lc 'unset LIBRARY_PATH CPATH C_INCLUDE_PATH CPLUS_INCLUDE_PATH CMAKE_PREFIX_PATH CONDA_BUILD_SYSROOT; make test-matlab-parity-if-available NIRS4ALL_METHODS_ROOT=/home/delete/nirs4all/_worktrees/RC-v1-methods'`
  -> `nirs4all MATLAB/Octave execution parity passed`.

Publication:

- `nirs4all-lite` / Core RC branch `rc/v1-full-refactor-core` and tag
  `n4a-v1-rc1-2026.07-refactor` now point to `1b505e9`.

## Web Client-Only Gate

Review:

- Codex subagent `019f2684-2912-7dd3-80d0-3b3c3866dab2` audited
  `RC-v1-web/studio-lite` read-only and found the product remains a static
  React/Vite browser/WASM app. Node dependencies are build/test/dev only; no
  production backend dependency was found.

Coordinator tests:

- `npm run typecheck` -> PASS.
- `npm run test` -> Vitest `21` files / `134` tests passed.
- `npm run test:client-only` -> `2` tests passed.
- `npm run validate:catalog` -> `64` catalog symbols checked against `702`
  upstream exports; catalog/ABI sync PASS.
- `npm run build` -> static Vite build PASS.
- `npm run build:single` -> single offline HTML build PASS.
- `npm run smoke` -> all `23` Chromium smokes passed, with no JS console
  errors.

Decision:

- `web.nirs4all.org` remains client-side-only. Node modules in the repo are
  build/test/development dependencies, not a production server requirement.

## IO and Datasets Gates

IO tests:

- `cargo fmt --all --check` -> PASS.
- `cargo clippy --workspace --all-targets -- -D warnings` -> PASS.
- `cargo test --workspace` -> PASS.
- `cargo build --workspace --no-default-features` -> PASS.
- `bash scripts/dag_ml_data_conformance.sh` -> both CLI conformance cases
  passed through `dag-ml-data-cli validate-envelope` and
  `dag-ml-cli validate-data-binding`.
- `bash tests/cross_binding/verify.sh` -> no failure, but cross-binding parity
  did not run because fewer than two binding toolchains were available in that
  shell. This remains an explicit skipped local gate, not a proof.

Datasets tests:

- `cargo fmt --all --check` -> PASS.
- `cargo clippy --workspace --all-targets -- -D warnings` -> PASS.
- `cargo test --workspace` -> PASS.
- `ruff check .` -> PASS.
- `mypy --config-file pyproject.toml src` -> PASS.
- `python3.11 catalog/scripts/validate.py` -> `164` descriptors valid.
- `python3.11 catalog/scripts/validate.py --check-publish` -> `164`
  descriptors valid.
- `python3.11 -m pytest -q -m "not network" -rs` -> `226 passed`,
  `6 skipped`; every skip is an optional bridge dependency absent from the
  standalone environment (`nirs4all_io` or `nirs4all`).
- Integrated bridge rerun with RC `nirs4all_io` and RC Python `nirs4all` on
  `PYTHONPATH` -> `7 passed`, covering the tests that skipped standalone.

Decision:

- Datasets still has legitimate distribution/retrieval roadmap items, but the
  release-candidate bridge skips are covered by an integrated local gate and
  must not be counted as untested parity holes for this batch.
- Datasets is not a software blocker for an RC that claims catalog/bridge
  readiness. It would become a blocker only if the RC promises that remote
  `get(id)` works for every dataset without local canonical bytes or dataset
  hosting; that global distribution claim remains explicitly out of scope.

## Methods ABI Freshness

Tests:

- `make test-abi-freshness PRESET=dev-release` -> CMake configure/build OK,
  native ABI snapshot up to date, ABI compatibility OK for header `2.0.x`,
  Linux dynamic dependencies listed, and `Native ABI freshness OK`.
- After the docs hygiene patch on Methods `cb9159dd`:
  `scripts/bump_version.sh --check` -> project `1.0.1`, ABI `2.0.0`, every
  manifest in sync; `cmake --build --preset dev-release --target n4m_tests
  n4m_internal_tests --parallel && ctest --preset dev-release
  --output-on-failure` -> `2/2` tests passed; `make test-js-wasm` -> WASM
  runtime `1.0.1+abi.2.0.0`, `npm test` PASS, `npm pack --dry-run` PASS.
- GitHub Actions on `cb9159dd`: `CI`, `Cross-binding parity`, `Parity gate`,
  `ABI Surface`, `Coverage`, `Sanitizers`, `version-sync`, and
  `version-guard` all completed with success.

Review:

- Codex subagent `019f2691-c1b9-7322-91e9-8aa1a9dbdd4e` audited Methods
  read-only. It found the runtime targets for ABI, JS/WASM, R, Octave/MEX, and
  MATLAB present, and identified stale release-readiness documentation rather
  than missing local gates.

Decision:

- Methods ABI freshness is current on the selected RC head. Wave 4AC remains
  the source record for Methods R binding, Octave/MEX, and JS/WASM parity gates.
- The stale RC-readiness docs and stale JS fixture provenance were corrected on
  `cb9159dd`. `RELEASE_READINESS.md` now separates the June audit baseline from
  the current RC state, and `release_process.md` no longer contradicts
  `release-npm.yml`.
- Remaining Methods debt is release-distribution and coverage hardening:
  CRAN incoming/PDF/win-builder/R-hub/macbuilder evidence, `nirs4all-methods`
  sdist and post-publish smoke, broader R/Octave surface coverage beyond current
  smoke/parity fixtures, and a full-registry/multi-shape parity dashboard.

## Ecosystem Lock and Docs

Files modified:

- `README.md`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/RC_V1_FULL_REFACTOR_CONTROL.md`
- `docs/agent_reports/WAVE_4AC_NONPY_GATES_SECURITY.md`
- `docs/agent_reports/WAVE_4AD_SURFACE_TOPOLOGY_WEB_DATASETS.md`

Decisions:

- The README now states that parent-repo submodule gitlinks are not the RC V1
  authority. Aggregate RC heads are governed by `aggregation-lock` and each
  manifest `selected_workspace_path`; product surfaces outside the aggregate
  lock are governed by the surface matrix and agent reports.
- The lock now pins Core `1b505e9` and records Rust and MATLAB/Octave in Core
  `v1_release_surfaces`.

## Parallel Reviews

- Web reviewer: no backend/prod-server surface found; coordinator closed the
  static-audit limitation by running the full web gate.
- Ecosystem reviewer: lock and remote refs matched selected RC heads; reviewer
  flagged the submodule-gitlink ambiguity and missing Rust/MATLAB Core
  surfaces, both addressed in this batch.
- Non-Python reviewer: recommended IO/Datasets/Methods/Core gates. Coordinator
  closed IO Rust workspace, Datasets standalone + integrated bridge, Methods
  R/Octave/WASM from Wave 4AC, and Core Rust/Python/WASM/R/Octave in this batch.

## Remaining Risks

- Full Python parity was intentionally not rerun in this batch.
- Licensed MATLAB runtime proof remains outside this Linux/Octave environment.
- Datasets public distribution/retrieval readiness remains a release-management
  item separate from the local bridge parity gates. Do not claim global remote
  `get(id)` coverage for all datasets until canonical hosting/DOI/file-id
  routes are complete.
- IO cross-binding parity still needs a shell/CI environment with at least two
  binding toolchains available at the same time.
