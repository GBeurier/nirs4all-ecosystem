# Wave 3AK - Release Reconciliation Audit

Date: 2026-07-01

## Scope

Follow-up on the W101 package/release review after several integration batches.
This was a read-mostly reconciliation pass: no old worktrees were merged, no
private repos were touched, and no full parity run was started.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Mencius the 2nd | W93 IO/datasets cross-repo adapter audit | done | Confirmed the real `NirsDataset` -> `nirs4all_io.load(..., target="dataset_package")` test already exists in datasets main, but is non-skipping only with the IO integration checkout. |
| McClintock the 2nd | W92 methods release-lock source audit | done | Confirmed W92 is integrated locally and central manifest now reads tracked methods metadata, not ignored generated package dirs. |
| Boyle the 2nd | W94 lite topology/license audit | done | Confirmed lite topology and R license metadata are integrated locally and central topology consumption already exists. |

## Current Findings

### W92 Methods

- Local `nirs4all-methods/main` includes W92 through merge `46912485`.
- Central `aggregation-manifest.n4a.json` now reads tracked methods metadata,
  notably `bindings/python/pyproject.toml`, instead of ignored generated
  package directories.
- `scripts/n4a_release_lock.py` has tracked-source validation for version
  sources.
- Remaining risk is procedural: W92 is local and not on `origin/main` at the
  time of this audit.

Validation:

- `nirs4all-ecosystem`: `python3 -m pytest -p no:cacheprovider tests/test_release_lock.py -q` -> 8 passed.
- `nirs4all-methods`: `PYTHONPATH=bindings/python/src python3 -m pytest -p no:cacheprovider bindings/python/tests/test_release_surface_metadata.py -q` -> 1 passed.

### W93 IO/Datasets

- `nirs4all-datasets/main` includes the real combined adapter test:
  `tests/test_dataset.py::test_nirs4all_io_load_accepts_real_reference_dataset`.
- The test is meaningful only when importing the Python MVP/integration IO
  checkout, because IO `main` still lacks `to_dataset_package` and the
  duck-typed `to_io_spec()` adapter.
- No new datasets patch is needed; release evidence still depends on selecting
  and publishing the W93/integration IO head.

Validation:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/delete/nirs4all/nirs4all-io/src:/home/delete/nirs4all/nirs4all-datasets/src /home/delete/nirs4all/nirs4all-datasets/.venv/bin/python -m pytest -p no:cacheprovider tests/test_dataset.py::test_nirs4all_io_load_accepts_real_reference_dataset -q` -> 1 passed.

### W94 Lite

- `nirs4all-lite/main` contains W94 topology plus the later R license metadata
  fix.
- The central release manifest declares the lite `release_topology_manifest`
  `python_function_json` artifact, and the lock embeds that topology JSON.
- Old W94 worktrees remain stale; they should not be treated as authoritative.

Validation:

- `nirs4all-lite`: `PYTHONPATH=bindings/python/src python3 -m unittest -v bindings/python/tests/test_release_topology.py` -> 12 tests passed.

### W97 Tools Goldens

- The W101 concern about placeholder fixture claims is already addressed in
  `nirs4all-tools/main`.
- `tests/fixtures/legacy/README.md` now labels `store.duckdb` as an opaque
  sentinel and `sample.meta.parquet` as a valid reduced Parquet sidecar.
- `tests/test_real_golden_fixtures.py::test_golden_mixed_workspace_fixture_labels_are_release_honest`
  locks those claims.

Validation:

- `nirs4all-tools`: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3.11 -m pytest tests/test_real_golden_fixtures.py::test_golden_mixed_workspace_fixture_labels_are_release_honest -q -p no:cacheprovider` -> 1 passed.

## Release-Lock Blocker

Live workspace validation still fails as stale/inconsistent:

- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> failed.

The selected-member checkout flow also cannot validate the current lock because
most locked commits are not fetchable from their remotes:

- `python3 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output <tmp>` -> failed first on `dag_ml` commit `a428926cf8b412ebe30931a6e5349c73d4f4c764`.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output-json /tmp/n4a-fetchability.json` -> `1/7` fetchable.

Unfetchable locked members:

- `dag_ml`: `a428926cf8b412ebe30931a6e5349c73d4f4c764`
- `dag_ml_data`: `e6816854365350722777056ccfc8d26184940ef1`
- `datasets`: `44662562b0073afa08b350b0f360166ebc819a91`
- `io`: `7e90b4d2161caf990d87bccc872280b9acbb0587`
- `lite`: `786688d2ee4aec905c8deda17d0ec888d12c43ad`
- `methods`: `98148c14bbe548c23db8d68903c445de8d8b82b8`

Fetchable locked member:

- `formats`: `89231b2786efc13f357092c0779a396e429a3158`

## Decision

Do not regenerate the aggregation lock from the live workspace in this state.
The next release-lock action needs an explicit selected-member decision:

- either publish/fetchable-pin the current selected heads, then rerun
  `checkout-members` and lock validation;
- or intentionally select older remote-fetchable heads and accept the loss of
  local post-W101 fixes from the release claim.

Full parity remains deferred until after a larger selected-head batch, per user
guidance.
