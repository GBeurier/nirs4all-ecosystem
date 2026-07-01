# Wave 2U Superseded Work Audit

Date: 2026-07-01T16:09:53+02:00

## Scope

Follow-up after W2T. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2U exists because the workspace was reset after an earlier interrupted run and
older agent work may still exist in branches/worktrees. The goal is audit first,
not merge first.

Primary targets:

- `nirs4all/refactor/L17-pyref@13157d79`, which diverges from
  `_worktrees/INT-nirs4all@7ab1ec1e`.
- Claude-era local work under
  `nirs4all/.claude/worktrees/agent-a5af0970d430760ab`.
- Older W1-W89 worktrees and other dirty states that might be superseded.

Full Python-reference parity remains deferred. W2U must not run
`pyref_oracle_full`; it should only classify work and propose safe next actions.

## Starting State

- W2T integrated:
  - `nirs4all-ecosystem` `ba771bd`
  - `nirs4all-lite` `272e07f`
  - `_worktrees/INT-nirs4all` `7ab1ec1e`
  - `_worktrees/INT-providers` `314c8681`
- W2T non-full cutover passed with `pyref_oracle_full` skipped.
- The selected release lock now pins `nirs4all-lite@272e07f`.
- The public V1 matrix includes `nirs4all` Python, R, and WASM/browser surfaces.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| K/L17 | pending | read-only `nirs4all` + `_worktrees/INT-nirs4all`; no edits | Audit `refactor/L17-pyref` against `refactor/integration-nirs4all`; classify each unique commit/patch as integrated, superseded, or still potentially valuable. |
| K/Claude | pending | read-only local worktrees only; no edits | Audit Claude-era and old W1-W89 worktrees for untracked/dirty work that must be preserved or can be ignored; do not merge or delete anything. |
| K/Release | coordinator | `nirs4all-ecosystem` report only | Integrate audit results into this report and decide whether a follow-up implementation lane is warranted. |

## Review Criteria

- No old branch/worktree merge without fresh audit.
- No private repos touched.
- No edits outside this report unless a later implementation wave is explicitly
  started.
- Prefer patch-id/log/status evidence over commit-subject guesses.
- Any potentially valuable code must be named with path, branch/worktree, commit,
  and risk; do not rely on "looks useful".

## Expected Gates

- Read-only git comparisons and status audits.
- No full parity.
- Existing W2T non-full cutover result remains the latest integration proof.

## Integration Log

Pending.
