# Wave 2Z dag-ml-data Python Binary Freshness

Date: 2026-07-01T18:35:00+02:00

## Scope

Follow-up after W2Y. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2Z targets the release blocker found by Carson:

- `dag-ml-data` had a dirty tracked Python extension:
  `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`.
- The tracked `HEAD` binary was older than current tracked Rust sources.
- The preexisting dirty binary did not match a freshly built release wheel.

The lane resolves this by replacing the tracked source extension with the
extension extracted from a freshly built `dag_ml_data-0.2.2` release wheel.

## Starting State

- `dag-ml-data`: `818616e` on `refactor/L20-lockstep`.
- Dirty tracked file:
  `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`.
- Preexisting dirty worktree binary:
  - size: `2051128`
  - Build ID: `ece44a158a7c32afaa0e8dbf21ba878fc08e1ed2`
- Tracked `HEAD` binary:
  - size: `2046976`
  - Build ID: `b2cf77a1e1378fe4ff0242c067ec71d4b2651ddb`

## Implementation

Coordinator built a fresh release wheel:

```bash
(cd crates/dag-ml-data-py && maturin build --release --features extension-module --out ../../target/wheels)
```

Then extracted the wheel extension into the tracked source path:

```bash
unzip -p target/wheels/dag_ml_data-0.2.2-cp311-abi3-manylinux_2_34_x86_64.whl dag_ml_data/_dag_ml_data.abi3.so > crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so
```

Resulting tracked source extension:

- size: `2062960`
- SHA-256: `b339b416b5a3a0a3c37de825b5ba0bc7fe30d736d4b0ed84e3ed2cd4495fe94a`
- Build ID: `0607f546ad696f0f8b8dab55893e0be202bffa27`

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| G/A | coordinator | `dag-ml-data` binary artifact only; ecosystem report | Rebuild/extract verified Python extension, run focused gates. |
| K | Singer | read-only `dag-ml-data` diff | Final reviewer for binary freshness change; approved commit after noting wheel cache hygiene. |

## Gates Run

- PASS: `PYO3_PYTHON=python3.11 cargo test --manifest-path crates/dag-ml-data-py/Cargo.toml`
  - 4 passed.
- PASS: local source import smoke:
  `PYTHONPATH=crates/dag-ml-data-py/python python3.11 ...`
  - version `0.2.2`, crate `dag-ml-data`, built-in model count `26`.
- PASS: installed wheel smoke:
  `/tmp/w2z-dag-ml-data-wheel-venv/bin/python scripts/smoke_python_bindings.py`
- PASS: `python3.11 scripts/smoke_python_wheel_metadata.py target/wheels/dag_ml_data-0.2.2-cp311-abi3-manylinux_2_34_x86_64.whl`
- PASS: `python3.11 scripts/validate_release_metadata.py`
- PASS: `python3.11 scripts/release/check_publish_plan.py`
- PASS: `python3 scripts/validate_contracts.py --sibling-root /home/delete/nirs4all/dag-ml`
  from `dag-ml-data`.
- PASS: `python3 scripts/validate_contracts.py --sibling-root /home/delete/nirs4all/dag-ml-data`
  from `dag-ml`.
- PASS: clean wheel provenance rerun after removing ignored `__pycache__`:
  `target/w2z-clean-wheels/dag_ml_data-0.2.2-cp311-abi3-manylinux_2_34_x86_64.whl`
  - `python3.11 scripts/smoke_python_wheel_metadata.py ...` passed.
  - Extracted extension SHA-256 matched the tracked `.so` exactly:
    `b339b416b5a3a0a3c37de825b5ba0bc7fe30d736d4b0ed84e3ed2cd4495fe94a`.
  - Clean wheel contained no `__pycache__` entries.

## Review

Singer findings: no blockers. The `.so` is already a tracked artifact, the diff
is limited to that file, and the refreshed artifact matches the freshly built
0.2.2 wheel extension exactly. Residual non-blocking risk: absolute build paths
exist in the binary, but this was already true for the previous tracked binary.

## Integration

- `dag-ml-data` commit:
  `e681685 chore(py): refresh dag-ml-data abi3 extension`.
- `_worktrees/INT-dmd` was fast-forwarded to `e681685`, keeping the selected
  release root clean.
- `docs/contracts/release/aggregation-lock.n4a.lock.json` was regenerated from
  `_release_roots/W2L-selected`.
  - Diff is limited to the `dag_ml_data` commit pin:
    `818616e9a2c28ae940b9a21543d666c058361dfb` ->
    `e6816854365350722777056ccfc8d26184940ef1`.
  - Shared contract artifact hashes remain unchanged.

## Post-Integration Gates

- PASS: `python3 -B scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_release_roots/W2L-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
- PASS: `python3 -B scripts/n4a_release_surface_matrix.py validate`
- PASS: `python3 -B -m pytest tests/test_release_surface_matrix.py tests/test_release_lock.py tests/test_cutover_state_gate.py -q`
  - 13 passed.

Raw workspace release-lock validation still fails because the raw workspace does
not match the selected release root, notably `nirs4all-io` raw checkout versus
`INT-io`. This is now a workspace-selection issue, not a dirty `dag-ml-data`
binary issue.

## Deferred Gates

- Full `cargo test --workspace` and Cargo clippy/fmt were not rerun for this
  binary-only PyO3 artifact refresh.
- `pyref_oracle_full` is intentionally deferred.
