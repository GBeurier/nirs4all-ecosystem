# Agent run supervision

**Date:** 2026-06-30
**Supervisor:** Codex in current API session
**Scope:** first-wave 10 agents from `MANUAL_AGENT_LAUNCH.md`

## Current process state

Detected active agent-like processes:

| PID | Tool | State | CWD | TTY | Action |
|---:|---|---|---|---|---|
| `208304` | `claude --dangerously-skip-permissions` | running/interactive | `/home/delete/nirs4all` | `/dev/pts/10` | leave running |
| `208423` | `claude --dangerously-skip-permissions` | running/interactive | `/home/delete/nirs4all` | `/dev/pts/7` | leave running |

The current Codex API session also appears as a `codex ... resume` process and
must not be treated as a managed child agent.

Follow-up inspection:

- `pstree -ap 208304` shows one Claude top-level session with a CodeGraph MCP
  child (`codegraph.js serve --mcp`) plus Claude threads.
- `pstree -ap 208423` shows the same shape: one Claude top-level session with a
  CodeGraph MCP child plus Claude threads.
- No extra top-level `claude` child processes were found under those two
  sessions; no active `pytest`, `cargo`, `npm`, or build child was attached
  during the latest inspection.
- If those Claude sessions spawned internal `Task` subagents, they are internal
  to the Claude process and are not exposed as separate OS-level processes.
- The many `claude-code-mcp`, `sentry-mcp`, `node`, and `npm exec` processes in
  `ps` are MCP servers attached to Codex/Claude tooling or old app-server
  sessions. They are not first-wave refactoring agents and were left untouched.

Fresh audit 2026-07-01:

- `208304` and `208423` are still the two relevant external interactive Claude
  CLI sessions at the workspace root.
- Each has a CodeGraph MCP child and Claude threads. No separate OS-level
  `pytest`, `cargo`, `npm`, Vite preview, `codex exec`, or `claude -p` worker was
  attached at inspection time.
- If these Claude sessions created Claude `Task` subagents, they remain internal
  to the Claude process and are not distinguishable as independent Unix
  processes. They are therefore tracked as external interactive sessions, not as
  managed Wave-2B agents.
- Multiple `claude-code-mcp` server processes are still alive. They are tooling
  servers, not lane agents, and were also left untouched.

## First-wave reports found

All expected first-wave reports exist and are non-empty:

| Agent | Expected role | Report |
|---|---|---|
| `A1` | preflight/evidence | `docs/agent_reports/A1_A1-preflight.md` |
| `A2` | PYREF/oracle | `docs/agent_reports/A2_A2-pyref.md` |
| `A3` | dag-ml runtime/native coverage | `docs/agent_reports/A3_A3-dagml.md` |
| `A4` | controllers/bindings | `docs/agent_reports/A4_A4-controllers.md` |
| `A5` | methods/n4m | `docs/agent_reports/A5_A5-methods.md` |
| `A6` | Studio/UI extraction | `docs/agent_reports/A6_A6-studio-ui.md` |
| `A8` | migration/tools | `docs/agent_reports/A8_A8-migration.md` |
| `A9` | dag-ml/dag-ml-data lockstep | `docs/agent_reports/A9_A9-lockstep.md` |
| `A13` | core/release topology | `docs/agent_reports/A13_A13-core-release.md` |
| `A0 digest` | integration digest | `docs/agent_reports/INTEGRATION_DIGEST_A0.md` |

Additional report present:

| Report | Meaning |
|---|---|
| `docs/agent_reports/CAP_spec.md` | capability/portability vocabulary report |
| `docs/agent_reports/RT_spec.md` | runtime API/report contract report |
| `docs/agent_reports/IO_spec.md` | IO/DMD/report contract report landed by external A0 |
| `docs/agent_reports/UI_spec.md` | UI/report contract report produced by external A0 lane |

## Decision

No replacement first-wave agents were launched. Launching duplicates would
create report conflicts and could overwrite the already completed first-wave
evidence.

The next useful work is not "launch more of the same"; it is integration:

1. Reconcile `INTEGRATION_DIGEST_A0.md` with the now-present `A6`, `CAP_spec.md`,
   and `RT_spec.md` reports.
2. Update `PARALLEL_REFACTORING_SYNC.md` from the first-wave reports.
3. Keep the two external Claude sessions running unless the maintainer asks to
   stop them.
4. Launch second-wave agents only after the sync board has absorbed this batch.

## Managed second-wave sessions

Launched by the Codex supervisor through Claude Code MCP after first-wave
deduplication. These are report-only tasks and must not edit the sync board or
code.

| Agent | Session ID | Status at launch | Report file |
|---|---|---|---|
| `SW1` IO/DMD audit | `ebf3b6c3-3875-420e-b7c6-474d11358168` | redirected running | `docs/agent_reports/SW1_IO_DMD_spec.md` |
| `SW2` GOV/core naming audit | `8de39b06-7786-4df0-86d1-dbdb5a123661` | redirected running | `docs/agent_reports/SW2_GOV_CORE_NAMING_spec.md` |
| `SW3` REL manifest/lockfile | `fe097f66-027f-4c9a-93c7-987436b5decb` | idle/complete | `docs/agent_reports/SW3_REL_MANIFEST_LOCKFILE_spec.md` |
| `SW4` MIG converter | `fd0ee2f9-ee7e-4c52-b418-bd8302ea83a8` | idle/complete | `docs/agent_reports/SW4_MIG_CONVERTER_spec.md` |
| `SW5` PYREF ledger | `510099fd-e335-4aa8-a9e0-05385e4913fc` | idle/complete | `docs/agent_reports/SW5_PYREF_COMPATIBILITY_LEDGER_spec.md` |
| `SW6` providers/plugins | `4713b0a5-0ef5-4fd5-9fec-16480ddcf373` | idle/complete | `docs/agent_reports/SW6_PROV_PLUGINS_spec.md` |
| `SW7` cluster | `1af49b03-2686-4780-93f0-7ed43f1bc8d8` | idle/complete | `docs/agent_reports/SW7_CLUSTER_DISTRIBUTED_spec.md` |
| `SW8` runtime/Studio implementation | `28ff2689-759a-4bbb-b7c1-29072cb20b18` | idle/complete | `docs/agent_reports/SW8_RT_STUDIO_IMPL_spec.md` |

Launch policy:

- Two external Claude sessions (`208304`, `208423`) were already active and
  were left untouched. With `SW1..SW8`, this makes ten active top-level agent
  streams under supervision/observation.
- External A0 landed `LOCK-GOV` and `LOCK-IO` while `SW1`/`SW2` were starting.
  Those two managed sessions were interrupted and redirected into validation
  audits instead of duplicate source-of-truth specs.
- All managed sessions use Claude Opus (`claude-opus-4-8` as resolved by MCP)
  with `effort=max`, `maxTurns=30`, and `allowedTools=[Bash, Read, Write, Edit,
  Glob, Grep, Task]`.
- Each managed session has a unique report file. If a report already exists,
  inspect before overwriting; do not write outside the assigned report path.

Final managed-session state:

- All `SW1..SW8` sessions reached `idle` with no pending permissions.
- Reports `SW1..SW8` exist and were integrated into
  `PARALLEL_REFACTORING_SYNC.md`.
- The eight idle MCP sessions were cleaned from the supervisor's in-memory
  session registry after integration; report files remain on disk.
- External Claude processes `208304` and `208423` were still left untouched.

Follow-up state:

- `nirs4all` is on branch `refactor/L17-pyref`.
- The external L17 agent completed the full PYREF run green
  (`556 passed, 14 skipped, 197 deselected, 11 xfailed`, exit 0) and created
  `docs/compatibility.md` plus the `pyproject.toml` dev-extra fix.
- Codex then closed the non-overlapping `B-009` machine-readable authority
  slice by adding `docs/compatibility.json`,
  `tests/integration/parity/_authority.py`, and
  `tests/integration/parity/test_compatibility_ledger.py`.
- The two external Claude CLI processes remain open and were not killed or
  controlled by the supervisor; they should not be counted as missing managed
  sessions, only as external interactive sessions to avoid duplicating.
- `nirs4all-ecosystem` L3/REL implementation has been added by Codex:
  `scripts/n4a_release_lock.py`,
  `docs/contracts/release/aggregation-manifest.n4a.json`, and
  `docs/contracts/release/aggregation-lock.n4a.lock.json`.

## Managed implementation wave

Started after the maintainer asked Codex to inspect the failed manual windows
and manage the remaining agents directly. The two external Claude CLI sessions
above are still treated as external/interactive and were not killed.

| Lane | Session ID | Worktree / cwd | Latest observed state | Report |
|---|---|---|---|---|
| `L14` providers/plugins impl map | `38f8706a-a3e8-4af8-8d44-3d9a96cdcc10` | `/home/delete/nirs4all` | idle/complete | `docs/agent_reports/IMP_L14_PROVIDERS_IMPL_PLAN.md` |
| `L15` cluster RBAC | `ea835ccc-8b66-4db7-8663-f5b128320c71` | `_worktrees/L15-cluster-rbac` | idle/complete | `docs/agent_reports/IMP_L15_CLUSTER_RBAC.md` |
| `L16` controller manifests | `2c44fbb8-b73f-4a88-8fd9-2e4d63bc11ac` | `_worktrees/L16-dagml-controllers` | idle/complete | `docs/agent_reports/IMP_L16_CONTROLLER_MANIFESTS.md` |
| `L11` Studio UI view-models | `76f63623-8548-497d-ade1-c02f34564e59` | `_worktrees/L11-studio-ui` | idle/complete | `docs/agent_reports/IMP_L11_STUDIO_UI_VM.md` |
| `L12` Studio runtime routes | `60d77be6-b36b-4fb2-91b4-98cddbaea7ae` | `_worktrees/L12-studio-runtime` | idle/complete | `docs/agent_reports/IMP_L12_STUDIO_RUNTIME.md` |
| `L13` Web runtime errors/fallback | `79dece39-c813-4972-b006-127f859cfe66` | `_worktrees/L13-web-rt` | idle/complete | `docs/agent_reports/IMP_L13_WEB_RT.md` |
| `L6` DMD registry | `959121b9-b048-4aa8-ab4b-6dcd54735785` | `_worktrees/L6-dmd-registry` | idle/complete | `docs/agent_reports/IMP_L6_DMD_REGISTRY.md` |
| `L18` tools/migration scaffold | `02aa2b96-9613-4594-ad5b-8b8e6b17abec` | `/home/delete/nirs4all` | maxTurns, completed by supervisor | `docs/agent_reports/IMP_L18_TOOLS_SCAFFOLD.md` |

Latest process check:

- External Claude CLI processes `208304` and `208423` remain running at the
  workspace root. Their process trees show CodeGraph MCP children but no
  separate top-level `pytest`/`cargo`/`npm` children at inspection time.
- Current managed worktree diffs are isolated to lane worktrees and staged for
  review: `L6` representation registry, `L11` score UI extraction, `L12` Studio
  runtime `RtError`, `L13` web runtime fallback/error surface, `L15` cluster
  RBAC, and `L16` controller adapter.
- `nirs4all-tools` is now a new sibling git repo initialized on `main`; the
  scaffold is staged there, validated, and uncommitted. No remote is configured.
- `L14` found a provider dependency-cycle risk and recommends a standalone,
  dependency-light `nirs4all-providers` package with soft-import adapters; this
  is a design decision for `DEC-PROV-001`, not yet applied as code.
- Reports `IMP_L6_DMD_REGISTRY.md`, `IMP_L12_STUDIO_RUNTIME.md`,
  `IMP_L13_WEB_RT.md`, `IMP_L15_CLUSTER_RBAC.md`, and
  `IMP_L18_TOOLS_SCAFFOLD.md` are present and force-staged in
  `nirs4all-ecosystem/docs/agent_reports/`.

## Useful monitor commands

```bash
ps -eo pid,ppid,stat,etime,cmd | rg -i 'claude --dangerously|codex --dangerously|codex exec|claude -p'
find nirs4all-ecosystem/docs/agent_reports -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n' | sort
```

## Managed review wave

Started after the implementation wave was staged, to catch issues before
commit/merge and to plan the next implementation wave without writing code over
staged diffs. These agents are report-only: they may write only their assigned
`docs/agent_reports/RV*.md` report.

| Agent | Session ID | Scope | Status at launch | Report |
|---|---|---|---|---|
| `RV1` | `283103bb-0c70-4bed-9487-a7e9566c480c` | L6 DMD registry | idle/complete | `docs/agent_reports/RV1_L6_DMD_REGISTRY_REVIEW.md` |
| `RV2` | `a040fb2e-95bc-4003-a5d3-addbca8d46e3` | L16 controller manifests | idle/complete | `docs/agent_reports/RV2_L16_CONTROLLER_MANIFESTS_REVIEW.md` |
| `RV3` | `c2e2769b-1826-4b45-bae8-0960ac3163f0` | L12 Studio `RtError` | idle/complete | `docs/agent_reports/RV3_L12_STUDIO_RTERROR_REVIEW.md` |
| `RV4` | `cf224dc3-8355-43ce-887f-99e69e0f9149` | L13 Web/WASM `RtError` | idle/complete after one resume | `docs/agent_reports/RV4_L13_WEB_RT_REVIEW.md` |
| `RV5` | `f245f2fb-8a2d-4986-ab93-f87018a92a7a` | L15 cluster RBAC | idle/complete | `docs/agent_reports/RV5_L15_CLUSTER_RBAC_REVIEW.md` |
| `RV6` | `2df15a4c-0ebc-4656-87c6-f70fba81cc94` | L11 Studio UI VM | idle/complete | `docs/agent_reports/RV6_L11_STUDIO_UI_VM_REVIEW.md` |
| `RV7` | `f40cd5a8-7926-417a-b2ca-1e7c20161c4a` | L18 `nirs4all-tools` scaffold | idle/complete | `docs/agent_reports/RV7_L18_TOOLS_SCAFFOLD_REVIEW.md` |
| `RV8` | `76b24fbf-f869-4862-8163-f1b375e5d14b` | L17 PYREF/parity | idle/complete | `docs/agent_reports/RV8_L17_PYREF_REVIEW.md` |
| `RV9` | `aa251b76-9891-40cd-b302-a8fd8b7d4576` | L3/L7/L20 release-lockstep-IO gates | idle/complete | `docs/agent_reports/RV9_RELEASE_LOCKSTEP_IO_REVIEW.md` |
| `RV10` | `fb020ed0-6639-4e6d-bb06-e18249b220c9` | next-wave plan for B-010/B-011/B-014/B-017/B-018 | idle/complete | `docs/agent_reports/RV10_NEXT_WAVE_PLAN.md` |

Launch note: three initial MCP session inits timed out before returning a
session id; they were relaunched successfully with a longer `advanced.sessionInitTimeoutMs`.

Final managed-review state:

- All `RV1..RV10` reports exist and are staged in `docs/agent_reports/`.
- RV7 found three medium issues in `nirs4all-tools`; the supervisor fixed them
  in the staged `nirs4all-tools` repo before updating the sync board.
- RV10 found a load-bearing prerequisite for the next implementation wave:
  current lane slices are staged but not committed, so new worktrees must not be
  branched for W2 until each lane branch/repo has an actual commit.
- External Claude CLI processes `208304` and `208423` still remain untouched.

## Managed Wave-2B implementation sessions

Started 2026-07-01 after resolving PRE-W2a (`B-022`) by committing every staged
Wave-2A slice on its lane branch. These agents are implementation agents in
fresh worktrees. They must not edit `PARALLEL_REFACTORING_SYNC.md`; each writes
only its assigned `docs/agent_reports/W*.md` report and may make local commits
on its isolated W branch if its gates are green. No agent may push.

Committed base tips used for W2B:

| Lane | Repo / branch | Tip |
|---|---|---|
| ecosystem docs | `nirs4all-ecosystem/main` | `75f7736` |
| tools | `nirs4all-tools/main` | `93f7050` |
| L17 | `nirs4all/refactor/L17-pyref` | `1e4d8043` |
| L7 | `nirs4all-io/refactor/L7-io-dagml-sibling` | `5651da5` |
| L20 core | `dag-ml/refactor/L20-lockstep` | `4f0a3b5` |
| L20 data | `dag-ml-data/refactor/L20-lockstep` | `2214f75` |
| L6 | `dag-ml-data/refactor/L6-dmd-registry` | `4003480` |
| L11 | `nirs4all-studio/refactor/L11-ui-vm` | `8d6a1f0` |
| L12 | `nirs4all-studio/refactor/L12-runtime-routes` | `155678b` |
| L13 | `nirs4all-web/refactor/L13-web-rt` | `488176b` |
| L15 | `nirs4all-cluster/refactor/L15-rbac` | `259d598` |
| L16 | `dag-ml/refactor/L16-controller-manifests` | `2143c57` |

| Agent | Session ID(s) | Scope | Worktree / cwd | Final state | Code commit(s) | Report |
|---|---|---|---|---|---|---|
| `W1` | `597c2cdf-0e98-40c5-a64d-5b54ef7d8bac` | B-010 fallback coverage meter | `_worktrees/W1-nirs4all` | committed | `nirs4all/refactor/W1-fallback-meter` `b135baef` | `docs/agent_reports/W1_FALLBACK_METER.md` |
| `W2` | `8b54536f-ce87-4e33-ae11-b7d179fe30b4` | B-010 native fallback lowering | `_worktrees/W2-nirs4all` | committed | `nirs4all/refactor/W2-native-fallback` `2f2f9c40` | `docs/agent_reports/W2_NATIVE_FALLBACK.md` |
| `W3` | `d9749b9f-9c4a-44c2-9059-cdb0ec0c1657`, `2caf0e76-83d7-4c4f-9345-35a812d7ee57` | B-010/B-011 native `.n4a` parity coverage | `_worktrees/W3-nirs4all` | committed after resume | `nirs4all/refactor/W3-native-export` `c708b02e` | `docs/agent_reports/W3_NATIVE_EXPORT.md` |
| `W4` | `23618bd3-1c71-4899-bca7-31aa62beabf6` | B-011 cross-engine parity | `_worktrees/W4-nirs4all` | committed despite MCP `maxTurns` after useful work | `nirs4all/refactor/W4-cross-engine` `01bfb809` | `docs/agent_reports/W4_CROSS_ENGINE.md` |
| `W5` | `039683db-68ce-4993-b610-4d246e2e3ded` | B-014 lockstep contracts | `_worktrees/W5-dmd` + `_worktrees/W5-dagml` | completed by supervisor after session limit | `dag-ml-data/refactor/W5-contracts-dmd` `4f858c3`; `dag-ml/refactor/W5-contracts-dagml` `e55d8aa` | `docs/agent_reports/W5_CONTRACTS_LOCKSTEP_SUPERVISED.md` |
| `W6` | `ba11ad50-88e3-4fcd-9f9a-025236eb930f` | B-014 controller `data_requirements` | `_worktrees/W6-dagml` | committed | `dag-ml/refactor/W6-data-requirements` `77f50df` | `docs/agent_reports/W6_DATA_REQUIREMENTS.md` |
| `W7` | `4325df06-2b5e-4c33-87b3-26c0ba5520d4` | B-018 runtime envelopes | `_worktrees/W7-nirs4all` | committed by supervisor from W7 draft | `nirs4all/refactor/W7-rt-envelopes` `7f8cfe69`; ecosystem contracts/report `2e93a16` | `docs/agent_reports/W7_RT_ENVELOPES.md` |
| `W8` | `512b108d-4394-4177-bf78-805cd7d4446d`, `0e6c7b20-dc66-4714-9c8d-d885c982ac46` | B-017/B-018 Studio routing | `_worktrees/W8-studio` | committed; final MCP hit `maxTurns` after commit | `nirs4all-studio/refactor/W8-studio-routing` `5cb98f2` | `docs/agent_reports/W8_STUDIO_ROUTING.md` |
| `W9` | `8e6f6cbd-cba0-4dfc-bf60-47a8d22a67c2`, `9e04cf1e-c6bc-427c-8d4c-3a53e2b60c53` | B-018 Web RtError contract alignment | `_worktrees/W9-web` | committed | `nirs4all-web/refactor/W9-web-rt` `5cc8d8c` | `docs/agent_reports/W9_WEB_RT.md` |
| `W10` | `ceae37ad-37e7-473b-a076-2fccdd6a2165` | L14 providers scaffold | `nirs4all-providers` | committed | `nirs4all-providers/main` `3ecc679` | `docs/agent_reports/W10_PROVIDERS.md` |

Launch notes:

- Claude Code MCP setup was ready and authenticated before launch.
- All `claude_code` calls included
  `allowedTools=["Bash","Read","Write","Edit","Glob","Grep","Task"]`.
- External interactive Claude CLI processes `208304` and `208423` remain
  untouched; no visible `pytest`/`cargo`/`npm run` children were attached at the
  launch audit.

Final Wave-2B state after reset/resume supervision:

- All `W1..W10` reports are present and have been force-added to ecosystem
  history despite `/docs/` being gitignored. Latest report commits include
  `c1c9d8e` (W1/W2/W6), `c8c1657` (W3), `3385009` (W4), `2e93a16` (W7
  runtime schemas/report), `2f8f4ad` (W10), `98c459c` (W9), and `003b0d5`
  (W8).
- `W8` and `W9` were resumed/managed directly after the manual terminal
  windows failed. `W8` reached `maxTurns` after the Studio commit; the
  supervisor independently verified the branch, hash, clean tree, report, and
  process state.
- External Claude CLI processes `208304` and `208423` remain running at the
  workspace root and were not killed. Latest process audit showed only those two
  top-level external Claude sessions plus MCP server processes; no lingering
  Vite/codex preview server was left running.

## Managed Wave-2C implementation sessions

Started 2026-07-01 after creating local integration branches from the successful
Wave-2B commits. These agents run from `_worktrees/W11-*` through
`_worktrees/W20-*`, consuming the shared prompt program
`docs/WAVE_2C_AGENT_PROMPTS.md`.

Integration bases created before launch:

| Repo | Integration branch / worktree | Contents | Quick gate |
|---|---|---|---|
| `nirs4all` | `refactor/integration-nirs4all` / `_worktrees/INT-nirs4all` | W1+W2+W3+W4+W7 | `27 passed` for RT envelopes + fallback meter tests |
| `dag-ml` | `refactor/integration-dagml` / `_worktrees/INT-dagml` | L20+L16+W5+W6 | `cargo test -p dag-ml-core controller_adapter --lib` -> 18 passed |
| `dag-ml-data` | `refactor/integration-dmd` / `_worktrees/INT-dmd` | L20+L6+W5 | `cargo test -p dag-ml-data-core representation_registry --lib` -> 5 passed |
| `nirs4all-studio` | `refactor/integration-studio` / `_worktrees/INT-studio` | L11+L12+W8 | compile attempted; backend tests need FastAPI env |
| `nirs4all-web` | `refactor/integration-web` / `_worktrees/INT-web` | L13+W9 | typecheck attempted; current PATH resolves Windows npm |
| `nirs4all-cluster` | `refactor/integration-cluster` / `_worktrees/INT-cluster` | L15 | compile attempted; tests need FastAPI env |
| `nirs4all-io` | `refactor/integration-io` / `_worktrees/INT-io` | L7 | clean worktree |

Known environment limits at launch:

- Studio and Cluster backend tests require a Python environment with `fastapi`;
  supervisor `python3` did not have it.
- Web typecheck/build require WSL-local Node/npm; the observed `npm` on PATH was
  Windows npm.

| Agent | Session ID | Scope | Worktree / cwd | Report |
|---|---|---|---|---|
| `W11` | `c8189b12-2edd-4539-99d8-c060db0a5d4f` | B-010 branch/dup fallback lowering | `_worktrees/W11-nirs4all-branch` | `docs/agent_reports/W11_BRANCH_FALLBACK.md` |
| `W12` | `baa2b9d1-2340-449d-a738-876b09b22e21` | B-010 multi-source fallback lowering | `_worktrees/W12-nirs4all-multisource` | `docs/agent_reports/W12_MULTISOURCE_FALLBACK.md` |
| `W13` | `09bd4fa1-41a2-48eb-9956-a33f95286d2c` | native `.n4a` export production slice | `_worktrees/W13-nirs4all-export` + `_worktrees/W13-dagml-export` | `docs/agent_reports/W13_NATIVE_N4A_EXPORT.md` |
| `W14` | `d08edf50-3183-421b-ba8d-74daa4b98300` | Studio-bypass parity + engine-record gates | `_worktrees/W14-studio-parity` | `docs/agent_reports/W14_STUDIO_BYPASS_PARITY.md` |
| `W15` | `ba591d16-31da-4bf3-93a5-d1a29d0464c7` | Studio compute push-down first slice | `_worktrees/W15-studio-compute` | `docs/agent_reports/W15_STUDIO_COMPUTE_PUSHDOWN.md` |
| `W16` | `afb6d3a8-4411-4d31-8bd5-62bdeced6ccd` | Web served smoke + RtError diagnostics | `_worktrees/W16-web-rt-smoke` | `docs/agent_reports/W16_WEB_RT_SMOKE.md` |
| `W17` | `dae4db7d-eb6d-4ac6-ae26-6f9e4a6eac61` | DatasetPackage v2 first implementation | `_worktrees/W17-io-dataset-package` | `docs/agent_reports/W17_DATASET_PACKAGE.md` |
| `W18` | `ef4d87b0-da0b-4126-92a7-0800382b45f6` | provider adapters phase 2 | `_worktrees/W18-providers` | `docs/agent_reports/W18_PROVIDERS_PHASE2.md` |
| `W19` | `6982df22-b082-4747-9075-f011329a17b4` | cluster typed client/adapter | `_worktrees/W19-cluster-client` | `docs/agent_reports/W19_CLUSTER_CLIENT.md` |
| `W20` | `b2942e83-e228-41cb-8e62-3e53788752d9` | lite -> `nirs4all-core` aggregate + `n4a` facade | `_worktrees/W20-lite-core` | `docs/agent_reports/W20_LITE_CORE.md` |

Launch notes:

- All `claude_code` calls used
  `allowedTools=["Bash","Read","Write","Edit","Glob","Grep","Task"]`.
- All agents were started with `effort=max`; the MCP resolved model as
  `claude-opus-4-8`.
- External interactive Claude CLI PIDs `208304` and `208423` remain untouched.

Final Wave-2C state after supervisor salvage:

- All `W11..W20` MCP sessions have ended. Most ended by `maxTurns`; useful
  patches were inspected, fixed where needed, independently verified, committed,
  and reported by the supervisor.
- No managed `pytest`, `cargo`, `npm`, `vite preview`, `codex exec`, or Claude
  worker process remains running. The W16 Vite preview was verified closed after
  the smoke runner teardown.
- External interactive Claude CLI processes `208304` and `208423` are still
  running at the workspace root and were left untouched.
- Worktrees `_worktrees/W11-*` through `_worktrees/W20-*` are clean after
  integration.

| Agent | Final state | Code commit(s) | Verification summary |
|---|---|---|---|
| `W11` | no commit; temporary probe removed | none | worktree clean |
| `W12` | committed | `nirs4all/refactor/W12-multisource-fallback` `bea5323d` | `py_compile` + `ruff check` on conformance file |
| `W13` | committed | `nirs4all/refactor/W13-native-n4a-export` `97eb7585` | ruff clean; 9 bundle/native export tests passed |
| `W14` | committed | `nirs4all-studio/refactor/W14-studio-bypass-parity` `83b0580` | ruff clean; 59 backend tests passed |
| `W15` | committed by agent | `nirs4all-studio/refactor/W15-studio-compute` `7c131d5` | agent report present |
| `W16` | committed | `nirs4all-web/refactor/W16-web-rt-smoke` `1a1bdba` | typecheck; 115 Vitest tests; build; 23 browser smokes; preview closed |
| `W17` | committed | `nirs4all-io/refactor/W17-dataset-package` `0a06943` | fmt; targeted core/dagml tests; clippy; workspace tests passed |
| `W18` | committed | `nirs4all-providers/refactor/W18-providers-phase2` `2411568` | ruff; pytest; mypy passed |
| `W19` | committed | `nirs4all-cluster/refactor/W19-cluster-client` `7a8d48f` | ruff; full pytest `116 passed, 1 skipped`; mypy passed |
| `W20` | committed by agent | `nirs4all-lite/refactor/W20-lite-core` `2f379ef` | agent-reported unit, ruff, build and wheel import gates |

## Wave-2C integration branches

After the W11-W20 salvage, the supervisor merged the successful Wave-2C commits
into integration branches so the next wave can branch from combined, tested
state instead of independent lane branches.

| Repo | Integration branch / worktree | Tip | Included Wave-2C commits |
|---|---|---|---|
| `nirs4all` | `refactor/integration-nirs4all` / `_worktrees/INT-nirs4all` | `1cecf6a5` | W12 `bea5323d`, W13 `97eb7585` on top of W1/W2/W3/W4/W7 |
| `nirs4all-studio` | `refactor/integration-studio` / `_worktrees/INT-studio` | `fb6f413` | W14 `83b0580`, W15 `7c131d5` on top of L11/L12/W8 |
| `nirs4all-web` | `refactor/integration-web` / `_worktrees/INT-web` | `1a1bdba` | W16 `1a1bdba` on top of L13/W9 |
| `nirs4all-io` | `refactor/integration-io` / `_worktrees/INT-io` | `0a06943` | W17 `0a06943` on top of L7 |
| `nirs4all-cluster` | `refactor/integration-cluster` / `_worktrees/INT-cluster` | `7a8d48f` | W19 `7a8d48f` on top of L15 |
| `nirs4all-providers` | `refactor/integration-providers` / `_worktrees/INT-providers` | `2411568` | W18 `2411568` on top of W10 |
| `nirs4all-lite` | `refactor/integration-lite` / `_worktrees/INT-lite` | `2f379ef` | W20 `2f379ef` on top of main |

Post-merge gates:

- `nirs4all`: ruff clean on touched files; `36 passed` for native bundle,
  native `.n4a`, runtime envelopes, and native fallback boundary tests.
- `nirs4all-studio`: ruff clean; `63 passed` for engine routing, runtime engine,
  run execution backend, and prediction metrics.
- `nirs4all-web`: `npm ci`, typecheck, `115` Vitest tests, Vite build,
  `23/23` browser smokes, preview port closed.
- `nirs4all-io`: `cargo fmt --all --check`, clippy targeted clean,
  `cargo test --workspace` passed.
- `nirs4all-cluster`: ruff clean, full pytest `116 passed, 1 skipped`,
  targeted mypy success.
- `nirs4all-providers`: ruff clean, pytest with expected optional-extra skips,
  mypy success.
- `nirs4all-lite`: ruff clean, Python tests `22 passed, 1 skipped,
  56 subtests passed`, sdist + wheel build passed.

## Wave-2D launch and quota interruption

Wave-2D branches were created from the Wave-2C integration tips on
2026-07-01. The prompt source is
`docs/WAVE_2D_AGENT_PROMPTS.md`. External interactive Claude CLI PIDs `208304`
and `208423` remain running at the workspace root and must stay untouched.

| Agent | Session ID | Scope | Worktree / cwd | Report | Status |
|---|---|---|---|---|---|
| `W21` | `27195ede-e318-4e78-acff-b01c3a37d30a` | B-010 fallback drain audit + safe lowering | `_worktrees/W21-nirs4all-fallback` | `docs/agent_reports/W21_FALLBACK_DRAIN.md` | quota-stopped; no code |
| `W22` | `c3f99c7d-afe6-45c7-a372-fa14cd58348e` | B-011 workspace/artifact `.n4a` parity | `_worktrees/W22-nirs4all-artifacts` | `docs/agent_reports/W22_ARTIFACT_PARITY.md` | quota-stopped; no code |
| `W23` | `3b6c5119-1bcd-414c-9d93-67283c48b986` | B-011/B-018 error and refusal parity | `_worktrees/W23-nirs4all-errors` | `docs/agent_reports/W23_ERROR_PARITY.md` | quota-stopped; no code |
| `W24` | `e84bd37a-9ec0-4851-a2c3-480bfa336725` | Studio runtime route adoption | `_worktrees/W24-studio-runtime` | `docs/agent_reports/W24_STUDIO_RUNTIME_ROUTES.md` | salvaged + committed `455e1f3` |
| `W25` | `7c18896f-d655-4a4b-ba62-a858dd3b4b3c` | Studio compute push-down slice 2 | `_worktrees/W25-studio-compute2` | `docs/agent_reports/W25_STUDIO_COMPUTE_PUSHDOWN2.md` | quota-stopped; no code |
| `W26` | `8b470fc8-0b7e-4c23-b72b-3841fc82d1f0` | Web runtime adoption + served failure smokes | `_worktrees/W26-web-runtime` | `docs/agent_reports/W26_WEB_RUNTIME_ADOPTION.md` | quota-stopped; no code |
| `W27` | `6b83caa8-a000-4bf8-a9fd-a0f856183aab` | DatasetPackage public API + provider bridge | `_worktrees/W27-io-dataset-api` + `_worktrees/W27-providers-dataset-api` | `docs/agent_reports/W27_DATASET_PROVIDER_BRIDGE.md` | quota-stopped; no code |
| `W28` | `235b0aea-5460-42f9-98d0-3251f21e269a` | Cluster client/core adapter + distributed parity scaffold | `_worktrees/W28-cluster-core-client` | `docs/agent_reports/W28_CLUSTER_CORE_CLIENT.md` | quota-stopped; no code |
| `W29` | `1e527685-5402-4941-a999-c0f907851ad3` | dag-ml/dag-ml-data data requirements consumption | `_worktrees/W29-dagml-datareq` + `_worktrees/W29-dmd-datareq` | `docs/agent_reports/W29_DATAREQ_LOCKSTEP.md` | quota-stopped; no code |
| `W30` | `3e2fdfcd-de30-48cd-b640-0e979e5b504b` | nirs4all-tools legacy converter first real transform | `_worktrees/W30-tools-migration` | `docs/agent_reports/W30_TOOLS_MIGRATION.md` | quota-stopped; no code |

Launch notes:

- All successful `claude_code` calls used
  `allowedTools=["Bash","Read","Write","Edit","Glob","Grep","Task"]`.
- All successful agents resolved as `claude-opus-4-8` with `effort=max`.
- `W23` launch attempts initially timed out during Claude session
  initialization before any session ID was created, then succeeded with a longer
  init timeout.

Final Wave-2D state after quota interruption:

- Claude reported `You've hit your weekly limit - resets Jul 3, 7am
  (Europe/Paris)` for all W21-W30 sessions before the agents could complete
  their reports.
- Supervisor-created reports now exist for `W21..W30`.
- `W24` left a small coherent diff; the supervisor tested and committed it as
  `nirs4all-studio/refactor/W24-runtime-routes` `455e1f3`.
- The W24 commit was merged into `nirs4all-studio/refactor/integration-studio`
  as `f0b0906` and re-gated on the integration branch.
- `W21`, `W22`, `W23`, `W25`, `W26`, `W27`, `W28`, `W29`, and `W30` left clean
  worktrees and no code commits.
- External interactive Claude CLI processes `208304` and `208423` remain
  untouched.

W24 integration gates:

- `PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m pytest tests/test_runs_engine_routing.py -k retry_run_preserves_requested_engine -q`
  -> `2 passed, 11 deselected`
- `PYTHONPATH=. /home/delete/nirs4all/nirs4all-studio/.venv/bin/python -m compileall -q api/runs.py tests/test_runs_engine_routing.py`
- `ruff check api/runs.py tests/test_runs_engine_routing.py` -> all checks
  passed

## Wave-2D Codex continuation and integration

After the Claude quota stop, the supervisor resumed W21-W30 with Codex workers
and one local W30 continuation. External interactive Claude CLI PIDs `208304`
and `208423` were still left untouched.

Final worker commits:

| Agent | Repo(s) | Commit(s) | Result |
|---|---|---|---|
| `W21` | `nirs4all` | `b8205343` | fallback boundary hardened; `EXPECTED_FALLBACK` still 10 |
| `W22` | `nirs4all` | `303ded0e` | dag-ml-data JSON envelope builder compatibility for artifact/workspace parity |
| `W23` | `nirs4all` | `e3335e56` | error/refusal parity + shared `RtError` mappings |
| `W24` | `nirs4all-studio` | `69f576a` on top of prior `455e1f3` | requested/actual engine and runtime route metadata preserved |
| `W25` | `nirs4all-studio` | `f83d6c4` | spectra statistics centralized through shared compute helper |
| `W26` | `nirs4all-web` | `d501734` | served runtime fallback/`allowFallback=false` smokes |
| `W27` | `nirs4all-io`, `nirs4all-providers` | `5e0d35e`, `55f79cd` | public DatasetPackage API + provider bridge |
| `W28` | `nirs4all-cluster` | `bd8ce70` | core nirs4all run adapter + CLI contract |
| `W29` | `dag-ml`, `dag-ml-data` | `beef11b`, `2a850a5` | consumed controller data requirements + registry-backed model-input validation |
| `W30` | `nirs4all-tools` | `082765f` | first real SQLite legacy-arrays migration transform |

Merged integration tips:

| Repo | Integration branch / worktree | Tip | Notes |
|---|---|---|---|
| `nirs4all` | `refactor/integration-nirs4all` / `_worktrees/INT-nirs4all` | `3e291992` | W21 + W22 + W23 merged; `envelope.py` conflict resolved with W23 factorized helper |
| `nirs4all-studio` | `refactor/integration-studio` / `_worktrees/INT-studio` | `8f3b944` | W24 + W25 merged |
| `nirs4all-web` | `refactor/integration-web` / `_worktrees/INT-web` | `4d724bd` | W26 merged |
| `nirs4all-io` | `refactor/integration-io` / `_worktrees/INT-io` | `ccfea29` | W27 IO half merged |
| `nirs4all-providers` | `refactor/integration-providers` / `_worktrees/INT-providers` | `6b9324a` | W27 providers half merged |
| `nirs4all-cluster` | `refactor/integration-cluster` / `_worktrees/INT-cluster` | `686374d` | W28 merged |
| `dag-ml` | `refactor/integration-dagml` / `_worktrees/INT-dagml` | `4982d5a` | W29 dag-ml half merged |
| `dag-ml-data` | `refactor/integration-dmd` / `_worktrees/INT-dmd` | `9131cdf` | W29 dag-ml-data half merged |
| `nirs4all-tools` | `main` / `nirs4all-tools` | `b392660` | W30 merged into main |

Post-merge gates:

- `nirs4all`: W22 artifact/workspace parity tests `15 passed, 2 warnings`;
  W21/W23 boundary/error/dataplane/RT tests `54 passed`; `coverage_meter OK
  (fallback=10, target=0)`; py_compile and Ruff clean on touched files.
- `nirs4all-studio`: combined W24/W25 pytest subset `73 passed, 2 warnings`;
  compileall and Ruff clean.
- `nirs4all-web`: Node pinned to WSL nvm path; typecheck passed; focused
  Vitest `4 passed`; build and build:single passed; served `rt-fallback`
  smoke passed after rebuilding fresh assets.
- `nirs4all-io`: Ruff clean; mypy clean; full pytest with
  `PYTHONPATH=/home/delete/nirs4all/_worktrees/INT-io/src` -> `228 passed`.
- `nirs4all-providers`: Ruff clean; mypy clean; pytest -> `50 passed,
  4 skipped`.
- `nirs4all-cluster`: full pytest -> `124 passed, 1 skipped, 1 warning`;
  Ruff clean; mypy clean.
- `dag-ml`: fmt check; targeted data-requirements tests; full
  `dag-ml-core` crate tests -> `433 passed, 2 ignored`; touched-crate clippy;
  CLI `validate-execution-plan` and `validate-graph`; cross-repo
  `validate_contracts.py` against `INT-dmd`.
- `dag-ml-data`: fmt check; targeted registry tests; full
  `dag-ml-data-core` crate tests -> `202 passed, 2 ignored`; CLI crate tests;
  touched-crate clippy; CLI `validate-model-input` and `fingerprint-schema`;
  cross-repo `validate_contracts.py` against `INT-dagml`.
- `nirs4all-tools`: pytest -> `66 passed`; compileall/Ruff/diff-check clean;
  CLI smoke `legacy migrate --verify` on inline SQLite legacy-arrays fixture
  returned expected exit `10` and produced `store.sqlite`, contracts, and
  `preserved/legacy-prediction-arrays.jsonl`.

## Wave-2E Codex continuation and integration

Wave-2E was executed after the user reported that external Claude CLI sessions
were still running. The supervisor audited the process tree first and left the
external interactive Claude CLI PIDs `208304` and `208423` untouched. These
sessions have CodeGraph MCP children and Claude threads, but no separately
visible managed `pytest`/`cargo`/`npm` worker process at the latest audit.

Wave-2E final commits:

| Agent | Repo(s) | Commit(s) | Result |
|---|---|---|---|
| `W31` | `nirs4all` | `b6cd230f` | safe preprocessing modifiers run native |
| `W32` | `nirs4all` | `0f772104` | duplication `merge="features"` runs native |
| `W33` | `nirs4all` | `03fbc1c` | native branch/fusion `.n4a` export subset |
| `W34` | `nirs4all` | `4ffff0d` | shared by-source preprocessing + concat runs native |
| `W35` | `dag-ml` | `a1b9697` | multi-source/source-index runtime contract hardened |
| `W36` | `nirs4all-studio` | `f5094c2` | Studio spectral stats prefer core runtime helper |
| `W37` | `nirs4all-web` | `02a3570` | Web runtime result/error goldens |
| `W38` | `nirs4all-cluster` | `4ffda1d` | live distributed parity harness |
| `W39` | `nirs4all-tools` | `ce8ed47` | native result artifacts preserved by toolbox |
| `W40` | `nirs4all-ecosystem` | `80e6ac6` | non-mutating cutover gate runner |

Merged integration tips after Wave-2E:

| Repo | Integration branch / worktree | Tip | Notes |
|---|---|---|---|
| `nirs4all` | `refactor/integration-nirs4all` / `_worktrees/INT-nirs4all` | `e6299d52` | W31 + W34 + W33 + W32 merged; `coverage_meter OK (fallback=6, target=0)` |
| `dag-ml` | `refactor/integration-dagml` / `_worktrees/INT-dagml` | `35e9e00` | W35 merged |
| `nirs4all-studio` | `refactor/integration-studio` / `_worktrees/INT-studio` | `64b43c7` | W36 merged |
| `nirs4all-web` | `refactor/integration-web` / `_worktrees/INT-web` | `94ccc66` | W37 merged |
| `nirs4all-cluster` | `refactor/integration-cluster` / `_worktrees/INT-cluster` | `afacc0e` | W38 merged |
| `nirs4all-tools` | `main` / `nirs4all-tools` | `b76458d` | W39 merged into main |
| `nirs4all-ecosystem` | `main` / `nirs4all-ecosystem` | `9c97948` | W40 merged into main |

Post-merge Wave-2E gates:

- `nirs4all`: full native/fallback boundary selection
  `test_conformance_dual_engine.py -k 'branch_dup_two_way_merge_features or native_fallback_boundary'`
  -> `88 passed`; `test_native_fallback_boundary.py` -> `12 passed`;
  `test_compatibility_ledger.py` -> `2 passed`; `coverage_meter --check` ->
  `fallback=6`; targeted Ruff/py_compile/JSON validation passed.
- `dag-ml`: fmt, `dag-ml-core` tests (`439 passed, 2 ignored`), touched
  clippy, and cross-repo `validate_contracts.py` passed.
- `nirs4all-studio`: `tests/test_spectra_perf.py` -> `10 passed`; targeted
  compileall/Ruff passed.
- `nirs4all-web`: focused runtime Vitest target -> `21 passed`; typecheck and
  build passed.
- `nirs4all-cluster`: full pytest -> `125 passed, 1 skipped`; Ruff and mypy
  passed.
- `nirs4all-tools`: pytest -> `69 passed`; compileall/Ruff/diff-check and
  native-results migrate/verify smoke passed.
- `nirs4all-ecosystem`: cutover gate runner validate/list, compileall,
  `json.tool`, Ruff, and diff-check passed.

Remaining Wave-2E facts:

- `EXPECTED_FALLBACK` is not empty. Remaining cases are
  `branch_dup_three_way_merge_predictions`, `branch_dup_named_with_metamodel`,
  `branch_dup_merge_all`, `multi_source_by_source_branch_distinct_preproc`,
  `multi_source_per_source_models_stacking`, and
  `multi_source_sources_concat_then_rf`.
- `DEFAULT_ENGINE` was not flipped.
- No managed Wave-2E worker or test process remains running at final audit.
- External Claude CLI PIDs `208304` and `208423` remain external interactive
  sessions and were not controlled by the supervisor.

## Managed Wave-2F implementation sessions

Started 2026-07-01 from the Wave-2E integration tips. Six Codex worker agents
were launched first (`W41..W46`), then slots were reused for `W47` and `W48`;
`W49` and `W50` were executed locally by the supervisor. The two external Claude
CLI sessions (`208304`, `208423`) stayed external and were not killed or
controlled.

| Agent | Scope | Worktree / cwd | Final state | Code commit(s) | Report |
|---|---|---|---|---|---|
| `W41` | final fallback drain probe | `_worktrees/W41-nirs4all-fallback-final` | no code commit; blocker report | none | `docs/agent_reports/W41_FALLBACK_FINAL.md` |
| `W42` | native `.n4a` export expansion | `_worktrees/W42-nirs4all-native-export2` | committed | `nirs4all/refactor/W42-native-export2` `8bba1f51` | `docs/agent_reports/W42_NATIVE_EXPORT2.md` |
| `W43` | Python runtime goldens | `_worktrees/W43-nirs4all-rt-goldens` | committed | `nirs4all/refactor/W43-rt-goldens` `379ede0a` | `docs/agent_reports/W43_PY_RT_GOLDENS.md` |
| `W44` | Studio compute push-down 3 | `_worktrees/W44-studio-compute3` | committed | `nirs4all-studio/refactor/W44-compute-pushdown3` `13bd36f` | `docs/agent_reports/W44_STUDIO_COMPUTE_PUSHDOWN3.md` |
| `W45` | Studio UI runtime/status helpers | `_worktrees/W45-studio-ui-runtime` | committed | `nirs4all-studio/refactor/W45-ui-runtime` `8654ea7` | `docs/agent_reports/W45_STUDIO_UI_RUNTIME.md` |
| `W46` | Web cross-runtime fixtures | `_worktrees/W46-web-cross-rt` | committed | `nirs4all-web/refactor/W46-cross-rt` `a7b98bd` | `docs/agent_reports/W46_WEB_CROSS_RT.md` |
| `W47` | cluster real-DAG parity | `_worktrees/W47-cluster-real-dag` | committed | `nirs4all-cluster/refactor/W47-real-dag-parity` `e2a99c2` | `docs/agent_reports/W47_CLUSTER_REAL_DAG.md` |
| `W48` | providers service/adapters hardening | `_worktrees/W48-providers-services` | committed | `nirs4all-providers/refactor/W48-provider-services` `074d07d` | `docs/agent_reports/W48_PROVIDER_SERVICES.md` |
| `W49` | tools runtime-readable result lowering | `_worktrees/W49-tools-results-lowering` | committed by supervisor | `nirs4all-tools/refactor/W49-results-lowering` `7b2e390` | `docs/agent_reports/W49_TOOLS_RESULTS_LOWERING.md` |
| `W50` | cutover gate CI integration | `_worktrees/W50-ecosystem-cutover-ci` | committed by supervisor | `nirs4all-ecosystem/refactor/W50-cutover-ci` `adde4ef` | `docs/agent_reports/W50_CUTOVER_CI.md` |

Merged integration tips after Wave-2F:

| Repo | Integration branch / worktree | Tip | Notes |
|---|---|---|---|
| `nirs4all` | `refactor/integration-nirs4all` / `_worktrees/INT-nirs4all` | `c12fea5d` | W42 + W43 merged; W41 report only |
| `nirs4all-studio` | `refactor/integration-studio` / `_worktrees/INT-studio` | `609f756` | W44 + W45 merged |
| `nirs4all-web` | `refactor/integration-web` / `_worktrees/INT-web` | `1adc71c` | W46 merged |
| `nirs4all-cluster` | `refactor/integration-cluster` / `_worktrees/INT-cluster` | `297aec1` | W47 merged |
| `nirs4all-providers` | `refactor/integration-providers` / `_worktrees/INT-providers` | `818fbd0` | W48 merged |
| `nirs4all-tools` | `main` / `nirs4all-tools` | `a9fd589` | W49 merged into main |
| `nirs4all-ecosystem` | `main` / `nirs4all-ecosystem` | `395f9b7` | W50 merged into main |

Post-merge Wave-2F gates reported by workers/supervisor:

- `nirs4all` W42: native bundle tests `7 passed, 1 xfailed`;
  cross-engine `.n4a` tests `3 passed`; focused artifact round-trip/tamper
  tests `2 passed`; targeted Ruff/py_compile passed.
- `nirs4all` W43: runtime golden tests `10 passed`; fallback/ledger tests
  `10 passed`; JSON parse, Ruff, py_compile passed.
- `nirs4all` W41: fallback boundary and ledger tests `14 passed`;
  `coverage_meter --check` OK with `fallback=6`; exploratory drains failed
  parity and were not merged.
- `nirs4all-studio` W44: preprocessing runtime tests, spectra perf tests,
  targeted playground tests, compileall, and Ruff passed.
- `nirs4all-studio` W45: targeted Vitest `21 passed`, `npm run lint:tsc`,
  targeted ESLint, and diff-check passed.
- `nirs4all-web` W46: targeted Vitest runtime tests, typecheck, build, full
  test, and diff-check passed.
- `nirs4all-cluster` W47: full pytest `126 passed, 1 skipped`, Ruff, format
  check, and mypy passed.
- `nirs4all-providers` W48: full pytest `56 passed, 4 skipped`, focused pytest
  `36 passed, 4 skipped`, Ruff, and mypy passed.
- `nirs4all-tools` W49: full pytest `70 passed`, Ruff, mypy, py_compile, and
  diff-check passed using `/home/delete/miniconda3/bin/python3`.
- `nirs4all-ecosystem` W50: py_compile, JSON validation, gate-runner validate,
  list/selfcheck/advisory smoke, workflow YAML parse, and Ruff passed.

Remaining Wave-2F facts:

- `EXPECTED_FALLBACK` remains `6`; W41 records the exact native-contract
  blockers instead of making unsafe lowering changes.
- Native stacking `.n4a` export remains xfailed until a replay graph /
  column-order manifest exists for base predictions into the meta-model.
- `DEFAULT_ENGINE` was not flipped.
- No managed Wave-2F worker or test process remains running at final audit.
- External Claude CLI PIDs `208304` and `208423` remain external interactive
  sessions and were not controlled by the supervisor.
