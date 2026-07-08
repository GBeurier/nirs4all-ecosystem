# WAVE 10A - Provider Repository R Parity

Date: 2026-07-08

## Summary

Promoted `e2e-dataset-provider-repository-roundtrip` from hybrid to strict by requiring the provider-materialized repository descriptor to execute through `nirs4all-core` Python, R, and JavaScript/WASM surfaces with pairwise numeric parity.

## Files Modified

- `nirs4all-core`
  - `scripts/e2e/consume_repository_descriptor.py`
  - `tests/test_consume_repository_descriptor.py`
  - version manifests bumped to `0.3.5` across Rust, Python, R, and npm/WASM.
- `nirs4all-ecosystem`
  - `docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - `docs/CROSS_LANGUAGE_E2E.md`
  - `tests/test_e2e_scenarios.py`
  - `docs/contracts/release/aggregation-manifest.n4a.json`
  - `docs/contracts/release/aggregation-lock.n4a.lock.json`
  - `nirs4all-core` submodule pinned to `0a7c507` / `v0.3.5`.

## Tests Run

- Core:
  - `scripts/bump_version.sh --check`
  - `PYTHONPATH=. python3.11 -m unittest discover -s tests -p 'test_consume_repository_descriptor.py' -v`
  - `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests -q`
  - `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm --prefix bindings/wasm test`
  - `cargo test -p nirs4all`
  - real provider/repository scenario through Python/R/WASM with `prediction_abs_max <= 4.89e-15`.
- Ecosystem:
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 scripts/n4a_e2e_scenarios.py coverage --json`
  - `python3.11 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - `python3.11 scripts/n4a_release_surface_matrix.py --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json validate`
  - `python3.11 -m pytest tests/test_release_lock.py tests/test_gitmodules_topology.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py -q`

## Review Notes

- Claude e2e audit confirmed the suite still distinguishes declared orchestration from real execution; this lane closes one concrete hybrid gap but does not make every scenario executable in default CI.
- Claude Studio RC audit found Windows RC local builds depend on a built sibling `../nirs4all-ui/dist`; release workflow/docs still need hardening before relying on workflow-dispatch installers.

## Decisions

- Core was released as `v0.3.5` because ecosystem now depends on new core e2e behavior; keeping the lock on `v0.3.4` would overclaim strict R coverage.
- The provider/repository parity check keeps one contract metadata check for descriptor loader normalization, and adds two strict numeric checks for R and Python/R/WASM execution.

## Risks

- `Rscript` and Node paths remain explicit in the e2e manifest command for the local RC environment.
- Remaining e2e debt is five strictness gaps and two V1 contract phases outside this lane.
