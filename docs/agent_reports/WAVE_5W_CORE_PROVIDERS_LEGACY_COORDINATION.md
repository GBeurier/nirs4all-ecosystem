# Wave 5W - Core/providers legacy coordination

Date: 2026-07-04

## Scope

- `nirs4all-providers`: public docs/site install wording while PyPI Trusted Publisher is still pending.
- `nirs4all-org`: ecosystem HUD wording for `nirs4all-core` and `nirs4all-providers` RC/source state.
- `nirs4all-lite`: legacy checkout alignment with the completed `nirs4all-core` cutover.
- `nirs4all-ecosystem`: submodule pointer coordination.

## Integrated heads

- `nirs4all-providers`: `8c1c85e` (`docs(release): mark provider pypi publishing pending`)
- `nirs4all-org`: `436e1ea` (`docs(site): clarify core and providers rc install state`)
- `nirs4all-lite`: `96c392b` (`chore(core): align legacy lite metadata with core cutover`)
- `nirs4all-core`: unchanged at canonical `0df950a` / `v0.2.4`

## Review decisions

- Keep `nirs4all-core` as the canonical release repo and publication source.
- Keep `nirs4all-lite` as a legacy/compatibility line only; it now points metadata, docs, RTD URLs, upstream pins, and package versions at the current core cutover state.
- Do not tag or publish from `nirs4all-lite`. Its `release_guard.py` blocks canonical publish from the legacy repo.
- Add an explicit legacy skip in `nirs4all-lite` `version-guard.yml`, otherwise the legacy repo would fail on main because its remote tags stop before the canonical `v0.2.4` tag.
- Make public install text for providers source-checkout only until the PyPI Trusted Publisher exists.

## Tests run

- `nirs4all-providers`: `python3.11 scripts/ci_gate.py` passed.
- `nirs4all-providers`: `git diff --check` passed.
- `nirs4all-providers`: `index.html` parsed with Python `html.parser`.
- `nirs4all-org`: `git diff --check` passed.
- `nirs4all-org`: `index.html` parsed with Python `html.parser`.
- `nirs4all-lite`: `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py` passed, 16 tests.
- `nirs4all-lite`: `cargo test --workspace` passed, 8 tests.
- `nirs4all-lite`: `scripts/bump_version.sh --check` passed.
- `nirs4all-lite`: `git diff --check` passed.
- `nirs4all-lite`: `scripts/release_guard.py` checked for both `GBeurier/nirs4all-lite` and `GBeurier/nirs4all-core`.

## Not run

- `nirs4all-lite` WASM npm tests: local PATH exposes Windows npm in WSL.
- `nirs4all-lite` R checks: `Rscript` is not installed locally.
- Full parity suites: deferred until the next large integration batch.

## Risks / follow-up

- `nirs4all-core` PyPI remains blocked on Trusted Publisher setup for project `nirs4all-core`.
- `nirs4all-providers` PyPI remains blocked on Trusted Publisher setup for project `nirs4all-providers`.
- Providers Pages deployment initially failed with a GitHub Pages deployment retry error after a successful build; rerun is pending.
