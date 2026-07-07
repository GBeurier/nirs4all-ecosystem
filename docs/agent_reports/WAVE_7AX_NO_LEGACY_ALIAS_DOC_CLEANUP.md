# Wave 7AX - No Legacy Alias Doc Cleanup

Date: 2026-07-07

## Scope

- Documentation-only cleanup in `nirs4all-ecosystem/docs/agent_reports`.
- `nirs4all-ui`, `nirs4all-quality`, `nirs4all`, and `nirs4all-studio` were not modified.

## Changes

- Marked older coordination reports that mentioned a `nirs4all-lite` compatibility line as superseded by the later no-legacy-alias decision.
- Reworded cockpit/org topology copy so `nirs4all-lite` is described as a retired historical name, not a current release alias.
- Clarified that no final retired-name publication is required for the V1 RC target.

## Validation

- `python3.11 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`

## Risk

- This is documentation alignment only. Runtime/package alias guards remain enforced by `nirs4all-core`, `nirs4all-web`, and `nirs4all-cockpit` tests.
