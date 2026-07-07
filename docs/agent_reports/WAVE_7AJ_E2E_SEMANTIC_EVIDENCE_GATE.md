# WAVE 7AJ - E2E semantic evidence gate

Date: 2026-07-07

Scope:
- `nirs4all-ecosystem` only.
- `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, and `nirs4all-lab` untouched.

Modified files:
- `.github/workflows/cross-language-e2e.yml`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

Changes:
- Hardened JSON artifact evidence validation: non-finite numeric values, negative deltas/tolerances, non-positive row/count evidence, false boolean evidence, and delta values exceeding their declared tolerance now fail artifact verification.
- Added `evidence --ready-only` so CI can verify artifacts produced by currently executable scenarios without failing on intentionally blocked public-checkout data scenarios.
- Added post-execution artifact verification to the cross-language E2E workflow for both `run-ready --execute` and selected scenario execution.
- Added regression tests for semantic artifact failures, `--ready-only`, workflow wiring, and selected scenario evidence freshness.

Review:
- Read-only subagent audit confirmed the main gap: the suite had 11 ready hybrid scenarios and 48 verified artifacts, but the CI path did not relaunch `evidence` after execution and JSON evidence accepted weak `{"status": "passed"}` payloads too broadly.
- Claude Opus read-only review found two correctness issues before commit: signed `*_delta` fields were accidentally rejected through generic non-negative fragments, and `evidence --ready-only` could have passed with an empty ready set. Both were fixed and covered by regression tests.
- Integrated the low-risk hardening now; broader manifest refactors such as artifact-bound parity checks, mandatory tolerance sidecars for every delta, and runtime-pair edges remain explicit debt.

Tests run:
- `python3 -m pytest -q tests/test_e2e_scenarios.py` -> 101 passed.
- `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios.
- `python3 scripts/n4a_e2e_scenarios.py coverage` -> 11/11 ready, debt remains explicit.
- `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --json` -> 11/11 verified, 48 artifacts.
- `git diff --check` -> clean.

Known risks / debt:
- The suite is still `hybrid`, not fully strict: `strictness_gaps=12`, `v1_contract_phases=13`, `v1_gap_phases=31`.
- `e2e-multimodal-python-r-wasm-roundtrip` still has no strict parity check.
- Non-JSON artifacts are still structural checks only: PNG/ZIP/Parquet validity, not full semantic sidecar validation.
- Some current artifacts expose `max_abs_delta` without a sibling tolerance in the same object; mandatory tolerance pairing is deferred until producers are normalized.
- Full Python-reference parity was not relaunched in this batch because it is intentionally reserved for larger integration batches.
