# RC Python Parity Refresh - 2026-07-02

Lane: B/C - Python parity, dag-ml runtime bridge
Agent: Codex coordinator with Claude read-only review assist

## Summary

Closed the four failures from the previous full parity run and refreshed the
Python RC proof head.

New Python head:

- `42448821 fix(parity): handle disabled chart steps in dagml`
- Branch: `rc/v1-full-refactor-python`
- Tag: `n4a-v1-rc1-2026.07-refactor`

## Files Modified

In `RC-v1-nirs4all-python`:

- `nirs4all/api/run.py`
- `nirs4all/pipeline/dagml/run_backend.py`
- `tests/integration/parity/test_conformance_examples_smoke.py`
- `tests/integration/parity/test_dagml_cli_runner.py`

## Decisions

- Chart-only pipeline steps are side effects. On the dag-ml engine they are
  stripped only when both `save_charts=False` and `plots_visible=False`.
- If chart rendering is requested, dag-ml refuses with `DagMlUnsupported`
  instead of pretending to create legacy chart artifacts.
- The public preprocessing example now runs on dag-ml when charts are disabled.
- The public classification example still refuses, but now for the real
  remaining gap: `feature_augmentation` followed by a downstream X transform
  requiring processing-axis / 3D dataplane support.
- Sample augmentation direct baselines now compare against the already
  preprocessed augmented dataset; they no longer double-apply SNV.

## Review

Claude read-only review started on the diff and found a missing chart controller
keyword surface: `spectra_dist`, `spectral_distribution`, and
`spectra_envelope`. The coordinator patched the list and extended the direct
chart-step test before rerunning the gates. Claude stopped at maxTurns before a
final report, so the usable review result is this finding only.

## Tests

Python RC:

- `ruff check nirs4all/api/run.py nirs4all/pipeline/dagml/run_backend.py tests/integration/parity/test_dagml_cli_runner.py tests/integration/parity/test_conformance_examples_smoke.py`
  -> passed.
- Targeted:
  `pytest tests/integration/parity/test_conformance_examples_smoke.py tests/integration/parity/test_dagml_cli_runner.py::test_dagml_chart_steps_are_inert_only_when_disabled tests/integration/parity/test_dagml_cli_runner.py::test_run_via_dagml_sample_augmentation tests/integration/parity/test_dagml_cli_runner.py::test_run_via_dagml_fold_local_stateful_augmentation -q -ra`
  -> `12 passed, 11 warnings`.
- Full parity:
  `pytest tests/integration/parity -q -ra`
  -> `853 passed, 14 skipped, 6 xfailed, 1794 warnings in 2281.65s`.

## Remaining Risks

- Full parity is green but not clean: 14 skips and 6 xfails remain release
  treatment items.
- The local environment lacks `n4m`, SHAP, and `referencing`; a zero-skip
  release proof needs either those dependencies installed or separate explicit
  optional-environment gates.
- `feature_augmentation` followed by a downstream X transform remains a real
  dag-ml V1 gap for the classification tutorial.
