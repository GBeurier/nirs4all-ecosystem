# Wave 7E - RC7 Hermetic Lock Fix

Date: 2026-07-06

## Scope

- Audited the RC5 custom app host gate after a read-only Claude review reported that the ecosystem submodule pins could mask a false green.
- Repinned ecosystem submodules for the custom-host path:
  - `nirs4all-core` -> `5c652e66855908cc2a7ac60cb9fa20164e9bde6b`
  - `nirs4all-web` -> `4346fd7`
  - `nirs4all-ui` remains `73dcce9ac7e92b4cc02884eeb9e4ce11d81aff2d`
- Regenerated the aggregation lock after the core RC head moved to `0.2.7`.

## Code Fixes

- `nirs4all-core`: merged the main E2E/runtime gates into `rc/v1-full-refactor`, then bumped the aggregate to `0.2.7`.
- `nirs4all-web`: fixed `sync-ui-shim.mjs` so clean ecosystem submodule checkouts do not fail on missing option defaults or an unbuilt upstream `nirs4all-ui/dist`.

## Publications

- crates.io: published `nirs4all 0.2.7`.
- npm: published `nirs4all 0.2.7`.
- PyPI: `nirs4all-core 0.2.7` wheel and sdist build and pass `twine check`; upload remains blocked by missing PyPI Trusted Publisher/token.
- R: `nirs4all_0.2.7.tar.gz` builds locally; CRAN/R-universe publication remains separate/manual.

## Validation

- `nirs4all-core`: `scripts/bump_version.sh --check`
- `nirs4all-core`: `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests` -> 60 tests, 1 skipped
- `nirs4all-core`: `npm run test:js --prefix bindings/wasm` -> 16 tests
- `nirs4all-core`: `node bindings/wasm/node_modules/typescript/bin/tsc --project bindings/wasm/tsconfig.typecheck.json`
- `nirs4all-core`: `cargo test --manifest-path bindings/rust/nirs4all/Cargo.toml` -> 9 tests
- `nirs4all-core`: `python3.11 -m pytest -q tests/test_consume_repository_descriptor.py tests/test_verify_cluster_handoff.py` -> 5 tests
- `nirs4all-core`: `cargo publish --manifest-path bindings/rust/nirs4all/Cargo.toml --dry-run --allow-dirty`
- `nirs4all-core`: `npm pack --dry-run` from `bindings/wasm`
- `nirs4all-core`: `python3.11 -m build bindings/python`
- `nirs4all-core`: `python3.11 -m twine check bindings/python/dist/*`
- `nirs4all-core`: `R CMD build bindings/r --no-build-vignettes`
- `nirs4all-ecosystem`: `python3 scripts/n4a_release_lock.py ... generate`
- `nirs4all-ecosystem`: `python3 scripts/n4a_release_lock.py ... validate`
- `nirs4all-ecosystem`: `python3 scripts/n4a_release_surface_matrix.py validate`
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py` -> 80 tests
- Hermetic custom-host gate:
  - `python3 scripts/n4a_e2e_scenarios.py --workspace-root /home/delete/nirs4all/nirs4all-ecosystem --artifacts-dir /tmp/n4a-e2e-rc7-custom-host-hermetic run e2e-core-ui-custom-app-host --execute`

## Remaining Hermetic Limits

- `e2e-r-dataset-io-pipeline-save` remains blocked inside the ecosystem checkout because canonical generated dataset files are ignored in `nirs4all-datasets`.
- `e2e-cluster-dag-rights-client-core` remains blocked inside the ecosystem checkout because `nirs4all-data` is not a public submodule/repo in `nirs4all-ecosystem`.
- Some runtime substeps need native `nirs4all-methods` dev-release/JS-WASM builds inside the ecosystem submodule tree. The earlier parent-workspace run covered these using the sibling build artifacts; a fully hermetic CI run should either build those artifacts first or explicitly mark those requirements as build prerequisites.
