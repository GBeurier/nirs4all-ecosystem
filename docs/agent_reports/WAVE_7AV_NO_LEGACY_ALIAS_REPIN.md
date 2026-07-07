# Wave 7AV - No Legacy Alias Repin

Date: 2026-07-07

## Scope

- Apply the user decision that no public legacy alias has to be kept for the
  core aggregate.
- Repin only the ecosystem submodules that changed after the public cockpit and
  site cleanup.
- Keep the concurrent `nirs4all-ui` / `nirs4all-quality` work untouched.
- Keep `nirs4all` Python and `nirs4all-studio` production releases out of scope.

## Files changed

- `nirs4all-cockpit` submodule pointer
- `nirs4all-org` submodule pointer
- `docs/agent_reports/WAVE_7AV_NO_LEGACY_ALIAS_REPIN.md`

## Integrated heads

- `nirs4all-cockpit`: `04f51e5` -> `76b2766`
  - `fix(collect): prefer public manifests over dirty checkouts`
  - `chore(targets): drop legacy core alias target`
  - collect refresh commits for `data/current.json`
- `nirs4all-org`: `9dc6119` -> `0257215`
  - `docs(site): remove legacy lite alias copy`

## Decisions

- `nirs4all-lite` is no longer tracked as a public release target in the
  cockpit.
- The public site no longer advertises the old alias path.
- The aggregation manifest and lock were not regenerated in this batch because
  they do not include `nirs4all-cockpit` or `nirs4all-org` as lock members.
- The `nirs4all` submodule is intentionally left in manual-review state because
  that production repo remains outside the current release push.

## Tests run

- `python3.11 scripts/n4a_submodule_repin.py plan --json`
  - Result: `19` up to date, `0` fast-forward remaining, `1` manual-review
    submodule (`nirs4all`, intentionally held).
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - Result: `OK: 11 cross-language E2E scenarios`.
- `python3.11 -m pytest -q tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py tests/test_e2e_scenarios.py`
  - Result: `149 passed`.
- `python3.11 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-lock-selected-7av-PD9ZiZ`
- `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-selected-7av-PD9ZiZ validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - Result: validated `docs/contracts/release/aggregation-lock.n4a.lock.json`.
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output-json /tmp/n4a-lock-fetchability-7av.json --fail-on-unfetchable`
  - Result: `7/7` members fetchable, `0` unfetchable.

## Risks

- This batch does not run full parity; it is a topology/publication-state repin.
- Internal package imports may still keep backward-compatible Python module
  names until a dedicated API-breaking cleanup is reviewed.
