# Wave 2V Claude-Era Parity Artifact Audit

Date: 2026-07-01T16:15:31+02:00

## Scope

Follow-up after W2U. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2U found five untracked files in a Claude-era nirs4all worktree:

- `tests/integration/parity/conformance/README.md`
- `tests/integration/parity/conformance/__init__.py`
- `tests/integration/parity/conformance/_pack.py`
- `tests/integration/parity/conformance/conformance_pack.json`
- `tests/integration/parity/test_dual_engine_conformance.py`

W2V audits those files read-only, compares them to the current
`_worktrees/INT-nirs4all` parity gates, and records whether any content should be
reimplemented later. It must not merge or copy the untracked files.

Full Python-reference parity remains deferred. W2V must not run
`pyref_oracle_full`.

## Starting State

- W2U concluded `refactor/L17-pyref@13157d79` is superseded by
  `_worktrees/INT-nirs4all@7ab1ec1e`.
- W2T remains the latest integrated, non-full verified release state.
- The Claude-era worktree commit itself is superseded, but the five untracked
  files have not yet been content-audited.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| K/ClaudeArtifact | Plato `019f1e09-7a60-7513-a2f5-ac1bfc154a76` | read-only Claude-era worktree and `_worktrees/INT-nirs4all`; no edits | Done: content-audited the five untracked files; do not integrate them as-is. |
| K/CurrentParity | Epicurus `019f1e09-7b14-76f0-8827-1bf17d6b0fa5` | read-only `_worktrees/INT-nirs4all` and ecosystem reports; no edits | Done: current INT parity/ledger suite already supersedes the Claude-era harness. |
| K/Release | coordinator | `nirs4all-ecosystem` report only | Integrate findings and decide whether follow-up work is needed. |

## Review Criteria

- No merge, cherry-pick, or file copy from the Claude-era worktree.
- No full parity.
- Classify content, not author/source.
- If a concept is useful, describe a new implementation task against current INT
  heads rather than reusing the old untracked files directly.

## Integration Log

### 2026-07-01T16:19:12+02:00

Lane K/ClaudeArtifact completed read-only.

The five untracked Claude-era files propose an older cross-binding conformance
pack:

- A JSON pack with serialized DSL, `dataset_ref`, task, and legacy-captured
  expectations.
- A Python harness that reloads the pack and compares `legacy`,
  `dag-ml-inproc=1`, and `dag-ml-inproc=0`.
- A gated `N4A_CONFORMANCE_NUM_PREDICTIONS` assertion.

Classification:

| File / Concept | Classification | Reason |
| --- | --- | --- |
| `conformance/README.md` | superseded / do not use as current docs | Describes a separate pack/harness authority. INT already has `test_conformance_dual_engine.py`, `test_native_fallback_boundary`, `KNOWN_DIVERGENCES`, `NUM_PREDICTIONS_DIVERGENCE`, and `_conformance_helpers.dual_engine_runner`. |
| `conformance/__init__.py` | do not use | Package docstring only. |
| `conformance/_pack.py` | potentially useful concept, do not use as-is | The `ConformanceFixture` / `load_pack()` / `regenerate()` idea may be useful later, but it writes a separate `conformance_pack.json` and would need to be rebuilt from current INT registry/baselines. |
| `conformance/conformance_pack.json` | do not use as artifact | The 11 fixture names exist in INT, but expected values are stale. Example: `baseline_vertical_slice` records old `r2=0.5425947638590629`, while current INT baseline records `r2=0.5499299067664708` after the known `RunResult.best_r2` correction. |
| `test_dual_engine_conformance.py` | already covered / superseded | INT's `test_conformance_dual_engine.py` already forces `engine="legacy"` / `engine="dag-ml"`, detects fallback, and verifies scores, `num_predictions`, `RunResult` contract, winner identity, and `y_pred`. |

The 11 pack case names are already represented in INT as `PipelineCase`s and
baseline JSON files:

- `baseline_vertical_slice`
- `baseline_snv_plsr_shuffle`
- `baseline_msc_y_processing_ridge`
- `baseline_kennard_stone_plsr`
- `baseline_spxy_plsr`
- `baseline_classification_rf_stratified`
- `preprocessing_explicit_keyword`
- `preprocessing_fit_on_all`
- `preprocessing_force_layout_2d`
- `round_trip_baseline_export_predict`
- `round_trip_with_y_processing_inverse`

Lane K/CurrentParity completed read-only.

Current INT parity artifacts that supersede the Claude-era proposal:

- `tests/integration/parity/_registry.py` and `cases_*` registry.
- `tests/integration/parity/baselines/*.json` committed baselines.
- `tests/integration/parity/test_conformance_dual_engine.py`.
- `tests/integration/parity/_conformance_helpers.py`.
- `tests/integration/parity/_oracle.py`.
- `tests/integration/parity/coverage_meter.py`.
- `tests/integration/parity/test_native_fallback_boundary.py`.
- `docs/compatibility.json` and `docs/compatibility.md`.

Current ledger state reported by INT:

- 95 registered cases.
- 87 executable cases.
- 87 native cases.
- `fallback=0`.
- 11 strict xfails.
- 6 skips.
- 2 pinned `num_predictions_divergence` pass cases.

Current real gaps are not "missing conformance pack"; they are the explicit
ledger gaps:

- Studio does not yet ride the oracle.
- Installed `n4m` parity lane is still partial in the regular parity suite,
  though W2T now gates the installed-`n4m` proof separately.
- nirs4all-side wheel / `.so` freshness checks remain incomplete.
- `.n4a` export round-trip remains partial.
- 6 skips remain explicit: 3 fixtures and 3 unknown-semantics cases.

Decision:

- Do not merge or copy the Claude-era files.
- Preserve them as local audit evidence until a cleanup policy is agreed.
- If the portable pack idea is needed for R/MATLAB/WASM bindings, implement a
  fresh exporter from current INT registry/baselines/ledger, not from the stale
  Claude-era files. That would be a new explicit lane, not a merge.

`pyref_oracle_full` was not run.
