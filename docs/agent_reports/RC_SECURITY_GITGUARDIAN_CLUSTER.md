# RC Security: GitGuardian Cluster Alert

Date: 2026-07-02

Repository: `GBeurier/nirs4all-cluster`

Alert reported by user:

- Type: Generic CLI Option Secret
- Pushed date: 2026-07-02 09:41:03 UTC

## Findings

Local audit found no real credential in `nirs4all-cluster`. The scanner-like
matches were documentation placeholders:

- `docs/operations.md`: `--token SECRET`
- `docs/operations.md`: `N4CLUSTER_TOKEN=SECRET`
- `docs/quickstart.md`: `--token SECRET`
- `PROTOTYPE_DESIGN.md`: `--token dev`

History attribution:

- `--token SECRET` and `N4CLUSTER_TOKEN=SECRET` originated in commit `df1d41f`
  (`v0.1.0`, 2026-06-16).
- `--token dev` originated in commit `908fbd4` (prototype, 2026-06-04).
- The 2026-07-02 push likely caused GitGuardian to rescan those existing
  examples, not a newly introduced production token.

## Remediation

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

## Decision

Treat as false positive / dummy placeholder, not credential compromise. No
secret rotation is required from the local evidence. Do not rewrite history for
this unless GitGuardian policy requires removing historical false positives from
GitHub's retained unreachable objects instead of resolving them as false
positive in the GitGuardian UI.

Before final RC tag, ensure the selected cluster head includes `75e89e7` or a
descendant, not the earlier `ac84df7` cluster-only lane head.
