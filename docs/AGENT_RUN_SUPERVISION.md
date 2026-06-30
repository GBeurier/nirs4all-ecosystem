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

| Agent | Session ID | Scope | Worktree / cwd | Status at launch | Report |
|---|---|---|---|---|---|
| `W1` | `597c2cdf-0e98-40c5-a64d-5b54ef7d8bac` | B-010 fallback coverage meter | `_worktrees/W1-nirs4all` | running | `docs/agent_reports/W1_FALLBACK_METER.md` |
| `W2` | `8b54536f-ce87-4e33-ae11-b7d179fe30b4` | B-010 native fallback lowering | `_worktrees/W2-nirs4all` | running | `docs/agent_reports/W2_NATIVE_FALLBACK.md` |
| `W3` | `d9749b9f-9c4a-44c2-9059-cdb0ec0c1657` | B-010 native `.n4a` export | `_worktrees/W3-nirs4all` + `_worktrees/W3-dagml` | running | `docs/agent_reports/W3_NATIVE_EXPORT.md` |
| `W4` | `23618bd3-1c71-4899-bca7-31aa62beabf6` | B-011 cross-engine parity | `_worktrees/W4-nirs4all` | running | `docs/agent_reports/W4_CROSS_ENGINE.md` |
| `W5` | `039683db-68ce-4993-b610-4d246e2e3ded` | B-014 lockstep contracts | `_worktrees/W5-dmd` + `_worktrees/W5-dagml` | running | `docs/agent_reports/W5_CONTRACTS_LOCKSTEP.md` |
| `W6` | `ba11ad50-88e3-4fcd-9f9a-025236eb930f` | B-014 controller `data_requirements` | `_worktrees/W6-dagml` | running | `docs/agent_reports/W6_DATA_REQUIREMENTS.md` |
| `W7` | `4325df06-2b5e-4c33-87b3-26c0ba5520d4` | B-018 runtime envelopes | `_worktrees/W7-nirs4all` | running | `docs/agent_reports/W7_RT_ENVELOPES.md` |
| `W8` | `512b108d-4394-4177-bf78-805cd7d4446d` | B-017/B-018 Studio routing | `_worktrees/W8-studio` | running | `docs/agent_reports/W8_STUDIO_ROUTING.md` |
| `W9` | `8e6f6cbd-cba0-4dfc-bf60-47a8d22a67c2` | B-018 Web RtError | `_worktrees/W9-web` | running | `docs/agent_reports/W9_WEB_RT.md` |
| `W10` | `ceae37ad-37e7-473b-a076-2fccdd6a2165` | L14 providers scaffold | `nirs4all-providers` | running | `docs/agent_reports/W10_PROVIDERS.md` |

Launch notes:

- Claude Code MCP setup was ready and authenticated before launch.
- All `claude_code` calls included
  `allowedTools=["Bash","Read","Write","Edit","Glob","Grep","Task"]`.
- External interactive Claude CLI processes `208304` and `208423` remain
  untouched; no visible `pytest`/`cargo`/`npm run` children were attached at the
  launch audit.
