# Wave 3AB - Release Lock Refresh

Date: 2026-07-01

## Scope

Lane A release-lock tranche focused on `nirs4all-ecosystem`: refresh the aggregation lock after integrated W3K/W3N/W3P/W3AA member commits without accepting unrelated sibling branch drift. No full parity was run.

## Commit

- `nirs4all-ecosystem` same commit as this report - `chore(release): refresh aggregation lock pins`

## Files Modified

`nirs4all-ecosystem`:

- `docs/contracts/release/aggregation-lock.n4a.lock.json`

## Pinned Member Changes

| Member | Previous | New | Source |
| --- | --- | --- | --- |
| `datasets` | `ac455f321144` | `44662562b007` | W3K IO loading reference dataset guard |
| `io` | `eae8263f0c5f` | `7e90b4d2161c` | W3V-W3AA native Parquet / NA / Python-WASM-R public-surface smokes |
| `lite` | `12612f444baa` | `786688d2ee4a` | W3P public V1 Python/R/WASM surface gate |
| `methods` | `00ca846705bc` | `0f328018348b` | W3N methods WASM broad model smoke |

No `dag_ml`, `dag_ml_data`, `formats`, version metadata, contract artifact digest, lockstep attestation, manifest digest, or public-surface matrix churn was accepted.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Plato the 2nd | W3AB release-lock review | go | Confirmed the tracked diff is exactly four commit-field changes and is coherent with reports W3K/W3N/W3P/W3AA plus IO W3V-W3Z intermediate commits. |

## Decisions

- Generated the lock from a temporary symlink workspace that points locked members to the intended integration heads:
  - `dag-ml` -> `_worktrees/INT-dagml`
  - `dag-ml-data` -> `_worktrees/INT-dmd`
  - `nirs4all-io` -> `_worktrees/INT-io`
  - `nirs4all-datasets`, `nirs4all-formats`, `nirs4all-lite`, `nirs4all-methods` -> their current audited sibling repos.
- Did not generate from raw `/home/delete/nirs4all` sibling directories because `nirs4all-io` there is on `refactor/L7-io-dagml-sibling`, not the authoritative integration branch.
- Kept public `nirs4all` R/Python/WASM release accounting unchanged; `scripts/n4a_release_surface_matrix.py report` now lists locked `io @ 7e90b4d2161c`, `lite @ 786688d2ee4a`, `methods @ 0f328018348b`, and `datasets @ 44662562b007`.

## Tests Run

`nirs4all-ecosystem`:

- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-ws validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py report` -> passed.
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py -q -p no:cacheprovider` -> 11 passed.
- `python3 -m py_compile scripts/n4a_release_lock.py scripts/n4a_release_surface_matrix.py scripts/n4a_cutover_gates.py` -> passed.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> passed.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output-json /tmp/n4a-release-lock-fetchability-w3ab.json` -> diagnostic pass, 1/7 fetchable and 6/7 unfetchable.
- `git diff --check` -> passed.

Reviewer also ran:

- Read-only JSON/diff/status checks over the lock and referenced reports -> GO.

## Risks / Follow-Ups

- Strict remote fetchability remains red until the selected local commits are pushed or replaced by fetchable immutable refs: `dag_ml`, `dag_ml_data`, `datasets`, `io`, `lite`, and `methods` are currently unfetchable from their configured remotes.
- Full Python-reference parity and long dag-ml/native parity were deferred per batch policy.
- Missing local R/Rscript remains a public-surface execution risk; the release matrix and W3AA document it as CI/local-R gated.
