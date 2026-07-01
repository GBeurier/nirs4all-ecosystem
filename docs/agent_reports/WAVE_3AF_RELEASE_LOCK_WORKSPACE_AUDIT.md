# Wave 3AF - Release Lock Workspace Audit

Date: 2026-07-01
Lane: A - integration train / release lock / topology
Scope: `nirs4all-ecosystem` only

## Decision

GO for the release-lock workspace-root hardening patch.

NO-GO for refreshing `docs/contracts/release/aggregation-lock.n4a.lock.json`.
The current lock remains the selected release-lock source of truth. The live
sibling workspace may contain reset or superseded branches and must not be used
as implicit release selection evidence.

## Agents

- Euler the 2nd: audited `_worktrees/INT-lite` versus the locked
  `nirs4all-lite` checkout. Verdict: NO-GO for lock refresh to `6c08b92`;
  `INT-lite` is already absorbed by the current locked main pin.
- Dewey the 2nd: audited release-lock validation roots and cutover-gate
  behavior. Verdict: GO for selected-root validation with `/tmp/n4a-lock-ws` and
  GO for a small docs/error-message patch.
- Planck the 2nd: reviewed the patch. Initial NO-GO found a missing
  `--manifest`/`--lock` in the docs `checkout-members` command; after correction
  the re-review verdict was GO.

## Files Modified

- `docs/CUTOVER_GATE_RUNNER.md`
  - Documents that most gates read the live sibling workspace, while
    `release_lock_validation` must validate the selected member root.
  - Adds the direct `/tmp/n4a-lock-ws` validation command.
  - Documents the cutover-gate override:
    `N4A_RELEASE_WORKSPACE_ROOT=/tmp/n4a-lock-ws`.
  - Includes the full `checkout-members --manifest --lock --output` command.
- `scripts/n4a_release_lock.py`
  - Keeps validation logic unchanged.
  - Improves the stale/inconsistent lock error to print `workspace_root`, point
    to selected-member validation, mention `N4A_RELEASE_WORKSPACE_ROOT`, and
    warn against regenerating from an unselected live workspace.
- `tests/test_release_lock.py`
  - Adds a regression test that generates a lock from a selected root, validates
    it against a different live root, and asserts that the error message points
    to selected-root recovery.

No release manifest, release lock, or surface matrix pins were modified.

## State Audit

- `_worktrees/INT-lite` HEAD: `6c08b92bd5f1d15870d442d0f078728635f3d651`.
- Locked/current `nirs4all-lite` HEAD: `786688d2ee4aec905c8deda17d0ec888d12c43ad`.
- `INT-lite` is an ancestor of the locked/current `nirs4all-lite` HEAD.
- Commits in current lock pin after `INT-lite`: 8.
- Commits in `INT-lite` absent from current lock pin: 0.

Conclusion: `INT-lite` is superseded/absorbed. Refreshing the lock to
`6c08b92` would be a rollback, not an integration.

## Surface Matrix Checkpoint

The V1 public surface matrix continues to include the requested NIRS4ALL
surfaces:

- `nirs4all.python.oracle`: Python `nirs4all`, outside aggregation lock,
  required for NIRS4ALL V1.
- `nirs4all.r.aggregate`: R `nirs4all`, covered by locked member `lite`,
  required for NIRS4ALL V1.
- `nirs4all.browser_wasm.aggregate`: browser/WASM `nirs4all`, covered by locked
  member `lite`, required for NIRS4ALL V1.

## Tests Run

- `python3 -m pytest tests/test_release_lock.py -q -p no:cacheprovider`
  - Result: 8 passed.
- `python3 -m py_compile scripts/n4a_release_lock.py tests/test_release_lock.py`
  - Result: passed.
- `python3 -m ruff check scripts/n4a_release_lock.py tests/test_release_lock.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-ws validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - Result: passed.
- `N4A_RELEASE_WORKSPACE_ROOT=/tmp/n4a-lock-ws python3 scripts/n4a_cutover_gates.py --gate release_lock_validation run --workspace-root /home/delete/nirs4all --json`
  - Result: passed.
- `python3 scripts/n4a_release_surface_matrix.py validate`
  - Result: passed.
- `python3 scripts/n4a_release_surface_matrix.py report | rg 'nirs4all\.(python|r|browser_wasm)|required nirs4all V1|public/accounting' -n`
  - Result: confirmed Python/R/WASM NIRS4ALL surfaces.

Full Python-reference parity was not rerun for this documentation/tooling patch,
per the current policy to reserve the expensive parity run for larger batches.

## Risks And Follow-Ups

- `/tmp/n4a-lock-ws` is a selected-member root and must be refreshed only when
  the release train intentionally changes member pins.
- Running `n4a_release_lock.py validate` without `--workspace-root` still fails
  in the reset live workspace by design; the new error explains why and how to
  recover.
- `audit-fetchability --fail-on-unfetchable` is independent of selected-root
  validation and remains a separate gate.
