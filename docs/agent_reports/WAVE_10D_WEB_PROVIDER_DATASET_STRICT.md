# Wave 10D - Web provider dataset strict parity

Lane: Web/WASM, repository pipeline, providers/datasets bridge

## Summary

Promoted `e2e-wasm-open-repo-pipeline-alt-dataset` from hybrid to strict by
running the Web/WASM repository-pipeline smoke on an alternate dataset exported
through `nirs4all-datasets` catalog APIs and resolved through
`nirs4all-providers` `DatasetProvider`.

The fixture is hermetic and public-checkout safe: the helper builds a temporary
synthetic catalog fixture, organizes canonical files, resolves it via the
provider, exports repository CSVs plus a provenance manifest, then Web reruns
the checked-in repository pipeline against those files.

## Files Modified

- `nirs4all-web` submodule pinned to `e273674`.
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/CROSS_LANGUAGE_E2E.md`
- `scripts/export_repository_dataset_fixture.py`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Tests Run

- `cd nirs4all-web/studio-lite && npm run check:ui-shim`
- `cd nirs4all-web/studio-lite && npm run smoke:shared-ui-contract`
- `cd nirs4all-web/studio-lite && npm run build`
- `cd nirs4all-web/studio-lite && N4A_WEB_PYTHON=python3.11 N4A_REPOSITORY_DATASET_DIR=/tmp/n4a-repo-catalog-dataset N4A_REPOSITORY_DATASET_EXPECTED_BADGE='48 samples x 2151 wavelengths' ARTIFACTS_DIR=/tmp/n4a-web-provider-repo-smoke npm run smoke:pipeline-repository`
- `cd nirs4all-web/studio-lite && npm run typecheck`
- `cd nirs4all-web/studio-lite && npm run test`
- `cd nirs4all-web/studio-lite && npm run validate:catalog`
- `cd nirs4all-web/studio-lite && npm run build:single`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-web-provider run --execute e2e-wasm-open-repo-pipeline-alt-dataset`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-web-provider evidence --scenario e2e-wasm-open-repo-pipeline-alt-dataset`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --markdown-out /tmp/n4a-e2e-coverage-web-provider.md`
- `python3.11 scripts/n4a_release_surface_matrix.py validate`
- `python3.11 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 -m pytest tests/test_e2e_scenarios.py -q`
- `python3.11 -m pytest tests/test_release_lock.py tests/test_gitmodules_topology.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py -q`

## Decisions

- Keep `nirs4all-web` client-side only. The dataset exporter is an ecosystem
  test harness helper; it is not a Web backend.
- Do not reopen `nirs4all-ui`; Web only vendored the already integrated shared
  UI package output required by its shim check.
- Keep Web's vendored `nirs4all-core` shim in sync with the current core WASM
  package metadata so the CI client-only gate stays green.
- Treat `nirs4all-ecosystem` helper paths as orchestration surfaces, not
  submodule repos, in the E2E contract tests.

## Risks

- The dataset is a synthetic catalog fixture, not the pending Dataverse
  collection. It proves the provider/catalog path, manifest provenance, and
  Web/WASM numeric parity, but it does not replace future Dataverse corpus
  coverage.
- Remaining ecosystem strictness debt is not hidden: coverage now reports
  8 strict and 3 hybrid scenarios, with 3 strictness gaps left.
