# Wave 3F - Release Lock Lite Pin

Date: 2026-07-01T18:56:17+02:00

## Scope

Lane A follow-up after W3E:

- refresh the aggregation lock to point the locked `nirs4all-lite` member at the
  W3E commit `12612f444baa4fdf2734bf777781af5355160e58`;
- keep the public V1 surface matrix unchanged: Python `nirs4all` remains the
  oracle outside the lock, while R `nirs4all` and browser/WASM `nirs4all` are
  covered by locked `nirs4all-lite`;
- avoid accepting unrelated local sibling/worktree drift into the lock.

No full parity run in this batch.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Schrodinger | Read-only lock/matrix audit | done | Approved the minimal `lite` pin refresh; warned not to regenerate from current sibling repos because `nirs4all-io` would move to an unrelated branch/commit. |

## Decisions

- Commit only the `lite.state.commit` update from `272e07fb82d252269474f30bd6b5a5e89271d8a8` to `12612f444baa4fdf2734bf777781af5355160e58`.
- Do not accept branch-name churn for `dag-ml` / `dag-ml-data` into this batch.
- Do not repin `nirs4all-io` from locked integration commit `eae8263f0c5f6a9b4751950a308c3bf3d3d483b1` to sibling branch `refactor/L7-io-dagml-sibling` commit `e52eecd827a0d68afd0d4ecd05b65651e9747928`.
- Validate the lock against a temporary workspace whose symlinks point to the integration worktrees that match the pinned branches.

## Files Changed

`nirs4all-ecosystem`:

- `docs/contracts/release/aggregation-lock.n4a.lock.json`
- `docs/agent_reports/WAVE_3F_RELEASE_LOCK_LITE_PIN.md`

## Gates

- `python3 scripts/n4a_release_lock.py --workspace-root <integration-symlink-workspace> validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` - passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` - passed.
- `python3 scripts/n4a_release_surface_matrix.py report` - passed; report lists `lite @ 12612f444baa`.
- `python3 -m pytest tests/test_release_surface_matrix.py -q` - 4 passed.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` - passed.
- `python3 -m py_compile scripts/n4a_release_lock.py scripts/n4a_release_surface_matrix.py` - passed.
- `git diff --check` - passed.

## Risks

- A raw `n4a_release_lock.py generate` from the current sibling directories is not a pure W3E refresh because the `nirs4all-io` sibling is on a different lane than the locked integration worktree.
- The lock still relies on the integration worktrees for validation until the corresponding sibling directories are realigned deliberately.
