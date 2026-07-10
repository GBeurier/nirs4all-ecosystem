# WAVE 9ZN - nirs4all-core WASM alias cleanup release

Date: 2026-07-10

## Scope

- Repo: `nirs4all-core`
- Lane: core/runtime/package topology
- Change: removed unpublished legacy WASM upstream aliases from the `nirs4all`
  npm package and runtime loader.

## Files modified in `nirs4all-core`

- `bindings/wasm/package.json`
- `bindings/wasm/package-lock.json`
- `bindings/wasm/src/index.js`
- `bindings/wasm/tests/index.test.js`
- `bindings/python/tests/test_release_topology.py`
- `bindings/rust/nirs4all/Cargo.toml`
- `bindings/python/pyproject.toml`
- `bindings/python/src/nirs4all_core/__init__.py`
- `bindings/r/DESCRIPTION`
- `Cargo.lock`
- `CHANGELOG.md`
- `docs/BINDINGS.md`
- `docs/RELEASE.md`

## Decisions

- Kept only published canonical WASM peers:
  `@nirs4all/formats-wasm`, `@nirs4all/io-wasm`,
  `@nirs4all/datasets-wasm`, `@nirs4all/methods`,
  `dag-ml-wasm`, and `dag-ml-data-wasm`.
- Removed runtime loader fallbacks for unpublished aliases:
  `nirs4all-formats-wasm`, `nirs4all-io-wasm`, and
  `@nirs4all/nirs4all-datasets-wasm`.
- Bumped the aggregate release train to `0.3.10` because the npm package
  surface changed.

## Tests and validation

- `scripts/bump_version.sh --check`
- `npm test` in `bindings/wasm` with Linux Node from `nvm`
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=bindings/python/src python3 -m pytest -q bindings/python/tests/test_release_topology.py bindings/python/tests/test_cross_language_surface.py`
- `cargo test --workspace`
- `source /home/delete/.nvm/nvm.sh && make test-v1-surfaces`
- `npm pack --dry-run` in `bindings/wasm`
- `cargo package -p nirs4all --allow-dirty --no-verify`

## Published artifacts

- Commit: `cc06b45862230a6d70a7c92a2cf7fa16020fa13c`
- Tag: `v0.3.10`
- GitHub Release: <https://github.com/GBeurier/nirs4all-core/releases/tag/v0.3.10>
- npm: `nirs4all@0.3.10`
- crates.io: `nirs4all@0.3.10`
- PyPI: `nirs4all-core==0.3.10`
- GitHub Release assets:
  - `nirs4all-core-0.3.10-src.tar.gz`
  - `nirs4all-core-0.3.10-src.zip`
  - `nirs4all-core-0.3.10.cdx.json`
  - `nirs4all-matlab-octave-0.3.10.zip`
  - `nirs4all_0.3.10.tar.gz`
  - `SHA256SUMS`

## Risks

- Local `make test-v1-surfaces` could not execute R and Octave parity because
  those toolchains are not installed locally. The tag release workflows for R
  and MATLAB/Octave completed successfully on GitHub.
