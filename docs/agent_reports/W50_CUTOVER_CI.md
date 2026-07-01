# W50 report - cutover CI

Summary:
Made the W40 cutover gate runner CI-ready without flipping defaults. The runner now has an advisory mode for pre-cutover CI visibility, can skip absent sibling/worktree cwd paths when requested, and the gate manifest includes a self-check gate that runs in a plain ecosystem checkout.

Code changed:
- Added `run --advisory` to report required-gate failures while exiting 0.
- Added `run --missing-cwd skip` so advisory CI can report absent sibling repos as skipped instead of crashing.
- Added `cutover_gate_contract_selfcheck` to the cutover gate manifest.
- Added `.github/workflows/cutover-gates.yml` with PR/push tooling validation and manual `workflow_dispatch` validate/advisory/strict modes.
- Updated `CUTOVER_GATE_RUNNER.md` for the current fallback count and CI modes.

Files touched:
- `.github/workflows/cutover-gates.yml`
- `scripts/n4a_cutover_gates.py`
- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/CUTOVER_GATE_RUNNER.md`
- `docs/agent_reports/W50_CUTOVER_CI.md`

Commits:
- `nirs4all-ecosystem/refactor/W50-cutover-ci` HEAD (`ci(cutover): add advisory gate workflow`)

Tests run:
- `python3 -m py_compile scripts/n4a_cutover_gates.py`
- `python3 -m json.tool docs/contracts/cutover/drop-gates.n4a.json`
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all validate`
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all list --json`
- `python3 scripts/n4a_cutover_gates.py --workspace-root /home/delete/nirs4all --gate cutover_gate_contract_selfcheck run --json` -> passed
- `python3 scripts/n4a_cutover_gates.py --workspace-root /tmp/does-not-exist-n4a --gate pyref_coverage_zero run --advisory --missing-cwd skip --json` -> exit 0, report marks the required gate skipped/failed in advisory mode
- PyYAML parse of `.github/workflows/cutover-gates.yml`
- `ruff check scripts/n4a_cutover_gates.py`

Tests not run and why:
- Full strict cutover gate run was not run because `EXPECTED_FALLBACK` is still 6 and `default_engine_postflip` is expected to fail before the final cutover commit.

Blockers:
- This does not close `LOCK-DROP`. It only makes the gate runner visible and CI-addressable before the cutover.

Impact on blockers/locks:
Advances `L19`/`LOCK-DROP` operational readiness. The final flip still requires `EXPECTED_FALLBACK == empty`, native export parity, runtime parity, migration readiness, and strict gate success.

Next action:
After W41/B-010 reaches zero fallback, run the workflow in strict mode from a prepared release workspace and only then consider the default-engine flip.

Sync doc updated: no
