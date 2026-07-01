# W98 Full Python Reference Parity Gate

Date: 2026-07-01

## Status

Completed and integrated into `nirs4all` integration.

## Scope

- Worker worktree: `_worktrees/W98-nirs4all-full-parity`
- Worker branch: `refactor/W98-full-parity-gate`
- Integration branch: `_worktrees/INT-nirs4all` on
  `refactor/integration-nirs4all`

## Commits

- Worker commit: `23155948 test(parity): gate strict dag-ml cutover surfaces`
- Integration merge: `17ed929e Merge branch 'refactor/W98-full-parity-gate' into refactor/integration-nirs4all`

## Changes

Changed files:

- `tests/integration/parity/test_conformance_examples_smoke.py`
- `tests/integration/parity/test_dagml_cli_runner.py`
- `tests/integration/parity/test_dagml_operator_generation_phase7.py`
- `tests/integration/parity/test_parity_smoke.py`

What changed:

- Public example smoke now accepts dag-ml failures only when they are structured
  `RtError` refusals and are recorded in an explicit per-example refusal ledger.
  Legacy examples still have to run.
- Named-dict stacking is now covered by an execution-level parity test:
  dag-ml runs native, matches the legacy CV-only no-refit surface, preserves
  `fallback=0`, and emits no `fold_id="final"` rows.
- Runtime unsupported outcomes now assert both strict default refusal and
  explicit fallback diagnostics in `RtResult`.
- Bundle export smoke keeps the V1 native-export refusal visible, asserts no
  partial bundle is written, then uses the named
  `compatibility="legacy-refit"` bridge only for legacy bundle/retrain paths.

## Review

W105 reviewed the initial W98 diff and rejected committing it as-is. The main
risk was that example-smoke refusals could become an untracked parity escape
hatch. The final patch adds the requested ledger, named-dict stacking execution
coverage, fallback diagnostics assertion, and no-partial-export assertion before
commit.

## Verification

Worker/final full gate from `_worktrees/W98-nirs4all-full-parity`:

- `PYTHONPATH=/home/delete/nirs4all/_worktrees/W98-nirs4all-full-parity /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -q -ra`
  - `804 passed, 32 skipped, 11 xfailed`
  - duration: `1885.90s`
  - log: `/tmp/w98_full_parity.log`

Focused worker gates:

- example/refusal + named-dict stacking + runtime diagnostics targeted pytest:
  `12 passed`
- full `test_parity_smoke.py` targeted batch after W105 edits:
  `102 passed, 9 skipped` before the one ledger casing fix; the fixed ledger was
  then covered by the 12-test targeted rerun and the full parity gate.
- `coverage_meter --check`: `fallback=0, target=0`
- Ruff on touched parity files: passed.
- mypy on touched parity files: passed.
- `git diff --check`: passed.

Coordinator verification after merging into `_worktrees/INT-nirs4all`:

- targeted pytest on examples, stacking, and runtime diagnostics:
  `12 passed, 6 warnings`
- `coverage_meter --check`: `fallback=0, target=0`
- Ruff on touched parity files: passed.
- mypy on touched parity files: passed.
- `git diff --check`: passed.

## Remaining Notes

No W98 code blocker remains. The suite still reports documented skips and strict
xfails from the existing parity ledger; those are not new fallback paths.
