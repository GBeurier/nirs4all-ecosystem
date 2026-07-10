# WAVE 9ZS - E2E, cutover, and cockpit status

Date: 2026-07-10

## Scope

- Closed the CI regression that made the Web/WASM repository-refit scenario fail on a vendored `nirs4all-ui` shim drift.
- Re-ran the selected Web/Python/native scenario and then the full ready cross-language E2E suite.
- Updated cutover gate metadata to target the current `nirs4all-web/web-app` layout instead of the retired `studio-lite` path.
- Rechecked the public cockpit and R-universe state after the datasets 0.3.6 release.

## Files changed

- `nirs4all-ui` gitlink advanced to `1450b5a` so the ecosystem checkout matches the Web shim source used by `nirs4all-web`.
- `.github/workflows/cross-language-e2e.yml` now skips R setup for selected non-R scenarios and filters only the workspace-wide readiness tests that require R in plan/non-R selected runs.
- `docs/contracts/cutover/drop-gates.n4a.json` now uses `_worktrees/RC-v1-web/web-app` for `web_runtime_contract`.
- `tests/test_e2e_scenarios.py` and `tests/test_cutover_state_gate.py` were updated to lock those workflow and cutover expectations.

## Validation

- Local selected scenario:
  `python3.11 scripts/n4a_e2e_scenarios.py run e2e-python-reopen-paper-repository-refit --execute`
  passed, including Web/WASM import of the repository best-pipeline handoff with max delta `3.0233593406592263e-12`.
- GitHub selected scenario:
  workflow `Cross-language E2E scenarios` run `29087738513` passed on `main`.
- GitHub full ready runtime suite:
  workflow `Cross-language E2E scenarios` run `29088345220` passed on `2880712ffae326022f846a96effbbe1fe239ada2`.
  The run executed ready scenarios, verified ready scenario artifacts, and checked the committed runtime evidence ledger.
- GitHub cutover tooling:
  workflow `cutover-gates` validate run `29089122983` passed on `2880712ffae326022f846a96effbbe1fe239ada2`.
- Local contract checks:
  `python3.11 -m pytest -q tests/test_e2e_scenarios.py tests/test_cutover_state_gate.py` passed (`141 passed`).
  `python3.11 scripts/n4a_e2e_scenarios.py validate` passed (`OK: 11 cross-language E2E scenarios`).

## Cockpit and R-universe status

- Public cockpit snapshot timestamp: `2026-07-10T10:03:45.403130+00:00`.
- Public cockpit still reports `nirs4all-datasets` rollup `stale`.
- Published datasets evidence is otherwise current: source manifest/tag/release are `0.3.6`, PyPI is `0.3.6`, crates are `0.3.6`, npm is `0.3.6`, GitHub release is `0.3.6`, Pages is green.
- R-universe still serves `nirs4alldatasets` `0.3.5` at `RemoteSha` `67d47c557bcb8770506409d2c688cb3b60384c18`.
- The cockpit manual action for `runiverse-datasets-rebuild` remains valid; no cockpit refresh was pushed because the external registry state did not change.

## Decisions

- The failed older E2E runs are superseded by run `29088345220` on the current head.
- The full Python-reference parity batch was not relaunched in this wave; the user asked to reserve full parity for large batches, and the current batch's runtime gate is the cross-language E2E layer.
- Strict cutover execution remains a prepared-workspace gate. GitHub `validate` proves the runner/manifest contract, while `strict` still requires the selected RC worktrees to exist at the expected release workspace paths.

## Risks / follow-up

- R-universe is the only observed external publication lag for `nirs4all-datasets`; recheck and refresh cockpit once it serves `0.3.6`.
- If a production cutover decision is requested, run the strict cutover gate in a prepared RC workspace or update the cutover manifest to a new release workspace topology before treating strict GitHub execution as authoritative.
