# Cross-language V1 E2E scenarios

The canonical scenario contract lives at
`docs/contracts/e2e/cross-language-scenarios.n4a.json`.

The suite deliberately separates planning from execution:

- `python3 scripts/n4a_e2e_scenarios.py validate` validates the manifest.
- `python3 scripts/n4a_e2e_scenarios.py list` lists the eleven scenarios.
- `python3 scripts/n4a_e2e_scenarios.py plan --json` renders tool/env blockers
  without running long tests.
- `python3 scripts/n4a_e2e_scenarios.py run <scenario-id>` is a dry run.
- `python3 scripts/n4a_e2e_scenarios.py run <scenario-id> --execute` runs the
  commands and fails with exit code 2 if required tools or env vars are missing.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` reports readiness,
  language/tag coverage, and V1 strict/contract/gap phase counts.
- `python3 scripts/n4a_e2e_scenarios.py evidence` verifies an existing artifact
  archive; add `--max-age-seconds <N>` when the gate must prove a fresh run.

The runner reports missing toolchains as `blocked`; it does not xfail or silently
skip. Full parity scenarios are meant to run after large integration batches or
on selected release heads, not on every small commit.

Coverage output also includes an explicit `debt_summary`. Keep this visible in
boards and CI logs: it names scenarios without strict parity checks, counts
strictness gaps, and totals V1 phases that remain `contract` or `gap`. A green
coverage command therefore means the contracts are coherent and executable; it
does not mean all V1 phases are strict until the debt summary reaches zero for
the relevant cutover gates.

Current coverage is intentionally hybrid: every parity-tagged scenario has at
least one strict parity check, while the multimodal proxy scenario records
contract-level roundtrip evidence without claiming strict numeric parity. The
manifest also records contract-level surfaces and explicit gaps for pending
runtimes such as native multimodal replay and some Web/WASM reuse paths. Do not
present this suite as full strict ecosystem parity unless those phase statuses
are promoted in the manifest and the coverage tests are updated with matching
evidence.

The validator also protects the suite shape from collapsing into shallow smoke
claims. Each scenario must include Python as the portable oracle runtime, at
least two runtime/language surfaces, at least two repos, at least two step kinds,
and at least three unique produced artifacts. Suite-level workflow coverage must
continue to include:

- a `nirs4all-core` + `nirs4all-ui` + `nirs4all-web` custom app path;
- R/Python/WASM roundtrip execution;
- datasets/IO/repository handoff;
- papers/repository/workspace-save provenance;
- multimodal and multisource workflows;
- formats/IO/datasets/methods language-binding parity.

## Orchestrated scenario set

The manifest intentionally stays at eleven complex scenarios. The validator enforces
that count and the tests assert the expected handoff for each workflow:

| Scenario | Primary orchestration proof |
| --- | --- |
| `e2e-r-dataset-io-pipeline-save` | R loads a catalog dataset, reshapes it through IO, runs/saves a pipeline, and records Python/native parity evidence. |
| `e2e-python-reopen-paper-repository-refit` | Python reopens/reruns a saved pipeline, papers export preserves provenance, repository handoff is emitted, and Web/WASM imports it. |
| `e2e-wasm-open-repo-pipeline-alt-dataset` | A fresh Web/WASM session imports a repository pipeline over an alternate dataset and compares against a Python oracle. |
| `e2e-multimodal-python-r-wasm-roundtrip` | Python creates multimodal evidence and R/WASM consume the persisted dense-fused proxy artifacts. |
| `e2e-multisource-branching-stacking-replay` | Python builds multisource stacking replay evidence and native/core replay verifies score parity. |
| `e2e-converter-legacy-save-predictions-web` | Python converts a legacy save and Web renders the lowered prediction result panels. |
| `e2e-dataset-provider-repository-roundtrip` | Providers materialize data into a repository descriptor consumed by Python core and JavaScript/WASM. |
| `e2e-pipeline-generation-performance-compare` | Python generates a pipeline family and Web/native runtimes compare prediction and performance evidence. |
| `e2e-cluster-dag-rights-client-core` | Cluster DAG execution is compared with a local Python numeric oracle and core handoff checks. |
| `e2e-formats-io-datasets-methods-language-bindings` | Formats/IO assemble reference datasets and methods bindings compare Python/R/WASM/native prediction evidence. |
| `e2e-core-ui-custom-app-host` | A custom client host records the R binding surface, proves runtimeContracts expose serialized-model prediction only for JavaScript/WASM, runs nirs4all-core WASM predictions against a Python oracle, and renders reusable nirs4all-ui result components. |

Every step must declare at least one explicit dependency gate through
`requires_tools`, `requires_env`, or `requires_paths`. Missing dependencies may
block execution, but divergence must fail the step: commands that hide failures
with soft-success, pytest skip/xfail, or continue-on-error fragments are rejected
by the manifest validator.
