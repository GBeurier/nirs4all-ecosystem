# W12 - Multisource Fallback Contract

Status: salvaged after max-turns, verified, and committed.

## Scope

W12 investigated why the multi-source conformance cases must remain in explicit
fallback instead of being lowered to native dag-ml today.

## Findings

- Legacy applies preprocessing per source, then concatenates for the model.
- The current native model-node path materializes multi-source `X` as an
  early-fusion concatenation and applies the preprocessing chain on that concat.
- For float-robust PLSR this is under tolerance, so `multi_source_baseline_snv_plsr`
  can run native.
- For fixed-seed RF the difference is visible:
  - legacy per-source SNV RF: about `21.0678`;
  - native on-concat SNV RF: about `21.0846`;
  - delta is about `1.7e-2`, above the `1e-3` parity tolerance.
- The by-source branch cases also differ in prediction bookkeeping: legacy emits
  per-source-replicated rows that the native branch paths do not yet reproduce.
- The per-source stacking case has no clean legacy oracle because legacy stacking
  refit is already skipped for by-source branches.
- The sources-concat RF case is not a good native contract target because the
  fixed-seed RF is sensitive to the legacy merge storage round-trip and native
  currently matches neither legacy value within tolerance.

## Changes

- Documented these boundaries directly in `EXPECTED_FALLBACK` inside
  `tests/integration/parity/test_conformance_dual_engine.py`.
- Removed the temporary local probe before commit.

## Verification

From `_worktrees/W12-nirs4all-multisource`:

```bash
/home/delete/nirs4all/nirs4all/.venv/bin/python -m py_compile \
  tests/integration/parity/test_conformance_dual_engine.py
ruff check tests/integration/parity/test_conformance_dual_engine.py
```

Result: both passed.

## Commit

`bea5323d test(parity): document multisource fallback contract`
