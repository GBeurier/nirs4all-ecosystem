# Wave 3AQ - Studio/Web Runtime and Tools Golden Freshness Audit

Date: 2026-07-02

## Scope

This batch re-audited old W95/W96/W97 worktrees after reset, without merging
them wholesale:

- Lane H: `nirs4all-studio` strict runtime and runtime diagnostics.
- Lane H: `nirs4all-web` studio-lite runtime diagnostics.
- Lane D: `nirs4all-tools` W97 real-golden migration fixtures.

No source patch was needed. Full Studio/Web e2e and full parity gates were
intentionally not run in this audit batch.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Lagrange the 2nd | `nirs4all-studio` W95/W96 audit | no-op, verified | W95 `88fbd99` and W96 `a32fbb9` are already ancestors of current `main`. |
| Goodall the 2nd | `nirs4all-web` W96 audit | no-op, verified | W96 `f3ba05e` is already ancestor of current `main`; W3AN added the remaining worker `rtResult` follow-up. |
| Archimedes the 2nd | `nirs4all-tools` W97 audit | no-op, verified | W97 `c10934a` is already integrated; post-W101 fixture honesty fixes are present. |

## Findings

### `nirs4all-studio`

- No code change was required.
- The old W99 finding that W95/W96 were uncommitted is superseded by current
  `main`.
- Current Studio has strict runtime defaults for run/model request paths:
  `allow_fallback=False` is present on the model/run request and driver surfaces.
- Runtime diagnostics coverage from W96 is present.
- No Studio route was changed in this batch.

### `nirs4all-web`

- No code change was required.
- W96 runtime-error UI support is already present:
  - `App.tsx` consumes the shared runtime error formatting;
  - `runtimeErrors.ts` and `runtimeErrors.test.ts` exist;
  - W3AN already integrated the later worker-result `rtResult` propagation.
- No backend/native behavior was reimplemented in Web.

### `nirs4all-tools`

- No code change was required.
- W97 is already integrated through `0ff31c2`.
- The post-W101 fixture honesty corrections are present:
  - `sample.meta.parquet` is a real reduced Parquet sidecar;
  - `store.duckdb` is documented and tested as an opaque preserved sentinel,
    not a semantic DuckDB golden.
- Tools remains an offline converter/migration surface; runtime legacy support
  was not introduced.

## Validation

`nirs4all-studio`:

- `rtk .venv/bin/python -m pytest tests/test_execution_driver.py tests/test_runs_engine_routing.py tests/test_runs_execution_backend.py -q --tb=short` -> 67 passed.
- `vitest run src/components/runtime/RuntimeComponents.test.tsx src/ui/runtime/resultMetadata.test.ts` with explicit Node 24 -> 9 passed.
- Targeted Playwright W96 diagnostic test was attempted but blocked before app
  execution because local port `8000` was occupied by a `nirs4all-benchmarks`
  server. The server was not stopped.

`nirs4all-web`:

- `npm run typecheck` -> passed.
- `npx vitest run --config vitest.config.ts src/app/runtimeErrors.test.ts src/engine/worker-engine.test.ts src/engine/rt-result.goldens.test.ts` -> 14 passed.
- `git diff --check -- studio-lite/src/app studio-lite/src/engine studio-lite/tests` -> passed.

`nirs4all-tools`:

- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest tests/test_real_golden_fixtures.py tests/test_commands.py tests/test_native_results.py tests/test_detect.py -q -p no:cacheprovider` -> 76 passed.
- `python3.11 -m ruff check src tests` -> passed.
- `git diff --check` -> passed.

## Gate Policy

- No full Studio `lint:parallel`, full `test:parallel`, or full Playwright suite
  was run.
- No full Web smoke/browser gate was run.
- No full Python-reference parity was run.
- No tests were reduced, xfailed, or weakened.
- No superseded Claude/worktree branch was merged blindly.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Risks

- Studio/Web release still needs the strict cutover gates in a clean prepared
  workspace, especially served browser smoke and Playwright diagnostics.
- Local Studio Playwright was blocked by port `8000` being occupied by a
  benchmarks server; this is an environment conflict, not a Studio test failure.
- Tools still treats DuckDB as opaque preservation coverage, not semantic
  DuckDB conversion.
- Studio, Web, and Tools local heads are ahead of their remotes; Web is also
  behind one remote commit. No remote sync was performed in this batch.
