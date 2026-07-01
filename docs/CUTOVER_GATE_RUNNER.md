# Cutover Gate Runner

`scripts/n4a_cutover_gates.py` turns the `LOCK-DROP` release condition into a
machine-readable checklist. It is non-mutating: list/validate/run only executes
commands from `docs/contracts/cutover/drop-gates.n4a.json`.

Typical usage from the ecosystem repo:

```bash
python3 scripts/n4a_cutover_gates.py list --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py readiness --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py post-w2j-state --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py --gate pyref_coverage_zero run --workspace-root /home/delete/nirs4all
python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --json > cutover-gate-report.json
```

## Workspace Roots

Most gates read the live sibling workspace through `--workspace-root`. The
aggregation lock is different: it must validate the intentionally selected
member commits, not whatever reset or superseded branches happen to be checked
out in the live workspace.

Validate the lock directly against a prepared selected-member root:

```bash
python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-ws validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json
```

When running the full cutover gate runner, keep the live workspace root for
other gates and override only the release-lock root:

```bash
N4A_RELEASE_WORKSPACE_ROOT=/tmp/n4a-lock-ws python3 scripts/n4a_cutover_gates.py --gate release_lock_validation run --workspace-root /home/delete/nirs4all --json
```

If a selected-member root is missing, recreate one from the lock with
`scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output <selected-root>`
before validating. Do not regenerate the lock from `/home/delete/nirs4all`
unless the release train has intentionally selected those current sibling
commits.

`readiness` reads `docs/contracts/cutover/readiness-matrix.n4a.json`. It maps
each blocker to one owning repo, one evidence command, expected evidence, and the
exact missing contract. Rows with `required_for_cutover=false` are advisory V1
ecosystem rows; they should not block the `nirs4all` default-engine flip unless a
release manager explicitly promotes them into `drop-gates.n4a.json`.

The post-W2J integration state is checked by `post_w2j_cutover_state`, which is a
direct source/ledger inspection rather than a long parity run. It asserts that
`refactor/integration-nirs4all` now declares `DEFAULT_ENGINE = "dag-ml"`,
`nirs4all.api.run.run` defaults to `allow_fallback=False`, explicit legacy
fallback remains opt-in, dag-ml export reaches the legacy-refit bridge only via
`compatibility="legacy-refit"`, and the compatibility ledger reports
`coverage_meter.fallback == 0`. It also checks that the Studio, Web, tools,
cluster, and providers integration heads contain the Wave 2J source markers used
for L19 accounting.

The final V1 release is still not ready until all required gates pass in a
prepared release workspace. The current docs no longer treat
`DEFAULT_ENGINE="legacy"` or `fallback=6` as the expected state; any failure of
`post_w2j_cutover_state` or `pyref_coverage_zero` is a regression.

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

- Required rows cover the post-W2J cutover state, Python-reference parity,
  native `.n4a` export, dag-ml / dag-ml-data lockstep contracts, Studio/Web
  runtime adoption, migration tooling, and release locks.
- Advisory rows track provider and cluster readiness. They remain visible because
  they matter for the V1 ecosystem release, but they are not prerequisites for
  replacing the default `nirs4all` pipeline engine.

Use JSON output when coordinating agents:

```bash
python3 scripts/n4a_cutover_gates.py readiness --workspace-root /home/delete/nirs4all --json
python3 scripts/n4a_cutover_gates.py --gate pyref_coverage_zero readiness --workspace-root /home/delete/nirs4all --json
```
