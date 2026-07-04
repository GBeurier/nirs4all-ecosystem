# WAVE 4BH - R ABI and E2E contract hardening

Date: 2026-07-04

## Scope

- Fixed stale R binding risk across `nirs4all-methods` and `nirs4all-core`.
- Hardened the `nirs4all-ecosystem` cross-language E2E manifest so declared
  scenario artifacts must be produced by at least one step.
- Kept full parity deferred; only targeted R/core parity and runner contract
  tests were executed.

## Integrated commits

- `nirs4all-methods`: `f1eae4229917ca10da675ea081f887b4749ddacb`
  - `test(r): isolate methods parity package installs`
- `nirs4all-core`: `fe6c4243eca7945a493de45de12ac3350c38520f`
  - `test(r): pin strict parity to fresh methods install`

## Files changed

### nirs4all-methods

- `bindings/r/n4m/configure`
- `bindings/r/pls4all/configure`
- `scripts/e2e/cross_binding_methods_parity.py`
- `scripts/e2e/test_cross_binding_methods_parity.py`

### nirs4all-core

- `.github/workflows/ci.yml`
- `Makefile`
- `bindings/r/tests/parity.R`
- `compat/upstreams.toml`

### nirs4all-ecosystem

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Tests run

- `nirs4all-methods`
  - `python3.11 -m pytest -q scripts/e2e/test_cross_binding_methods_parity.py`
  - `python3.11 -m py_compile scripts/e2e/cross_binding_methods_parity.py`
  - `python3.11 -m ruff check scripts/e2e/cross_binding_methods_parity.py scripts/e2e/test_cross_binding_methods_parity.py`
  - R preflight install of `pls4all` into a temporary library: version `1.0.1`, ABI `2.0.0`
- `nirs4all-core`
  - `PATH=/home/delete/miniconda3/envs/pls4all_r/bin:$PATH make test-r-parity`
  - `PYTHONPATH=bindings/python/src python3.11 -m unittest -v bindings/python/tests/test_upstreams.py`
  - `Rscript --vanilla -e 'parse("bindings/r/tests/parity.R")'`
  - workflow YAML parse for `.github/workflows/ci.yml`
- `nirs4all-ecosystem`
  - `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 scripts/n4a_e2e_scenarios.py plan --json`
  - `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`

## Decisions

- Strict R parity must install `n4m` from the pinned `nirs4all-methods` checkout
  and verify ABI major `>= 2`.
- R package installs in parity gates now use `--preclean` so stale native object
  files cannot satisfy a build.
- `nirs4all-core` CI now reads the Methods pin from `compat/upstreams.toml`
  instead of using an older hard-coded SHA.
- E2E scenario-level `artifacts` are now contract-checked against step
  `produces`.

## Agent review notes

- The R failure was caused by stale global R packages and stale native objects,
  not missing source functions.
- `nirs4all-ui` exists and has a Pages showcase, but Web/Studio component
  sharing remains partial; Web consumes only a narrow shared surface today.
- The E2E manifest still contains 8 blocked scenarios and 2 ready scenarios;
  several blocked scenarios are contractual placeholders until their entrypoints
  are implemented.

## Risks

- Full ecosystem parity was intentionally not rerun in this batch.
- `e2e-dataset-provider-repository-roundtrip` and
  `e2e-formats-io-datasets-methods-language-bindings` are runnable but still too
  narrow for final release confidence: they do not yet prove full pipeline
  execution across all target languages.
- Web/WASM scenarios still need to be rebased onto the existing `.mjs` smokes or
  new real harnesses, not non-existent `tests/e2e/*.spec.ts` files.
