# Wave 4DE - Repository/Papers E2E Contract

Date: 2026-07-04

## Scope

- Strengthened the 10 cross-language E2E scenarios with an explicit V1 refactor contract matrix.
- Covered six required phases for every scenario: Python open, Python rerun, Python parity, papers export, repository forced best-refit handoff, and WASM/Web reuse.
- Kept non-existent runtime claims honest: missing or descriptor-only paths are encoded as `gap` or `contract` entries with acceptance criteria.

## Decisions

- `strict` means the scenario currently executes and validates that phase.
- `contract` means a descriptor, handoff, fixture, or partial runtime contract exists, but the matrix also records any remaining gap.
- `gap` means no runtime/entrypoint exists in that scenario today, and the acceptance entry is the testable requirement to close it.
- `e2e-python-reopen-paper-repository-refit` now owns the suite-level papers export and repository forced best-refit contract. The repository phase remains descriptor-only because `nirs4all-repository` has no independent runtime in this gate; the contract requires `force_best_refit=true` plus `refit.executed=true` from the paired Python ledger until that changes.
- `e2e-wasm-open-repo-pipeline-alt-dataset` now records strict Python-vs-WASM parity: the browser smoke computes a Python nirs4all/sklearn oracle over the Web-emitted dag-ml folds and fails if the oracle cannot run.
- WASM/Web reuse is strict only where an actual Web/WASM import/render/reuse path exists. Other scenarios record explicit missing-runtime requirements.

## Validation Added

- The manifest must declare the same six V1 phases globally and for every scenario.
- Scenario coverage keys must exactly match the 10 scenario ids.
- V1 statuses are restricted to `strict`, `contract`, and `gap`.
- `gap` entries must explain the missing runtime/contract.
- `strict` entries cannot also declare a gap.
- V1 phase artifact references must be declared scenario artifacts.
- The CLI plan JSON exposes the per-scenario V1 contract block.

## Tests

- `rtk python3 scripts/n4a_e2e_scenarios.py validate` -> passed.
- `rtk python3 -m json.tool docs/contracts/e2e/cross-language-scenarios.n4a.json >/tmp/n4a-e2e-json-check.txt` -> passed.
- `rtk python3 -m pytest -q tests/test_e2e_scenarios.py` -> `32 passed`.

## Risks

- This lane strengthens contract validation; it does not add new runtime implementations.
- Repository best-refit remains a handoff descriptor, not an executed repository runtime; the executed refit evidence is Python-backed.
- Several scenario phases intentionally remain gaps until Python reopen/rerun, paper publishing, repository runtime, or Web/WASM import entrypoints exist in their owning repos.
