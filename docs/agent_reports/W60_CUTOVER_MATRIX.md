# W60 report - cutover readiness matrix

Summary:
Added a machine-readable readiness matrix for the dag-ml cutover and adjacent V1
ecosystem blockers. The matrix maps each blocker to one owner repo, one evidence
command, expected evidence, and the missing contract that must be closed before a
release manager can treat the row as ready.

Code changed:
- Added `docs/contracts/cutover/readiness-matrix.n4a.json`.
- Extended `scripts/n4a_cutover_gates.py` with readiness-matrix validation and a
  `readiness` listing command.
- Updated `docs/CUTOVER_GATE_RUNNER.md` with readiness usage and the distinction
  between required cutover rows and advisory V1 ecosystem rows.

Files touched:
- `scripts/n4a_cutover_gates.py`
- `docs/contracts/cutover/readiness-matrix.n4a.json`
- `docs/CUTOVER_GATE_RUNNER.md`
- `docs/agent_reports/W60_CUTOVER_MATRIX.md`

Cutover interpretation:
- Required rows remain hard blockers for the `nirs4all` `DEFAULT_ENGINE="dag-ml"`
  flip.
- Provider and cluster rows are advisory for that flip, but tracked for the
  broader V1 ecosystem release.
- `DROP-002-DEFAULT-ENGINE` is intentionally `expected-fail` until the final
  release commit.

Tests run:
- `python3 -m py_compile scripts/n4a_cutover_gates.py`
- `python3 -m json.tool docs/contracts/cutover/drop-gates.n4a.json`
- `python3 -m json.tool docs/contracts/cutover/readiness-matrix.n4a.json`
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all validate`
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all readiness --json`
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all --gate pyref_coverage_zero readiness`
- `python3 -m ruff check scripts/n4a_cutover_gates.py`
- `git diff --check`

Next action:
Refresh the matrix after W51-W59 finish. Promote advisory rows into strict gates
only when the corresponding project is included in the release artifact set.
