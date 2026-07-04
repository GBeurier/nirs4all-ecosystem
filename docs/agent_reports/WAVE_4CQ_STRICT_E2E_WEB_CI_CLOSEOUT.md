# WAVE 4CQ - Strict E2E/Web CI closeout

Date: 2026-07-04
Owner: Codex integration

## Scope

Closed the strict E2E evidence and shared UI contract batch after review of the
parallel audit findings from Wegener, Curie, and Hubble.

## Integrated changes

- `nirs4all-ecosystem@e87a460`
  - E2E runner now rejects stale produced artifacts and non-passing JSON
    evidence (`not_run`, `not_requested`, `skipped`, `xfail`, failed status
    fields, false success booleans).
  - Cross-language scenario contracts now state the actual evidence scope:
    cluster numeric oracle required, multisource table/schema audit without
    unsupported vector-parity claim, converter fixture parity, Web/WASM smoke +
    shared UI contract.
- `nirs4all-core@c554b34`
  - Cluster handoff verifier requires numeric oracle status `passed`.
  - Multisource stacking replay reports prediction table coverage and records
    that native per-sample arrays are not yet emitted in the current table.
- `nirs4all-cluster@4d34e8a`
  - Numeric oracle E2E worker receives source checkout `PYTHONPATH` for both
    cluster and Python reference packages.
- `nirs4all-tools@dee3724`
  - Legacy converter E2E now reports deterministic fixture parity honestly
    instead of claiming a Python replay that is not executed.
- `nirs4all-web@765506b`
  - Web shared UI smoke imports `nirs4all-ui` contract surfaces.
  - UI shim check remains install-stable in CI: generated `node_modules` under
    the vendored file dependency is no longer treated as shim drift.

## Tests run locally

- Ecosystem:
  - `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - Executed strict ready scenarios for cluster, multisource, legacy converter,
    and Web/WASM artifact flows.
- Core:
  - `python3.11 -m pytest -q tests/test_verify_cluster_handoff.py`
  - `python3.11 scripts/e2e/run_multisource_stacking_replay.py --artifacts-dir /tmp/n4a-multisource-probe`
  - `python3.11 -m py_compile scripts/e2e/verify_cluster_handoff.py scripts/e2e/run_multisource_stacking_replay.py`
- Cluster:
  - Default E2E cluster handoff.
  - Strict `N4A_CLUSTER_NUMERIC_ORACLE=1` E2E plus core handoff verification.
- Tools:
  - `python3.11 -m pytest -q tests/e2e/test_legacy_save_predictions_web.py::test_convert_legacy_save --artifacts-dir=/tmp/n4a-tools-legacy-check`
- Web:
  - `npm run check:ui-shim`
  - `npm run smoke:shared-ui-contract`
  - `npm run typecheck`
  - `npm run test`

## Remote CI status

- `nirs4all-ecosystem@e87a460`: green.
- `nirs4all-core@c554b34`: green, including strict parity.
- `nirs4all-cluster@4d34e8a`: green.
- `nirs4all-tools@dee3724`: green.
- `nirs4all-web@765506b`: green, including build, deploy, client-only gate, and guard.

## Decisions

- Do not accept artifact presence alone as E2E proof; produced files must be
  freshly written and semantically passing.
- Do not claim native vector parity for multisource stacking until native
  prediction tables persist per-sample arrays.
- Keep Web client-side only and require shared UI contract smoke, but avoid SSR
  React identity checks against vendored dependencies.

## Residual risks

- Web/WASM scenarios are still client artifact/rendering smoke, not a full
  numeric parity oracle.
- R dataset IO currently validates the language bridge and saved artifacts, but
  does not yet provide a full cross-language numeric oracle against the Python
  reference for every dataset family.
- Full parity remains expensive and should stay batched after large integration
  waves, per operating constraint.
