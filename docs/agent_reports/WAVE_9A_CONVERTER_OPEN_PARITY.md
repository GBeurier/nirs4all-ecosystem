# Wave 9A - Converter Open Parity

## Scope

Promote `e2e-converter-legacy-save-predictions-web` `python_open_pipeline` only after adding strict evidence that Python reopens the converted workspace metadata, not an executable repository descriptor.

## Files Modified

- `nirs4all-tools/tests/e2e/test_legacy_save_predictions_web.py`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`

## Decisions

- Added `python-open-pipeline.json` as a produced artifact from the converter rerun step.
- Evidence now opens `converted-workspace-v2/store.sqlite` read-only and checks SQLite integrity, FK identity, user version, row counts, pipeline/chain/prediction metadata, runtime result identity, store checksum, and array checksum.
- Wording is deliberately `pipeline metadata` reopen. The converter lane does not claim a converter-produced executable pipeline descriptor or repository best-refit coverage.
- `python_open_pipeline` moves from `contract` to `strict`; ecosystem V1 contract phases drop from 8 to 7.

## Tests

- `cd nirs4all-tools && python3.11 -m ruff check tests/e2e/test_legacy_save_predictions_web.py`
- `cd nirs4all-tools && PYTHONPATH=/home/delete/nirs4all/nirs4all:$PYTHONPATH PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_legacy_save_predictions_web.py --artifacts-dir=/tmp/n4a-converter-open`
- `cd nirs4all-tools && PYTHONPATH=/home/delete/nirs4all/nirs4all:$PYTHONPATH PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py validate`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `cd nirs4all-ecosystem && NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-converter-open-evidence run e2e-converter-legacy-save-predictions-web --execute`
- `cd nirs4all-ecosystem && python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-converter-open-evidence evidence --scenario e2e-converter-legacy-save-predictions-web --json`
- `cd nirs4all-ecosystem && python3.11 -m pytest tests/test_e2e_scenarios.py -q`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q`

## Risks

- The lane is strict for converted workspace/pipeline metadata reopen and rerun parity. It is still intentionally not repository forced-best-refit coverage.
- The Web scenario was run with `NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin` because the local `nirs4all-ui` checkout has unrelated dirty/behind work owned by another agent.
