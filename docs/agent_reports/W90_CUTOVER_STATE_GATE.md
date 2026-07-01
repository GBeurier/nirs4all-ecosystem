# W90 Cutover State Gate

Date: 2026-07-01

## Summary

Fact-checked the post-Wave-2J cutover state directly in the integration worktrees
and updated the ecosystem cutover gate/docs so they no longer claim the pre-W2J
state.

Current direct evidence:

- `INT-nirs4all` `f970bf0e` on `refactor/integration-nirs4all` declares
  `DEFAULT_ENGINE = "dag-ml"`.
- `nirs4all.api.run.run` defaults `allow_fallback=False`; legacy fallback is
  only explicit opt-in (`engine="legacy"` or `allow_fallback=True`).
- `RunResult.export()` / `export_model()` reach the legacy-refit bridge only
  through `compatibility="legacy-refit"`.
- `docs/compatibility.json` reports `coverage_meter.fallback == 0` and an empty
  `expected_fallback`.
- Studio/Web/tools/cluster/providers integration heads used for L19 accounting
  are present: Studio `1979b72`, Web `60a0967`, tools `44ce7a3`, cluster
  `eac4d0b`, providers `1e289a9`.

## Changed Files

- `scripts/n4a_cutover_gates.py`
- `tests/test_cutover_state_gate.py`
- `docs/contracts/cutover/drop-gates.n4a.json`
- `docs/contracts/cutover/readiness-matrix.n4a.json`
- `docs/CUTOVER_GATE_RUNNER.md`
- `docs/PARALLEL_REFACTORING_SYNC.md`
- `docs/agent_reports/W90_CUTOVER_STATE_GATE.md`

## Commit

- W90 ecosystem commit: this report is committed with the gate/docs changes; final
  hash is recorded in the assistant handoff after the commit is created.

## Verification

- `python3 -m pytest tests/test_cutover_state_gate.py -q` -> 2 passed.
- `python3 scripts/n4a_cutover_gates.py --gate cutover_gate_contract_selfcheck --gate post_w2j_cutover_state run --workspace-root /home/delete/nirs4all --json` -> passed, no required failures.
- `python3 -m py_compile scripts/n4a_cutover_gates.py tests/test_cutover_state_gate.py` -> passed.
- `git diff --check` -> passed.
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all` -> passed.

## Failures

- An intermediate `post-w2j-state` run failed because the new cluster source
  marker looked for the literal phrase `worker loss`; the integration code uses
  `dead_worker_tasks_requeue` / `worker lost`. The marker was corrected and the
  gate passed.

## Blockers

`LOCK-DROP` / `L19` is no longer blocked on `DEFAULT_ENGINE="legacy"` or
`fallback=6`. Remaining named blockers before a V1 release claim:

- strict full cutover gate run on the final selected heads;
- W91 dag-ml / dag-ml-data lockstep freshness;
- W95 Studio strict runtime fallback default.

## Follow-Up

Coordinator integration is needed only to run the final strict multi-repo gate
after the Wave 2K follow-ups land. W90 did not edit runtime code in `nirs4all`,
Studio, Web, tools, cluster, or providers.
