# Wave 4CU — E2E Evidence Level Audit

Date: 2026-07-04

## Scope

- Lane C / K: cross-language E2E coverage and final parity audit.
- Repo changed: `nirs4all-ecosystem`.
- Trigger: read-only agent audit found that all 10 scenarios exist, but several were still contract smokes or partial proofs while carrying broad parity wording.

## Changes Integrated

- `scripts/n4a_e2e_scenarios.py`
  - Added scenario-level `evidence_level`: `strict`, `hybrid`, or `contract_smoke`.
  - Added parity-check-level `evidence_level`: `strict`, `hybrid`, or `contract`.
  - `contract_smoke` scenarios may no longer carry the `parity` tag.
  - `hybrid` and `contract_smoke` scenarios must declare `strictness_gaps`.
  - Any scenario with the `parity` tag must declare at least one strict parity check.
  - `plan --json` now exposes `evidence_level`, `strictness_gaps`, and `parity_checks`.
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Marked strict scenarios explicitly.
  - Downgraded Web repository import and provider repository descriptor scenarios to `contract_smoke`.
  - Marked R dataset IO, multisource replay, performance compare, and formats/methods as `hybrid` with named gaps.
  - Renamed the Web repository scenario id from `e2e-wasm-open-repo-pipeline-parity-alt-dataset` to `e2e-wasm-open-repo-pipeline-alt-dataset`.
- `tests/test_e2e_scenarios.py`
  - Added negative tests so smoke scenarios cannot claim parity and hybrid scenarios cannot hide missing strict proof.

## Current Evidence Split

Strict:

- Python reopen/rerun/paper repository refit.
- Multimodal Python/R/WASM roundtrip.
- Legacy save conversion/prediction/Web result contract.
- Cluster DAG rights plus local-vs-cluster numeric oracle.

Hybrid:

- R dataset IO pipeline save: strict portable R parity fixture, but real catalog dataset path still lacks numeric R-vs-Python comparison.
- Multisource stacking replay: strict score parity, but native vector-level prediction equality is still only audited.
- Pipeline generation performance: strict Python-vs-dag-ml parity, Web timing remains contract evidence and Studio is outside the gate.
- Formats/IO/datasets/methods: strict native/Python/R method parity, WASM remains fixture-scoped and Rust is archive evidence.
- Provider/dataset/repository descriptor roundtrip: strict Python/WASM portable pipeline execution was added in `nirs4all-core@a853894`, but R and provider-materialized dataset prediction parity remain outside this gate.

Contract smoke:

- Web/WASM repository pipeline import and result rendering.

## Verification

From `nirs4all-ecosystem`:

- `python3.11 -m json.tool docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py list --json`
- `python3.11 scripts/n4a_e2e_scenarios.py plan --scenario e2e-wasm-open-repo-pipeline-alt-dataset --json`
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_gitmodules_topology.py tests/test_release_lock.py` — 40 passed.
- `python3.11 -m pytest -q tests/test_e2e_scenarios.py` — 28 passed after plan JSON exposure.
- `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py` — OK.

## Risks / Next Work

- The contract no longer overclaims, but the goal still requires replacing the remaining `contract_smoke` scenario and hybrid gaps with stricter numeric/runtime evidence.
- Full parity remains intentionally deferred until the next large batch.
