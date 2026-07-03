# Wave 4AL - Language topology audit

Date: 2026-07-03
Lane: E/Core language topology
Agent: Codex

## Scope

Audit limited to:

- `_worktrees/RC-v1-nirs4all-core`
- `_worktrees/RC-v1-cockpit`
- `_worktrees/RC-v1-ecosystem/docs/agent_reports/WAVE_4AL_LANGUAGE_TOPOLOGY_AUDIT.md`

`_worktrees/RC-v1-lite` does not exist in this workspace. `git worktree list`
shows the `nirs4all-lite` repository's RC worktree as
`_worktrees/RC-v1-nirs4all-core`, so this audit treats that path as the
core/lite RC surface. `nirs4all-drafts` and `nirs4all-lab` were not inspected
or modified.

## Findings

- Core aggregate representation is explicit and machine-checked. The
  `nirs4all-core` README, `docs/NAMING.md`,
  `bindings/python/src/nirs4all_lite/_topology.py`, and
  `compat/capabilities.toml` declare Python, Rust, JavaScript/WASM, R, and
  MATLAB/Octave. The Python release topology tests enforce the V1 release
  surfaces and the static cross-language/capability gates enforce all five
  bindings.
- Ecosystem release accounting is explicit. The public V1 surface matrix
  requires `nirs4all.python.oracle`, `nirs4all.python.core`,
  `nirs4all.r.aggregate`, `nirs4all.javascript_wasm.aggregate`,
  `nirs4all.rust.aggregate`, and `nirs4all.matlab_octave.aggregate`, plus the
  scoped WASM methods/datasets packages. The aggregation manifest/lock keep the
  locked member key `lite` on repo path `nirs4all-lite` while declaring
  `nirs4all-core` as the target aggregate and `nirs4all-matlab-octave` as the
  MATLAB/Octave archive.
- Naming is release-honest on the current RC heads:
  - `nirs4all-core` is the Python aggregate distribution for RC V1.
  - `nirs4all-lite` remains the current repo/submodule path and legacy Python
    distribution until external GitHub/PyPI/RTD admin actions complete.
  - bare Python `nirs4all` remains the full Python oracle package, not the
    aggregate import.
  - non-Python aggregate packages use the idiomatic `nirs4all` name, except the
    MATLAB/Octave release archive name `nirs4all-matlab-octave`.
- Cockpit already tracked Python/Rust/npm/R for the logical `nirs4all-core`
  package. I made the existing GitHub Release row explicitly document that it
  carries the MATLAB/Octave archive artifacts, without inventing a duplicate
  target that the collector cannot validate at asset granularity.

## Files modified

`_worktrees/RC-v1-cockpit`:

- `ops/targets.yaml` - added release metadata explaining that the
  `nirs4all-lite` GitHub Release row carries source/SBOM and MATLAB/Octave
  archive artifacts audited by core topology.
- `tests/test_targets_topology.py` - added assertions that cockpit accounts for
  the five V1 language surfaces: Python, Rust, JavaScript/WASM, R, and
  MATLAB/Octave.

`_worktrees/RC-v1-ecosystem`:

- `docs/agent_reports/WAVE_4AL_LANGUAGE_TOPOLOGY_AUDIT.md` - this report.

No `RC-v1-nirs4all-core` files were modified.

## Tests run

`_worktrees/RC-v1-cockpit`:

- `/home/delete/nirs4all/nirs4all-cockpit/.venv/bin/python -m pytest tests/test_targets_topology.py -q` - 4 passed.
- `/home/delete/nirs4all/nirs4all-cockpit/.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml` - OK, 21 packages, 94 targets.
- `/home/delete/nirs4all/nirs4all-cockpit/.venv/bin/python -m ruff check tests/test_targets_topology.py` - passed.

`_worktrees/RC-v1-nirs4all-core`:

- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py bindings/python/tests/test_cross_language_surface.py bindings/python/tests/test_capability_matrix.py -v` - 27 tests passed.

`_worktrees/RC-v1-ecosystem`:

- `python3 scripts/n4a_release_surface_matrix.py validate` - passed.
- `pytest tests/test_release_surface_matrix.py -q` - 6 passed.
- `python3 -m py_compile scripts/n4a_release_surface_matrix.py` - passed.

## Not run

- No full parity gates or long cross-runtime parity suites.
- R and Octave local runtime gates were not run.

## Risks

- External admin work remains pending: GitHub repo rename
  `GBeurier/nirs4all-lite` -> `GBeurier/nirs4all-core`, PyPI
  `nirs4all-core` Trusted Publisher/first publish, final `nirs4all-lite` alias
  release, and RTD slug/repo URL cleanup.
- Some older strategic roadmap documents still contain historical
  "temporary nirs4all-core clone" wording. The current release authority is the
  core topology manifest plus the ecosystem public surface matrix/aggregation
  lock; do not use those older paragraphs as the RC V1 naming source of truth.
- The cockpit GitHub Release collector is release-level, not asset-level. It can
  account for the MATLAB/Octave archive release surface, but it does not prove a
  specific archive asset exists; core release topology/parity gates own that
  proof.

## Decisions

- No core correction was needed.
- Keep `nirs4all-lite` visible as legacy/current repo path while making
  `nirs4all-core` the logical RC aggregate name. This avoids falsely implying
  that external registry/repo rename actions are already complete.
- Do not introduce public names such as `nirs4all-core-r` or
  `nirs4all-core-wasm`; use the governed per-language names already encoded by
  core topology.
- Treat `nirs4all-python` as an architectural description of the full Python
  product, not as a current release package name.
