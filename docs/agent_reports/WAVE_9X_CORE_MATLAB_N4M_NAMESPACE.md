# WAVE 9X - Core MATLAB n4m namespace

Date: 2026-07-08

## Scope

Aligned the `nirs4all-core` MATLAB/Octave aggregate runtime surface with the
canonical `nirs4all-methods` `+n4m` namespace.

## Files Modified

- `nirs4all-core` submodule pointer
- Upstream commit: `536c15a fix(matlab): use n4m methods namespace`

## Decisions

- Removed live `+pls4all` usage from `nirs4all-core` MATLAB runtime, parity gate, and topology metadata.
- Kept Python `pls4all.sklearn` as a known methods-backed dependency until `nirs4all-methods` exposes a canonical `n4m` estimator replacement with parity.
- Did not touch `nirs4all-ui`; concurrent quality work remains isolated.

## Validation

In `nirs4all-core`:

- `PYTHONPATH=bindings/python/src python3.11 -m unittest bindings.python.tests.test_cross_language_surface bindings.python.tests.test_release_topology bindings.python.tests.test_capability_matrix -q`
- `git diff --check`
- `rg` confirmed the only active core `pls4all` runtime dependency left is Python `pls4all.sklearn`.

In `nirs4all-ecosystem`:

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 -m pytest tests/test_e2e_scenarios.py -q`

## Risks

- Octave is not installed locally in this WSL environment, so MATLAB/Octave parity must be covered by CI or a Windows/Octave runner.
- Full removal of Python/R `pls4all` requires a coordinated `nirs4all-methods` migration.
