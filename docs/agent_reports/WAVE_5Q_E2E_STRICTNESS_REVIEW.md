# Wave 5Q - Cross-language E2E strictness review

Date: 2026-07-04

## Scope

- Read-only review of the 10 cross-language E2E scenarios after the Wave 5O execution.
- Preserve the distinction between contract/planning gates, hybrid execution gates, and true full-parity gates.
- Do not claim Python-reference full parity from the current E2E suite alone.

## Inputs Reviewed

- `docs/CROSS_LANGUAGE_E2E.md`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `.github/workflows/cross-language-e2e.yml`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- Prior reports `WAVE_5D`, `WAVE_5E`, `WAVE_5I`, `WAVE_5L`, and `WAVE_5O`.

## Findings

- The default push/PR workflow validates the contract, pytest gate, and plan. It does not execute the scenarios unless the manual workflow dispatch is run with `execute=true`.
- The runner validates produced artifacts mostly by existence, JSON parseability, mtime refresh, and absence of known bad status tokens. Strong parity proof is therefore delegated to each scenario command, not enforced centrally by the runner.
- The current phase matrix is mixed: Python parity is strict across the 10 scenarios, but cross-language and workflow-completion phases still contain many `contract` or `gap` cells.
- No scenario currently proves a complete cross-language full-parity path across Python, R, WASM/Web, native methods, repository refit, papers export, datasets, and cluster behavior.

## Scenario Strictness

- `e2e-r-dataset-io-pipeline-save`: hybrid; R fixture parity and finite native/R predictions are checked, but public CI remains data-blocked and no R-vs-Python numeric parity is enforced on the same catalog payload.
- `e2e-python-reopen-paper-repository-refit`: strongest Python slice; reopen/rerun/parity ledger and papers export are strict, but repository refit is still descriptor-level rather than an independent repository runtime.
- `e2e-wasm-open-repo-pipeline-alt-dataset`: hybrid; repo import, prediction roundtrip, and web smoke execute, but the dataset is fixture-scoped and not a full Python rerun over the same external/catalog data.
- `e2e-multimodal-python-r-wasm-roundtrip`: hybrid; current parity uses a fused dense-matrix proxy rather than native multimodal structures and full Web/Studio roundtrip.
- `e2e-multisource-branching-stacking-replay`: hybrid; score-set parity is strict, but native prediction checks remain schema/coverage oriented rather than per-sample vector parity.
- `e2e-converter-legacy-save-predictions-web`: executable and narrow-strict for converter/save/render, but the Web leg is a smoke and the broader Python rerun/papers/repository matrix remains incomplete.
- `e2e-dataset-provider-repository-roundtrip`: hybrid; portable Python/WASM roundtrip is strict on synthetic NIRS data, but R and provider-materialized dataset parity are not yet in the strict path.
- `e2e-pipeline-generation-performance-compare`: hybrid; Python-vs-dag-ml prediction parity is strict, but Web is a timing/performance contract and Studio is outside the bounded gate.
- `e2e-cluster-dag-rights-client-core`: strict locally but effectively placeholder in public CI because the required `GRAPEVINE_LeafTraits` fixture is allowlist-blocked.
- `e2e-formats-io-datasets-methods-language-bindings`: hybrid; native/Python/R method parity is a smoke sample, not a registry sweep; WASM is fixture-scoped and JS/WASM rebuild-from-HEAD provenance is not proven.

## Recommended Batches

1. Make the gate bite publicly: add scheduled or label-gated `run-ready --execute`, commit public synthetic fixtures for the currently blocked data paths, and move the cluster numeric oracle out of the allowlisted blocker path.
2. Harden the runner: require positive numeric-oracle fields, expected checksums or tolerance ledgers, and forbid `gap` phases in scenarios labeled `strict` unless they are renamed as partial/hybrid.
3. Implement real repository forced-best-refit runtime evidence so `refit.executed` is not a descriptor-only assertion.
4. Upgrade cross-language legs to numeric parity: R-vs-Python on the same provider/IO payload, native per-sample vector parity, provider dataset through R, and real multimodal/Web/Studio roundtrip.
5. Strengthen WASM/Web/method provenance: Python rerun over the same uploaded/catalog dataset, JS/WASM rebuild-from-HEAD proof, methods registry sweep, and a bounded Studio parity/performance gate.

## Decision

- Treat Wave 5O as proof that the 10-scenario contract and current executable slices can run, not as proof of production full parity.
- Full parity remains gated by the hardening batches above and by the dedicated Python-reference parity suite after a larger integration batch.
