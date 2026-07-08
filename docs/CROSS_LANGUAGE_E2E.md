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
  language/tag coverage, V1 strict/contract/gap/not-applicable phase counts,
  and per-scenario `scenario_details` for blocked steps, parity checks, and
  strictness gaps.
- `python3 scripts/n4a_e2e_scenarios.py coverage --markdown-out <path>`
  writes the same readiness/debt board as a human-readable Markdown artifact,
  including an explicit strictness gap detail table.
- `python3 scripts/n4a_e2e_scenarios.py evidence` verifies an existing artifact
  archive; add `--max-age-seconds <N>` when the gate must prove a fresh run.
- `python3 scripts/n4a_e2e_scenarios.py evidence --json-out <path>` writes the
  same verification report to disk for CI artifact upload.

The runner reports missing toolchains as `blocked`; it does not xfail or silently
skip. Full parity scenarios are meant to run after large integration batches or
on selected release heads, not on every small commit.

GitHub Actions validates and plans on push/PR. Every run uploads a coverage debt
board under `.n4a-e2e-artifacts/coverage/`, including `coverage-summary.json`
and `coverage-debt.md`, so the hybrid-vs-strict state is visible even when the
runtime scenarios are only planned. Runtime execution is explicit: dispatch
`Cross-language E2E scenarios` with `execute=true`, optionally selecting one
scenario. Those manual runs additionally upload `.n4a-e2e-artifacts`, including
`evidence-summary.json`, so fresh runtime proof can be audited after the job.

Coverage output also includes an explicit `debt_summary`. Keep this visible in
boards and CI logs: it names scenarios without strict parity checks, counts
strictness gaps, and totals V1 phases that remain `contract`, true `gap`, or
`not_applicable`. Use `gap` only for missing evidence that belongs to the
scenario objective. Use `not_applicable` when a phase is deliberately outside
that lane, with an `applicability` explanation; this keeps the debt board from
counting unrelated paper/repository/Web phases as missing implementation. A
green coverage command therefore means the contracts are coherent and
executable; it does not mean all relevant V1 phases are strict until the
contract/gap counts reach zero for the relevant cutover gates.
The JSON `scenario_details` and Markdown strictness detail table are the audit
surface to review before any production switch: they expose what remains hybrid
without relying on skipped or xfailed tests.

Current coverage is intentionally mixed: every parity-tagged scenario has at
least one strict parity check, and the R dataset/IO/save lane, custom-app-host,
and legacy-save converter/rendering scenarios are strict end to end for their
declared scope.
The manifest still records contract-level surfaces and explicit gaps for
residual work such as source-aware native multimodal replay, Web/Studio runtime
reuse, provider-backed browser datasets, broader source-aware by_source
multisource/catalog corpora, and fixture-scoped WASM coverage. Do not present
this suite as full strict ecosystem parity unless those phase statuses and
non-numeric strict exceptions are promoted in the manifest and the coverage
tests are updated with matching evidence.

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

Every `parity_checks` entry must point to produced scenario artifacts. Strict
parity checks must use JSON evidence artifacts so the runner can reject skipped,
xfail, false boolean, non-finite, or out-of-tolerance ledgers during `evidence`
verification. Non-JSON outputs such as screenshots or paper ZIPs can still be
scenario or phase artifacts, but they cannot be the sole strict parity proof.
The coverage report also lists current strict checks whose artifact requirements
are structural rather than numeric; new strict checks without numeric evidence
requirements are rejected unless they are explicitly added to that debt list.

## Orchestrated scenario set

The manifest intentionally stays at eleven complex scenarios. The validator enforces
that count and the tests assert the expected handoff for each workflow:

| Scenario | Primary orchestration proof |
| --- | --- |
| `e2e-r-dataset-io-pipeline-save` | R loads a catalog dataset, reshapes it through IO, runs/saves a pipeline, and records Python/native parity evidence. |
| `e2e-python-reopen-paper-repository-refit` | Python reopens/reruns a saved pipeline, papers export preserves provenance, repository handoff is emitted, and Web/WASM imports it. |
| `e2e-wasm-open-repo-pipeline-alt-dataset` | A Python oracle opens and reruns the repository descriptor, then a fresh Web/WASM session imports the same pipeline over a nirs4all-providers/nirs4all-datasets catalog dataset and compares predictions. |
| `e2e-multimodal-python-r-wasm-roundtrip` | Python persists and reopens the multimodal pipeline artifact, then R/WASM consume the dense-fused artifacts with strict numeric parity against the Python oracle. |
| `e2e-multisource-branching-stacking-replay` | Python builds, persists and reopens multisource stacking replay evidence before native/core replay verifies score and prediction-vector parity. |
| `e2e-converter-legacy-save-predictions-web` | Python converts a legacy save and Web renders the lowered prediction result panels. |
| `e2e-dataset-provider-repository-roundtrip` | Providers materialize a deterministic NIRS CSV dataset, publish a repository descriptor, and Python/R/JavaScript-WASM core surfaces execute the same pipeline with strict prediction parity. |
| `e2e-pipeline-generation-performance-compare` | Python persists and reopens one generated candidate, then Web/native runtimes compare prediction and performance evidence. |
| `e2e-cluster-dag-rights-client-core` | Cluster DAG execution on the public `F01_regression` fixture is compared with a local Python numeric oracle and core handoff checks. |
| `e2e-formats-io-datasets-methods-language-bindings` | Formats/IO assemble reference datasets, methods bindings compare Python/R/WASM/native prediction evidence, and archived Rust remains explicit non-release-target evidence. |
| `e2e-core-ui-custom-app-host` | A custom client host runs R parity against the Python oracle, proves runtimeContracts expose serialized-model prediction only for JavaScript/WASM, runs nirs4all-core WASM predictions against the same oracle, renders reusable nirs4all-ui result components, and bundles a downstream Vite/React app from the published nirs4all and nirs4all-ui packages. |

Every step must declare at least one explicit dependency gate through
`requires_tools`, `requires_env`, or `requires_paths`. Missing dependencies may
block execution, but divergence must fail the step: commands that hide failures
with soft-success, pytest skip/xfail, or continue-on-error fragments are rejected
by the manifest validator.
