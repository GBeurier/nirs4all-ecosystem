# Wave 6J - Ecosystem E2E coverage audit

Date: 2026-07-06

## Scope

- Audit the 10 cross-language E2E scenarios in `docs/contracts/e2e/cross-language-scenarios.n4a.json`.
- Distinguish executable evidence from declared hybrid/contract coverage.
- Keep changes limited to E2E contracts/tests and `docs/agent_reports`.

## Audit result

- The manifest still declares exactly 10 complex scenarios and all 10 plan as ready in this checkout.
- Evidence level is `hybrid` for all 10 scenarios; none should be described as full strict ecosystem E2E.
- Existing artifacts verify structurally: `10/10` scenarios, `43` artifacts, `0` semantic failures.
- Freshness is not current: `evidence --max-age-seconds 86400` fails for `10/10` scenarios because the artifacts are from 2026-07-04.

| Scenario | Real coverage found | Still declared/hybrid |
| --- | --- | --- |
| `e2e-r-dataset-io-pipeline-save` | R dataset IO, save/reopen artifacts, fixture parity gate. | Real catalog R-vs-Python numeric parity is still not strict. |
| `e2e-python-reopen-paper-repository-refit` | Python reopen/rerun parity, papers export, Web import evidence. | Repository forced best-refit remains contract-level. |
| `e2e-wasm-open-repo-pipeline-alt-dataset` | Web/WASM import/reuse, Python oracle comparison, screenshots/artifacts. | Alternate dataset is fixture-scoped, not external provider/catalog execution. |
| `e2e-multimodal-python-r-wasm-roundtrip` | Python/R/WASM dense-fused proxy parity. | Native multimodal runtime and Web/Studio roundtrip remain pending. |
| `e2e-multisource-branching-stacking-replay` | Python/native score-set replay parity. | Native vector-level prediction parity is still schema/array coverage. |
| `e2e-converter-legacy-save-predictions-web` | Legacy save conversion and Web prediction panel rendering. | Narrow slice only; broader rerun/papers/repository phases are outside this scenario. |
| `e2e-dataset-provider-repository-roundtrip` | Provider descriptor, repository descriptor, Python/WASM portable execution. | R and provider-materialized dataset parity are not strict. |
| `e2e-pipeline-generation-performance-compare` | Python-vs-dag-ml prediction parity and Web runtime ledger. | Web timing remains a contract/performance gate. |
| `e2e-cluster-dag-rights-client-core` | Cluster/local numeric oracle and core handoff artifacts. | Public-checkout data dependence remains a release risk. |
| `e2e-formats-io-datasets-methods-language-bindings` | Native/Python/R method parity plus WASM fixture evidence. | WASM is fixture-scoped and Rust is archived/non-release-target evidence. |

## Test hardening

- Added CLI regression coverage for `evidence --max-age-seconds`, so selected-scenario evidence now proves the stale-artifact failure path through the command-line interface, not only through the Python helper.

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate` -> passed.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> passed, `ready_count=10`, `blocked_count=0`.
- `python3 scripts/n4a_e2e_scenarios.py evidence --json` -> passed, `verified_count=10`.
- `python3 scripts/n4a_e2e_scenarios.py evidence --max-age-seconds 86400 --json` -> expected failure, `failed_count=10`, stale artifacts.
- `python3 -m pytest -q tests/test_e2e_scenarios.py` -> passed, `73 passed`.

## Decisions and risks

- Do not promote any scenario to `strict`: current coverage is executable but explicitly hybrid.
- Treat artifact existence as historical proof only unless a freshness window is supplied or `run-ready --execute` is rerun.
- No full E2E execution batch was launched in this audit turn; the targeted contract/evidence gates were run instead.
