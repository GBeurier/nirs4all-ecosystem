# WAVE 10AG - ecosystem strict submodule pins

Date: 2026-07-09

## Scope

Fix the strict E2E blocker from GitHub run `28988132331` in
`e2e-formats-io-datasets-methods-language-bindings.core-web-import-assembled-ledger`.

## Files changed

- `dag-ml` submodule pin
- `nirs4all-benchmarks` submodule pin
- `nirs4all-io` submodule pin
- `nirs4all-repository` submodule pin

## Decision

The local sibling workspace had newer, already pushed heads than the ecosystem
submodules used by GitHub Actions. The strict run failed because the GitHub
checkout used `nirs4all-io@9de9b42`, which predates the
`web_core_fixture` ledger payload required by the Core/Web import evidence.

The fix advances the stale non-prod submodule pins to the selected sibling
heads. Python `nirs4all` and `nirs4all-studio` remain untouched.

## Validation

- `nirs4all-io` submodule ledger generation:
  `python3.11 scripts/n4a_e2e_scenarios.py --workspace-root /home/delete/nirs4all/nirs4all-ecosystem --artifacts-dir /tmp/n4a-e2e-submodule-pins-fix run e2e-formats-io-datasets-methods-language-bindings --execute`
  reached the expected local methods-WASM artifact prerequisite after the IO
  test passed and produced `web_core_fixture` for both reference datasets.
- `nirs4all-core` Core/Web consumer against that ledger:
  `NIRS4ALL_METHODS_JS_DIST=/home/delete/nirs4all/nirs4all-methods/bindings/js/dist LD_LIBRARY_PATH=/home/delete/nirs4all/nirs4all-ecosystem/nirs4all-methods/build/dev-release/cpp/src:${LD_LIBRARY_PATH:-} PYTHONDONTWRITEBYTECODE=1 python3.11 nirs4all-core/scripts/e2e/run_formats_io_core_web_import.py --artifacts-dir /tmp/n4a-e2e-submodule-pins-fix/formats-io-methods`
  -> passed for `io_single_source_split` and `io_multi_source`, all comparison
  deltas `0.0`.

## Risks

- The full GitHub strict run still needs to be relaunched after this repin.
- The release lock is intentionally not regenerated from the live workspace in
  this step because some published lock members are ahead of local siblings;
  lock refresh belongs to the publication batch with a coherent selected
  workspace.
