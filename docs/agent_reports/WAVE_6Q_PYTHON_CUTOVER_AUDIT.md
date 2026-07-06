# Wave 6Q - Python Cutover Audit

Date: 2026-07-06

## Scope

- Repo: `nirs4all`
- Mode: read-only audit
- Main checkout: `refactor/L17-pyref` at `8f8b2b57`
- RC worktree: `rc/v1-full-refactor-python` at `bf242e48`

## Findings

The main `nirs4all` checkout is not cutover-ready. It remains in the legacy-default posture while
the RC worktree carries the stricter dag-ml cutover posture.

- `nirs4all/pipeline/engine.py` still sets `DEFAULT_ENGINE = "legacy"` in the main checkout.
- `nirs4all/api/run.py` still falls back transparently from dag-ml errors to legacy execution in
  the main checkout.
- `docs/compatibility.json` in the main checkout reports:
  - `fallback = 11`
  - `xfail_strict = 9`
  - `skip = 3`
  - `expected_fallback_target = 0`
- The RC worktree reports:
  - `fallback = 0`
  - `xfail_strict = 0`
  - `skip = 0`
- Marker-audit and coverage-meter guardrails present in the RC worktree are absent from the main
  checkout.

## Commands Run By The Agent

- `.venv/bin/pytest -p no:cacheprovider tests/unit/pipeline/test_engine_selector.py tests/integration/parity/test_compatibility_ledger.py -q`
  - Passed: 9 tests
- `.venv/bin/pytest -p no:cacheprovider tests/integration/parity/test_generators_conformance_extra.py::test_or_count_uses_local_seed tests/integration/parity/test_generators_conformance_extra.py::test_or_weighted_count_uses_local_seed -q`
  - Passed: 2 tests
- `.venv/bin/pytest -p no:cacheprovider --collect-only -q tests/integration/parity/test_conformance_dual_engine.py`
  - Collected: 187 tests

## Decision

Do not publish or promote the main `nirs4all` checkout as the cutover release. Either keep Python
explicitly held back, as requested, or promote/audit the selected RC head before any production
switch. Do not run full parity again until the selected Python head is fixed or chosen.

## Next Checks Before Full Parity

- `tests/integration/parity/test_conformance_dual_engine.py::test_native_fallback_boundary`
- Selected `test_dual_engine_conformance` cases for branch/concat/generator parity
- `tests/integration/parity/test_parity_compiles.py`
- `tests/integration/parity/test_parity_smoke.py`
