# Wave 4J - RC publication audit

Date: 2026-07-02  
Coordinator: Codex

## Scope

Verify that the selected RC worktrees are clean and that their local heads match
the published RC branch and the peeled `n4a-v1-rc1-2026.07-refactor` tag. This
is a publication/topology audit only; full Python parity was not rerun.

## Result

All 20 selected RC worktrees were clean. For each worktree, the local head,
remote RC branch, and peeled RC tag matched.

| Worktree | Repo | Branch | Head | Remote branch | Peeled tag |
| --- | --- | --- | --- | --- | --- |
| `RC-v1-nirs4all-python` | `nirs4all` | `rc/v1-full-refactor-python` | `3d568abe504f` | `3d568abe504f` | `3d568abe504f` |
| `RC-v1-dagml` | `dag-ml` | `rc/v1-full-refactor` | `7f86a9b3db66` | `7f86a9b3db66` | `7f86a9b3db66` |
| `RC-v1-dmd` | `dag-ml-data` | `rc/v1-full-refactor` | `e68168543653` | `e68168543653` | `e68168543653` |
| `RC-v1-nirs4all-core` | `nirs4all-lite` | `rc/v1-full-refactor-core` | `29d6d04a5bb0` | `29d6d04a5bb0` | `29d6d04a5bb0` |
| `RC-v1-studio` | `nirs4all-studio` | `rc/v1-full-refactor` | `8141e2eddb2d` | `8141e2eddb2d` | `8141e2eddb2d` |
| `RC-v1-web` | `nirs4all-web` | `rc/v1-full-refactor` | `1ccb8393232a` | `1ccb8393232a` | `1ccb8393232a` |
| `RC-v1-ui` | `nirs4all-ui` | `rc/v1-full-refactor` | `8f9f2f6810f9` | `8f9f2f6810f9` | `8f9f2f6810f9` |
| `RC-v1-cockpit` | `nirs4all-cockpit` | `rc/v1-full-refactor` | `71786b1dc2b0` | `71786b1dc2b0` | `71786b1dc2b0` |
| `RC-v1-org` | `nirs4all-org` | `rc/v1-full-refactor` | `9417073b59e7` | `9417073b59e7` | `9417073b59e7` |
| `RC-v1-ecosystem` | `nirs4all-ecosystem` | `rc/v1-full-refactor` | `5dc07b9ba307` | `5dc07b9ba307` | `5dc07b9ba307` |
| `RC-v1-providers` | `nirs4all-providers` | `rc/v1-full-refactor` | `5146908286ea` | `5146908286ea` | `5146908286ea` |
| `RC-v1-tools` | `nirs4all-tools` | `rc/v1-full-refactor` | `7c5070f52d9d` | `7c5070f52d9d` | `7c5070f52d9d` |
| `RC-v1-cluster` | `nirs4all-cluster` | `rc/v1-full-refactor` | `e8430735e368` | `e8430735e368` | `e8430735e368` |
| `RC-v1-formats` | `nirs4all-formats` | `rc/v1-full-refactor` | `86218e633d13` | `86218e633d13` | `86218e633d13` |
| `RC-v1-io` | `nirs4all-io` | `rc/v1-full-refactor` | `c064ecf9f301` | `c064ecf9f301` | `c064ecf9f301` |
| `RC-v1-datasets` | `nirs4all-datasets` | `rc/v1-full-refactor` | `d9cbd995a2e9` | `d9cbd995a2e9` | `d9cbd995a2e9` |
| `RC-v1-methods` | `nirs4all-methods` | `rc/v1-full-refactor` | `44cc94891348` | `44cc94891348` | `44cc94891348` |
| `RC-v1-repository` | `nirs4all-repository` | `rc/v1-full-refactor` | `534c907cc8d2` | `534c907cc8d2` | `534c907cc8d2` |
| `RC-v1-benchmarks` | `nirs4all-benchmarks` | `rc/v1-full-refactor` | `45f4cf78538b` | `45f4cf78538b` | `45f4cf78538b` |
| `RC-v1-papers` | `nirs4all-papers` | `rc/v1-full-refactor` | `acde191f2c29` | `acde191f2c29` | `acde191f2c29` |

## Command

The audit iterated the selected `_worktrees/RC-v1-*` directories and recorded:

- `git rev-parse --abbrev-ref HEAD`
- `git rev-parse --short=12 HEAD`
- `git status --porcelain`
- `git ls-remote --heads origin <branch>`
- `git ls-remote --tags origin n4a-v1-rc1-2026.07-refactor^{}`

## Remaining Release Risks

- This proves publication alignment, not functional completeness.
- Language/environment gates that need unavailable local toolchains remain
  risk items until CI or release infrastructure runs them.
- The production branches are still intentionally not switched to these RC
  heads.
