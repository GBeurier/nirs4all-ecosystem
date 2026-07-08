# WAVE 9Y - Methods/Core 0.3.4/1.0.7 Release Lock

## Scope

Finalize the no-legacy MATLAB/Octave namespace release chain for
`nirs4all-methods` and `nirs4all-core`, then refresh the ecosystem lock.

## Modified Files

- `nirs4all-methods`: removed the live MATLAB/Octave `+pls4all` namespace in
  favor of `+n4m`; aligned R/MATLAB build environment variables on `N4M_*`;
  corrected MATLAB/Octave packaging documentation; bumped and tagged `v1.0.7`.
- `nirs4all-core`: repinned methods to `nirs4all-methods@v1.0.7`; removed
  `PLS4ALL_*` runtime/build fallbacks from core parity paths; bumped and tagged
  `v0.3.4`.
- `nirs4all-ecosystem`: updated `nirs4all-core` and `nirs4all-methods`
  submodule pointers; updated `aggregation-manifest.n4a.json`; regenerated
  `aggregation-lock.n4a.lock.json`.
- `nirs4all-cockpit`: refreshed status tracking for `nirs4all-core@v0.3.4`
  and `nirs4all-methods@v1.0.7`, then advanced the ecosystem submodule pointer.

## Tests And Gates

- `nirs4all-methods`: `scripts/bump_version.sh --check`; catalog selftest and
  validation; cross-binding parity-gate unit tests.
- `nirs4all-methods@f789b960`: GitHub Actions all green before the release bump,
  including CI, ABI Surface, Parity gate, and Cross-binding parity.
- `nirs4all-core`: `scripts/bump_version.sh --check`; Python unittest discover;
  `tests/test_run_multimodal_roundtrip_env.py`; `cargo test -p nirs4all`.
- `nirs4all-core@bfb3ba7`: GitHub Actions CI and version-guard green before the
  release bump.
- `nirs4all-ecosystem`: release lock generated and validated from clean temporary
  clones; fetchability audit checked out `7/7` member commits.
- `nirs4all-cockpit`: `python3.11 -m pytest -q`; dashboard DOM smoke; targets
  validation. The manual blockers section remains below all dashboard sections
  and above the footer.

## Decisions

- No MATLAB/Octave legacy alias is kept for V1: the methods namespace is `+n4m`.
- Python/R `pls4all` remains a slim published subset distribution, not a
  MATLAB namespace alias; removing it requires a separate methods/core API
  migration.
- Full parity suites remain reserved for larger batches; this wave ran targeted
  parity gates plus CI-backed cross-binding gates.

## Risks / Follow-Up

- `nirs4all-methods@v1.0.7` and `nirs4all-core@v0.3.4` publication workflows
  are running and must be monitored to completion.
- Local WASM npm testing in WSL was blocked by the Windows `npm` binary using a
  UNC working directory; Linux CI is the authoritative gate for that surface.
