# Cutover Gate Runner

`scripts/n4a_cutover_gates.py` turns the `LOCK-DROP` release condition into a
machine-readable checklist. It is non-mutating: list/validate/run only executes
commands from `docs/contracts/cutover/drop-gates.n4a.json`.

Typical usage from the ecosystem repo:

```bash
python3 scripts/n4a_cutover_gates.py list --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py readiness --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py --gate pyref_coverage_zero run --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --json > cutover-gate-report.json
```

`readiness` reads `docs/contracts/cutover/readiness-matrix.n4a.json`. It maps
each blocker to one owning repo, one evidence command, expected evidence, and the
exact missing contract. Rows with `required_for_cutover=false` are advisory V1
ecosystem rows; they should not block the `nirs4all` default-engine flip unless a
release manager explicitly promotes them into `drop-gates.n4a.json`.

The final cutover is not ready until all required gates pass. Today,
`pyref_coverage_zero` is expected to fail because `coverage_meter.summary.fallback`
is still `6`, and `default_engine_postflip` is expected to fail before the final
commit that changes `DEFAULT_ENGINE` to `dag-ml`.

## CI Modes

`.github/workflows/cutover-gates.yml` always validates the runner and manifest
syntax on PRs that touch the cutover gate files. It does not run the full gate
set automatically because most gates require sibling repositories or integration
worktrees.

Manual `workflow_dispatch` supports:

- `validate`: validate tooling and publish the gate inventory.
- `advisory`: run selected gates with `--advisory --missing-cwd skip`; missing
  sibling repos are reported as skipped and failures do not fail the workflow.
- `strict`: run selected gates normally; required gate failures fail the
  workflow.

Use `advisory` while the ecosystem is still pre-cutover. Use `strict` only on a
prepared release workspace where the expected sibling repositories or
integration worktrees exist.

## Reading The Matrix

The matrix currently separates hard cutover blockers from adjacent V1 ecosystem
readiness:

- Required rows cover Python-reference parity, native `.n4a` export, dag-ml /
  dag-ml-data lockstep contracts, Studio/Web runtime adoption, migration tooling,
  release locks, and the final `DEFAULT_ENGINE` flip.
- Advisory rows track provider and cluster readiness. They remain visible because
  they matter for the V1 ecosystem release, but they are not prerequisites for
  replacing the default `nirs4all` pipeline engine.

Use JSON output when coordinating agents:

```bash
python3 scripts/n4a_cutover_gates.py readiness --workspace-root /home/delete/nirs4all --json
python3 scripts/n4a_cutover_gates.py --gate pyref_coverage_zero readiness --workspace-root /home/delete/nirs4all --json
```
