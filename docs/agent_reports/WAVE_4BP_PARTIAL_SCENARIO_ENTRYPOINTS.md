# Wave 4BP - Partial Scenario Entrypoints

## Scope

- Integrated two parallel agent lanes into the ecosystem manifest.
- Kept the scenarios honest: both now have executable ready steps, but both still exit non-green because their remaining cross-repo runtime/UI steps are absent.

## Commits Integrated

- `nirs4all-tools`: `440e588 test(e2e): add legacy converter artifact entrypoint`
- `nirs4all-repository`: `05f4a44 test(recipes): reject archival paper step records`
- `nirs4all-papers`: `1a730dd test(e2e): add paper repository refit handoff`

## Manifest Changes

- `e2e-python-reopen-paper-repository-refit`
  - `papers-export-repository-refit` is ready and uses `python3.11`.
  - `python-reopen-rerun` remains blocked on `nirs4all/tests/e2e/test_pipeline_reopen_paper_repository.py`.
- `e2e-converter-legacy-save-predictions-web`
  - `convert-legacy-save` is ready and uses `python3.11`.
  - `web-open-predictions` remains blocked on `nirs4all-web/studio-lite/tests/e2e/converted-predictions-render.spec.ts`.

## Tests

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-partial-4bp run e2e-python-reopen-paper-repository-refit --execute --allow-blocked`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-partial-4bp run e2e-converter-legacy-save-predictions-web --execute --allow-blocked`

## Artifacts

- `/tmp/n4a-e2e-partial-4bp/python-paper-repository/paper-export.zip`
- `/tmp/n4a-e2e-partial-4bp/python-paper-repository/repository-best-pipeline.json`
- `/tmp/n4a-e2e-partial-4bp/legacy-converter/converted-workspace.n4a.json`
- `/tmp/n4a-e2e-partial-4bp/legacy-converter/predictions.rt_result.json`

## Risks

- The paper/repository smoke intentionally does not execute a runtime refit; that still belongs to the `nirs4all` Python oracle lane.
- The converter smoke intentionally marks legacy replay parity as `not_run`; it proves deterministic migration/lowering and leaves Web panel rendering to the pending Web entrypoint.
