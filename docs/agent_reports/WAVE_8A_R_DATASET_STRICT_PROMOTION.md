# Wave 8A - R Dataset Strict Promotion

Date: 2026-07-08

## Summary

Promoted `e2e-r-dataset-io-pipeline-save` from `hybrid` to `strict` because the
same-dataset R/Python/native parity ledger already proves numeric equality on the
real catalog dataset within tolerance.

## Files Modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/CROSS_LANGUAGE_E2E.md`
- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`

## Tests Run

- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --json-out /tmp/n4a-e2e-coverage-r-strict.json --markdown-out /tmp/n4a-e2e-coverage-r-strict.md`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-r-dataset-strict run --execute e2e-r-dataset-io-pipeline-save`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-r-dataset-strict evidence --scenario e2e-r-dataset-io-pipeline-save --json`

## Result

- Coverage debt moved from `strictness_gaps=7` to `strictness_gaps=6`.
- Real R run produced 10 verified artifacts.
- `python-reopen-ledger.json` reported `status=passed`, `tolerance=1e-08`,
  `targets_max_abs_delta=0.0`, selected prediction/R artifact max delta
  `4.9112713895738125e-11`, and finite targets/predictions.

## Risks

- The strict non-numeric exception for the fixture gate itself remains listed:
  `make test-r-parity fixture gate passes`.
- Broader formats/WASM/Rust and multimodal Web/Studio gaps remain intentionally
  `hybrid` or `contract`; they were reviewed and not promoted by label only.
