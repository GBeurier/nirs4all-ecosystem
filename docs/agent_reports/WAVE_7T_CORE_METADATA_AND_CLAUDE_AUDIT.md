# Wave 7T - Core Metadata And Claude Architecture Audit

Date: 2026-07-07

## Scope

Closed the read-only Claude Code audit that was launched in Wave 7S, integrated the one safe `nirs4all-core` metadata fix it identified, and kept `nirs4all-ui` / `nirs4all-quality` untouched because another agent is actively working there.

## Agents / Reviews

- Codex main lane: reviewed the Claude findings, applied the minimal core metadata patch, ran core V1 surface gates, committed and pushed.
- Claude Code read-only audit (`opus`, effort `max`): inspected core/methods/providers/cross-repo naming and packaging. It used read-only tools only and did not modify files.

## Repos / Files Changed

- `nirs4all-core`
  - `CHANGELOG.md`
  - `README.md`
  - `bindings/python/pyproject.toml`
  - `bindings/python/src/nirs4all_lite/_topology.py`
  - `bindings/r/LICENSE`
  - Commit pushed: `e29ee1b` (`chore(release): align core license metadata`).

No files were modified in `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, or `nirs4all-lab`.

## Validation

- `nirs4all-core`
  - `PYTHONPATH=bindings/python/src python3.11 -m unittest -v bindings/python/tests/test_release_topology.py bindings/python/tests/test_facade.py bindings/python/tests/test_pipeline_contract.py bindings/python/tests/test_upstreams.py bindings/python/tests/test_cross_language_surface.py bindings/python/tests/test_capability_matrix.py` -> 59 passed.
  - `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH make test-v1-surfaces` -> Rust/Python/WASM passed.
  - Rust: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace` -> 9 passed.
  - WASM: Node test suite -> 15 passed, 0 skipped; TypeScript typecheck passed.
  - R and Octave gates reported `SKIP/RISK` because R/Rscript and Octave are not installed in this WSL environment.

## Integrated Fix

- Normalized the Python package SPDX expression to `CECILL-2.1 OR AGPL-3.0-or-later`.
- Aligned the release topology manifest pointer with `bindings/python/pyproject.toml`.
- Aligned the R package local `LICENSE` SPDX line and README license prose.
- Removed stale ignored local artifacts `bindings/python/dist/nirs4all_core-0.2.4*` from the workspace; they were not tracked.

## Claude Audit Findings

High-signal findings to keep on the board:

- `nirs4all-core` is already the canonical portable aggregate repo. Rust, npm/WASM, R, and MATLAB/Octave core surfaces publish/import as `nirs4all`; Python intentionally remains distribution `nirs4all-core` with `nirs4all_lite`, `nirs4all_core`, and `n4a` imports until the full Python production cutover.
- Core still needs external registry provisioning before full publication: PyPI Trusted Publisher for `nirs4all-core`, crates.io ownership for `nirs4all`, and npm ownership for `nirs4all`.
- `nirs4all-methods` still has naming gaps: MATLAB full binding is exposed as `+pls4all` only, and JS still uses `@nirs4all/methods-wasm` plus `Pls4allError` / `pls4all_wasm` naming. Python/R methods surfaces are much stronger and more idiomatic.
- `nirs4all-providers` has clean dependency direction and real code, but only `datasets` and `repository` are justified by neutral contracts. `benchmarks` and `papers` are over-scoped Python convenience facets unless reduced to zero-logic public-facade passthroughs or moved back to their owning repos.
- `nirs4all-core` exposes a fixed portable pipeline facade across bindings; a broad idiomatic operator library remains future/gated, especially for JS.

## Decisions / Risks

- Full Python parity was not rerun in this wave; per maintainer instruction it remains reserved for a larger batch.
- The R/Octave skips are environment/toolchain gaps in this WSL session, not accepted parity waivers.
- `nirs4all-ui` asset/style consolidation remains pending and intentionally untouched in this wave due concurrent `nirs4all-quality` work.
