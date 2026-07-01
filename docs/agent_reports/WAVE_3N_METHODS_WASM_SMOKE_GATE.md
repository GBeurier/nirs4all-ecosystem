# Wave 3N - Methods WASM Broad-Model Smoke Gate

Date: 2026-07-01

## Scope

Lane F tranche focused on `nirs4all-methods` JS/WASM binding test wiring. No numerical kernel changes, no ABI changes, and no full registry parity run.

## Commit

- `nirs4all-methods` `0f328018` - `test(wasm): include broad model smoke in npm gate`

## Files Modified

`nirs4all-methods`:

- `bindings/js/package.json`
- `bindings/js/README.md`
- `docs/dev/release_process.md`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Mencius | Read-only Lane F methods binding audit | done | Recommended wiring existing `bindings/js/test/run_new_pack.mjs` into `npm test`; noted this remains smoke coverage, not full parity. |
| Pasteur | Initial review of W3N diff | NO-GO | Blocked a README command block that mixed repo-root and `bindings/js` working directories. |
| Confucius | Follow-up review after README fix | GO | Confirmed `npm test` includes `run_new_pack.mjs`, README flow is runnable, and release docs describe the full JS/WASM smoke suite. |

## Decisions

- Add the already-existing `test/run_new_pack.mjs` broad-model-pack smoke to the JS/WASM package `npm test` script.
- Keep numerics inside `nirs4all-methods`; do not duplicate or reimplement methods elsewhere.
- Update docs to describe `npm test` as the JS/WASM smoke suite, covering PLS parity, API/generic method path, POP/AOM helpers, and broad-model-pack smoke.
- Fix the README smoke-test block to run from `bindings/js` consistently.
- Do not present `run_new_pack.mjs` as full parity. It gates finite outputs, correlation thresholds, and splitter mask sanity for `ECR`, `O2PLS`, AOM Ridge/Stack, DataTwinning, and SystematicCircular.

## Tests Run

`nirs4all-methods/bindings/js`:

- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm test` -> passed.
  - Executes `run_smoke.mjs`, `run_api.mjs`, `run_generic_method.mjs`, `run_pop_aom.mjs`, and `run_new_pack.mjs`.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node examples/consume.mjs` -> passed.

`nirs4all-methods`:

- `python3 -m json.tool bindings/js/package.json` -> passed.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- `run_new_pack.mjs` is a deterministic smoke/correlation gate, not a strict numerical parity suite for the broad-model-pack methods.
- Full methods binding parity, ABI gates, and cross-binding registry sweeps remain deferred to larger batches.
- The repo remains ahead of origin and behind one remote commit from the pre-existing state; no remote merge/push was performed.
