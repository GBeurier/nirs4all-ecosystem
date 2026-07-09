# WAVE 10BB - Ecosystem Actions v6 and custom-host audit

Date: 2026-07-09T18:32:22Z

Lane: CI/workflow hygiene + custom-app-host consistency

## Summary

- Migrated `nirs4all-ecosystem` first-party GitHub Actions from Node20-era
  majors to the current v6 majors used by cockpit:
  `actions/checkout@v6`, `actions/setup-python@v6`,
  `actions/setup-node@v6`, and `actions/upload-artifact@v6`.
- Updated the workflow contract test that intentionally checks artifact upload
  actions in the cross-language E2E workflow.
- Kept runtime/full parity execution untouched; this wave improves workflow
  health and keeps the existing contract gates intact.
- Ran a read-only custom-app-host audit in parallel: `nirs4all-core`,
  `nirs4all-ui`, and `nirs4all-web/studio-lite` remain coherent for the
  published custom host surface.

## Repositories touched

- `nirs4all-ecosystem`

## Files modified

- `.github/workflows/cross-language-e2e.yml`
- `.github/workflows/cutover-gates.yml`
- `.github/workflows/version-guard.yml`
- `tests/test_e2e_scenarios.py`

## Validation

Local:

- `python3 scripts/n4a_e2e_scenarios.py validate` -> 11 scenarios OK.
- `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict` ->
  11/11 ready, strictness gaps 0.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> OK.
- `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> OK.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable`
  -> 7/7 member commits fetchable.
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all validate`
  -> manifest and readiness matrix OK.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py tests/test_release_surface_matrix.py tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py tests/test_release_lock.py`
  -> 163 passed.
- `rg --hidden 'actions/(checkout|setup-node|setup-python|upload-artifact|download-artifact|cache)@v[45]' .github/workflows tests`
  -> no matches.

## Parallel audit findings

Custom-app-host read-only audit:

- `nirs4all-core` publication topology is coherent: Python package
  `nirs4all-core`, other target language surfaces published as `nirs4all`.
- `nirs4all-ui` exports reusable `brand`, `components`, `runtime`, `dataset`,
  and `assets/*` surfaces.
- `nirs4all-web/studio-lite` consumes public `nirs4all` and `nirs4all-ui`
  vendors and the custom-app-host example imports only those public packages.
- Public pages checked by the auditor did not expose `nirs4all-lite`.

Observed non-blocking debt:

- Historical `nirs4all-lite` mentions remain in changelogs/hand-off docs.
- `studio-lite` remains a developer-facing directory/package name in web docs.
- Remaining `nirs4all-lite` code occurrences are negative compatibility tests,
  not public runtime aliases.

## Decisions

- Do not rename `studio-lite` in this wave; it is a broader repo/package
  migration and not necessary for the current published custom-app-host surface.
- Do not remove negative legacy-format tests; they prove old aliases are not
  accepted silently.
- Do not run full parity here; no numerical/runtime behavior changed.
