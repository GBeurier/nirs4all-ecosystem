# Wave 7AN — canonical patch releases, lock, cockpit

Date: 2026-07-07

## Scope

- Published/tagged canonical main heads for `nirs4all-core` and `nirs4all-formats`.
- Repointed the aggregation manifest/lock away from superseded RC worktrees and onto canonical main checkouts with exact semver tags.
- Refreshed `nirs4all-cockpit` inventory, manual actions, and public snapshot after the release batch.
- Did not touch `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, or `nirs4all-lab`.

## Files Modified

- `nirs4all-core`: version manifests only, committed as `38f5363 chore(release): bump core to 0.2.13`, tag `v0.2.13`.
- `nirs4all-formats`: version manifests only, committed as `6c5ad98 chore(release): bump formats to 0.2.3`, tag `v0.2.3`.
- `nirs4all-ecosystem/docs/contracts/release/aggregation-manifest.n4a.json`
- `nirs4all-ecosystem/docs/contracts/release/aggregation-lock.n4a.lock.json`
- `nirs4all-ecosystem/tests/test_release_lock.py`
- `nirs4all-cockpit/ops/targets.yaml`
- `nirs4all-cockpit/ops/manual-actions.yaml`
- `nirs4all-cockpit/data/current.json`
- `nirs4all-cockpit/tests/test_targets_topology.py`

## Tests And Gates

- `nirs4all-core`: `cargo test --workspace`; `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests`; `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH npm test --prefix bindings/wasm`.
- `nirs4all-formats`: `cargo fmt --all --check`; `cargo test --workspace`; `cargo clippy --workspace --all-targets -- -D warnings`; `cargo build -p nirs4all-formats --no-default-features`.
- `nirs4all-ecosystem`: `scripts/n4a_release_lock.py validate`; `scripts/n4a_release_surface_matrix.py validate`; `pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py`.
- `nirs4all-cockpit`: `n4a-cockpit validate-targets ops/targets.yaml`; `n4a-cockpit collect --out data/current.json`; `pytest -q`; `ruff check .`.

## Publication State

- `nirs4all-core v0.2.13`: crates, npm, source, R, MATLAB workflows succeeded; Python failed on PyPI Trusted Publisher `invalid-publisher`.
- `nirs4all-formats v0.2.3`: crates, npm, source succeeded; R/release workflows were still propagating at the time of this report; PyPI may remain stale until Trusted Publisher/release propagation catches up.
- `dag-ml v0.2.5` and `dag-ml-data v0.2.5`: crates/npm succeeded; Python failed on PyPI Trusted Publisher `invalid-publisher`.
- `nirs4all-providers v0.2.7` and `nirs4all-tools v0.0.4`: GitHub releases exist; PyPI remains blocked by Trusted Publisher `invalid-publisher`.

## Decisions

- Kept the full Python `nirs4all` and `nirs4all-studio` production release lines held.
- Chose exact semver patch tags for `core`/`formats` even though a read-only audit noted the deltas were mostly tests/docs, because the release lock should not point at RC tags or floating untagged commits.
- Did not run the long full parity suite in this batch; only targeted release/lock/cockpit gates were run.

## Risks

- PyPI Trusted Publisher setup remains a human/account blocker for several packages.
- R-universe and registry propagation can leave cockpit targets stale for a while after successful release workflows.
- Dependabot branch CI failures observed during monitoring are not release blockers for canonical main/tag refs.
