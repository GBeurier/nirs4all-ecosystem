# RC Security: GitGuardian Cluster Alert

Date: 2026-07-02

Repository: `GBeurier/nirs4all-cluster`

Alert reported by user:

- Type: Generic CLI Option Secret
- Pushed date: 2026-07-02 09:41:03 UTC

## Findings

Local audit found no real credential in `nirs4all-cluster`. The scanner-like
matches were documentation placeholders and deterministic test credentials:

- `docs/operations.md`: `--token SECRET`
- `docs/operations.md`: `N4CLUSTER_TOKEN=SECRET`
- `docs/quickstart.md`: `--token SECRET`
- `PROTOTYPE_DESIGN.md`: `--token dev`
- `tests/conftest.py` / `tests/test_release_smoke.py`: role/test tokens

History attribution:

- `--token SECRET` and `N4CLUSTER_TOKEN=SECRET` originated in commit `df1d41f`
  (`v0.1.0`, 2026-06-16).
- `--token dev` originated in commit `908fbd4` (prototype, 2026-06-04).
- The 2026-07-02 push likely caused GitGuardian to rescan those existing
  examples, not a newly introduced production token.

## First Remediation

Replaced literal values with environment-variable usage:

- `--token "$N4CLUSTER_TOKEN"`
- no inline `N4CLUSTER_TOKEN=SECRET` assignment.

Commits:

- `nirs4all-cluster/main`: `8ef2667 docs(security): avoid literal cluster token examples`
- `RC-v1-cluster`: `75e89e7 docs(security): avoid literal cluster token examples`

`main` was pushed to `origin/main`.

After the user-reported GitGuardian alert, the published refs were audited again.
The remaining `SECRET` matches were only in obsolete public tags:

- `v0.1.0`
- `v0.1.1`
- `n4a-cluster-2026.07-refactor`

Those tags were deleted from `origin`, `rc/v1-full-refactor` was pushed, and a
clean tag was published:

- `n4a-v1-rc1-2026.07-refactor` -> `ee94a77`

Remote refs now exposed by `GBeurier/nirs4all-cluster`:

- `main` -> `8ef2667`
- `rc/v1-full-refactor` -> `ee94a77`
- `n4a-v1-rc1-2026.07-refactor` -> `ee94a77`

No `SECRET` placeholder remains in those published refs.

## History Rewrite Remediation

GitGuardian scans reachable history, not only the current tree. A second audit
showed that `main`, `rc/v1-full-refactor`, and the RC tag were clean at their
tips but still reached historical commits with scanner-like `--token` examples
and long test-token constants.

Actions taken:

- Built a temporary mirror clone of `GBeurier/nirs4all-cluster`.
- Ran a targeted history rewrite over the published refs only:
  - documentation examples no longer pass literal values after `--token`;
  - test fixtures use short deterministic credentials;
  - release smoke/auth tests were adjusted consistently.
- Recreated the annotated RC tag on the rewritten RC head.
- Force-pushed only:
  - `main`;
  - `rc/v1-full-refactor`;
  - `n4a-v1-rc1-2026.07-refactor`.

Published refs after the rewrite:

- `origin/main` -> `21e16cd docs(security): remove literal cluster credentials`
- `origin/rc/v1-full-refactor` -> `fef2f5c docs(security): remove literal cluster credentials`
- `n4a-v1-rc1-2026.07-refactor` -> annotated tag `6d4ce4c`, peeled commit `fef2f5c`

Validation:

- History scan over `origin/main`, `origin/rc/v1-full-refactor`, and
  `n4a-v1-rc1-2026.07-refactor^{}` for CLI-option-secret-like patterns:
  no matches.
- `uv run --extra dev pytest -q --run-release-smoke` from
  `_worktrees/RC-v1-cluster`: `146 passed, 1 skipped, 3 warnings`.
- `python3 -m ruff check tests/conftest.py tests/test_rbac.py
  tests/test_release_smoke.py tests/test_server_api.py`: passed.

Local note: stale superseded `refactor/*` worktrees may still contain old local
commits. They were not pushed and were not merged. They should be deleted or
rebased only after the separate old-worktree audit.

## Decision

Treat as false positive / dummy placeholder from the local evidence, not a known
production credential. If any value shown by GitGuardian is an actual deployed
credential, it must still be rotated because it was published before the rewrite.

If GitGuardian continues to report the same alert after the force-push, request
a rescan or mark the historical placeholder as remediated/false-positive; GitHub
may retain unreachable objects and cache scan results after refs are rewritten.
