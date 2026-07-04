# Wave 5I - E2E coverage gap audit

Date: 2026-07-04

## Scope

- Read-only Codex agent audit of the ten complex cross-language E2E scenarios.
- Goal: compare the current ecosystem contract with the requested R/Python/WASM/Web, multimodal, multisource, repository, papers, predictions, cluster, and methods coverage.

## Agent Report

- Agent: Carson the 4th (`019f2d0e-1686-7403-99f9-561def19bc07`).
- Mode: read-only.
- Result: the ten requested scenarios exist and are validated by the ecosystem contract runner, but coverage is not uniformly strict.

## Coverage Confirmed

- R dataset/IO/pipeline/save:
  - real bridge through `providers -> datasets -> io -> R`;
  - saved `workspace.n4a.json`, `pipeline.n4a.json`, `r-predictions.json`;
  - R rerun of saved artifacts.
- Python open/rerun/parity/papers:
  - strict Python reopen/rerun/parity ledger;
  - reproducible paper export path present.
- WASM/Web:
  - repository pipeline import and execution;
  - prediction artifact roundtrip;
  - converted predictions rendered in Web.
- Multimodal, multisource, performance, cluster, methods/formats:
  - all present as contract scenarios with dedicated entrypoints.

## Gaps Confirmed

- R dataset/IO still lacks a strict Python oracle rerun on the same provider/IO payload.
- Repository forced best-refit is currently a handoff descriptor backed by Python evidence, not an independently executed `nirs4all-repository` runtime.
- WASM alternate dataset path is hybrid: no Python open/rerun over that same non-demo uploaded dataset and no forced-best-refit descriptor emitted by a repository runtime.
- Multimodal parity currently uses a dense fused proxy matrix, not arbitrary native multimodal structures.
- Multisource parity has score coverage but not full per-sample native vector parity for `MetaModel` rows.
- Performance covers Web, while Studio remains explicitly outside that gate.
- Methods/formats/io/datasets coverage is a real cross-binding smoke, not a full registry sweep; Rust remains archived evidence and JS/WASM rebuild-from-HEAD is not proved by this audit.

## Files Inspected

- `docs/CROSS_LANGUAGE_E2E.md`.
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`.
- `scripts/n4a_e2e_scenarios.py`.
- `tests/test_e2e_scenarios.py`.
- Previous E2E agent reports under `docs/agent_reports/`.
- Child-repo E2E entrypoints referenced by the contract in `nirs4all-core`, `nirs4all`, `nirs4all-papers`, `nirs4all-web`, `nirs4all-cluster`, `nirs4all-methods`, and `nirs4all-io`.

## Checks

- Already run in Wave 5H:
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> `OK: 10 cross-language E2E scenarios`;
  - `python3 scripts/n4a_e2e_scenarios.py plan --json` -> `10 ready` in the full local workspace;
  - `pytest -q` -> `63 passed`.
- GitHub Actions on `3d53022`:
  - `version-guard` -> success;
  - `Cross-language E2E scenarios` -> success.

## Decisions

- Do not claim full strict parity from these scenarios yet.
- Keep the hybrid gaps visible as acceptance criteria instead of replacing them with skips, xfails, or relaxed fallbacks.
- Defer the expensive full parity executions until after larger integration batches, as requested.
