# WAVE 9I - Core 0.3.2 release lock

## Scope

- Lane A: publish and lock the selected `nirs4all-core` head after multisource vector parity promotion.
- Repositories: `nirs4all-core`, `nirs4all-ecosystem`.

## Files modified

- `nirs4all-core`: version manifests bumped from `0.3.1` to `0.3.2`.
- `nirs4all-ecosystem/docs/contracts/release/aggregation-manifest.n4a.json`
- `nirs4all-ecosystem/docs/contracts/release/aggregation-lock.n4a.lock.json`

## Tests run

- `scripts/bump_version.sh --check`
- `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests`
- `cargo test --workspace`
- `cargo package -p nirs4all --allow-dirty`
- `python3.11 -m build bindings/python --outdir /tmp/n4a-core-py-dist-0.3.2`
- `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-v032 validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`

## Published / verified

- Git tag: `nirs4all-core` `v0.3.2`
- PyPI: `nirs4all-core==0.3.2`
- npm: `nirs4all@0.3.2`
- crates.io: `nirs4all 0.3.2`
- GitHub Release assets: source archives, SBOM, `SHA256SUMS`, `nirs4all_0.3.2.tar.gz`, `nirs4all-matlab-octave-0.3.2.zip`

## Decisions

- Kept Python distribution named `nirs4all-core` because the full Python `nirs4all` package remains the production oracle/project.
- Kept Rust, npm/WASM, R, and MATLAB/Octave publications named/imported as `nirs4all`.
- Did not add any legacy alias.

## Risks

- Local WSL lacks Linux `node`, `R`, and `octave`; npm/R/MATLAB validation was covered by the successful GitHub release workflows.
- R-universe still reported `nirs4all 0.3.1` immediately after release; it is expected to rebuild asynchronously from Git.
