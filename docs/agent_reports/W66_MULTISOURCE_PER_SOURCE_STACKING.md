# W66 Multi-Source Per-Source Stacking

Date: 2026-07-01

Status: blocked, fallback kept.

## Target

`multi_source_per_source_models_stacking`

Pipeline shape:

- by-source branch with shared `SNV() + PLSRegression(...)` body;
- `{"merge": "predictions"}`;
- downstream `Ridge` meta stage.

## Result

The native path can now reach execution for the boundary check, but dual-engine parity is not green.
No core commit was made and the fallback must remain.

Latest targeted run:

```text
.venv/bin/python -m pytest tests/integration/parity/test_conformance_dual_engine.py -k 'multi_source_per_source_models_stacking' -q
```

Outcome:

```text
1 passed, 1 failed
```

The boundary part passed, but dual-engine parity failed:

- legacy RMSE: `13.42399962265869`
- current native RMSE: `13.471697181183343`

`py_compile` passed for the touched dagml files during the investigation.

## Finding

This case is not a pure 3-column OOF stacking problem in legacy. Manual probing showed that the legacy
Ridge stage fits on a `10755`-feature layout:

- merged transformed source block: `SNV(src0) + SNV(src1) + SNV(src2)` = `6453`
- plus remaining transformed `source1` and `source2` blocks = `2151 + 2151`
- total = `10755`

That manual layout reproduced legacy closely:

- average train: `15.262224886966942`
- average validation: `19.665215493501826`
- average test: `13.424000134732905`

## Contract Notes

W68's OOF/refit guidance applies: this is documented legacy no-refit behavior, so `cv_only` is the
appropriate policy if/when the native lowering matches the legacy feature layout. Using
`require_full_coverage` would produce a different native/refit result.

W69's source-layout contract is necessary but not sufficient. The remaining implementation must apply
that source-layout contract to the Ridge stage and reproduce the cumulative post-merge multi-source
feature layout, not just feed a 3-column OOF prediction matrix.

## Next Step

Keep `multi_source_per_source_models_stacking` in `EXPECTED_FALLBACK`.

The next implementation slice should target the legacy cumulative source-layout replay for the
post-`{"merge": "predictions"}` Ridge stage and preserve the CV-only/no-refit row surface.
