# Wave 4BG - Provider Repository Core E2E

Date: 2026-07-04

## Scope

Turned `e2e-dataset-provider-repository-roundtrip` into an executable gate over
providers, datasets/io, repository, and core Python + JavaScript/WASM loaders.

## Files changed

- `nirs4all-repository/pipelines/core_portable_snv_savgol_pls/`
  - Adds a repository recipe using only the current core portable operator
    vocabulary: Kennard-Stone, SNV, Savitzky-Golay, and PLSRegression.
  - Adds descriptor, card, manifest, RO-Crate metadata, and canonical recipe.
- `nirs4all-repository/catalog/index.json`
  - Regenerated from the repository builder; catalogue count is now 6.
- `nirs4all-providers/tests/conftest.py`
  - Adds `--artifacts-dir` support for ecosystem-driven E2E tests.
- `nirs4all-providers/tests/e2e/test_dataset_provider_repository_roundtrip.py`
  - Validates neutral provider descriptors.
  - Lists a real dataset catalogue and materializes a small CSV through the
    `nirs4all-io` package bridge.
  - Resolves the portable repository pipeline, verifies its bundle, and writes
    provider-resolution, repository-index, and repository-pipeline artifacts.
- `nirs4all-core/scripts/e2e/consume_repository_descriptor.py`
  - Consumes the repository-pipeline artifact through the Python binding and the
    JavaScript/WASM package loader, then compares normalized classes, name, and
    random state.
  - Resolves Windows `node.exe` under WSL when Linux `node` is absent.
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
  - Wires the two executable steps.
  - Uses `python3.11` explicitly.
  - Runs `npm ci --ignore-scripts --no-audit --no-fund` before the JS/WASM
    loader gate so fresh checkouts get the `yaml` dependency.

## Tests run

- `nirs4all-repository`: `PYTHONPATH=src python3.11 -m nirs4all_repository.cli build`
- `nirs4all-repository`: `PYTHONPATH=src python3.11 -m nirs4all_repository.cli validate --all`
- `nirs4all-providers`: `PYTHONPATH=src:/home/delete/nirs4all/nirs4all-datasets/src:/home/delete/nirs4all/nirs4all-io/src:/home/delete/nirs4all/nirs4all-repository/src python3.11 -m pytest -q tests/e2e/test_dataset_provider_repository_roundtrip.py`
- `nirs4all-providers`: `python3.11 -m ruff check tests/conftest.py tests/e2e/test_dataset_provider_repository_roundtrip.py`
- `nirs4all-core`: `python3.11 -m py_compile scripts/e2e/consume_repository_descriptor.py`
- `nirs4all-core`: `PYTHONPATH=bindings/python/src python3.11 -m unittest discover -s bindings/python/tests -p 'test_pipeline_contract.py'`
- `nirs4all-core`: `python3.11 -m ruff check scripts/e2e/consume_repository_descriptor.py`
- `nirs4all-core`: `npm --prefix bindings/wasm ci --ignore-scripts --no-audit --no-fund`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py run e2e-dataset-provider-repository-roundtrip --execute`
- `nirs4all-ecosystem`: `python3.11 -m pytest -q` -> 33 passed.
- `nirs4all-ecosystem`: `python3.11 -m ruff check scripts/n4a_e2e_scenarios.py tests`

## Decisions

- This scenario now honestly claims Python + JavaScript/WASM loader parity only.
  It no longer claims R parity for this provider/repository path.
- R remains a separate follow-up because the current local `n4m` R binding does
  not expose the preprocessing/splitter functions required by this pipeline.
- The repository descriptor wording was softened from "shared Python/R/WASM/
  MATLAB subset" to "core portable operator vocabulary" to avoid overstating
  binding parity.
- The gate compares loader normalization and portable class metadata; it does
  not claim prediction parity or full pipeline execution parity.

## Review

- Claude Code review was launched with `fable`/max; it fell back to Opus. It
  inspected repository hashes, manifests, Python/WASM loader shape, and the
  `card().recipe.path` vs index `recipe.relpath` distinction.
- The long review was interrupted before a final summary because it kept
  exploring. Findings acted on during review:
  - generated `__pycache__` files in new E2E directories were removed;
  - JS/WASM loader has a hard top-level `yaml` dependency, so the ecosystem step
    now runs `npm ci` before invoking it.
- A second bounded Opus review hit `maxTurns` before producing a final summary;
  it did not surface a blocking issue before the limit.
- Manual follow-up review confirmed `card()["recipe"]["path"]` is descriptor
  shape while `repository-index.json` uses `recipe.relpath`; the test handles
  both separately.

## Risks

- This is still a loader/contract gate. It does not replace the later full
  Python-reference parity, prediction parity, or R/MATLAB execution gates.
- The JS/WASM step requires npm network/cache access for a fresh checkout.
- The dataset package proof uses a synthetic CSV to exercise the IO bridge; it
  does not fetch or reshape one of the missing Dataverse datasets.
