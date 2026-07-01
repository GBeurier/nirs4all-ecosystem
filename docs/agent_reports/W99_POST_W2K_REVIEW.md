# W99 Post-W2K Review

Date: 2026-07-01
Owner: W99
Scope: read-only review across current Wave 2K reports and integration heads.

W99 made no code changes outside this report. No test suites were run by W99; this
is a direct code and git inspection review.

## Report Availability

Reports present during review:

- W90: `docs/agent_reports/W90_CUTOVER_STATE_GATE.md`
- W91: `docs/agent_reports/W91_DAGML_LOCKSTEP_FRESHNESS.md`
- W92: `docs/agent_reports/W92_METHODS_RELEASE_SURFACE.md`
- W93: `docs/agent_reports/W93_IO_DATASETS_REFERENCE_BRIDGE.md`
- W94: `docs/agent_reports/W94_LITE_RELEASE_TOPOLOGY.md`
- W97: `docs/agent_reports/W97_TOOLS_REAL_GOLDENS.md`

Reports absent during review:

- W95: no report was present. The W95 Studio worktree had uncommitted changes.
- W96: no report was present. The W96 Studio and Web worktrees had uncommitted changes.
- W98: no report was present. The W98 core parity worktree was clean and matched
  `refactor/integration-nirs4all`, but did not publish a report.

W97 appeared while W99 was already reviewing W90-W94. It was fact-checked after it
appeared.

## Integration Heads Observed

| Area | Integration or target head observed | W2K worker head observed | State |
| --- | --- | --- | --- |
| `nirs4all` | `refactor/integration-nirs4all` at `f970bf0e` | W98 worktree also `f970bf0e` | no W98 report |
| `nirs4all-studio` | `refactor/integration-studio` at `1979b72` | W95/W96 worktrees also `1979b72` plus dirty edits | not integrated |
| `nirs4all-web` | `refactor/integration-web` at `60a0967` | W96 worktree also `60a0967` plus dirty edits | not integrated |
| `dag-ml` | `refactor/integration-dagml` at `618ffb2` | W91 worktree `618ffb2` | integrated |
| `dag-ml-data` | `refactor/integration-dmd` at `818616e` | W91 worktree `818616e` | integrated |
| `nirs4all-methods` | `main` at `7602eb08` | W92 branch `d077ea5f` | not merged |
| `nirs4all-io` | `refactor/integration-io` at `ccfea29` | W93 branch `ac7809d` | not merged |
| `nirs4all-datasets` | `main` at `ae414964` | W93 branch `20b41824` | not merged |
| `nirs4all-lite` | `refactor/integration-lite` at `0dad1c6` | W94 branch `d9d92d7` | not merged |
| `nirs4all-tools` | `main` at `44ce7a3` | W97 branch `c10934a` | not merged |

## Ranked Blockers For V1 Completion

### 1. Studio strict runtime cutover is not landed

Current Studio integration still defaults public run paths to fallback-enabled
behavior, while the W95 fixes exist only as uncommitted worktree edits.

Evidence:

- `_worktrees/INT-studio/api/runs.py:206` has `Run.allow_fallback: bool = True`.
- `_worktrees/INT-studio/api/runs.py:237` has `ExperimentConfig.allow_fallback`
  defaulting to `Field(True, ...)`.
- `_worktrees/INT-studio/api/runs.py:258` has `QuickRunRequest.allow_fallback`
  defaulting to `Field(True, ...)`.
- `_worktrees/INT-studio/api/runs.py:1294` still declares
  `_execute_pipeline_training(..., allow_fallback: bool = True, ...)`.
- `_worktrees/W95-studio-strict-runtime/api/runs.py:206`,
  `_worktrees/W95-studio-strict-runtime/api/runs.py:237`,
  `_worktrees/W95-studio-strict-runtime/api/runs.py:258`, and
  `_worktrees/W95-studio-strict-runtime/api/runs.py:1294` show the intended
  `False` defaults, but `git status --short` in that worktree showed those files
  as modified and no W95 report existed.
- `docs/contracts/cutover/readiness-matrix.n4a.json:116` through
  `docs/contracts/cutover/readiness-matrix.n4a.json:132` mark the Studio route
  blocker ready, which does not match the current Studio integration head.

Exact next actions:

1. Finish W95, commit the Studio strict-runtime changes, and publish the W95 report.
2. Merge the W95 commit into `refactor/integration-studio`.
3. Rerun the `studio_runtime_routes` cutover gate against the updated Studio head.
4. Update the readiness matrix only after the gate passes on the merged head.

### 2. Runtime diagnostics and web error UX coverage are not landed

W96 did not publish a report. Its Studio and Web worktrees contain uncommitted test
and UI edits, while integration heads still lack the reviewed runtime diagnostics
coverage.

Evidence:

- `_worktrees/INT-studio/e2e/tests/runs-redesign.spec.ts:39` through
  `_worktrees/INT-studio/e2e/tests/runs-redesign.spec.ts:140` define the run
  redesign mock without `engine`, `engine_requested`, or `engine_diagnostics`
  fields.
- `_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:49` through
  `_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:58` add those
  runtime fields.
- `_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:417` through
  `_worktrees/W96-studio-runtime-e2e/e2e/tests/runs-redesign.spec.ts:434` add
  Playwright coverage for legacy fallback, runtime diagnostics, unsupported shape,
  message, and mitigation rendering.
- `_worktrees/INT-web/studio-lite/src/app/App.tsx:551` renders raw error text as
  `<span>{error}</span>`.
- `_worktrees/W96-web-runtime-e2e/studio-lite/src/app/runtimeErrors.ts:1` through
  `_worktrees/W96-web-runtime-e2e/studio-lite/src/app/runtimeErrors.ts:23` add
  structured RtError formatting, but that file is untracked in the W96 worktree.
- `docs/contracts/cutover/readiness-matrix.n4a.json:135` through
  `docs/contracts/cutover/readiness-matrix.n4a.json:151` mark the Web runtime
  blocker ready, which is premature until W96 is committed, reported, and merged.

Exact next actions:

1. Finish W96, commit the Studio and Web runtime diagnostics changes, and publish
   the W96 report.
2. Merge W96 into `refactor/integration-studio` and `refactor/integration-web`.
3. Rerun the Studio e2e runtime diagnostics coverage and the Web runtime error
   tests on the merged heads.
4. Update the cutover readiness matrix only after those merged-head checks pass.

### 3. Final full parity proof is missing

W98 has no report, and the compatibility ledger still records stale reconciliation
metadata. This blocks V1 because the strict post-cutover full parity gate must run
on the final selected heads, not on an intermediate or undocumented state.

Evidence:

- No `docs/agent_reports/*W98*` report was present.
- `docs/contracts/cutover/drop-gates.n4a.json:70` through
  `docs/contracts/cutover/drop-gates.n4a.json:84` require the full
  `pyref_oracle_full` parity gate.
- `_worktrees/W98-nirs4all-full-parity/tests/integration/parity/test_conformance_dual_engine.py:396`
  through
  `_worktrees/W98-nirs4all-full-parity/tests/integration/parity/test_conformance_dual_engine.py:452`
  contain the full dual-engine conformance test, but W99 found no W98 execution
  report.
- `_worktrees/W98-nirs4all-full-parity/tests/integration/parity/test_conformance_dual_engine.py:362`
  through
  `_worktrees/W98-nirs4all-full-parity/tests/integration/parity/test_conformance_dual_engine.py:394`
  contain the never-xfailed native fallback boundary coverage.
- `_worktrees/INT-nirs4all/docs/compatibility.json:5` through
  `_worktrees/INT-nirs4all/docs/compatibility.json:8` still record
  `last_reconciled` as `2026-06-30`, `nirs4all_commit` `e41362b4`, and
  `dag_ml_commit` `f58d7bf`, which do not match the observed integration heads
  `f970bf0e` and `618ffb2`.
- `_worktrees/INT-nirs4all/docs/compatibility.json:228` has
  `"expected_fallback": []`, so any final proof must preserve zero expected
  fallback.

Exact next actions:

1. After W95, W96, W92-W94, and W97 are merged to their target heads, rerun the
   required full parity and native export gates on the final selected heads.
2. Publish W98 with exact commands, final commit SHAs, and results.
3. Update `docs/compatibility.json` reconciliation metadata only as part of the
   verified final-head parity update.

### 4. W92 release-surface fixes are complete but not on the methods target head

The W92 report matches the branch content, but `nirs4all-methods` `main` still
contains stale packaging and README release-surface text.

Evidence:

- `nirs4all-methods/bindings/python/pyproject.toml:11` through
  `nirs4all-methods/bindings/python/pyproject.toml:13` still describe the package
  as `pls4all`.
- `nirs4all-methods/bindings/python/pyproject.toml:38` through
  `nirs4all-methods/bindings/python/pyproject.toml:42` still point URLs at
  `https://github.com/GBeurier/pls4all`.
- `nirs4all-methods/README.md:60` through `nirs4all-methods/README.md:64` still
  document `from n4m.sklearn import PLSRegression`.
- `_worktrees/W92-methods-release-surface/bindings/python/pyproject.toml:11`
  through
  `_worktrees/W92-methods-release-surface/bindings/python/pyproject.toml:13` show
  the corrected nirs4all-methods description.
- `_worktrees/W92-methods-release-surface/bindings/python/tests/test_release_surface_metadata.py:24`
  through
  `_worktrees/W92-methods-release-surface/bindings/python/tests/test_release_surface_metadata.py:56`
  add regression coverage for distribution naming, repository URLs, and public
  import-surface wording.

Exact next actions:

1. Merge W92 commit `d077ea5f` into the `nirs4all-methods` release target.
2. Rerun the W92 metadata tests and any methods release gate used for V1.
3. Recheck generated release artifacts for stale `pls4all` package identity or
   flat `n4m.sklearn` guidance before tagging.

### 5. W93 IO/datasets bridge is complete but not merged

W93's direct code changes match the report, but the IO integration and datasets
target heads still lack the bridge APIs required for the reference dataset flow.

Evidence:

- `_worktrees/W93-io-datasets-bridge/src/nirs4all_io/api.py:34` through
  `_worktrees/W93-io-datasets-bridge/src/nirs4all_io/api.py:49` adapt objects
  exposing `to_io_spec()`.
- `_worktrees/W93-io-datasets-bridge/src/nirs4all_io/api.py:95` through
  `_worktrees/W93-io-datasets-bridge/src/nirs4all_io/api.py:118` implement the
  duck-typed bridge adapter.
- `refactor/integration-io` was still at `ccfea29`; W93 branch `ac7809d` was one
  commit ahead.
- `_worktrees/W93-datasets-reference-bridge/src/nirs4all_datasets/dataset.py:318`
  through
  `_worktrees/W93-datasets-reference-bridge/src/nirs4all_datasets/dataset.py:365`
  implement `Dataset.to_io_spec()`.
- `_worktrees/W93-datasets-reference-bridge/src/nirs4all_datasets/dataset.py:367`
  through
  `_worktrees/W93-datasets-reference-bridge/src/nirs4all_datasets/dataset.py:378`
  implement `Dataset.to_dataset_package()`.
- `nirs4all-datasets` `main` was still at `ae414964`; W93 branch `20b41824` was
  one commit ahead.

Exact next actions:

1. Merge W93 IO commit `ac7809d` into `refactor/integration-io`.
2. Merge W93 datasets commit `20b41824` into the datasets target branch.
3. Rerun the W93 reference bridge tests and any downstream dataset assembly smoke
   tests that consume `to_io_spec()`.

### 6. W94 lite release topology is complete but not merged

The W94 branch adds the expected aggregate topology manifest, but
`refactor/integration-lite` still has only a sparse topology contract.

Evidence:

- `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:46`
  through
  `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:101`
  define namespace facades.
- `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:103`
  through
  `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:241`
  define install distributions.
- `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:243`
  through
  `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:386`
  define upstream component boundaries.
- `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:388`
  through
  `_worktrees/W94-lite-release-topology/bindings/python/src/nirs4all_lite/_topology.py:424`
  define release pointers.
- `_worktrees/INT-lite/bindings/python/src/nirs4all_lite/_topology.py:44`
  through
  `_worktrees/INT-lite/bindings/python/src/nirs4all_lite/_topology.py:120`
  still show the sparse current integration manifest.

Exact next actions:

1. Merge W94 commit `d9d92d7` into `refactor/integration-lite`.
2. Rerun the lite topology tests and release metadata checks on the merged head.
3. Use the merged topology manifest as the source for final release lock validation.

### 7. W97 real-golden fixture coverage is complete but not on the tools target head

W97 was clean and its report matched the branch, but the cutover gate still points
at `nirs4all-tools` `main`, which does not include W97.

Evidence:

- `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:46`
  through
  `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:80`
  test unsupported dry-run reporting without output.
- `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:83`
  through
  `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:120`
  test payload preservation and checksum verification.
- `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:123`
  through
  `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:147`
  test resume opt-in behavior.
- `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:150`
  through
  `_worktrees/W97-tools-real-goldens/tests/test_real_golden_fixtures.py:205`
  test SQLite legacy array migration behavior.
- `docs/contracts/cutover/drop-gates.n4a.json:169` through
  `docs/contracts/cutover/drop-gates.n4a.json:183` define the migration tool
  smoke gate against `nirs4all-tools`, whose observed `main` was still `44ce7a3`.

Exact next actions:

1. Merge W97 commit `c10934a` into the `nirs4all-tools` target used by the
   cutover gate.
2. Rerun the migration tool smoke gate from `drop-gates.n4a.json` on that target.
3. Record the merged tools head in the final V1 release evidence.

### 8. Cutover docs are ahead of merged reality

Several central cutover documents assert or imply readiness before the reviewed
heads contain the relevant changes. This is a release-process blocker because V1
evidence must be reproducible from documented heads.

Evidence:

- `docs/contracts/cutover/readiness-matrix.n4a.json:116` through
  `docs/contracts/cutover/readiness-matrix.n4a.json:132` mark Studio runtime routes
  ready even though current Studio integration still defaults fallback to true.
- `docs/contracts/cutover/readiness-matrix.n4a.json:135` through
  `docs/contracts/cutover/readiness-matrix.n4a.json:151` mark Web runtime ready
  even though W96 was uncommitted and unreported.
- `docs/contracts/cutover/readiness-matrix.n4a.json:173` through
  `docs/contracts/cutover/readiness-matrix.n4a.json:188` require release lock
  validation to rerun after selecting final heads.
- `docs/contracts/cutover/drop-gates.n4a.json:6` through
  `docs/contracts/cutover/drop-gates.n4a.json:10` require clean worktrees and all
  required gates to pass before release.
- `_worktrees/INT-nirs4all/docs/compatibility.json:302` through
  `_worktrees/INT-nirs4all/docs/compatibility.json:343` still list cross-engine
  surface gaps or partial surfaces, including `studio_oracle` and
  `methods_installed`.

Exact next actions:

1. Treat the readiness matrix as provisional until W95/W96/W98 reports and all
   W92-W94/W97 merges are complete.
2. Update readiness, compatibility, and release-lock documents only with final
   merged-head SHAs and rerun evidence.
3. Reject V1 signoff if the documented head SHAs do not match the heads used for
   gate execution.

### 9. Dirty and overlapping worktrees make current gate results non-final

Several W2K worktrees were dirty or shared the same base head as their integration
branch. That means any local successful checks from those worktrees cannot be
treated as final V1 evidence until committed and rerun from target heads.

Evidence:

- `_worktrees/W95-studio-strict-runtime` had modified
  `api/execution_driver.py`, `api/runs.py`, and three tests.
- `_worktrees/W96-studio-runtime-e2e` had modified e2e, runtime component, and
  result metadata files.
- `_worktrees/W96-web-runtime-e2e` had modified `studio-lite/src/app/App.tsx` and
  untracked `runtimeErrors.ts` plus `runtimeErrors.test.ts`.
- The top-level `nirs4all` checkout had unrelated dirty edits in
  `docs/compatibility.json`, DAG-ML detection/runtime files, and parity tests.
- The top-level `dag-ml-data` checkout had a dirty generated shared-object file.

Exact next actions:

1. Do not use dirty worktree test results as final V1 evidence.
2. Commit or deliberately discard worker-local changes only in the owning worker
   flow; W99 did not revert or edit them.
3. Run final V1 gates from clean target worktrees after all worker branches have
   been merged.

## Non-Blocking Fact Checks

W90 core cutover claims matched direct code inspection:

- `_worktrees/INT-nirs4all/nirs4all/pipeline/engine.py:24` sets
  `DEFAULT_ENGINE: Engine = "dag-ml"`.
- `_worktrees/INT-nirs4all/nirs4all/api/run.py:212` defaults
  `allow_fallback` to `False`.
- `_worktrees/INT-nirs4all/nirs4all/api/run.py:591` raises on DAG-ML errors unless
  explicit fallback is allowed.
- `_worktrees/INT-nirs4all/nirs4all/api/result.py:1421` through
  `_worktrees/INT-nirs4all/nirs4all/api/result.py:1427` document explicit
  `legacy-refit` compatibility for exports.
- `_worktrees/INT-nirs4all/nirs4all/api/result.py:1448` through
  `_worktrees/INT-nirs4all/nirs4all/api/result.py:1478` only delegates DAG-ML
  export to legacy refit when compatibility is explicit.

W91 lockstep claims matched direct code and git inspection:

- `_worktrees/W91-dagml-lockstep/scripts/validate_contracts.py:24` through
  `_worktrees/W91-dagml-lockstep/scripts/validate_contracts.py:41` enumerate the
  shared contract files.
- `_worktrees/W91-dagml-data-lockstep/scripts/validate_contracts.py:23` through
  `_worktrees/W91-dagml-data-lockstep/scripts/validate_contracts.py:30` enumerate
  the sibling DMD contract files.
- Observed integration heads were `dag-ml` `618ffb2` and `dag-ml-data` `818616e`,
  matching the W91 report state.

## Bottom Line

V1 is not ready for final refactor completion signoff. The strict core cutover is
present in `nirs4all`, and W91 plus W92-W94 and W97 appear technically coherent in
their respective branches. The blocking gap is release integration and proof:
W95, W96, and W98 did not publish final reports; W95/W96 had dirty uncommitted
work; W92-W94/W97 were not merged into the heads used by release gates; and central
cutover docs currently overstate readiness relative to those heads.
