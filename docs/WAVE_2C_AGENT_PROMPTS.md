# Wave-2C agent prompts

**Date:** 2026-07-01
**Supervisor:** Codex API session
**Base state:** Wave-2B local commits collected; integration branches created
from those commits.

Agents must not edit `PARALLEL_REFACTORING_SYNC.md`. Each agent writes one
report under `nirs4all-ecosystem/docs/agent_reports/` and may commit only in its
assigned worktree/repo when its gates pass. No agent may push.

All agents must inspect code directly before editing. CodeGraph may be used as
an accelerator, but current files and test output are authoritative.

## Integration bases

| Repo | Branch / worktree | Tip at launch |
|---|---|---|
| `nirs4all` | `_worktrees/INT-nirs4all` / `refactor/integration-nirs4all` | W1+W2+W3+W4+W7 merged |
| `dag-ml` | `_worktrees/INT-dagml` / `refactor/integration-dagml` | L20+L16+W5+W6 merged |
| `dag-ml-data` | `_worktrees/INT-dmd` / `refactor/integration-dmd` | L20+L6+W5 merged |
| `nirs4all-studio` | `_worktrees/INT-studio` / `refactor/integration-studio` | L11+L12+W8 merged |
| `nirs4all-web` | `_worktrees/INT-web` / `refactor/integration-web` | L13+W9 merged |
| `nirs4all-cluster` | `_worktrees/INT-cluster` / `refactor/integration-cluster` | L15 merged |
| `nirs4all-io` | `_worktrees/INT-io` / `refactor/integration-io` | L7 merged |
| `nirs4all-tools` | `main` | migration scaffold |
| `nirs4all-providers` | `main` | provider scaffold |

Known environment limits at launch:

- Studio and Cluster backend tests require a Python environment with `fastapi`;
  the supervisor's system `python3` does not have it.
- Web typecheck/build require a WSL-local Node/npm; the current `npm` on PATH is
  Windows npm and is not reliable from WSL UNC paths.
- Agents must report environment limits clearly instead of treating missing
  local tooling as code failure.

## W11 - B-010 branch/dup fallback lowering

**CWD:** `/home/delete/nirs4all/_worktrees/W11-nirs4all-branch`
**Base:** `refactor/integration-nirs4all`
**Report:** `docs/agent_reports/W11_BRANCH_FALLBACK.md`

Goal: reduce `EXPECTED_FALLBACK` by implementing native host-bridge lowering for
as many `branch_dup_*` cases as is correct without lying about parity.

Owned files: `nirs4all/pipeline/dagml/detect.py`,
`nirs4all/pipeline/dagml/run_paths.py`,
`nirs4all/pipeline/dagml/run_backend.py`,
`tests/integration/parity/test_conformance_dual_engine.py`, and the
`expected_fallback` / coverage-derived sections of `docs/compatibility.json`.

Do not edit runtime envelopes, `.n4a` export methods, or Studio/Web code.
If a Rust scheduler/core gap is real, document the exact missing native contract
and leave the case in fallback.

Gate: targeted parity for branch/dup cases, `test_native_fallback_boundary.py`,
`test_compatibility_ledger.py`, `py_compile`, Ruff if available.

## W12 - B-010 multi-source fallback lowering

**CWD:** `/home/delete/nirs4all/_worktrees/W12-nirs4all-multisource`
**Base:** `refactor/integration-nirs4all`
**Report:** `docs/agent_reports/W12_MULTISOURCE_FALLBACK.md`

Goal: reduce `EXPECTED_FALLBACK` by implementing native host-bridge lowering for
as many `multi_source_*` cases as is correct without changing legacy semantics.

Owned files are the same B-010 host-bridge files as W11, but this agent must
touch only multi-source code paths and ledger entries. Do not touch
`branch_dup_*`, runtime envelopes, or export code.

Gate: targeted parity for multi-source cases, native fallback boundary,
compatibility ledger, `py_compile`, Ruff if available.

## W13 - Native `.n4a` export production slice

**CWD:** `/home/delete/nirs4all`
**Worktrees:** `_worktrees/W13-nirs4all-export`,
`_worktrees/W13-dagml-export`
**Bases:** `refactor/integration-nirs4all`,
`refactor/integration-dagml`
**Report:** `docs/agent_reports/W13_NATIVE_N4A_EXPORT.md`

Goal: replace or materially advance the legacy-refit `.n4a` bridge with a true
native export path from dag-ml native run artifacts. The minimum acceptable
slice is a real production code path plus tests proving it is not just a legacy
refit under another name.

Owned areas: `nirs4all` export methods and native-results export side;
`dag-ml` native bundle/export support if needed. Coordinate with W7's
`to_rt_result()` method by avoiding unrelated `api/result.py` edits.

Gate: export round-trip parity tests, native bundle tests, Rust fmt/test for any
dag-ml edits, `py_compile`, Ruff if available. Report any schema/interface
change explicitly.

## W14 - Studio-bypass parity and engine-record gates

**CWD:** `/home/delete/nirs4all/_worktrees/W14-studio-parity`
**Base:** `refactor/integration-studio`
**Report:** `docs/agent_reports/W14_STUDIO_BYPASS_PARITY.md`

Goal: close the Studio half of B-011 by adding tests and any narrow fixes needed
to prove Studio routes pass the requested `engine`, persist actual engine and
fallback diagnostics, and do not silently bypass the runtime route.

Owned areas: Studio backend route tests and narrow `api/runs.py` /
`api/runtime_engine.py` fixes required by those tests. Do not do deep compute
push-down here.

Gate: targeted backend tests via the repo runner when environment exists; at
minimum `python -m compileall` for touched files and a clear explanation of
missing FastAPI environment if tests cannot run.

## W15 - Studio compute push-down first slice

**CWD:** `/home/delete/nirs4all/_worktrees/W15-studio-compute`
**Base:** `refactor/integration-studio`
**Report:** `docs/agent_reports/W15_STUDIO_COMPUTE_PUSHDOWN.md`

Goal: start B-017 deep compute push-down with a small production slice that
removes duplicated Studio metric/math behavior in favor of library/runtime
helpers. Prefer prediction metric and result-analysis seams over broad UI work.

Owned areas: `api/predict.py`, `api/metrics_computer.py`, focused tests. Avoid
`api/runs.py` engine-record behavior owned by W14.

Gate: targeted backend tests if environment exists; compileall/Ruff otherwise.
Document exactly which trapped compute remains.

## W16 - Web served smoke and RtError diagnostics

**CWD:** `/home/delete/nirs4all/_worktrees/W16-web-rt-smoke`
**Base:** `refactor/integration-web`
**Report:** `docs/agent_reports/W16_WEB_RT_SMOKE.md`

Goal: finish the Web B-018 follow-up by making the served/browser smoke
reliable from WSL and adding forced-failure coverage for `RtError` diagnostics
without relying on silent fallback.

Owned areas: `studio-lite/src/engine/*`, `studio-lite/tests/*`, npm scripts only
if required for WSL-local execution. Do not broaden product UI.

Gate: unit tests/typecheck/build/browser smoke when Node/npm are available;
otherwise document missing WSL Node and keep code testable.

## W17 - DatasetPackage v2 first implementation

**CWD:** `/home/delete/nirs4all/_worktrees/W17-io-dataset-package`
**Base:** `refactor/integration-io`
**Report:** `docs/agent_reports/W17_DATASET_PACKAGE.md`

Goal: implement the first concrete `DatasetPackage` / `AssembledDataset v2`
contract in `nirs4all-io`, extending the existing io->dag-ml-data bridge rather
than replacing it.

Owned areas: nirs4all-io package models, manifest/serialization code, focused
tests. Respect `LOCK-IO`: typed payload blocks, payload manifest, content hashes,
explicit row-position fallback diagnostics.

Gate: Rust fmt/test or Python tests according to the touched crate/package,
plus existing cross-CLI conformance if feasible.

## W18 - Provider adapters phase 2

**CWD:** `/home/delete/nirs4all/_worktrees/W18-providers`
**Base:** `nirs4all-providers/main`
**Report:** `docs/agent_reports/W18_PROVIDERS_PHASE2.md`

Goal: extend `nirs4all-providers` beyond the scaffold with the next read-only
adapters and health/conformance tests grounded in the real datasets,
repository, benchmarks, and papers APIs. No ecosystem write path.

Owned areas: `nirs4all-providers` only. `to_dataset_package` is allowed only as
a soft/optional adapter if it consumes W17's public contract without duplicating
IO assembly.

Gate: `ruff`, `mypy`, `pytest` if available.

## W19 - Cluster client/adapter slice

**CWD:** `/home/delete/nirs4all/_worktrees/W19-cluster-client`
**Base:** `refactor/integration-cluster`
**Report:** `docs/agent_reports/W19_CLUSTER_CLIENT.md`

Goal: add the first concrete client/adapter layer after RBAC: a typed Python
client for server registration/job submit/status/cancel that respects rights
and can later be consumed by core/Studio/CLI.

Owned areas: `nirs4all_cluster/client*`, CLI/client tests, docs. Do not redesign
server RBAC.

Gate: targeted tests if FastAPI/httpx environment exists; compileall/Ruff
otherwise, with environment limits reported.

## W20 - lite -> nirs4all-core aggregate / `n4a` facade

**CWD:** `/home/delete/nirs4all/_worktrees/W20-lite-core`
**Base:** `nirs4all-lite/main`
**Report:** `docs/agent_reports/W20_LITE_CORE.md`

Goal: implement the first safe slice of `LOCK-GOV`: rename/prepare the aggregate
distribution from lite toward `nirs4all-core`, and add an additive `n4a.*`
facade where technically simple without breaking existing imports.

Owned areas: `nirs4all-lite` packaging/import facade/tests/docs. Do not remove
legacy public names in this slice.

Gate: package import tests, build metadata check, any existing test suite.
