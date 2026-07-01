# Wave 3O - Release Lock Fetchability Audit

Date: 2026-07-01

## Scope

Lane A tranche focused on release-lock reproducibility from clean remotes. This does not regenerate the lock, does not merge superseded worktrees, and does not run full parity. The existing public V1 surface gate for Python/R/WASM remains present through `lite_v1_surfaces`.

## Commit

- `nirs4all-ecosystem` same commit as this report - `test(release): audit lock fetchability`

## Files Modified

`nirs4all-ecosystem`:

- `scripts/n4a_release_lock.py`
- `tests/test_release_lock.py`
- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/contracts/cutover/readiness-matrix.n4a.json`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Jason | Read-only release-lock/topology audit | done | Found the lock validates only against prepared local worktrees; 6 of 7 member commits are not fetchable from configured GitHub repo URLs. Confirmed Python/R/WASM public surfaces are still represented in the release surface matrix and roadmap. |
| Franklin | W3O diff review | GO | No blocking or non-blocking findings. Confirmed the validation gate remains, fetchability is added as a strict proof, and `LOCK-REL-001` is correctly blocked. |

## Decisions

- Add `n4a_release_lock.py audit-fetchability` as a read-only audit that clones each lock member with `--filter=blob:none --no-checkout` and attempts the pinned checkout.
- Keep audit exit behavior non-blocking by default so it can be used diagnostically; make it strict only with `--fail-on-unfetchable`.
- Add a dedicated `release_lock_fetchability_audit` cutover gate instead of overloading `release_lock_validation`.
- Mark `LOCK-REL-001` as `blocked` until every locked commit is fetchable from the configured remotes.
- Do not rewrite release-lock pins in this tranche; publishing or selecting fetchable immutable refs remains the owner action.

## Tests Run

`nirs4all-ecosystem`:

- `python3 -m pytest tests/test_release_lock.py -q -p no:cacheprovider` -> 7 passed.
- `python3 -m pytest tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_cutover_state_gate.py -q -p no:cacheprovider` -> 15 passed.
- `python3 -m ruff check scripts/n4a_release_lock.py tests/test_release_lock.py` -> passed.
- `python3 -m py_compile scripts/n4a_release_lock.py scripts/n4a_cutover_gates.py scripts/n4a_release_surface_matrix.py` -> passed.
- `python3 -m compileall -q scripts tests` -> passed.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output-json /tmp/n4a-release-lock-fetchability.json` -> passed diagnostically; report shows 1/7 fetchable and 6/7 unfetchable.
- `python3 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` -> expected failure; 1/7 fetchable and 6/7 unfetchable.
- `python3 scripts/n4a_release_lock.py --workspace-root /home/delete/nirs4all validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> expected failure; current workspace heads are not the locked member states.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- Current remote fetchability: `formats` is fetchable; `dag_ml`, `dag_ml_data`, `datasets`, `io`, `lite`, and `methods` fail checkout because the configured remotes do not advertise the locked commits.
- `release_lock_fetchability_audit --fail-on-unfetchable` is intentionally red until those commits are pushed/tagged or replaced by fetchable pins.
- `release_lock_validation` is also red in the current workspace because local heads have advanced since the lock was generated.
- Before final cutover, rerun release-lock validation, strict fetchability audit, and the larger parity batches after selecting final integration heads.
