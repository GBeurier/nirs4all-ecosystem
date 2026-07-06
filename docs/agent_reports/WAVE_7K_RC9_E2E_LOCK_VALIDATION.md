# WAVE 7K - RC9 E2E and release-lock validation

Date: 2026-07-06

## Scope

- Re-ran the executable cross-language E2E board after the custom app host and UI asset publication batch.
- Fixed and selected the `nirs4all-core` RC head for the multimodal R/Python/WASM runner.
- Updated the aggregation lock only for `lite` / `nirs4all-core`.

## Files changed

- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/WAVE_7K_RC9_E2E_LOCK_VALIDATION.md`

Related core change:

- `nirs4all-core` selected RC head: `1708ab0305a80de5294763549596aa2191e26bc2`
- Tag: `n4a-v1-rc9-2026.07-refactor`
- Fix: `scripts/e2e/run_multimodal_roundtrip.py` now propagates the R toolchain path, `R_MAKEVARS_USER`, explicit `NIRS4ALL_METHODS_ROOT`, and scenario-local `n4m` package provenance.

## Validation

- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-rc9-20260706-rerun run-ready --execute`
  - 11/11 executable scenarios completed.
  - Covered R dataset/IO save, Python papers/repository refit, WASM repository import, multimodal Python/R/WASM roundtrip, multisource stacking replay, legacy converter + Web rendering, dataset provider repository roundtrip, pipeline generation performance comparison, cluster DAG rights handoff, formats/IO/datasets/methods bindings, and custom app host core+ui.
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py tests/test_e2e_scenarios.py -p no:cacheprovider`
  - 107 passed.
- Strong release-lock validation:
  - `python3 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-lock-validate-rbRWbW`
  - `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-validate-rbRWbW validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - Result: validated.

## Decisions

- Accepted the `nirs4all-core` RC9 repin because the E2E runner fix is required for strict multimodal R parity evidence.
- Did not accept the regenerated `dag_ml` head drift in this batch. The lockstep pair remains pinned to the previously validated `dag_ml` / `dag_ml_data` commits.
- Did not touch the main `nirs4all-ui` checkout. It contains concurrent work for `nirs4all-quality`; Web vendor checks read the published UI head, not dirty local files.

## Risks

- `nirs4all-core` package version remains `0.2.7`; RC9 is a coordination/source tag over the same package version plus E2E infrastructure hardening.
- Full Python production cutover and `nirs4all-studio` production release remain outside this release batch.
