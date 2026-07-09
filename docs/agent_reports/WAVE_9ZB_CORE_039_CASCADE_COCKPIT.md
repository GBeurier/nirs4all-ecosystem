# WAVE 9ZB — core 0.3.9 cascade, cockpit, release lock

Date: 2026-07-10

## Coordination

- Main Codex lane: published and verified `nirs4all-core` `v0.3.9`, synced release lock/e2e evidence, cockpit, org/web/device dependency cascade, and ecosystem gitlinks.
- Harvey the 3rd, read-only explorer: release-lock/topology audit. Reported stale gitlinks and cascade updates needed in `nirs4all-org`, `nirs4all-web`, and `nirs4all-device`.
- Linnaeus the 3rd, read-only explorer: cross-language e2e audit. Confirmed 11 ready scenarios and identified stale runtime evidence for MATLAB/Octave release gate and published custom host.
- Aristotle the 3rd, read-only explorer: core/ui/cockpit audit. Confirmed `nirs4all-core` `0.3.9`, custom-host capability surfaces, `nirs4all-ui` `0.1.10` assets/pages, and cockpit gaps.

## Files/repos changed

- `nirs4all-core`: bumped/tagged/published `v0.3.9`.
- `nirs4all-ecosystem`: updated release manifest/lock, e2e scenario constants, latest runtime evidence ledger, and release gitlinks.
- `nirs4all-cockpit`: updated train metadata/manual actions, refreshed `data/current.json` and `data/manual-actions.json` through GitHub collect.
- `nirs4all-org`: refreshed public V1 package versions.
- `nirs4all-web`: synced `nirs4all-core` and `nirs4all-ui` vendor shims; published custom host defaults now use `nirs4all 0.3.9`, `nirs4all-ui 0.1.10`, `methods 1.0.9`.
- `nirs4all-device`: bumped runtime dependencies and lockfile to current published stack.

## Validation

- `nirs4all-core`: `make test` passed before tag; GitHub CI and releases passed for source, Python, npm, crates, R, MATLAB.
- `nirs4all-ecosystem`: `n4a_release_lock.py validate`, `n4a_release_surface_matrix.py validate`, `n4a_e2e_scenarios.py validate`, `evidence-ledger --check`, and targeted pytest passed; GitHub cross-language e2e workflow passed.
- `nirs4all-cockpit`: `n4a-cockpit validate-targets`, targeted pytest passed; GitHub `collect`, `ci`, `version-guard`, and Pages passed.
- `nirs4all-web`: `check:core-shim`, `check:ui-shim`, and `smoke:published-custom-host` passed; GitHub web CI and Pages deploy passed.
- `nirs4all-device`: `npm test` and `npm run build` passed; GitHub CI, Pages, and Android APK passed.
- Registries verified: PyPI/npm/crates for core, methods, formats, io, dag-ml-data, and UI.

## Remaining risks/decisions

- `nirs4all-core` cockpit rollup remains `stale` only because R-universe still serves aggregate `nirs4all 0.3.8`; manual action stays `todo`.
- CRAN entries for `n4m`, `pls4all`, `nirs4allio`, and aggregate `nirs4all` remain manual/pending.
- This batch refreshed strict e2e runtime evidence ledgers but did not rerun the full parity suite end-to-end.
- Production `nirs4all` Python and `nirs4all-studio` remain intentionally held out of the release switch.
