# Wave 4BE - Methods Cross-Binding E2E

Date: 2026-07-04

## Scope

Turned the methods step of
`e2e-formats-io-datasets-methods-language-bindings` into a real executable
gate.

## Files changed

- `nirs4all-methods/scripts/e2e/cross_binding_methods_parity.py`
  - Adds an ecosystem-compatible E2E entrypoint.
  - Uses the existing `benchmarks/cross_binding/orchestrator.py`; it does not
    implement numerical parity logic itself.
  - Runs a PLS smoke cell across native C++, Python tier1, R tier1, and the
    sklearn canonical reference.
  - Runs the real JS/WASM smoke with Linux Node from nvm when `node` is not in
    the non-interactive PATH.
  - Records JS/WASM artifact metadata, including SHA-256 digests and whether
    the artifacts were rebuilt from HEAD in the current environment.
  - Writes `binding-parity.json` and `predictions-by-language.json` only after
    all release-target gates pass.
  - Records Rust as `rust_archive`, not a current release target, because the
    only Rust binding is under `bindings/_archive/` and still targets the
    removed `n4m_pls_fit_simple` helper.
- `nirs4all-methods/scripts/e2e/test_cross_binding_methods_parity.py`
  - Adds a lightweight unit test for required backend validation, prediction
    digests, and parity failure handling without invoking CMake/R/Node.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Wires the methods step to the new entrypoint.
  - Replaces the PATH-level `Rscript`/`npm`/`cargo` precheck with
    `python3.11` + `cmake` + `ninja`; the methods script resolves the repo's
    conda R env and nvm Node explicitly.
  - Renames the Rust coverage in this scenario to an archive audit instead of
    claiming release-target Rust parity.

## Results

- `nirs4all-methods`: `python3.11 -m py_compile
  scripts/e2e/cross_binding_methods_parity.py
  scripts/e2e/test_cross_binding_methods_parity.py` -> passed.
- `nirs4all-methods`: `python3.11 -m pytest -q
  scripts/e2e/test_cross_binding_methods_parity.py` -> 3 passed.
- `nirs4all-methods`: `python3.11
  scripts/e2e/cross_binding_methods_parity.py --artifacts-dir
  /tmp/n4a-methods-e2e-after-unit-test --timeout 240` -> passed.
- `nirs4all-methods`: `ruff check
  scripts/e2e/cross_binding_methods_parity.py
  scripts/e2e/test_cross_binding_methods_parity.py` -> passed.
- `nirs4all-ecosystem`: `python3.11 -m pytest -q` -> 33 passed.
- `nirs4all-ecosystem`: `ruff check scripts tests` -> passed.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py
  validate` -> OK, 10 scenarios.
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py
  --artifacts-dir /tmp/n4a-ecosystem-e2e-formats-io-methods-final-after-ninja
  run e2e-formats-io-datasets-methods-language-bindings --execute` -> passed.

Observed parity from the artifact:

- `cpp`: binding parity `0.0`, reference parity `4.04e-16`.
- `python_tier1`: binding parity `0.0`, reference parity `4.04e-16`.
- `r_tier1`: binding parity `4.44e-16`, reference parity `4.03e-16`.
- `js_wasm`: coefficients/predictions/x_mean/y_mean RMSE relative all below
  `3e-16`.

## Decisions

- The gate uses `dev-release`, not stale `blas-omp`, because the local
  `blas-omp` build was behind the current ABI and missed
  `n4m_model_selection_aom_pls_select`.
- The scenario contract declares `ninja` because the `dev-release` preset
  inherits the Ninja generator through the base CMake preset.
- The JS/WASM smoke is treated as a real runtime check, but not as a HEAD
  rebuild proof in this environment when `EMSDK`/`emcc` are unavailable; the
  artifact JSON records `head_rebuild_verified=false` plus artifact hashes.
- Rust is explicitly not greened: it is recorded as archived, non-release, and
  not applicable to the current methods release gate.
- No skip/xfail was introduced.

## Review

- Claude Code review found that the scenario contract originally declared
  `cmake` but not `ninja`; fixed in the contract and this report.
- Claude Code review found there was no lightweight test for the new methods
  gate; fixed with `test_cross_binding_methods_parity.py`.
- The same review confirmed `ref_python_scikit_learn` is the canonical PLS
  reference backend and that the archived Rust wrapper targets a removed helper
  symbol.

## Risks

- This is a smoke-sized PLS gate. It proves the scenario entrypoint and
  cross-language plumbing, not the full overnight method registry sweep.
- JS/WASM still needs a separate Emscripten-enabled release gate to prove the
  distributed WASM artifact is rebuilt from HEAD.
- The full registry sweep remains a final large-batch gate.
