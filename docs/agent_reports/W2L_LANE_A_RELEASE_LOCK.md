# W2L Lane A Release Lock

Date: 2026-07-01

## Agent

Codex Lane A release-lock/topology post-reset.

## Lane

Lane A: `nirs4all-ecosystem` only, release manifest/lock tooling and docs.

## Files modified

- `docs/agent_reports/W2L_LANE_A_RELEASE_LOCK.md`

No implementation repository was modified. The central aggregation lock was not
regenerated. This new report path is ignored by the repository-level `/docs/`
ignore rule and will need `git add -f` if the coordinator wants it tracked.

## Evidence

- Required docs read: root `AGENTS.md`, root `CLAUDE.md`,
  `docs/agent_reports/WAVE_2L_POST_RESET_CONTROL.md`,
  `docs/agent_reports/WAVE_2K_CONTROL.md`,
  `docs/contracts/release/aggregation-manifest.n4a.json`,
  `docs/contracts/release/aggregation-lock.n4a.lock.json`, and
  `/home/delete/nirs4all/RELEASE_DISTRIBUTION_INVENTORY.md`.
- Current-checkout validation failed:
  `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  returned `error: lockfile is stale or inconsistent`.
- A temporary current-checkout lock was generated at
  `/tmp/n4a-current.lock.json` for comparison only. It pins
  `dag_ml=4f0a3b5a7a96`, `dag_ml_data=2214f75aa3c7 dirty=true`,
  `io=5651da51fe74`, `lite=0486e1fc255f`,
  `methods=469124855ff1`, `datasets=ac455f321144`, and
  `formats=89231b2786ef`.
- A temporary W2K clean workspace was built in `/tmp/n4a-w2k-root` using
  `INT-dagml`, `INT-dmd`, `INT-io`, and current `main` for lite/methods/datasets.
  Its generated lock `/tmp/n4a-w2k.lock.json` validates successfully.
- Checked-in lock stale pins versus the W2K clean candidate:
  `dag_ml f58d7bf7098178b -> 618ffb220b5f5`,
  `dag_ml_data 347c15f69fab -> 818616e9a2c2`,
  `io 84ab189317d8 -> e52eecd827a0`,
  `lite c14dcca88fe6 -> 0486e1fc255f`,
  `methods 7602eb08f9a6 -> 469124855ff1`,
  `datasets ae414964554e -> ac455f321144`.
  `formats` commit is unchanged at `89231b2786ef`; it differs only because the
  current tool records `read_from=tracked_worktree` version metadata.
- Manifest digest changed from
  `sha256:84b2150a142fcdec719069feeb54b7d05fcb436a6558a65d41960a477e54ae6f`
  to
  `sha256:940b7dd67aef23fe721bd325dcf4eeb3ddab47af62e5a7b5b898a2ea3c713dd0`.
- The manifest now requires `lite_release_topology_manifest`; the checked-in
  lock has no lite contract artifact. The W2K candidate collects
  `release_topology_manifest` from `HEAD:bindings/python/src/nirs4all_lite/_topology.py`
  with schema `nirs4all-lite.release-topology.v1`,
  raw sha `sha256:5a754141b588185a6a50963f847d8afb2ff32c5d40529d095825d79485841630`,
  and canonical JSON sha
  `sha256:7529158d18ff54415b668b17b8f27712891c0857d4bba2433e6ef4d84a03476c`.
- `nirs4all-lite/main` contains W2K lane commits `d9d92d7`, `a08d91a`, and
  `6c08b92`; current head is `0486e1fc255f` and is clean.
- `nirs4all-methods/main` contains W2K lane commit `d077ea5f` and merge
  `46912485`; current head is `469124855ff1` and is clean.
- `nirs4all-datasets/main` contains W2K lane commits `20b41824`, `028fb1d7`,
  and `ac455f32`; current head is `ac455f321144` and is clean.
- Dirty blockers: `dag-ml-data/refactor/L20-lockstep` has modified generated
  binary `crates/dag-ml-data-py/python/dag_ml_data/_dag_ml_data.abi3.so`.
  `nirs4all/refactor/L17-pyref` is also dirty, but it is not a member of the
  current aggregation manifest.
- `RELEASE_DISTRIBUTION_MATRIX.md` is absent under `nirs4all-ecosystem/docs`.
  The only local substitute found is
  `/home/delete/nirs4all/RELEASE_DISTRIBUTION_INVENTORY.md`.

## Tests/gates run

- `pytest -q tests/test_release_lock.py`: `5 passed in 0.13s`.
- Current checked-in lock validation against `/home/delete/nirs4all`: failed
  with `lockfile is stale or inconsistent`.
- Temporary W2K generated lock validation:
  `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-w2k-root validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock /tmp/n4a-w2k.lock.json`:
  `validated /tmp/n4a-w2k.lock.json`.
- Checked-in lock validation against `/tmp/n4a-w2k-root`: failed with
  `lockfile is stale or inconsistent`, confirming the central lock is stale
  even against clean W2K-selected heads.

## Risks

- Regenerating the central lock from the current local workspace would record
  `dag_ml_data dirty=true`, so it should not be used as final release evidence.
- Regenerating from W2K integration heads is mechanically clean, but it still
  requires an explicit selection decision for `dag-ml`, `dag-ml-data`, and
  `nirs4all-io` because the main checkouts are not on those integration heads.
- The root distribution inventory is outside `nirs4all-ecosystem`; relying on
  it by memory creates path drift in future agent prompts.

## Decisions needed

- Select final release pins: use the clean W2K integration heads
  `dag_ml=618ffb220b5f5`, `dag_ml_data=818616e9a2c2`,
  `io=e52eecd827a0`, plus `lite=0486e1fc255f`,
  `methods=469124855ff1`, `datasets=ac455f321144`,
  `formats=89231b2786ef`, or first merge/reset the local main checkouts to
  those heads.
- Decide how to handle the dirty `dag-ml-data` generated binary in the live
  checkout. Do not final-lock from that checkout until it is clean or replaced
  by the clean `INT-dmd` head.
- Handle `RELEASE_DISTRIBUTION_MATRIX.md` absence by creating a short tracked
  pointer at `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md` to the
  root inventory, rather than renaming the root draft or silently documenting
  the substitution only in agent reports.

## Recommended integration steps

1. Keep the central lock unchanged until the coordinator selects clean final
   pins.
2. Prefer the W2K clean candidate heads listed above for final lock generation,
   or first make the corresponding main checkouts match them cleanly.
3. After final pin selection, run
   `python3 scripts/n4a_release_lock.py --workspace-root <selected-root> generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`.
4. Rerun
   `python3 scripts/n4a_release_lock.py --workspace-root <selected-root> validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
   and `pytest -q tests/test_release_lock.py`.
5. Add the distribution-matrix pointer doc in `nirs4all-ecosystem/docs` before
   launching more release-topology agents that reference that path.
