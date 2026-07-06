# Wave 6E - Cross-language E2E infrastructure review

Date: 2026-07-06

## Scope

- Review `nirs4all-ecosystem` cross-language E2E scenario orchestration.
- Review the post-run artifact evidence gate, including on-demand freshness checks.
- Keep the runner, tests, and workflow unchanged unless a clear defect is found.

## Result

- No code defect was found in `scripts/n4a_e2e_scenarios.py`, `tests/test_e2e_scenarios.py`, `docs/CROSS_LANGUAGE_E2E.md`, or `.github/workflows/cross-language-e2e.yml`.
- The current workspace contract is internally consistent:
  - `10/10` scenarios validate.
  - `10/10` scenarios are currently ready in this checkout.
  - The local `.n4a-e2e-artifacts` archive verifies cleanly.
  - The freshness gate also passes against the current archive with `--max-age-seconds 604800`.

## Commands run

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence --json`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence --json --max-age-seconds 604800`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`

## Notes

- The standalone `evidence` command is documented and tested, while the execution path still enforces per-step artifact refresh and non-passing JSON evidence rejection.
- The workflow does not run a separate post-run `evidence` step today, but the executed `run` and `run-ready --execute` paths already share the artifact validation logic, so this is not a correctness gap by itself.

## Remaining risk

- Scenario-level honesty is good, not complete: all `10` scenarios remain `hybrid`.
- The dominant non-strict areas are still `papers_export`, `repository_forced_best_refit`, and selected `wasm_web_reuse` or reopen/rerun phases depending on the scenario.
- A fresh archive can be proven on demand, but that proof is only as strong as the chosen `--max-age-seconds` threshold and the operator's discipline in using it.
