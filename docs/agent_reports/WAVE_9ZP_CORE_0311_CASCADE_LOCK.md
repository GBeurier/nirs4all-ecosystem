# WAVE 9ZP - Core 0.3.11 cascade lock

## Scope

- Integrated the published `nirs4all-core` `v0.3.11` release into the ecosystem release lock.
- Advanced ecosystem gitlinks for `nirs4all-core`, `nirs4all-web`, `nirs4all-org`, and `nirs4all-cockpit` to the selected published heads.
- Refreshed E2E contract references for the MATLAB/Octave release gate and published custom-app host smoke.

## Files changed

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `scripts/e2e/verify_core_matlab_octave_release_gate.py`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_release_lock.py`
- `tests/test_e2e_scenarios.py`
- submodules: `nirs4all-core`, `nirs4all-web`, `nirs4all-org`, `nirs4all-cockpit`

## Tests run

- `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- `python3 scripts/n4a_release_surface_matrix.py --matrix docs/contracts/release/public-v1-surface-matrix.n4a.json --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json validate`
- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py --artifacts-dir .n4a-e2e-artifacts evidence-ledger --out /tmp/n4a-latest-runtime-evidence-ledger.check.json`
- `python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_release_lock.py tests/test_gitmodules_topology.py`

Result: 11/11 E2E scenarios verified, 71 artifacts checked, 151 pytest tests passed.

## Decisions

- Kept Python `nirs4all` production and `nirs4all-studio` production outside this release cascade.
- Treated `nirs4all-core v0.3.11` as the selected portable aggregate head for release-lock purposes.
- Left R-universe/CRAN as manual downstream actions; the current lock only proves the selected core release and tracked runtime artifacts.

## Risks

- R-universe still needs the external merge/rebuild before it can report `nirs4all 0.3.11`.
- MATLAB/Octave parity is proven through the public `release-matlab` workflow evidence, not by a fresh local Windows/MATLAB run.
