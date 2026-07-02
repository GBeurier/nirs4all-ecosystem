# Wave 3AN - Web Runtime Result, Providers Capabilities, Tools Preview

Date: 2026-07-02

## Scope

This batch integrated three independent follow-ups:

- Lane H/Web: port only the useful `0f50c25` worker-runtime-result change from
  the old `INT-web` worktree into current `nirs4all-web`.
- Lane J/Providers: close the residual W3AL papers-provider capability risks.
- Lane D/Tools: add targeted native-results dry-run preview coverage.

No old worktree was merged wholesale. Full parity and heavy browser smoke gates
were intentionally deferred for a larger batch.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Hilbert the 2nd | `nirs4all-web` implementation | integrated | Commit `5562706` (`fix(studio-lite): preserve worker runtime result`). |
| James the 2nd | `nirs4all-web` review | GO | Confirmed the diff matches the minimal `0f50c25` port and that `worker.ts` already emitted `rtResult`. |
| Kuhn the 2nd | `nirs4all-providers` implementation | integrated | Commit `f1a8ba6` (`fix(papers): clamp provider capabilities`). |
| Nash the 2nd | `nirs4all-providers` review | GO | Confirmed `executes` is clamped to provider contract and portability fallback is restored. |
| Meitner the 2nd | `nirs4all-tools` implementation | integrated | Commit `044e22a` (`test(native-results): cover dry-run preview`). |
| Cicero the 2nd | `nirs4all-tools` review | GO | Confirmed dry-run preview coverage is scoped and does not broaden converter behavior. |

## Integrated Changes

### `nirs4all-web`

- Added `RunResult.rtResult?: RtResultWire` to the browser engine contract.
- Attached worker-emitted `rtResult` side-channel payloads to the resolved
  `RunResult` in `WorkerEngine`.
- Added focused Vitest coverage for:
  - worker facade propagation;
  - carrying the shared runtime-result envelope on Web `RunResult`.
- Did not change `worker.ts`; the current worker already emitted `rtResult`.

### `nirs4all-providers`

- Forced `PaperExportProvider.capabilities().executes` to `False` even when a
  papers facade claims execution.
- Preserved facade-provided `portability` when present.
- Restored the provider fallback portability text when a facade omits
  `portability`.
- Added regression coverage for a facade dict claiming `executes=True` and
  omitting `portability`.

### `nirs4all-tools`

- Added a dry-run native-results preview test for a lowerable source.
- The test verifies:
  - the output workspace is not created;
  - source bytes remain unchanged;
  - manifest, report, and unsupported report are coherent;
  - `native-results-v1` is present in the input inventory.
- No new converter format or binary golden fixture was introduced.

## Validation

`nirs4all-web/studio-lite`:

- `npm run typecheck` -> passed.
- `npx vitest run --config vitest.config.ts src/engine/worker-engine.test.ts src/engine/rt-result.goldens.test.ts` -> 12 passed.
- `git diff --check` -> passed in review.

`nirs4all-providers`:

- `PYTHONPATH=src python3.11 -m pytest tests/test_papers_provider.py tests/test_release_gate.py tests/test_conformance.py -q -p no:cacheprovider` -> 21 passed, 4 skipped.
- Reviewer also ran `PYTHONPATH=src pytest` -> 70 passed, 4 skipped.
- `PYTHONPATH=src python3.11 -m ruff check src tests` -> passed.
- `git diff --check` -> passed in review.

`nirs4all-tools`:

- `PYTHONPATH=src python3.11 -m pytest tests/test_commands.py::test_migrate_native_results_dry_run_reports_lowerable_preview tests/test_commands.py::test_migrate_native_results_lowers_preview_metadata tests/test_commands.py::test_migrate_native_results_multidimensional_arrays_dry_run_would_preserve tests/test_native_results.py -q -p no:cacheprovider` -> 6 passed.
- Reviewer also ran `PYTHONPATH=src pytest -q tests/test_commands.py` -> 45 passed.
- `python3.11 -m ruff check tests/test_commands.py` -> passed.
- `git diff --check` -> passed.

## Gate Policy

- No full Python-reference parity was run in this batch.
- No browser e2e/smoke suite was run; this Web change is engine-contract
  plumbing with targeted typecheck and Vitest coverage.
- No tests were reduced, xfailed, or weakened.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Risks

- `nirs4all-web`: `attachRtResult` lives in the generic worker call path, but
  current workers only send `rtResult` for `run`; tests cover the intended
  path.
- `nirs4all-providers`: the regression test covers dict-style facade
  capabilities; the implementation clamps all branches, including object and
  `Capabilities` inputs.
- `nirs4all-tools`: the new preview coverage uses existing synthetic fixtures,
  not a new real-world binary golden.
