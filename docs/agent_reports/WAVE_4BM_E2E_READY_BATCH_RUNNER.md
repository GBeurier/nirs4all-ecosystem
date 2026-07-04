# Wave 4BM - E2E Ready Batch Runner

## Scope

- Added a `run-ready` command to the cross-language E2E runner.
- Wired GitHub Actions so `workflow_dispatch` with an empty scenario and `execute=true` runs every currently ready scenario.
- Preserved strict semantics: the batch still exits `2` while any declared scenario remains blocked.

## Files changed

- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `.github/workflows/cross-language-e2e.yml`

## Decisions

- `run-ready` executes only plans whose status is `ready`.
- Blocked scenarios are reported after the ready batch and keep the overall run non-green.
- Dry-run mode prints a JSON summary of ready and blocked scenario ids.

## Tests

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py run-ready`
- YAML parse check for `.github/workflows/cross-language-e2e.yml`
- `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`
- `git diff --check`

## Risks

- `run-ready --execute` can be expensive because it runs every ready scenario in sequence. It intentionally avoids full parity and should be used after meaningful integration batches.
- The command returns `2` until all ten scenarios are truly executable; downstream CI must not treat that as a passing full gate.
