# Wave 3AC - Methods JS/WASM Parity Boundary

Date: 2026-07-01

## Scope

Lane F tranche focused on `nirs4all-methods`: codify the current cross-binding parity boundary for JS/WASM. The Python-driven `ci_parity_gate.py` harness remains Python/R/Octave only; JS/WASM is explicitly covered by the workflow `js-wasm` npm smoke/parity job until a dedicated `bench_js.*` driver exists. No full registry parity sweep was run.

## Commit

- `nirs4all-methods` `98148c14` - `test(methods): document js wasm parity boundary`

## Files Modified

`nirs4all-methods`:

- `.github/workflows/cross-binding-parity.yml`
- `benchmarks/cross_binding/ci_parity_gate.py`
- `benchmarks/cross_binding/tests/test_ci_parity_gate.py`

`nirs4all-ecosystem`:

- `docs/contracts/release/aggregation-lock.n4a.lock.json`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Linnaeus the 2nd | Lane F read-only implementation audit | done | Recommended the minimal contract patch: wording in `ci_parity_gate.py`, stale `p4a.{js,wasm}` workflow comments, and a static test around the JS/WASM boundary. |
| Herschel the 2nd | W3AC review | go | Confirmed wording and CLI/render compatibility; no numerical parity behavior changed. |

## Decisions

- Kept JS/WASM out of `BINDINGS` for now because the harness has no `scripts/bench_js.*` driver.
- Renamed the rendered unwired entry to `js-wasm` so it matches the real workflow job name.
- Added a static test proving JS/WASM is intentionally outside this harness and that the rendered note points to `cross-binding-parity.yml::js-wasm`.
- Corrected stale workflow comments from `p4a.{js,wasm}` to `n4m.{js,wasm}`.
- Refreshed the aggregation lock methods member from `0f328018348b` to `98148c14bbe5`; no other member, version, artifact digest, lockstep attestation, manifest digest, or public-surface matrix change was accepted.

## Tests Run

`nirs4all-methods`:

- `python3 -m pytest benchmarks/cross_binding/tests/test_ci_parity_gate.py -q -p no:cacheprovider` -> 12 passed.
- `python3 -m py_compile benchmarks/cross_binding/ci_parity_gate.py benchmarks/cross_binding/tests/test_ci_parity_gate.py` -> passed.
- `python3 -m ruff check benchmarks/cross_binding/ci_parity_gate.py benchmarks/cross_binding/tests/test_ci_parity_gate.py` -> passed.
- `git diff --check` -> passed.
- Targeted `rg` for stale `p4a.{js,wasm}` / `p4a.js` / `p4a.wasm` in `.github`, `bindings/js`, and the touched harness files -> no remaining matches.

`nirs4all-ecosystem`:

- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-ws validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py report` -> passed; methods member now reports `98148c14bbe5`.
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py -q -p no:cacheprovider` -> 11 passed.

Reviewer also ran:

- `python3 benchmarks/cross_binding/ci_parity_gate.py --help` -> passed.
- Read-only diff/status checks -> GO.

## Risks / Follow-Ups

- `nirs4all-methods` remains `ahead` locally and `behind origin/main` by the pre-existing SEO metadata commit. No remote merge/fetch/push was performed.
- Strict remote fetchability remains red until the selected local commits are pushed or replaced by fetchable immutable refs; `98148c14` is a local methods pin.
- Full methods binding parity, ABI release gates on built libraries, and cross-binding registry sweeps remain deferred to a larger batch.
