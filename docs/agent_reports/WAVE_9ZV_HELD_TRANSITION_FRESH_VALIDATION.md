# Wave 9ZV - Held Transition Fresh Validation

Date: 2026-07-11

## Scope

Fresh validation batch for the two production-held transition projects:

- `nirs4all` Python transition branch `refactor/L17-pyref`
- `nirs4all-studio` `main`

This batch does not switch production for either held project. It records focused
evidence for the transition requirements: backend selection, legacy workspace
conversion guidance, Studio conversion UX/API, and published methods bindings.

## Evidence

### `nirs4all`

Branch: `refactor/L17-pyref`

Head: `f6c201153b3921c0f214cd63a992beb29e10b7bc`

Fresh local gates:

```text
python3.11 -m pytest -q \
  tests/unit/workspace/test_workspace_compat.py \
  tests/unit/cli/test_main.py \
  tests/unit/api/test_engine_transition.py

45 passed
```

This covers:

- legacy workspace detection and conversion command guidance,
- `nirs4all workspace convert` CLI delegation to `nirs4all-tools`,
- transition extra dependency declaration for `nirs4all-tools[duckdb,parquet]`,
- explicit and env-driven `legacy` / `dag-ml` engine selection behavior.

Published methods binding gate:

```text
.venv/bin/python -m pip install --upgrade 'nirs4all-methods==1.0.9'
NIRS4ALL_REQUIRE_N4M=1 .venv/bin/python -m pytest -q -m methods \
  tests/unit/operators/methods/test_n4m_ops.py

11 passed, 2 warnings
```

This verifies the published `nirs4all-methods` / `n4m` binding is loadable from
the Python transition branch and that the opt-in methods operators pass the
strict local methods parity gate, including the dual-engine test legs.

Current remote full gate selected for the Python transition line remains:

- GitHub Actions `Pre-Publish Check`, run `29143740229`, success
- Branch `refactor/L17-pyref`
- Head `f6c201153b3921c0f214cd63a992beb29e10b7bc`

### `nirs4all-studio`

Branch: `main`

Head: `8654e4d24c22553717e08d6f646f423c02bf4667`

Fresh backend/API gates:

```text
./.venv/bin/python -m pytest -q \
  tests/test_runtime_engine.py \
  tests/test_workspace_transition.py \
  tests/test_runs_engine_routing.py

46 passed, 7 warnings
```

Fresh frontend gates:

```text
PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH npm run test:frontend -- --run \
  src/lib/runtimeBackendPreference.test.ts \
  src/components/runtime/RuntimeComponents.test.tsx \
  src/components/layout/__tests__/LegacyWorkspaceBanner.test.tsx \
  src/components/settings/__tests__/WorkspaceStats.test.tsx \
  src/lib/__tests__/pipelineExecutionContract.test.ts \
  src/lib/__tests__/experimentLaunchPayload.test.ts

26 passed across 6 test files
```

The first attempt used the Windows `npm` from PATH and failed before running
tests because CMD cannot use the WSL UNC path. The successful run above pins the
WSL Node toolchain explicitly.

These focused Studio gates cover:

- runtime backend preference persistence and payload threading,
- `legacy` / `dag-ml` routing metadata and fallback diagnostics,
- legacy workspace warning banner,
- conversion action from settings,
- backend API transition status and conversion behavior.

Current remote Studio gates remain:

- GitHub Actions `CI`, run `29145358143`, success on `8654e4d`
- GitHub Actions `Playwright E2E Tests`, run `29145358171`, success on `8654e4d`
- GitHub Actions `Release`, run `29145157945`, success on `b7f4105`, artifact-only RC4 installer build

## Review / Parallel Audit

Two read-only Claude Code audits were launched with explicit read-only intent:

- `1ff5e624-84e8-4d7f-8b05-96c15900f47f`: release/cockpit readiness audit
- `7202fdea-fd94-4f37-be1c-b8edb784404b`: Python/Studio transition audit

Both were still running when this report was drafted. Their final findings
should be reviewed before any production switch decision, but they are not a
blocker for recording the fresh focused validation above.

## Risks / Remaining Manual Gates

- `nirs4all` Python and `nirs4all-studio` remain production-held.
- Native Windows Studio RC4 smoke remains manual and required before a Studio
  production transition switch.
- CRAN manual submissions remain pending and outside this batch.
- Full Python pre-publish is already green on the selected Python transition
  head; do not rerun long full parity gates for documentation-only refreshes
  unless the selected release head changes.

## Decisions

- Keep the held-project readiness evidence as selected-head evidence, not a
  self-updating "latest run id" loop. A docs-only evidence refresh must not force
  an infinite lock/update/revalidate cycle.
- Use WSL Node explicitly for local Studio frontend tests when Windows Node is
  earlier on PATH.
