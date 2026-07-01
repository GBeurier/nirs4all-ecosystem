# Wave 3H - Core Runtime Methods SNV Parity

Date: 2026-07-01

## Scope

Focused W3H slice on `nirs4all` Python integration worktree:

- Add a short parity gate for the dag-ml node runner when the upstream
  `StandardNormalVariate` transform is routed through the opt-in
  `nirs4all-methods` SNV binding.
- Do not run full Python-reference parity in this batch; it remains reserved
  for larger integration batches.
- Keep current roadmap topology: public `nirs4all` V1 includes Python, R, and
  browser/WASM surfaces. The roadmap already states that `nirs4all done` cannot
  mean Python-only, and the release gates keep R/WASM in scope.

## Modified files

`_worktrees/INT-nirs4all`:

- `tests/integration/parity/test_dagml_node_runner.py`
  - Added `_require_methods_snv_available()`, which gates only on the SNV
    binding plus `n4m` ABI/library availability, not on `MethodsPLS`.
  - Added
    `test_fit_cv_methods_snv_opt_in_matches_python_oracle`, which sets
    `N4A_DAGML_METHODS_SNV=1`, runs one dag-ml `FIT_CV` node over
    `StandardNormalVariate -> PLSRegression`, asserts that `run_node` routed the
    upstream transform to `nirs4all.operators.methods.n4m_ops.MethodsSNV`, and
    compares predictions against the Python-reference
    `make_pipeline(StandardNormalVariate(), PLSRegression())` oracle.

`nirs4all-ecosystem`:

- `docs/agent_reports/WAVE_3H_CORE_RUNTIME_METHODS_SNV_PARITY.md`

## Agents and review

- Dewey: read-only audit of `_worktrees/INT-nirs4all`; recommended the targeted
  SNV native-route parity test.
- Hubble: first review; no-go until the test proved the native route was
  actually exercised and until the guard stopped depending on `MethodsPLS`.
- Peirce: second review after fixes; go, no blocking findings.
- Kepler: release pin policy audit; confirmed release-lock remote reachability
  remains blocked for 6/7 pins.

## Tests run

From `_worktrees/INT-nirs4all`:

- `pytest tests/unit/pipeline/test_dagml_operator_routing.py -q`
  - PASS: 4 passed.
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/INT-dmd/crates/dag-ml-data-py/python pytest tests/integration/parity/test_dagml_node_runner.py -q`
  - PASS: 5 passed, 1 skipped.
  - Skip is the new strict native-SNV test because `n4m` is not importable in
    this local session.
- `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/INT-dmd/crates/dag-ml-data-py/python NIRS4ALL_REQUIRE_N4M=1 pytest tests/integration/parity/test_dagml_node_runner.py -k methods_snv -q`
  - Expected FAIL: `n4m` missing. This verifies the test does not skip when
    native methods parity is explicitly required.
- `ruff check tests/integration/parity/test_dagml_node_runner.py`
  - PASS.
- `python3 -m py_compile tests/integration/parity/test_dagml_node_runner.py`
  - PASS.
- `python3 -m mypy tests/integration/parity/test_dagml_node_runner.py --follow-imports=skip`
  - PASS.
- `git diff --check`
  - PASS.

## Decisions

- The new test is intentionally integration-level and not mocked: it exercises
  `run_node` and records the actual operator routed inside the model node's
  upstream chain.
- The guard is aligned to this test's real dependency: SNV binding plus ABI/lib,
  because PLS remains the sklearn `PLSRegression` oracle/model in this slice.
- Full parity was not run, per batch policy and user instruction.
- No release refs were pushed. Kepler recommends protected
  `release/2026.07-refactor` branches for the six non-fetchable lock pins, but
  that requires an explicit release decision.

## Risks / remaining

- Local environment does not import `n4m`, so the new native-route parity test
  is structurally validated here but will only execute numerically in an env
  with the `nirs4all-methods` Python binding installed.
- Release-lock CI remains blocked until the locked commits are made
  remote-fetchable. Do not solve this by pushing `main`; do not tag without a
  coordinated lock regeneration.
