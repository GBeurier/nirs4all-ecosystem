# Wave 3E - Lite Public nirs4all Surfaces

Date: 2026-07-01T18:48:22+02:00

## Scope

Lane E/A focused batch on the public `nirs4all` V1 surface accounting:

- keep the roadmap and public surface matrix explicit for Python `nirs4all`,
  R `nirs4all`, and browser/WASM `nirs4all`;
- preserve the Python boundary: `nirs4all-lite` publishes Python
  `nirs4all-lite`, while the historical Python package `nirs4all` remains the
  Tier-1 oracle and reserved namespace;
- gate R/npm release workflows on strict parity against a pinned
  `nirs4all-methods` checkout, not an implicit upstream default branch;
- wire the ecosystem version guard to validate the public V1 surface matrix.

No full parity run in this batch.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Godel | Read-only R/WASM public surface audit in `nirs4all-lite` | done | Confirmed R and WASM surfaces exist; found release workflows were not strict-parity gated. |
| Boole | Read-only Python/public matrix audit across `nirs4all-lite` and ecosystem | done | Confirmed required IDs include Python/R/WASM `nirs4all`; found `version-guard` did not run the matrix validator. |
| Carver | W3E reviewer | done | First review blocked unpinned `nirs4all-methods` checkout. Follow-up review approved after `compat/upstreams.toml` pin and YAML/TOML topology tests. |

## Decisions

- Public V1 accounting remains three-part for the `nirs4all` name:
  - Python `nirs4all` is the historical/oracle package and stays outside the
    aggregation lock.
  - R `nirs4all` is emitted by the locked `nirs4all-lite` member.
  - browser/WASM `nirs4all` is emitted by the locked `nirs4all-lite` member,
    with scoped WASM packages tracked separately where applicable.
- `release-npm.yml` now runs strict WASM parity before pack/publish.
- `release-r.yml` now runs strict R parity before building the release tarball.
- Both strict release jobs checkout `GBeurier/nirs4all-methods` from
  `compat/upstreams.toml` via a pinned SHA.
- `version-guard.yml` now validates `public-v1-surface-matrix.n4a.json` and
  its tests, in addition to release-lock JSON/tool syntax.

## Files Changed

`nirs4all-lite`:

- `.github/workflows/release-npm.yml`
- `.github/workflows/release-r.yml`
- `bindings/python/tests/test_release_topology.py`
- `compat/upstreams.toml`

`nirs4all-ecosystem`:

- `.github/workflows/version-guard.yml`
- `docs/agent_reports/WAVE_3E_LITE_PUBLIC_SURFACES.md`

## Gates

- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py -v` - 10 passed.
- `make test-python` - 36 tests passed, 1 skipped.
- `make test-r-fixtures` - passed.
- PyYAML parse of `release-npm.yml`, `release-r.yml`, and `version-guard.yml` - passed.
- TOML parse of `compat/upstreams.toml` methods pin - passed.
- `python3 -m py_compile scripts/n4a_release_lock.py scripts/n4a_release_surface_matrix.py` - passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` - passed.
- `python3 scripts/n4a_release_surface_matrix.py report` - passed; report lists Python `nirs4all`, R `nirs4all`, and browser/WASM `nirs4all`.
- `python3 -m pytest tests/test_release_surface_matrix.py -q` - 4 passed.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` - passed.
- `git diff --check` in `nirs4all-lite` and `nirs4all-ecosystem` - passed.

## Risks

- Local full parity was intentionally not run; the new strict R/WASM parity jobs
  are CI release gates.
- Local WSL environment has no Linux `node`, and `npm` resolves to Windows npm
  over a UNC path, so `npm test --prefix bindings/wasm` locally discovered 0
  tests and was not counted as proof.
- Local `R` and Octave are not installed, so R CMD check and MATLAB/Octave
  parity remain CI/toolchain gates for this batch.
- The pinned `nirs4all-methods` SHA must be pushed before release workflows can
  checkout it from GitHub.
