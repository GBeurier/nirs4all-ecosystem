# Wave 4P - Release lock and provider gate refresh

Date: 2026-07-02
Coordinator: Codex

## Scope

Close the latest review findings without rerunning full Python parity:

- make the providers CI gate fail on canonical contract drift;
- pin the core strict-parity CI checkout to the selected `nirs4all-methods`
  RC commit;
- correct Cockpit release accounting for `dag-ml-data` crates that are stale
  relative to the selected RC head;
- regenerate the aggregation lock so the selected core commit matches the
  published tag;
- fold the Claude read-only GitGuardian audit into the security record.

## Published Code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-providers` | `rc/v1-full-refactor` | `7c7c6e9` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/ci.yml`, `README.md`, `scripts/ci_gate.py` |
| `nirs4all-lite` (`nirs4all-core` RC worktree) | `rc/v1-full-refactor-core` | `cdba11e` / `n4a-v1-rc1-2026.07-refactor` | `.github/workflows/ci.yml` |
| `nirs4all-cockpit` | `rc/v1-full-refactor` | `8b8e1a4` / `n4a-v1-rc1-2026.07-refactor` | `data/current.json` |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | aggregation lock, surface matrix source list, control/security reports, this report |

## Changes

- Providers now checks out `GBeurier/nirs4all-ecosystem` in CI and runs
  `scripts/validate_contracts.py --canonical ...` as part of
  `scripts/ci_gate.py`. A `NIRS4ALL_PROVIDERS_CANONICAL_CONTRACTS` override is
  available for nonstandard local checkout layouts.
- Core strict-parity CI now checks out `GBeurier/nirs4all-methods` at
  `44cc94891348e0ba3c8ca84ef32073147894cf1c`, avoiding accidental drift from
  the selected methods RC.
- Cockpit `data/current.json` now marks the six `dag-ml-data` crates still
  published at `0.2.1` as `stale` against source `0.2.2` and the selected RC
  tag, changing the snapshot summary from `green=75 stale=2` to
  `green=69 stale=8`.
- `docs/contracts/release/aggregation-lock.n4a.lock.json` was regenerated from
  the selected RC worktrees; the `lite` member now pins `cdba11e` instead of
  `29d6d04`.
- `WAVE_4N` and `RC_SECURITY_GITGUARDIAN_CLUSTER.md` now record the read-only
  Claude audit: the remaining hidden PR refs do not contain the GitGuardian
  secret; only deterministic unit-test token literals remain.

## Local Gates

Providers:

- `NIRS4ALL_PROVIDERS_CANONICAL_CONTRACTS=/home/delete/nirs4all/_worktrees/RC-v1-ecosystem/docs/contracts/providers python3.11 scripts/ci_gate.py`
  - Ruff: passed.
  - Mypy: `Success: no issues found in 12 source files`.
  - Tests: `80%...100%`.
  - Conformance: `......ssss`.
  - Neutral contracts: `provider contracts gate: PASS (5 schemas, 5 fixtures)`.

Core:

- `git diff --check`
- Workflow assertion: strict-parity checkout contains
  `ref: 44cc94891348e0ba3c8ca84ef32073147894cf1c`.

Cockpit:

- `python3.11 -m json.tool data/current.json`
- `n4a-cockpit validate-targets ops/targets.yaml` ->
  `OK: ops/targets.yaml - 21 packages, 94 targets`.
- `python3.11 -m pytest -q` -> `84 passed in 0.59s`.

Ecosystem:

- `python3.11 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all/_worktrees generate --manifest docs/contracts/release/aggregation-manifest.n4a.json --output docs/contracts/release/aggregation-lock.n4a.lock.json`

## Parallel Review Inputs

- Codex distribution/topology reviewer: requested syncing stale Cockpit and
  release matrix state after the reset.
- Codex providers/language reviewer: confirmed providers is still Python-only
  as an implementation package, so the release gate must treat neutral schemas
  and fixtures as the cross-language contract.
- Codex methods/core reviewer: flagged the unpinned core strict-parity checkout
  as a drift risk.
- Claude Code read-only security reviewer: confirmed current cluster
  branch/tag refs are clean and the hidden PR refs do not carry the reported
  secret.

## Remaining Risk

- Full Python-reference parity was not rerun in this wave by design. The latest
  full proof remains on Python runtime head `3d568abe`; rerun after the next
  material runtime batch or before production cutover.
- R, MATLAB/Octave, and local methods JS/WASM execution remain environment
  gates for the core/language package surfaces.
- Providers still has only a Python implementation package. Cross-language
  parity depends on the neutral provider schemas/fixtures until R/WASM/native
  clients are implemented.
- Cockpit is a public release accounting snapshot. It now exposes stale
  `dag-ml-data` crates instead of masking them, but it is not proof that those
  packages have been published.
