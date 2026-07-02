# Wave 4B - Python parity closeout

Date: 2026-07-02

## Scope

- Worktree: `/home/delete/nirs4all/_worktrees/RC-v1-nirs4all-python`
- Branch: `rc/v1-full-refactor-python`
- Lane: Python reference parity / dag-ml native parity gate
- Related security lane: `nirs4all-cluster` GitGuardian cleanup verification

## Agents

- Codex parity reviewer, read-only: audited `tests/integration/parity/**` and `nirs4all/pipeline/dagml/**`.
- Codex cluster security reviewer, read-only: audited published cluster refs and local contaminated branches.
- Codex architecture/release reviewer, read-only: audited roadmap coverage for core/python/R/WASM/UI/providers.
- Claude Code Opus, read-only: audited seeded RNG, fallback/skip gates, CLI/schema prerequisites, and ran targeted parity checks.

## Changes Integrated In Python Worktree

- Closed the remaining effective strict-xfail/skip debt in the registered parity matrix:
  - `KNOWN_DIVERGENCES` is empty.
  - `EXPECTED_FALLBACK` target remains empty.
  - coverage meter reports zero fallback, zero registry skip, zero strict xfail.
- Added native dag-ml support/coverage for separation branches:
  - `by_metadata`
  - `by_tag`
  - `by_filter`
- Added support/coverage for prematerialized `concat_transform` paths.
- Pinned RNG-sensitive parity operators:
  - `XOutlierFilter(method="mahalanobis", random_state=42)`
  - `PCA(..., random_state=42)`
  - `TruncatedSVD(..., random_state=42)`
- Added a static parity gate preventing unseeded RNG-sensitive `XOutlierFilter`, `PCA(auto|randomized)`, and `TruncatedSVD(randomized)` in registered cases.
- Declared parity runtime/test dependencies in project and requirements files:
  - `jsonschema>=4.18.0`
  - `referencing>=0.30.0`
  - `shap>=0.42.0`
- Updated compatibility ledger/docs and baselines for newly live branch/concat cases.

## Tests

Python worktree:

- `N4M_LIB_PATH=... PYTHONPATH=... rtk pytest tests/integration/parity -q -ra --tb=short`
  - Result: `886 passed`
- `N4M_LIB_PATH=... PYTHONPATH=... rtk pytest tests/integration/parity/test_conformance_dual_engine.py::test_dual_engine_conformance -q -ra --tb=short`
  - Result: `95 passed`
- `python3.11 -m tests.integration.parity._marker_audit --check`
  - Result: OK
- `python3.11 -m tests.integration.parity.coverage_meter --check`
  - Result: OK, `fallback=0`, `target=0`
- `rtk pytest tests/integration/parity/test_marker_audit.py tests/integration/parity/test_native_fallback_boundary.py tests/integration/parity/test_compatibility_ledger.py tests/integration/parity/test_rt_goldens.py -q`
  - Result: `38 passed`
- Targeted stress after RNG fixes:
  - `exclude_multi_any_y_and_x`: 10/10 repeated passes
  - `branch_dup_named_with_metamodel`: 5/5 repeated passes
- `rtk ruff check ...`
  - Result: no issues
- `rtk git diff --check`
  - Result: clean

Cluster security:

- Published refs verified clean for exact GitGuardian placeholder patterns:
  - `main` -> `911c0edd18496e74c0101e473aed1d761cf612a2`
  - `rc/v1-full-refactor` -> `7c4621b52ca742a74fc92e405c5af2197f3b42f1`
  - tag `n4a-v1-rc1-2026.07-refactor` -> `7c4621b52ca742a74fc92e405c5af2197f3b42f1`
- `rtk uv run --extra dev pytest -q --run-release-smoke`
  - Result: `143 passed, 1 skipped`

## Decisions

- Treat the current Python `nirs4all` package as the reference oracle until cutover.
- Do not ledger flaky parity as acceptable debt. Seed deterministic parity cases instead.
- Keep the one `_sample_` unseeded generator as a run-only nondeterministic contract with a seeded twin enforcing strict parity.
- Do not merge old local cluster `refactor/*` branches without audit; several remain locally contaminated with the old placeholder secret strings.
- Do not claim `nirs4all-ui` as public V1 release surface until the release matrix explicitly includes it. It is present locally and architecturally covered, but currently reads as internal reusable UI infrastructure.

## Residual Risks

- The full parity command relies on environment setup:
  - `N4M_LIB_PATH` must point at the built methods library.
  - `PYTHONPATH` must include methods, dag-ml Python, and dag-ml-data Python bindings.
  - `shap`, `jsonschema>=4.18.0`, and `referencing` must be installed.
- Several skip call sites remain as classified optional/runtime guards, but the verified full parity headline in the RC environment is `886 passed` with no effective skips or xfails.
- `_DAGML_CLI` test paths resolve via `_worktrees/dag-ml/target/release/dag-ml-cli` in this worktree layout. The binary exists here; freshness should stay part of release gate checks.
- Broader RNG hardening can be expanded later to additional estimator families, but no active registered parity case currently violates the new seed gate.
