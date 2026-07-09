# WAVE 10AX — core/provider patch release, Web cascade, and E2E lock refresh

Date: 2026-07-09

## Scope

- Published and verified the `nirs4all-core` patch release train at `v0.3.8`.
- Published and verified `nirs4all-providers` `v0.2.10`.
- Synced `nirs4all-web` vendored core metadata and published custom-host smoke defaults to `nirs4all@0.3.8`.
- Refreshed the central aggregation manifest/lock and E2E runtime evidence ledger.

## Files Modified

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `tests/test_release_lock.py`

Related commits outside this repo:

- `nirs4all-core`: `3b89f5f chore(release): bump core dependency floor`, tag `v0.3.8`.
- `nirs4all-providers`: `5a03f50 chore(release): align provider dependency floor`, tag/release `v0.2.10`.
- `nirs4all-web`: `0df5aac chore(studio-lite): sync core shim version`, `357e8de chore(studio-lite): align published core smoke`.
- `nirs4all-cockpit`: `1616758 chore(targets): track core provider patch releases`.

## Tests Run

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py run e2e-core-ui-custom-app-host --execute`
- `python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --json`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `pytest -q`

Result: `170 passed`; E2E evidence `11/11` scenarios, `70/70` artifacts, `0` failures. The custom app host published-package evidence now records `nirs4all_version=0.3.8`.

## Decisions

- Keep PyPI `nirs4all` production untouched; the portable aggregate remains published on PyPI as `nirs4all-core`, while npm/crates/R/MATLAB surfaces publish/import as `nirs4all` where available.
- Regenerate the aggregation lock from current `main` checkouts. This intentionally records a few documentation-only post-tag heads as selected workspace evidence when those heads are above their published tag.
- Do not rerun full Python parity in this wave; the latest full parity gate already passed with `799 passed`, and this patch batch touched release pins, lock/evidence metadata, and Web package smoke defaults.

## Risks

- CRAN submissions remain manual.
- Studio Windows RC installer smoke remains manual on Windows.
- Some registry mirrors may lag even after GitHub/PyPI/npm/crates release success; cockpit collection tracks public propagation.
