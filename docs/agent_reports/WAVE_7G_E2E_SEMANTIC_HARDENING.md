# Wave 7G - E2E Semantic Hardening

Date: 2026-07-06

## Scope

Hardened the cross-language E2E manifest and validator so the V1 refactor board no longer overclaims parity where evidence is proxy-only or repository delegation is implicit.

## Files Modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Decisions

- `e2e-python-reopen-paper-repository-refit` now treats `repository_forced_best_refit` as strict only because the scenario documents the repository subprocess/API calls and artifact evidence.
- Repository scenarios must expose either an actual `nirs4all-repository` step or a structured `delegated_invocations` record with calls, evidence, and produced artifacts.
- R scenarios must declare an `Rscript`-gated step and the gated command must invoke or probe `Rscript`.
- Strict parity checks reject proxy-only, schema-only, array-presence, smoke-only, and fixture-scoped evidence.
- `e2e-multimodal-python-r-wasm-roundtrip` is deliberately contract-level for `python_parity` and no longer carries the `parity` tag until source-aware multimodal runtime parity is implemented.
- `e2e-wasm-open-repo-pipeline-alt-dataset` keeps `parity` because it has strict numeric/display parity checks.

## Agent Review

- Codex Gibbs reviewed and implemented the repository delegation/forced-refit lane.
- Codex Darwin reviewed and implemented the R/native/multimodal semantic lane.
- Claude Code read-only review was launched after local green gates; any follow-up findings should be tracked as a later report if they arrive after this commit.

## Validation

- `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> 11 ready, 0 blocked, 10 parity-tagged scenarios, multimodal contract-only.
- `python3 -m pytest tests/test_e2e_scenarios.py -q` -> 85 passed.
- `git diff --check` -> OK.

## Risks

- These are manifest/contract gates, not a full runtime execution of every cross-language scenario.
- Full Python-reference parity remains intentionally deferred until the next large batch because it is slow.
- The multimodal scenario still uses dense-fused feature representation evidence and must remain contract-level until source-aware multimodal parity exists.
