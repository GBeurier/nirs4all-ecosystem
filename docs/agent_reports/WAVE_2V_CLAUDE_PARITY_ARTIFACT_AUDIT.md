# Wave 2V Claude-Era Parity Artifact Audit

Date: 2026-07-01T16:15:31+02:00

## Scope

Follow-up after W2U. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2U found five untracked files in a Claude-era nirs4all worktree:

- `tests/integration/parity/conformance/README.md`
- `tests/integration/parity/conformance/__init__.py`
- `tests/integration/parity/conformance/_pack.py`
- `tests/integration/parity/conformance/conformance_pack.json`
- `tests/integration/parity/test_dual_engine_conformance.py`

W2V audits those files read-only, compares them to the current
`_worktrees/INT-nirs4all` parity gates, and records whether any content should be
reimplemented later. It must not merge or copy the untracked files.

Full Python-reference parity remains deferred. W2V must not run
`pyref_oracle_full`.

## Starting State

- W2U concluded `refactor/L17-pyref@13157d79` is superseded by
  `_worktrees/INT-nirs4all@7ab1ec1e`.
- W2T remains the latest integrated, non-full verified release state.
- The Claude-era worktree commit itself is superseded, but the five untracked
  files have not yet been content-audited.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| K/ClaudeArtifact | pending | read-only Claude-era worktree and `_worktrees/INT-nirs4all`; no edits | Inspect the five untracked files and compare them to current INT parity/conformance gates. |
| K/CurrentParity | pending | read-only `_worktrees/INT-nirs4all` and ecosystem reports; no edits | Identify current W98/INT parity artifacts that already cover or supersede the Claude-era proposal. |
| K/Release | coordinator | `nirs4all-ecosystem` report only | Integrate findings and decide whether follow-up work is needed. |

## Review Criteria

- No merge, cherry-pick, or file copy from the Claude-era worktree.
- No full parity.
- Classify content, not author/source.
- If a concept is useful, describe a new implementation task against current INT
  heads rather than reusing the old untracked files directly.

## Integration Log

Pending.
