# Wave 6A - E2E artifact evidence gate

Date: 2026-07-04

## Scope

- `nirs4all-ecosystem`: add a post-run artifact evidence gate for the 10 cross-language E2E scenarios.
- Coordination goal constraints: keep the root `AGENTS.md` rules active for the V1 refactor, including no `nirs4all-drafts`/`nirs4all-lab`, Claude Code only with explicit `allowedTools`, and no artificial green from skips/xfails/fallback evidence.

## Changes

- Added `python3 scripts/n4a_e2e_scenarios.py evidence`.
- The new gate verifies every declared scenario/step artifact exists, is non-empty, and JSON evidence does not declare blocked, skipped, xfailed, not-run, hold, failed, or false success fields.
- The existing `run`/`run-ready --execute` path now shares the same structural/semantic artifact validation and still adds freshness checks during execution.

## Execution Evidence

- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir .n4a-e2e-artifacts/wave5y evidence`
- Result: `10/10` scenarios verified, `43` expected artifacts, `0` failures.

Verified scenario families:

- R dataset/IO/pipeline save.
- Python reopen/papers/repository/Web handoff.
- WASM repository pipeline on alternative dataset.
- Multimodal Python/R/WASM roundtrip.
- Multisource branching/stacking replay.
- Legacy converter/predictions/Web results.
- Dataset provider/repository roundtrip.
- Pipeline generation/performance comparison.
- Cluster DAG rights/client/core.
- Formats/IO/datasets/methods language bindings.

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate` passed.
- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir .n4a-e2e-artifacts/wave5y coverage` passed.
- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir .n4a-e2e-artifacts/wave5y evidence` passed.
- `python3 -m pytest -q tests/test_e2e_scenarios.py` passed, `49` tests.
- `python3 -m pytest -q` passed, `73` tests.
- `git diff --check` passed.

## Risks

- This gate proves the local `wave5y` batch produced complete declared artifacts; it does not replace the slower full historical parity suite.
- Several V1 refactor phases remain explicit contract/gap coverage rather than strict runtime coverage, especially repository forced best-refit and papers export outside the Python-focused scenario.
