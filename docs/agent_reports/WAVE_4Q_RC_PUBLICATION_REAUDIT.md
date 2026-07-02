# Wave 4Q - RC publication re-audit

Date: 2026-07-02
Coordinator: Codex

## Scope

Recheck publication alignment after Wave 4P moved providers, core, cockpit, and
ecosystem heads. This is a publication/topology audit only; full Python parity
was not rerun.

## Finding and Repair

The first re-audit found that six repositories had the RC branch published but
no remote peeled `n4a-v1-rc1-2026.07-refactor` tag:

- `nirs4all-studio`
- `nirs4all-ui`
- `nirs4all-org`
- `nirs4all-tools`
- `nirs4all-io`
- `nirs4all-datasets`

Each missing tag was recreated as an annotated tag at the selected local head
and force-pushed to its repository. No code changed in those repositories.

## Result

After the repair, all 20 selected RC worktrees were clean. For each worktree,
the local head, remote RC branch, and peeled RC tag matched.

| Worktree | Repo | Branch | Clean | Head | Remote branch | Peeled tag | Match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `RC-v1-nirs4all-python` | `nirs4all` | `rc/v1-full-refactor-python` | yes | `a103fd21e948` | `a103fd21e948` | `a103fd21e948` | yes |
| `RC-v1-dagml` | `dag-ml` | `rc/v1-full-refactor` | yes | `7f86a9b3db66` | `7f86a9b3db66` | `7f86a9b3db66` | yes |
| `RC-v1-dmd` | `dag-ml-data` | `rc/v1-full-refactor` | yes | `e68168543653` | `e68168543653` | `e68168543653` | yes |
| `RC-v1-nirs4all-core` | `nirs4all-lite` | `rc/v1-full-refactor-core` | yes | `cdba11ef2bb2` | `cdba11ef2bb2` | `cdba11ef2bb2` | yes |
| `RC-v1-studio` | `nirs4all-studio` | `rc/v1-full-refactor` | yes | `8141e2eddb2d` | `8141e2eddb2d` | `8141e2eddb2d` | yes |
| `RC-v1-web` | `nirs4all-web` | `rc/v1-full-refactor` | yes | `8a5dcff639f8` | `8a5dcff639f8` | `8a5dcff639f8` | yes |
| `RC-v1-ui` | `nirs4all-ui` | `rc/v1-full-refactor` | yes | `8f9f2f6810f9` | `8f9f2f6810f9` | `8f9f2f6810f9` | yes |
| `RC-v1-cockpit` | `nirs4all-cockpit` | `rc/v1-full-refactor` | yes | `8b8e1a4f4221` | `8b8e1a4f4221` | `8b8e1a4f4221` | yes |
| `RC-v1-org` | `nirs4all-org` | `rc/v1-full-refactor` | yes | `9417073b59e7` | `9417073b59e7` | `9417073b59e7` | yes |
| `RC-v1-ecosystem` | `nirs4all-ecosystem` | `rc/v1-full-refactor` | yes | `7c029b0d767b` | `7c029b0d767b` | `7c029b0d767b` | yes |
| `RC-v1-providers` | `nirs4all-providers` | `rc/v1-full-refactor` | yes | `7c7c6e9ee887` | `7c7c6e9ee887` | `7c7c6e9ee887` | yes |
| `RC-v1-tools` | `nirs4all-tools` | `rc/v1-full-refactor` | yes | `7c5070f52d9d` | `7c5070f52d9d` | `7c5070f52d9d` | yes |
| `RC-v1-cluster` | `nirs4all-cluster` | `rc/v1-full-refactor` | yes | `e8430735e368` | `e8430735e368` | `e8430735e368` | yes |
| `RC-v1-formats` | `nirs4all-formats` | `rc/v1-full-refactor` | yes | `86218e633d13` | `86218e633d13` | `86218e633d13` | yes |
| `RC-v1-io` | `nirs4all-io` | `rc/v1-full-refactor` | yes | `c064ecf9f301` | `c064ecf9f301` | `c064ecf9f301` | yes |
| `RC-v1-datasets` | `nirs4all-datasets` | `rc/v1-full-refactor` | yes | `d9cbd995a2e9` | `d9cbd995a2e9` | `d9cbd995a2e9` | yes |
| `RC-v1-methods` | `nirs4all-methods` | `rc/v1-full-refactor` | yes | `44cc94891348` | `44cc94891348` | `44cc94891348` | yes |
| `RC-v1-repository` | `nirs4all-repository` | `rc/v1-full-refactor` | yes | `534c907cc8d2` | `534c907cc8d2` | `534c907cc8d2` | yes |
| `RC-v1-benchmarks` | `nirs4all-benchmarks` | `rc/v1-full-refactor` | yes | `45f4cf78538b` | `45f4cf78538b` | `45f4cf78538b` | yes |
| `RC-v1-papers` | `nirs4all-papers` | `rc/v1-full-refactor` | yes | `acde191f2c29` | `acde191f2c29` | `acde191f2c29` | yes |

## Local Command

The audit iterated the selected `_worktrees/RC-v1-*` directories and recorded:

- `git status --porcelain`
- `git rev-parse HEAD`
- `git ls-remote --heads origin <branch>`
- `git ls-remote --tags origin n4a-v1-rc1-2026.07-refactor^{}`

## Remaining Risk

This proves publication alignment only. It does not prove functional
completeness, registry availability, environment-specific language gates, or
full Python-reference parity.
