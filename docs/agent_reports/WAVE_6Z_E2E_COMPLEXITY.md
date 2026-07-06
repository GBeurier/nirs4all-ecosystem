# Wave 6Z E2E Complexity Report

Date: 2026-07-06

## Scope

Owned paths only:

- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/agent_reports/WAVE_6Z_E2E_COMPLEXITY.md`

No submodules, lock files, private draft/lab repos, or root token files were touched.

## Audit

The current cross-language E2E manifest validates 10 scenarios and all 10 plan as
ready in this checkout. Coverage is broad enough for the V1 refactor objective:

- Python appears in all 10 scenarios as the portable oracle runtime.
- R appears in 3 scenarios, JavaScript/WASM in 7, Web in 4, native in 6.
- `nirs4all-core` appears in 8 scenarios, `nirs4all-ui` in 2, and
  `nirs4all-web` in 4.
- Required tags are present for datasets/io, repository, papers,
  workspace-save, predictions, multimodal, multisource, pipeline generation, and
  web results.
- Every scenario is hybrid and has at least one strict parity check.

The coverage gap was not a missing scenario in the current manifest. The gap was
that the validator still allowed future regressions toward shallow smoke claims:
two-step scenarios with weak orchestration shape, missing Python oracle runtime,
or loss of the `nirs4all-core` + `nirs4all-ui` + `nirs4all-web` custom app path.

## Patch

The runner now enforces complexity directly:

- every scenario must include Python, at least two runtime/language surfaces, at
  least two repos, at least two step kinds, and at least three unique produced
  artifacts;
- JavaScript/WASM scenarios must be backed by `nirs4all-core` or
  `nirs4all-web`;
- the suite must keep concrete workflow surfaces for core/ui/web custom apps,
  R/Python/WASM roundtrip, datasets/io/repository, papers/repository saves,
  multimodal, multisource, and multi-language methods bindings.

Tests now include negative regressions for missing Python oracle coverage, flat
single-kind orchestration, too few produced artifacts, and removal of the
core/ui/web custom app surface.

## Validation

- `python3 scripts/n4a_e2e_scenarios.py validate`: PASS
- `python3 scripts/n4a_e2e_scenarios.py coverage --json`: PASS, 10/10 ready
- `python3 -m py_compile scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`: PASS
- `pytest -q tests/test_e2e_scenarios.py`: PASS, 78 passed
- `git diff --check -- scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py docs/CROSS_LANGUAGE_E2E.md docs/agent_reports/WAVE_6Z_E2E_COMPLEXITY.md`: PASS

## Residual Risk

No full parity or long runtime execution was launched. Several V1 phase statuses
remain intentionally `contract` or `gap`, especially repository-owned best-refit,
papers outside the dedicated scenario, and some Web/WASM reuse paths. The patch
prevents complexity regressions in the contract; it does not promote those phases
to strict evidence.
