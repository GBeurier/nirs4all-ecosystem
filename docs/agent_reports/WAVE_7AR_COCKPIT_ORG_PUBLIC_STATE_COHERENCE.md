# Wave 7AR - Cockpit and org public state coherence

Date: 2026-07-07

## Scope

- Audited `nirs4all-cockpit` and `nirs4all-org` against the current release-doc state.
- Did not touch `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, or `nirs4all-lab`.
- Kept the existing `nirs4all` Python and `nirs4all-studio` production lines explicitly out of the final V1 RC publication batch.

## Changes made

- `nirs4all-cockpit`
  - Updated `ops/targets.yaml` so the `nirs4all-providers` GitHub Release target now matches the current state: `v0.2.7` is tagged and carries fallback wheel/sdist assets, while PyPI remains blocked by Trusted Publisher setup.
  - Refreshed `ROADMAP.md` release-inventory text for:
    - `nirs4all-core` -> `0.2.13`
    - `nirs4all-providers` -> `0.2.7`
    - `nirs4all-tools` -> `0.0.4`
    - `dag-ml` / `dag-ml-data` -> `0.2.5`
    - explicit `dagmldata` R-universe lag wording
  - Updated `tests/test_targets_topology.py` so the providers release-surface assertion matches the current fallback-asset state instead of the superseded "no assets" wording.

- `nirs4all-org`
  - Refreshed stale fallback/public versions in `index.html`:
    - `nirs4all-core` -> `0.2.13`
    - `nirs4all-providers` -> `0.2.7`
    - `nirs4all-formats` -> `0.2.4`
    - `nirs4all-io` -> `0.1.9`
    - `dag-ml` -> `0.2.5`
    - `dag-ml-data` -> `0.2.5`
  - Updated JSON-LD metadata for `nirs4all-core` and `nirs4all-providers`.
  - Reworded public copy so:
    - `nirs4all-core` and `nirs4all-providers` clearly remain blocked on PyPI Trusted Publisher setup while GitHub fallback assets exist.
    - R-universe is described as allowed to lag after release publication.
    - `nirs4all` Python and `nirs4all-studio` production lines are described as maintained but held outside the final V1 RC publication batch.
  - Updated `open-source-nirs-tools.html` copy to match the same release/blocker state.

## Validation

- `nirs4all-cockpit`
  - `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
  - `python3.11 -m pytest -q tests/test_targets_topology.py`

- `nirs4all-org`
  - HTML parser smoke for `index.html` and `open-source-nirs-tools.html`
  - `git diff --check`

## Decisions

- Left `data/current.json` untouched because the committed snapshot already reflected the newer release facts; the drift was in inventory prose and public-site fallback copy.
- Kept the PyPI and R-universe blockers visible instead of smoothing them over in marketing copy.

## Remaining risks

- PyPI Trusted Publisher remains an external blocker for `nirs4all-core`, `nirs4all-providers`, `dag-ml`, and `dag-ml-data`.
- R-universe can still lag GitHub/PyPI/npm/crates after publication, so the public site and cockpit copy intentionally describe it as eventually consistent rather than exact-current.
