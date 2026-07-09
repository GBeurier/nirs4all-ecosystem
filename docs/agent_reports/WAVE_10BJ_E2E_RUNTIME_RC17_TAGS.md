# Wave 10BJ - Fresh E2E Runtime Evidence and RC17 Tags

Date: 2026-07-09

## Scope

Recorded fresh runtime evidence after the ecosystem lock/gitlink refresh and
tagged the selected 7-member core train plus the ecosystem parent with a
non-publishing RC coordination tag.

## Evidence

- GitHub Actions run:
  `GBeurier/nirs4all-ecosystem` Cross-language E2E scenarios
  `29051545681`.
- Event: `workflow_dispatch` on
  `0dde7840b3146f4547d1024a498c56b6c7ece08c`.
- Inputs: `execute=true`, `allow_blocked=false`.
- Result: success.
- Runtime verification:
  - `11/11` scenarios verified.
  - `71` runtime artifacts verified.
  - `0` failures.
  - committed runtime evidence ledger check passed with
    `--max-age-seconds 14400`.
- Coverage gate:
  - `11/11` scenarios ready.
  - `full_strict_ready=true`.
  - `strictness_gap_count=0`.
  - required languages covered: Python `11`, R `5`, JavaScript/WASM `8`,
    Web `5`, MATLAB/Octave `1`.
  - required tags covered: `custom_app_host`, `datasets`, `io`,
    `multimodal`, `multisource`, `papers`, `parity`, `pipeline`,
    `pipeline_generation`, `predictions`, `repository`, `web_results`,
    `workspace_save`.

## Tags Pushed

The annotated tag `n4a-v1-rc17-2026.07-refactor` was pushed to:

| repo | commit |
| --- | --- |
| `dag-ml` | `366ca8bd09d558855055daa57199d923f51abb6d` |
| `dag-ml-data` | `4aaef0a43990a0f859ad4c28f40042f542858f59` |
| `nirs4all-core` | `5f207202124725d749cf3f2a013b57caaa1d0b20` |
| `nirs4all-datasets` | `67d47c557bcb8770506409d2c688cb3b60384c18` |
| `nirs4all-formats` | `548d04909e4b59010eaff2a0127f8a6fb0d13a12` |
| `nirs4all-io` | `684be731b72cbcdd7cbe4f548d5856efba34bb87` |
| `nirs4all-methods` | `7149d7dbf51b0c47e2f89aa29bc76ed388eead30` |
| `nirs4all-ecosystem` | `0dde7840b3146f4547d1024a498c56b6c7ece08c` |

These tags are coordination tags, not semver registry release tags. The
inspected registry workflows are gated on `v*` / `vX.Y.Z` tag patterns or
manual dispatch, so this RC tag did not trigger package publication.

## Files Updated

- `docs/contracts/release/aggregation-lock.n4a.lock.json`: regenerated after
  RC17 tags so the 7 lock members now carry `exact_tag:
  n4a-v1-rc17-2026.07-refactor`.
- `docs/agent_reports/WAVE_10BJ_E2E_RUNTIME_RC17_TAGS.md`: this evidence
  report.

## Remaining Risks

- `nirs4all` Python and `nirs4all-studio` production remain held.
- Studio Windows RC still needs manual smoke on Windows.
- Cockpit non-green package targets remain CRAN/manual only:
  `n4m`, `pls4all`, `nirs4allio`, `nirs4alldatasets`, and the `nirs4all`
  aggregate R package.
- The next semver patch publication batch should be decided separately for
  `nirs4all-ui`, `nirs4all-web`, `nirs4all-core`, and any other repo whose
  post-tag changes need registry artifacts.
