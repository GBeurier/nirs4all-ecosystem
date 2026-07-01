# W40 report - cutover gate runner

Summary:
W40 added a non-mutating cutover gate runner in `nirs4all-ecosystem`. The runner records the drop-gate contract and can list, validate, and run gate checks such as fallback coverage before any future `DEFAULT_ENGINE="dag-ml"` flip.

Code changed:
- Added `scripts/n4a_cutover_gates.py`.
- Added the machine-readable gate contract `docs/contracts/cutover/drop-gates.n4a.json`.
- Added usage documentation for the gate runner.

Files touched:
- `scripts/n4a_cutover_gates.py`
- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/CUTOVER_GATE_RUNNER.md`

Commits:
- `nirs4all-ecosystem/refactor/W40-cutover-gates` `80e6ac6`
- Integrated into `nirs4all-ecosystem/main` as merge `9c97948`

Tests run:
- Gate runner `validate` and `list` commands -> passed.
- `python3 -m compileall` on the runner -> passed.
- `python3 -m json.tool` on the gate contract -> passed.
- Ruff -> passed.
- Dry run of `pyref_coverage_zero` failed as expected while fallback coverage remains nonzero.

Impact:
Advances `LOCK-DROP` operationally. It does not flip defaults; it makes the eventual flip enforceable and repeatable.

Next action:
Wire the gate runner into CI after `EXPECTED_FALLBACK == empty` and native export/runtime parity are complete.

Sync doc updated: yes
