# Wave 3AR - Core Parity Gate Audit and Final Reviewer

Date: 2026-07-02

## Scope

This batch audited the remaining W98/core parity concern and ran a no-code final
review across recent W3 integrations.

- Lane C/K: `nirs4all` W98 full-parity gate freshness in
  `_worktrees/INT-nirs4all`.
- Lane K: final V1 blocker review over W3AM-W3AQ reports, release/cutover
  contracts, and current repo states.

No source patch was needed. Full parity was deliberately not launched in this
batch because it is long and must run on the final selected heads.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Pauli the 2nd | `nirs4all` W98 parity gate audit | no-op, verified | W98 is already ancestor of `INT`; fallback meter is `0`, ledger gates pass. |
| Erdos the 2nd | final no-code reviewer | NO-GO final V1 | Release-lock/fetchability, full parity, and Studio/Web strict gates remain open final blockers. |

## Core Parity Findings

- `_worktrees/INT-nirs4all` at `f3005903` already contains the W98 gate
  machinery:
  - `tests/integration/parity/test_native_fallback_boundary.py`;
  - `tests/integration/parity/coverage_meter.py`;
  - `tests/integration/parity/test_compatibility_ledger.py`;
  - `docs/compatibility.json` authority checks through `_authority.py`.
- W98 is an ancestor of current `INT`, while `INT` is newer:
  - W98: `native=87`, `skip=6`;
  - INT: `native=89`, `skip=4`.
- The primary checkout `nirs4all/` remains on superseded `refactor/L17-pyref`
  and must not be used as release evidence:
  - L17 still has `fallback=9`;
  - L17 lacks the newer static fallback boundary files.
- `docs/compatibility.json` in INT is coherent for the current static gate:
  - `expected_fallback: []`;
  - `coverage_meter.fallback: 0`;
  - `expected_fallback_target: 0`;
  - `native: 89`, `registered: 95`, `runnable: 89`.

## Validation

`_worktrees/INT-nirs4all`:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3.11 -m tests.integration.parity.coverage_meter --check` -> `coverage_meter OK (fallback=0, target=0)`.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3.11 -m pytest tests/integration/parity/test_native_fallback_boundary.py tests/integration/parity/test_compatibility_ledger.py -q -p no:cacheprovider` -> 13 passed, 1 skipped.
- Pauli also collected:
  - dynamic native fallback boundary: 89 tests collected;
  - full dual-engine conformance: 95 tests collected.
- `git diff --check` -> passed.

Final reviewer light checks:

- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> passed.
- `python3 scripts/n4a_cutover_gates.py post-w2j-state --workspace-root /home/delete/nirs4all` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> passed.
- `python3 scripts/n4a_release_surface_matrix.py report` still lists the
  required `nirs4all` Python/R/WASM V1 surfaces.
- `python3 scripts/n4a_release_lock.py validate ...` -> failed as expected:
  lockfile is stale/inconsistent against the current workspace.
- `python3 scripts/n4a_release_lock.py audit-fetchability ... --fail-on-unfetchable` -> failed as expected: 1/7 fetchable, 6/7 unfetchable.

## Final Reviewer Verdict

NO-GO for final V1 release.

The current work is coherent as an integration batch, but not yet publishable:

- `LOCK-REL-001` remains blocked; six locked member commits are not fetchable
  from configured remotes.
- Full Python-reference parity and native/cross-engine export gates have not
  been run on final selected heads.
- Studio/Web strict runtime gates still need to run in a clean prepared
  workspace with browser/Playwright smoke coverage.
- Several implementation repos are ahead of or behind remotes; local evidence
  is not yet a release-lock proof.

## Release Surface Accounting

The public V1 matrix and roadmap still include the required `nirs4all` surfaces:

- `nirs4all.python.oracle`;
- `nirs4all.r.aggregate`;
- `nirs4all.browser_wasm.aggregate`;
- `nirs4all.browser_wasm.methods_scoped`;
- `nirs4all.browser_wasm.datasets_scoped`.

This batch did not modify the surface matrix.

## Gate Policy

- No full parity suite was run.
- No test was reduced, xfailed, or weakened.
- No superseded Claude/worktree branch was merged blindly.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Remaining Decisions

1. Publish/tag the selected member heads, or choose fetchable pins, then
   regenerate/validate the release lock.
2. Run `pyref_oracle_full`, dynamic native fallback boundary, and native export
   gates on the final selected heads.
3. Run Studio/Web strict runtime gates in a clean workspace.
4. Decide whether cluster remains advisory or becomes a strict V1 release gate.
