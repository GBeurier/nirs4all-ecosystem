# Technical debt register

Cross-repository debt that is accepted for now and has a planned repayment.
Each entry names the owner, the interim behaviour, the repayment and the date
from which it should be scheduled.

## TD-2026-11-19-01 — AOM chain and operator names are formatted by hosts

- **Schedule from:** 26 November 2026.
- **Owner:** [Methods](https://github.com/GBeurier/nirs4all-methods) (C ABI and every binding); consumers: Web (single-dataset and multimodal labs).
- **Interim (Methods 1.4.2, ABI 2.24 unchanged):** a method result
  (`n4m_method_result_t`) carries double matrices, int32/int64 vectors and
  scalars only. The AOM estimators (`aom_pop.calibration`, `aom_pop.aom_pls`,
  `aom_pop.pop_pls`) therefore describe the screened preprocessing chains in
  their fit result numerically — operator kinds (`N4M_OP_*`), operator
  parameters and chain offsets — together with the per-chain internal scores.
  Web turns these descriptors into display names (for example
  `SNV › SG d1 w11 p2`).
- **Why it is debt:** the operator names are owner vocabulary (for example
  the versioned `strict10-gaussian-density-v2` bank). Formatting them in a host
  duplicates presentation that Methods should own, and every other host
  (Python SDK, R, Studio) would have to repeat it.
- **Repayment:** add a string-vector entry kind to method results (new getter
  and `N4M_RESULT_*` kind, an ABI minor and therefore a Methods minor), emit
  `chain_names` / `operator_names` from the AOM adapters, adopt the new kind in
  the JS, Python, R, Rust and MATLAB bindings, move consumers to the new
  Methods series, then remove the Web-side name formatter.
- **Scientific note:** the exposed per-chain scores come from AOM's internal
  cross-validation (or, in Fast mode, its covariance screening criterion) inside
  the training data of the fit. They are diagnostics of the internal selection
  and must never be presented as outer out-of-fold or test scores.
