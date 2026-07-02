# Wave 4N - Cluster GitGuardian PR refs audit

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up after the GitGuardian "Generic CLI Option Secret" alert reported for
`GBeurier/nirs4all-cluster`, pushed on 2026-07-02 at 09:41:03 UTC.

## Findings

- Published branch/tag refs are still rewritten to the clean heads:
  - `main` -> `97b2b389169e3a13fbc3f5f83785e7a87a35bf84`
  - `rc/v1-full-refactor` -> `e8430735e3688af6287b3506bcb80d630c0003ff`
  - `n4a-v1-rc1-2026.07-refactor` -> tag object
    `60c1b5a06ead75ec93bb677e334a61ce88c8530d`, peeled to `e8430735e3688`
- GitHub still exposes hidden pull request refs:
  - `refs/pull/1/head` -> `e5a70fd50485d0630de1bda9f263ccabecd7a23c`
  - `refs/pull/2/head` -> `d530536723cfd121faa716b472e254807fd013c3`
- PR #1 and PR #2 were merged on 2026-06-04 and their source branches no
  longer exist on the remote.
- A second read-only audit with Claude Code confirmed that the specific
  GitGuardian secret is not present in those PR refs. The later files that
  carried the cleaned examples (`docs/quickstart.md`, `docs/operations.md`,
  `tests/conftest.py`, `CLAUDE.md`) do not exist at the PR commits; the only
  remaining secret-shaped values are deterministic test literals in
  `tests/test_server_api.py`.
- Attempting to delete the GitHub pull refs with `git push origin
  :refs/pull/1/head :refs/pull/2/head` was rejected by GitHub because they are
  hidden refs.

## Local Checks

- `git ls-remote origin 'refs/*'`
- `git grep` sensitive CLI option scan over `origin/main`,
  `origin/rc/v1-full-refactor`, and the peeled RC tag: no matches.
- Same scan over `refs/remotes/origin/pull/1` and
  `refs/remotes/origin/pull/2`: placeholder matches only.
- `gh pr view 1` and `gh pr view 2`: both PRs are merged/closed and intra-repo.

## Decision

No further git rewrite is available from the repository side for the hidden PR
refs. The practical remediation path is outside git: rotate any value that was
ever real, request a GitGuardian rescan/closure as remediated, and optionally
ask GitHub Support to purge unreachable object/cache state from the earlier
force-push window.

No production credential was identified in the current published branch/tag
surface or in the remaining hidden PR refs during this audit.
