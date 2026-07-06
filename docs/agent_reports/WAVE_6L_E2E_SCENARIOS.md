# Wave 6L - E2E scenarios

Date: 2026-07-06

## Scope

- Verify that `nirs4all-ecosystem` still carries about 10 complex cross-language E2E scenarios/specs for the V1 refactor release gate.
- Keep edits limited to the owned scenario test file and this report.
- Do not run long suites, full parity batches, or broad integration jobs.

## Findings

- The manifest validates cleanly and still declares exactly `10` cross-language scenarios.
- Coverage breadth is real, not nominal:
  - required languages: `python=10`, `javascript_wasm=7`, `web=4`, `r=3`
  - requested tags: `pipeline=10`, `workspace_save=6`, `predictions=5`, `datasets=5`, `io=4`, `web_results=4`, `repository=3`, `pipeline_generation=2`, `papers=1`, `multimodal=1`, `multisource=1`
- The current test file was already strong; it was not a shallow smoke-only placeholder.
- What was missing was an explicit aggregate guard that the suite still spans the intended scenario families, plus a direct complexity guard on each scenario shape.

## Test hardening

- Added a portfolio-level test that requires distinct scenarios for:
  - R/Python dataset+IO save/reopen
  - papers+repository refit handoff
  - WASM/Web repository prediction reuse
  - converted save -> Web predictions
  - multimodal Python/R/WASM roundtrip
  - multisource/native pipeline-generation replay
  - formats/io/datasets/methods language bindings
- Added a per-scenario complexity test requiring each scenario to keep:
  - at least `2` declared languages
  - at least `2` declared repos
  - at least `2` distinct step kinds
  - at least `3` produced artifacts
- Tightened the CLI coverage JSON assertions to pin the exact current language/tag distribution instead of only checking that counts are non-zero.

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate` -> passed, `OK: 10 cross-language E2E scenarios`
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> passed, `ready_count=10`, `blocked_count=0`
- `python3 -m pytest -q tests/test_e2e_scenarios.py` -> passed, `76 passed`

## Decisions and risks

- No manifest or runtime helper changes were needed; the contract itself already reflects the intended 10-scenario release gate.
- I did not launch `run-ready --execute`, full parity, browser suites outside the owned test file, or long cross-repo execution batches.
- The suite still correctly describes hybrid coverage rather than claiming full strict ecosystem parity: `evidence_levels={"hybrid": 10}` remains accurate.
