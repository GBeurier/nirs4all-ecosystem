# W18 - Providers Phase 2

Status: salvaged after max-turns, verified, and committed.

## Scope

W18 expanded `nirs4all-providers` as a read-adapter layer while preserving the
rule that providers do not execute ML and do not write back to the ecosystem.

## Changes

- Repository provider:
  - added `recipe()` as served canonical pipeline config;
  - kept execution outside the provider boundary.
- Benchmark provider:
  - added `overview()`, `datasets()`, `operators()`, and `residuals()`;
  - kept benchmark execution/queueing deferred.
- Dataset provider:
  - added a soft `to_dataset_package()` pass-through to future
    `nirs4all_io.to_dataset_package`;
  - absent `nirs4all-io` raises `ProviderUnavailable`;
  - installed-but-missing entrypoint raises a clear LOCK-IO deferral.
- Paper provider:
  - added `list_papers()`, `citation()`, and `bibtex()`;
  - kept only explicit `build_repro_page()` as local-output write.
- Added conformance tests that pin adapter capability names and real backing API
  expectations where optional extras are installed.

## Verification

From `_worktrees/W18-providers` with a local Python 3.11 venv:

```bash
.venv/bin/ruff check src tests
.venv/bin/python -m pytest -q
.venv/bin/mypy src/nirs4all_providers
```

Results:

- Ruff: clean.
- Pytest: `51` total outcomes with expected skips for absent optional extras.
- Mypy: success on 9 source files.

## Commit

`2411568 feat(providers): expand read-adapter conformance surface`
