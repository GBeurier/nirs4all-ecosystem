# Wave 2U Superseded Work Audit

Date: 2026-07-01T16:09:53+02:00

## Scope

Follow-up after W2T. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2U exists because the workspace was reset after an earlier interrupted run and
older agent work may still exist in branches/worktrees. The goal is audit first,
not merge first.

Primary targets:

- `nirs4all/refactor/L17-pyref@13157d79`, which diverges from
  `_worktrees/INT-nirs4all@7ab1ec1e`.
- Claude-era local work under
  `nirs4all/.claude/worktrees/agent-a5af0970d430760ab`.
- Older W1-W89 worktrees and other dirty states that might be superseded.

Full Python-reference parity remains deferred. W2U must not run
`pyref_oracle_full`; it should only classify work and propose safe next actions.

## Starting State

- W2T integrated:
  - `nirs4all-ecosystem` `ba771bd`
  - `nirs4all-lite` `272e07f`
  - `_worktrees/INT-nirs4all` `7ab1ec1e`
  - `_worktrees/INT-providers` `314c8681`
- W2T non-full cutover passed with `pyref_oracle_full` skipped.
- The selected release lock now pins `nirs4all-lite@272e07f`.
- The public V1 matrix includes `nirs4all` Python, R, and WASM/browser surfaces.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| K/L17 | Kuhn `019f1e04-59d8-7090-8d53-b90d07297c7b` | read-only `nirs4all` + `_worktrees/INT-nirs4all`; no edits | Done: `refactor/L17-pyref` is superseded by `refactor/integration-nirs4all`; no commit should be merged or cherry-picked. |
| K/Claude | Kierkegaard `019f1e04-5a98-7331-aa48-24e3b6c24f68` | read-only local worktrees only; no edits | Done: all `_worktrees` are clean; Claude-era untracked parity files must be preserved but not merged blindly. |
| K/Release | coordinator | `nirs4all-ecosystem` report only | Integrate audit results into this report and decide whether a follow-up implementation lane is warranted. |

## Review Criteria

- No old branch/worktree merge without fresh audit.
- No private repos touched.
- No edits outside this report unless a later implementation wave is explicitly
  started.
- Prefer patch-id/log/status evidence over commit-subject guesses.
- Any potentially valuable code must be named with path, branch/worktree, commit,
  and risk; do not rely on "looks useful".

## Expected Gates

- Read-only git comparisons and status audits.
- No full parity.
- Existing W2T non-full cutover result remains the latest integration proof.

## Integration Log

### 2026-07-01T16:14:24+02:00

Lane K/L17 completed read-only.

- Compared `/home/delete/nirs4all/nirs4all` at
  `refactor/L17-pyref@13157d79` against
  `_worktrees/INT-nirs4all` at
  `refactor/integration-nirs4all@7ab1ec1e`.
- `git log --left-right --cherry-pick 7ab1ec1e...13157d79` found three
  commits genuinely unique to L17 after patch-equivalent filtering.
- Classification:

| Commit | Classification | Evidence |
| --- | --- | --- |
| `8eff3b57` `feat(dagml): expose multi-source source layout` | already integrated / superseded | Range-diff pairs it with INT `362c2d79`; INT already exposes `source_order`, `source_ids`, `blocks`, `per_source_preprocessing_outputs`, and `concat_layout`, and injects `plan.source_layout` for multi-source envelopes. |
| `5e00e400` `fix(dagml): support by-source distinct preprocessing` | already integrated / superseded | Range-diff pairs it with INT `4ef0b3fe`; INT already contains the distinct detector, source-layout validation/lowering, native runner, and dispatch. INT also preserves broader shared by-source concat support. |
| `13157d79` `fix(dagml): run source concat merge natively` | already integrated / superseded | Range-diff pairs it with INT `63976243`; INT already contains `_detect_source_concat_merge()`, `_run_source_concat_merge()`, and dispatch. INT is newer: `EXPECTED_FALLBACK` is empty and `docs/compatibility.json` records fallback `0`, native `87`; L17 remains at fallback `9`, native `78`. |

The non-`--cherry-pick` L17 commit `8ef94242` is patch-equivalent to INT
`0aa2a674`, so it was not counted as unique.

Decision:

- Do not merge `refactor/L17-pyref@13157d79`.
- Do not cherry-pick its three unique commits.
- Rationale: the global diff from INT to L17 would regress current INT by
  removing or reverting later runtime/proof surfaces, including
  `nirs4all/pipeline/dagml/rt.py`, `nirs4all/runtime.py`,
  `scripts/prove_installed_n4m.py`, native export/runtime tests, and W2T/W2S
  proof gates.

If a future human requests a narrowly scoped extraction, required targeted
checks would include:

- `ruff check nirs4all/pipeline/dagml tests/integration/parity`
- `mypy nirs4all`
- `pytest tests/integration/parity/test_dagml_cli_runner.py -k "source_layout or by_source_distinct_preproc or source_concat"`
- `pytest tests/integration/parity/test_conformance_dual_engine.py -k "multi_source_by_source_branch_distinct_preproc or multi_source_sources_concat_then_rf or fallback"`

Lane K/Claude completed read-only.

- All `_worktrees/W*`, `INT-*`, and `L*` inspected by the auditor had
  `git status --short = 0`.
- The only notable local state to preserve is
  `/home/delete/nirs4all/nirs4all/.claude/worktrees/agent-a5af0970d430760ab`,
  branch `worktree-agent-a5af0970d430760ab`, SHA `4e9dfe1ca0c0`, with five
  untracked files:
  - `tests/integration/parity/conformance/README.md`
  - `tests/integration/parity/conformance/__init__.py`
  - `tests/integration/parity/conformance/_pack.py`
  - `tests/integration/parity/conformance/conformance_pack.json`
  - `tests/integration/parity/test_dual_engine_conformance.py`
- These files are preservation-only evidence. They must not be merged without a
  separate patch-level audit.

Already integrated / do not remerge:

- W92 methods, W94 lite, W95/W96 Studio, W96 Web, W97 tools, W98 full parity
  gate, W93 IO/datasets/formats, and W2S providers.

Still audit-only / no automatic merge:

- Older non-ancestor W* worktrees across core/dag-ml/dag-ml-data/IO and late
  W76-W89 one-commit topics.
- `INT-*` worktrees are integration heads, not merge sources for primary repos
  without an explicit release selection step.
- `_worktrees/dag-ml` is a symlink to `/home/delete/nirs4all/dag-ml`; exclude it
  from cleanup decisions for W/Claude-era worktrees.

Conclusion:

- W2U does not authorize any code merge.
- W2T remains the latest integrated, non-full verified release state.
- `pyref_oracle_full` remains deferred; the last full proof remains W98.
