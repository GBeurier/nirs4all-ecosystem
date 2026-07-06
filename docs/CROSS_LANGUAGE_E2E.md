# Cross-language V1 E2E scenarios

The canonical scenario contract lives at
`docs/contracts/e2e/cross-language-scenarios.n4a.json`.

The suite deliberately separates planning from execution:

- `python3 scripts/n4a_e2e_scenarios.py validate` validates the manifest.
- `python3 scripts/n4a_e2e_scenarios.py list` lists the ten scenarios.
- `python3 scripts/n4a_e2e_scenarios.py plan --json` renders tool/env blockers
  without running long tests.
- `python3 scripts/n4a_e2e_scenarios.py run <scenario-id>` is a dry run.
- `python3 scripts/n4a_e2e_scenarios.py run <scenario-id> --execute` runs the
  commands and fails with exit code 2 if required tools or env vars are missing.

The runner reports missing toolchains as `blocked`; it does not xfail or silently
skip. Full parity scenarios are meant to run after large integration batches or
on selected release heads, not on every small commit.

## Orchestrated scenario set

The manifest intentionally stays at ten complex scenarios. The validator enforces
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

Every step must declare at least one explicit dependency gate through
`requires_tools`, `requires_env`, or `requires_paths`. Missing dependencies may
block execution, but divergence must fail the step: commands that hide failures
with soft-success, pytest skip/xfail, or continue-on-error fragments are rejected
by the manifest validator.
