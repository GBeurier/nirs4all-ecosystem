# Wave 4CH - Multimodal E2E

## Scope

- Closed `e2e-multimodal-python-r-wasm-roundtrip`.
- Added a full Python oracle that creates a synthetic multimodal NIRS plus metadata dataset, pipeline, predictions, workspace save, and `.n4a` export.
- Added the paired core runner that replays the same fused dense view through Python core, R, and JavaScript/WASM.

## Commits Integrated

- `nirs4all`: `ce08bd3d58ef test(e2e): add multimodal roundtrip oracle` on `refactor/L17-pyref`.
- `nirs4all-core`: `9ce5dd0fec64 test(e2e): add multimodal core roundtrip` on `main`.
- `dag-ml`: `5e2b988006a8 fix(runtime): scope by-source data views` on `refactor/L20-lockstep`.

## Ecosystem Contract Changes

- The scenario now declares `python`, `r`, and `javascript_wasm` only.
- Web is not claimed for this scenario because no concrete Web roundtrip step exists yet; Web coverage remains handled by the dedicated Web/WASM and converted-predictions scenarios.
- Runtime prediction files are produced only after real execution. Missing runtimes are written as blocker evidence instead of skipped or xfailed green.
- The paired core step records `core-roundtrip-evidence.json` as a required artifact.

## Tests

- `python3.11 -m py_compile tests/e2e/test_multimodal_roundtrip.py`
- `python3.11 -m ruff check tests/e2e/test_multimodal_roundtrip.py`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/e2e/test_multimodal_roundtrip.py::test_generate_oracle --artifacts-dir=/tmp/n4a-e2e-multimodal-4cg -q`
- `python3.11 -m py_compile scripts/e2e/run_multimodal_roundtrip.py`
- `python3.11 -m ruff check scripts/e2e/run_multimodal_roundtrip.py`
- `PATH=/home/delete/miniconda3/envs/pls4all_r/bin:/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH LD_LIBRARY_PATH=/home/delete/nirs4all/nirs4all-methods/build/dev-release/cpp/src:$LD_LIBRARY_PATH PYTHONDONTWRITEBYTECODE=1 python3.11 scripts/e2e/run_multimodal_roundtrip.py --workspace-root /home/delete/nirs4all --artifacts-dir /tmp/n4a-e2e-multimodal-4cg`
- `cargo test -p nirs4all`
- `make test-v1-surfaces`
- `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-multimodal-orchestrated-4ch run e2e-multimodal-python-r-wasm-roundtrip --execute`

## Artifacts

- `/tmp/n4a-e2e-multimodal-orchestrated-4ch/multimodal-roundtrip/multimodal-dataset.json`
- `/tmp/n4a-e2e-multimodal-orchestrated-4ch/multimodal-roundtrip/multimodal-pipeline.n4a.json`
- `/tmp/n4a-e2e-multimodal-orchestrated-4ch/multimodal-roundtrip/python-predictions.parquet`
- `/tmp/n4a-e2e-multimodal-orchestrated-4ch/multimodal-roundtrip/r-predictions.parquet`
- `/tmp/n4a-e2e-multimodal-orchestrated-4ch/multimodal-roundtrip/wasm-predictions.json`
- `/tmp/n4a-e2e-multimodal-orchestrated-4ch/multimodal-roundtrip/core-roundtrip-evidence.json`

## Result Snapshot

- Dataset SHA256 matched across oracle and core runner: `9702b4879e0f17942c7f9bacec4fb2fc8e59e84d73b1cf825e222922f928f8ba`.
- Pipeline SHA256 matched across oracle and core runner: `5eb87c4c23d7adf7f96076ad95094348d70d040d305430ff41b6c7746c27ea93`.
- `nirs4all-core-python`: `passed`, `prediction_abs_max=8.881784197001252e-16`, `rmse_abs_max=6.938893903907228e-17`.
- `r`: `passed`, `prediction_abs_max=8.881784197001252e-16`, `rmse_abs_max=6.938893903907228e-17`.
- `javascript_wasm`: `passed`, `prediction_abs_max=8.881784197001252e-16`, `rmse_abs_max=6.938893903907228e-17`, `predict_roundtrip_abs_max=0.0`.

## Risks

- The scenario proves the current portable dense fused view for multimodal data. It does not yet prove arbitrary nested multimodal IO structures in Web.
- The local Octave/MATLAB MEX gate required rebuilding ignored MEX binaries against the current `libn4m.so` ABI. The durable release job must rebuild those artifacts rather than relying on stale local binaries.
