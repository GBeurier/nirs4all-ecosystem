# Wave 6P - E2E complexity review

Date: 2026-07-06

## Scope

- Review whether the requested set of about 10 complex cross-language and multimodal E2E scenarios is actually covered.
- Keep writes limited to `tests/test_e2e_scenarios.py`, `docs/CROSS_LANGUAGE_E2E.md`, and this report.
- Do not touch private/out-of-scope repos or run broad full-parity batches.

## Result

- The manifest validates exactly `10` E2E scenarios.
- All `10` scenarios plan as ready in this checkout; no current tool/path blockers were reported by `coverage --json`.
- The scenario portfolio covers the requested surfaces: `python=10`, `javascript_wasm=7`, `web=4`, `r=3`, `native=6`, plus `rust=1` and `rust_archive=1`.
- The portfolio also covers the ecosystem repos explicitly reported by the coverage command, including `nirs4all-core=8`, `nirs4all=6`, `nirs4all-methods=5`, `nirs4all-web=4`, `dag-ml=4`, `nirs4all-datasets=4`, `nirs4all-io=3`, and `nirs4all-repository=3`.
- The suite is intentionally `hybrid=10`, not full strict ecosystem parity. Every scenario has strict Python parity, while contract/gap phases remain explicit for pending areas such as repository-owned best-refit execution, native multimodal/Web reuse, and fixture-scoped WASM surfaces.

## Changes

- Hardened `tests/test_e2e_scenarios.py` so the CLI coverage test now pins the full language distribution, not only required languages.
- Hardened the same coverage test so it also pins the repo distribution reported by `coverage --json`; this prevents nominal ecosystem coverage from silently collapsing to fewer repos.
- Updated `docs/CROSS_LANGUAGE_E2E.md` to state that the current gate is hybrid and must not be described as full strict parity until phase statuses and evidence are promoted.

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate` -> passed, `OK: 10 cross-language E2E scenarios`.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> passed, `ready_count=10`, `blocked_count=0`, `evidence_levels={"hybrid": 10}`.
- `python3 -m pytest -q tests/test_e2e_scenarios.py` -> passed, `76 passed in 2.50s`.

## Decisions and risks

- No manifest change was needed: the current scenario set already covers the requested 10 complex lanes.
- I added assertions rather than promoting any hybrid scenario to strict; the manifest's existing gaps are real and should stay visible.
- I did not run `run-ready --execute` or refresh artifact evidence, so this review verifies contract/coverage shape rather than a fresh full E2E execution batch.
