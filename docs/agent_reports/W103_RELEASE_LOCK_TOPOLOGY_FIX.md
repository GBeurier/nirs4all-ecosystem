# W103 Release Lock Topology Fix

Date: 2026-07-01

## Scope

Fixed central ecosystem release-lock handling for W101's release/topology
findings. No implementation repositories were edited, and the final aggregation
lock was not regenerated.

## Reproduced

The W101 central lock validation failure reproduces from
`/home/delete/nirs4all/nirs4all-ecosystem`:

```bash
python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json
```

Result: `error: lockfile is stale or inconsistent; regenerate ...`

## Changes

- `scripts/n4a_release_lock.py`
  - Version sources are now required to be git-tracked by default. Ignored or
    untracked paths, including stale generated package directories, raise a
    release-lock error instead of being read silently.
  - Version entries record `read_from: tracked_worktree` and preserve optional
    manifest annotations such as `distribution`, `module`,
    `generated_by`, and `generated_output_path`.
  - Added `python_function_json` contract artifacts. These read committed
    `HEAD:<path>` source via git, validate imports against an allow-list, execute
    the named function, and hash the canonical JSON result. Dirty working-tree
    Python code is not imported as release evidence.

- `docs/contracts/release/aggregation-manifest.n4a.json`
  - `methods.python_nirs4all_methods` and `methods.python_pls4all` now read the
    tracked `bindings/python/pyproject.toml` version and annotate the generated
    output paths that must not be used as release-lock sources.
  - `lite` now declares `lite_release_topology_manifest` as a required gate.
  - `lite` now declares `release_topology_manifest` as a `python_function_json`
    contract artifact from
    `bindings/python/src/nirs4all_lite/_topology.py`, read from git `HEAD`.

- `tests/test_release_lock.py`
  - Added focused tests for ignored generated metadata rejection, tracked methods
    metadata annotations, git-HEAD topology collection that ignores dirty
    worktree changes, import allow-list enforcement, and central manifest wiring.

## Fact Checks

A temporary generation to `/tmp/w103-aggregation-lock.n4a.lock.json` succeeds
without writing the committed lock. It shows:

- methods Python versions now come from tracked
  `bindings/python/pyproject.toml` and report `1.0.1` for both
  `nirs4all-methods` and `pls4all`;
- lite's topology artifact is `missing: true` in the current main lite checkout
  because W94's `_topology.py` is not selected there;
- the W94 worktree's committed topology manifest is consumable by the new
  artifact collector and reports schema
  `nirs4all-lite.release-topology.v1`, aggregate `nirs4all-lite`,
  future target `nirs4all-core`, additive imports `n4a` and
  `nirs4all_core`, 13 install distributions, 6 upstream components, and
  license expression `CeCILL-2.1 OR AGPL-3.0-or-later`.

## Verification

- `python3 -m pytest tests -q` -> 7 passed.
- `python3 -m pytest tests/test_release_lock.py -q` -> 5 passed.
- `python3 -m py_compile scripts/n4a_release_lock.py tests/test_release_lock.py`
  -> passed.
- `python3 -m ruff check scripts/n4a_release_lock.py tests/test_release_lock.py`
  -> passed.
- `python3 -m json.tool docs/contracts/release/aggregation-manifest.n4a.json`
  -> passed.
- Temporary lock generation:
  `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output /tmp/w103-aggregation-lock.n4a.lock.json`
  -> passed.
- `git diff --check` -> passed.
- Expected stale-lock check:
  `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> failed with `lockfile is stale or inconsistent`.

## Remaining Blockers

The committed aggregation lock still intentionally fails validation. I did not
regenerate it because current heads are not final release heads and
`dag-ml-data` is still dirty. Current temporary-lock evidence includes:

- `dag_ml`: `refactor/L20-lockstep@4f0a3b5`, not the committed lock's pinned
  `main@f58d7bf`.
- `dag_ml_data`: `refactor/L20-lockstep@2214f75`, dirty, not the committed
  lock's pinned clean `main@347c15f`.
- `io`: `refactor/L7-io-dagml-sibling@5651da5`, not the committed lock's pinned
  `main@84ab189`.
- `lite`: current main `c14dcca` lacks W94's committed topology artifact; final
  validation needs the W94 head or an equivalent merged head selected.

Final release validation should select clean final member heads, include the W94
lite topology head, resolve the dirty `dag-ml-data` artifact, and then regenerate
the aggregation lock once.
