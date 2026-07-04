# WAVE 4CP - strict E2E evidence and shared UI contract

Date: 2026-07-04

## Scope

Integrated the read-only audit findings from the parallel reviewers:

- Wegener: E2E artifacts could pass while stale or semantically `not_run` / `not_requested`.
- Curie: Web consumed `nirs4all-ui` only partially and ecosystem scenarios did not prove the shared UI shim.
- Hubble: release/cockpit audit was reviewed; cockpit refresh was already pushed before this batch.

## Files changed

- `nirs4all-ecosystem`
  - `scripts/n4a_e2e_scenarios.py`
  - `tests/test_e2e_scenarios.py`
  - `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-core`
  - `scripts/e2e/verify_cluster_handoff.py`
  - `scripts/e2e/run_multisource_stacking_replay.py`
  - `tests/test_verify_cluster_handoff.py`
- `nirs4all-cluster`
  - `tests/e2e/test_cluster_dag_rights_core_client.py`
- `nirs4all-tools`
  - `tests/e2e/test_legacy_save_predictions_web.py`
- `nirs4all-web`
  - `studio-lite/package.json`
  - `studio-lite/scripts/sync-ui-shim.mjs`
  - `studio-lite/src/app/shared-ui-contract.test.ts`

## Tests run

- `nirs4all-ecosystem`: `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: selected cluster, multisource, legacy converter, and WASM/Web scenarios with `--execute`
- `nirs4all-core`: `python3.11 -m pytest -q tests/test_verify_cluster_handoff.py`
- `nirs4all-core`: `python3.11 scripts/e2e/run_multisource_stacking_replay.py --artifacts-dir /tmp/n4a-multisource-probe`
- `nirs4all-cluster`: numeric oracle E2E with `N4A_CLUSTER_NUMERIC_ORACLE=1`
- `nirs4all-tools`: `python3.11 -m pytest -q tests/e2e/test_legacy_save_predictions_web.py::test_convert_legacy_save`
- `nirs4all-web`: `npm run check:ui-shim`, `npm run smoke:shared-ui-contract`, `npm run typecheck`

## Decisions

- E2E runner now rejects stale produced artifacts and JSON evidence containing `not_run`, `not_requested`, `blocked`, `skipped`, `xfail`, failed statuses, or false core evidence booleans.
- Cluster numeric oracle is mandatory in the ecosystem scenario; absence is now blocked/failing, not green.
- Legacy converter scenario no longer claims legacy Python replay. It claims deterministic fixture/checksum/result-contract preservation and Web rendering.
- Multisource scenario no longer claims native vector parity because current native `MetaModel_Ridge` rows do not persist per-sample arrays. It now audits `predictions.parquet` schema/coverage and keeps score-set parity.
- Web/WASM scenarios now run `check:ui-shim` and `smoke:shared-ui-contract`; Web vendor sync rejects `node_modules` to avoid duplicate React.

## Risks / follow-ups

- True native vector parity for multisource still requires native `predictions.parquet` to persist per-sample arrays for the MetaModel rows.
- WASM/Web scenario is still a client-side import/render smoke, not a numeric Python-vs-WASM parity oracle.
- R real-dataset IO scenario proves fixture parity plus real dataset finite/native execution; it does not yet compare real-dataset R predictions against a Python oracle.
