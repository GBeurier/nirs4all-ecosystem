# W13 - Native dag-ml `.n4a` Export

Status: salvaged after max-turns, fixed, verified, and committed.

## Scope

W13 implements the native `.n4a` bundle export path for a single-model dag-ml run:
when a dag-ml run captured exactly one native refit artifact, `RunResult.export()`
can package that artifact directly instead of refitting through the legacy Python
engine.

## Changes

- Added `write_single_model_bundle()` for minimal valid `.n4a` bundles around one
  predict-capable model.
- Exported that helper from `nirs4all.pipeline.bundle`.
- Added `RunResult._dagml_native_export_bundle()`:
  - native path only for `format == "n4a"`;
  - requires an existing native results dir;
  - requires exactly one captured artifact;
  - verify-then-loads via native results reader;
  - falls back to the legacy bridge for no native dir, multiple artifacts,
    `n4a.py`, or native-read failure.
- Added unit coverage for bundle reload-predict exactness and y inverse handling.
- Added integration coverage proving the native path does not touch legacy refit,
  plus fallback guards.

## Fix During Salvage

The agent's integration test initially failed because the monkeypatch target
`nirs4all.api.run.run` hit the package-level `run` function re-export. The test
now imports the `nirs4all.api.run` submodule explicitly with `importlib` before
patching its `run` attribute.

## Verification

From `_worktrees/W13-nirs4all-export`:

```bash
ruff check nirs4all/api/result.py \
  nirs4all/pipeline/bundle/generator.py \
  tests/unit/pipeline/bundle/test_native_bundle.py \
  tests/integration/parity/test_dagml_native_n4a_bundle.py

/home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest -q \
  tests/unit/pipeline/bundle/test_native_bundle.py \
  tests/integration/parity/test_dagml_native_n4a_bundle.py
```

Result: `9 passed, 22 warnings`. The warnings are existing Polars string-cache
deprecations from dataset indexing.

## Commit

`97eb7585 feat(export): build native dag-ml n4a bundles`
