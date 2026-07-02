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

Published refs after the rewrite and the follow-up GitGuardian hardening
refresh, then the Wave 4S CI trigger update:

- `origin/main` -> `97b2b38 docs(security): avoid token-shaped CLI examples`
- `origin/rc/v1-full-refactor` -> `9d6ab34 fix(ci): cover rc branches`
- `n4a-v1-rc1-2026.07-refactor` -> lightweight tag `9d6ab34`

Validation:

- Strict scan over the currently published refs for concrete `N4CLUSTER_TOKEN=...`,
  `Authorization/Bearer ...`, `--token VALUE`, and old `example-token`
  patterns: no matches.
- Remote refs were rechecked with `git ls-remote`: only `main`,
  `rc/v1-full-refactor`, and `n4a-v1-rc1-2026.07-refactor` are published for
  the selected names above.
- `uv run --extra dev pytest -q` from `nirs4all-cluster` main:
  `142 passed, 1 skipped, 1 deselected, 3 warnings`.
- `uv run --extra dev pytest -q` from `RC-v1-cluster`:
  `145 passed, 1 skipped, 1 deselected, 3 warnings`.

Local note: superseded local `refactor/*` refs were rewritten by the same local
filter pass and are still not selected RC integration branches.

## Hidden Pull Request Refs

Follow-up after the user received the GitGuardian alert timestamped
2026-07-02 09:41:03 UTC:

- GitHub still exposes hidden read-only refs for merged PR #1 and PR #2:
  `refs/pull/1/head` (`e5a70fd`) and `refs/pull/2/head` (`d530536`).
- Those refs are not branch or tag heads and GitHub rejects deletion attempts
  against `refs/pull/*/head`.
- A later Codex read-only follow-up confirmed the current `main`,
  `rc/v1-full-refactor`, and RC tag histories are still clean for concrete
  CLI secret-option patterns.
- A direct scan of the hidden PR refs found the historical documentation
  placeholder `--token dev` in `PROTOTYPE_DESIGN.md`. It is the only concrete
  CLI-option value found in the refs still exposed by GitHub, and the commits
  containing it are reachable only from `refs/pull/1/head` /
  `refs/pull/2/head`, not from the selected release branches or tag.
- Superseded local-only `refactor/*` tips can still contain
  placeholder-looking examples such as environment-token forms. They are not
  published remote branch heads.

Operational detail: the current remote branch/tag refs scanned clean with:

- `refs/remotes/origin/main`
- `refs/remotes/origin/rc/v1-full-refactor`
- `refs/tags/n4a-v1-rc1-2026.07-refactor`

The only remote PR-ref match was:

- `refs/remotes/origin/pull/1`: `PROTOTYPE_DESIGN.md` example
  `--token dev`
- `refs/remotes/origin/pull/2`: `PROTOTYPE_DESIGN.md` example
  `--token dev`

## Alert Timestamp Follow-up

Additional follow-up at `2026-07-02T22:31:02Z` tied the reported push window to
historical commit `1027e641dd4d92d75ad806d550b58825f307cf2e`
(`fix(cluster): requeue running-task failures through failed state`). That
commit is currently contained by `main` and `origin/main` history, but not by the
RC tag.

Evidence collected without printing secret values:

- `main`, `origin/main`, `rc/v1-full-refactor`, `origin/rc/v1-full-refactor`,
  and the RC tag tip have zero matches for concrete CLI secret-option values
  matching `--token/--secret/--api-key/--password` followed by a literal
  alphanumeric value.
- The broad option/env scan still finds documentation and code surfaces that
  mention token options or environment variables. Those are expected API
  references, not proof of an exposed value.
- The GitHub pull refs still visible remotely are `refs/pull/1/head` and
  `refs/pull/2/head`; they are hidden/read-only PR refs, not selected release
  heads.
- `gh pr list --repo GBeurier/nirs4all-cluster --state all` confirms PR #1
  (`feat/cluster-prototype`) and PR #2
  (`docs/distributed-execution-design`) are both merged PRs from 2026-06-04,
  not open integration branches.
- The workspace root contains untracked local token files outside the child Git
  repositories. Their values were not read. A root `.gitignore` guard was added
  locally to reduce accidental `git add -A` risk if the workspace root is ever
  treated as a repository.

Operational conclusion: the selected published tips and RC tag are clean for the
checked patterns, but GitGuardian may still flag history or cached/stale refs.
Do not mark the incident fully closed from local evidence alone; request a
GitGuardian rescan/support review and rotate any value that GitGuardian shows as
real rather than placeholder/example text.

## Second Security Review

A read-only Claude Code review with value-masked searches reached the same
substantive conclusion: the alert is most likely a false positive on
documentation/CLI examples using environment-token placeholders or the old
`--token dev` example. No high-entropy hardcoded secret value was identified in
the checked tree/history, and the 15-character candidate is consistent with the
public environment variable name `N4CLUSTER_TOKEN`.

Coordinator correction to that review: a fresh `git ls-remote origin
'refs/pull/*'` still shows `refs/pull/1/head` and `refs/pull/2/head`. They are
merged PR refs from 2026-06-04, not selected release heads, and they predate the
reported 2026-07-02 alert window.

## Decision

Treat as false positive / dummy placeholder from the local evidence, not a known
production credential. If any value shown by GitGuardian is an actual deployed
credential, it must still be rotated because it was published before the rewrite.

If the GitGuardian UI shows `dev` as the exposed value, dismiss it as a
documentation placeholder on merged PR refs. If it shows any other value, treat
that as new evidence and rotate that credential before any additional cleanup.

If GitGuardian continues to report the same alert after the force-push, request
a rescan/support review against `main`, `rc/v1-full-refactor`, and
`n4a-v1-rc1-2026.07-refactor`, noting that stale PR refs are read-only hidden
refs and current branch/tag tips are clean. Optionally open a GitHub Support
ticket to purge unreachable objects/cache state from the earlier force-push
window.

## Repeated Alert Recheck

The user reported the same GitGuardian class again for pushed date
2026-07-02 09:41:03 UTC. A fresh fetch of branch, tag, and hidden PR refs found:

- `origin/main` -> `97b2b38`
- `origin/rc/v1-full-refactor` -> `9d6ab34`
- `n4a-v1-rc1-2026.07-refactor` -> `9d6ab34`
- hidden PR refs: `refs/pull/1/head` -> `e5a70fd`,
  `refs/pull/2/head` -> `d530536`

The selected branch and tag refs have zero literal CLI option values for
`--token`, `--api-key`, `--secret`, `--password`, `--auth`, or bearer-style
patterns. The hidden PR refs still contain only placeholder documentation values
such as `--token dev` / `TOKEN`. These PR refs are not selected release heads
and cannot be deleted through normal Git pushes.

Operational conclusion is unchanged: current selected refs are clean for the
checked class. Treat continued alerts as GitGuardian stale-cache / hidden-PR-ref
review unless the UI reveals a real non-placeholder value.
