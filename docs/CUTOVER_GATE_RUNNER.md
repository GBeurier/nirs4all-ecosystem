# Cutover Gate Runner

`scripts/n4a_cutover_gates.py` turns the `LOCK-DROP` release condition into a
machine-readable checklist. It is non-mutating: list/validate/run only executes
commands from `docs/contracts/cutover/drop-gates.n4a.json`.

Typical usage from the ecosystem repo:

```bash
python3 scripts/n4a_cutover_gates.py list --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py --gate pyref_coverage_zero run --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --json > cutover-gate-report.json
```

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
