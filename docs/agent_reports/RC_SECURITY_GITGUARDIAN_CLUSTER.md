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

## Wave 4X Active-Head Hardening

The repeated GitGuardian class also prompted a scan for generic CLI-option
values beyond `--token`. The selected heads no longer contained token examples,
but still had a secret-shaped help/documentation example for RBAC principals:
`--principal alice:s3cr3t:submitter`.

Actions:

- Replaced the runtime help and CLI reference text with the neutral contract
  form `NAME:TOKEN:ROLES`, without changing parsing semantics.
- Pushed `main` to `16b4a2a docs(security): avoid secret-shaped principal examples`.
- Cherry-picked the same change to the RC worktree as `19384e2` and moved tag
  `n4a-v1-rc1-2026.07-refactor` to that head.

Validation:

- `ruff check nirs4all_cluster/cli.py`: passed on both `main` and RC.
- `PYTHONPATH=. pytest -q` on `main`: `142 passed, 1 skipped, 1 deselected, 3 warnings`.
- `PYTHONPATH=. pytest -q` on RC: `145 passed, 1 skipped, 1 deselected, 3 warnings`.
- Post-push `git ls-remote`:
  - `origin/main` -> `16b4a2a`
  - `origin/rc/v1-full-refactor` -> `19384e2`
  - `n4a-v1-rc1-2026.07-refactor` -> `19384e2`
- Post-push scan of active heads found no concrete `--token VALUE` or
  `--principal VALUE` examples. Hidden PR refs #1/#2 still contain only the
  historical `--token dev` placeholder.

## Wave 4AC Active-Ref Metavar Hardening

The active heads still contained scanner-sensitive CLI metavar examples for the
principal option. They were not real credentials, but GitGuardian classifies
generic CLI option values aggressively, so the active refs were hardened again.

Actions:

- Replaced docs/help text that placed a token-shaped value immediately after
  `--principal` with neutral option-only wording.
- Pushed `main` to `eaf79a0 docs(security): avoid cluster CLI option metavars`.
- Cherry-picked the same change to the RC worktree as `ffeaf4b` and moved tag
  `n4a-v1-rc1-2026.07-refactor` to that head.

Validation:

- Active remote refs scan over `origin/main`, `origin/rc/v1-full-refactor`, and
  `n4a-v1-rc1-2026.07-refactor` found zero inline `--principal` or `--token`
  secret-shaped values.
- `ruff check docs/cli-reference.md docs/rest-api.md nirs4all_cluster/cli.py`:
  passed on both main and RC worktrees.
- `pytest tests/test_rbac.py -q`: `24 passed` on both main and RC worktrees.
- GitHub Actions are green on both `eaf79a0` and `ffeaf4b` (`CI` and
  `version-guard`).

Decision remains unchanged: no real credential is known from accessible
evidence. Treat continued reports as stale/history/hidden-ref findings unless
GitGuardian shows a non-placeholder value.

## 2026-07-03 GitGuardian Email Recheck

The user reported a GitGuardian email for repository
`GBeurier/nirs4all-cluster`, secret type `Generic CLI Option Secret`, pushed
date `2026-07-02 09:41:03 UTC`.

Coordinator checks:

- `git ls-remote --heads --tags origin` shows only `main`,
  `rc/v1-full-refactor`, and `n4a-v1-rc1-2026.07-refactor` as visible remote
  refs. No old `refactor/*` heads are visible remotely from this clone.
- Active branch/tag refs still point to `main` `eaf79a0` and RC/tag `ffeaf4b`.
- Targeted scans over active refs for concrete inline `N4CLUSTER_TOKEN=...`,
  `--token ...`, `--api-key ...`, `--secret ...`, `--password ...`, and
  `--principal ...` credential-shaped values found zero candidates.
- GitHub's own secret-scanning REST endpoint returns `404 Secret scanning is
  disabled on this repository`, so the GitGuardian alert fingerprint is not
  available through GitHub API from this environment.

Parallel read-only reviews:

- Codex subagent `019f269e-7a70-7d90-81a4-dda7a27eb488` found no current-head
  secret value and classified the alert as most likely a documentation/example
  false positive. It confirmed that historical reachable commits still contain
  scanner-sensitive CLI examples/metavars, so an ancestor-walking scanner can
  continue to alert.
- Claude/Fable read-only audit `04cf6618-91b1-416e-b4bd-95c0b6eb29b8`
  completed with the same conclusion: the hits are placeholders/env-var
  references (`N4CLUSTER_TOKEN`), dummy examples such as `s3cr3t`, or test
  tokens, with no high-entropy credential value found in refs, tags or reachable
  history. It recommends closing as false positive/resolved and avoiding pushes
  of the obsolete local `refactor/*` branches unless they are rebased/cleaned.

Decision:

- No rotation is indicated from local evidence because no real credential was
  identified. If GitGuardian displays a non-placeholder value in the UI, rotate
  that value out of band immediately.
- Deleting superseded refs is not enough to clear this class of alert: the
  suspicious examples are in historical commits reachable from active branches.
  If the requirement is to make the alert disappear from scanners that inspect
  all ancestors, the only complete remediation is a history rewrite of active
  branches/tags followed by force-push and support/rescan requests.
- For the current RC, close as false positive/remediated unless GitGuardian
  provides a concrete non-placeholder secret value.

## 2026-07-03 CI Guard Hardening

The user reported the same GitGuardian email class again. A fresh local check
matched the alert window to historical commit `1027e64`
(`fix(cluster): requeue running-task failures through failed state`), which
still contained scanner-sensitive documentation/help examples such as
environment-token command examples and the old RBAC principal example shape.
No real credential was found in the current selected heads.

Additional checks:

- GitHub's secret-scanning REST API returns `404 Secret scanning is disabled on
  this repository`; the GitGuardian fingerprint cannot be retrieved from GitHub
  in this environment.
- Current `nirs4all-cluster` HEAD scans contain no concrete inline value for
  the checked `--token`, `--secret`, `--password`, `--api-key`, or
  `--principal` patterns.
- `detect-secrets` on tracked files reports only known false-positive dataset
  path strings, recorded by hash in a baseline. No raw secret value is stored in
  that baseline.

Hardening implemented:

- `rc/v1-full-refactor` moved to `9643460`
  (`ci(security): block token-shaped cluster examples`) and
  `n4a-v1-rc1-2026.07-refactor` was moved to the same commit.
- `main` received the same CI-only hardening as `aec2a10`.
- New CI job `secret scan` runs `detect-secrets-hook` against the tracked-file
  baseline and then `scripts/secret_shape_guard.py`.
- The guard rejects new token-shaped CLI examples, including concrete
  `--principal name:value:roles`, shell-token variables passed as concrete
  `--token` values, and common dummy token literals. This closes the recurrence
  vector that produced the GitGuardian false positives without changing runtime
  behavior.

Local validation on `RC-v1-cluster`:

- `python3 scripts/secret_shape_guard.py`: passed.
- `git ls-files -z | xargs -0 uvx --from detect-secrets detect-secrets-hook --baseline .secrets.baseline`: passed.
- Workflow YAML parse: passed.
- `uv run ruff check scripts/secret_shape_guard.py`: passed.
- `uv run pytest -q`: `145 passed`, `1 skipped`, `1 deselected`,
  `3 warnings`.

Local validation on `main` after cherry-pick:

- `python3 scripts/secret_shape_guard.py`: passed.
- `git ls-files -z | xargs -0 uvx --from detect-secrets detect-secrets-hook --baseline .secrets.baseline`: passed.

Remote validation:

- GitHub Actions on `9643460` (`rc/v1-full-refactor`): `CI` and
  `version-guard` completed with success.
- GitHub Actions on `aec2a10` (`main`): `CI` and `version-guard` completed
  with success.

Decision remains unchanged: the accessible evidence identifies placeholder /
documentation-triggered false positives, not a production credential. If
GitGuardian displays any non-placeholder value, rotate it immediately outside
the codebase and treat that as new evidence.
