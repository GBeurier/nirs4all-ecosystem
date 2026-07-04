# Wave 4DC - E2E Reinforcement Integration

Date: 2026-07-04

## Integrated lanes

| Repo | Commit | Scope |
| --- | --- | --- |
| `nirs4all-core` | `dfc5764` | Strengthen R dataset/workspace/pipeline E2E, add R roundtrip evidence, add multimodal source/header/sample-id audits, and add multisource prediction-table/vector-parity evidence fields. |
| `nirs4all-web` | `60cb1fa` | Strengthen the Web/WASM repository smoke with a deterministic repository pipeline fixture, stable `pipeline_id`, `descriptor_sha256`, non-demo uploaded dataset, screenshot/evidence checks, zero console-error gate, and source-vs-imported prediction comparison. |
| `nirs4all-ecosystem` | this batch | Pin those heads and update the cross-language E2E manifest so gaps match the new proof level. |

## Checks

- `nirs4all-core`: `python3.11 -m ruff check scripts/e2e/run_multimodal_roundtrip.py scripts/e2e/run_multisource_stacking_replay.py` -> passed.
- `nirs4all-core`: `python3.11 -m py_compile scripts/e2e/run_multimodal_roundtrip.py scripts/e2e/run_multisource_stacking_replay.py` -> passed.
- `nirs4all-core`: `python3.11 scripts/e2e/prepare_r_dataset_io_pipeline.py --out /tmp/nirs4all-r-e2e-dataset-review` -> prepared the provider-backed dataset payload.
- `nirs4all-core`: full targeted R sequence passed with `/home/delete/miniconda3/envs/pls4all_r/bin/Rscript`: dataset/IO prepare, `make test-r-parity`, saved workspace/pipeline/prediction reopen, rerun, and Python portable oracle fixture comparison.
- `nirs4all-web`: `node --check tests/pipeline-repository-smoke.mjs` -> passed.
- `nirs4all-web`: `npm run build` -> passed.
- `nirs4all-web`: `ARTIFACTS_DIR=/tmp/n4a-web-pipeline-repository-review npm run smoke:pipeline-repository` -> passed; evidence reported `status=passed`, `console_error_count=0`, `dataset_id=lab-transfer-corn-protein-2026-07`, prediction delta `0`, and non-empty screenshot/evidence artifacts.

## Remaining gaps

- R now reopens and reruns saved artifacts and compares the portable Python oracle fixture. It still lacks a Python oracle generated from the provider-backed dataset assembled by `prepare_r_dataset_io_pipeline.py`.
- Web now avoids the bundled demo/sample path and uses a non-demo uploaded fixture dataset. It still lacks a provider/catalog dataset run with a Python-vs-WASM numeric oracle.
- Multimodal now records source/header/sample-id audits and runtime metadata alignment, but Web/Studio roundtrip and native multimodal execution remain pending.
- Multisource now records prediction-table array coverage, sample/fold/partition/target-width alignment, and vector parity when native vectors are present. Missing native vectors remain explicit evidence gaps rather than strict claims.
