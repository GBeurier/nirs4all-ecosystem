# Wave 3D - Studio TypeScript Gate

Date: 2026-07-01T18:28:40+02:00

## Scope

Focused Studio batch on the two pre-existing `tsc --noEmit --project tsconfig.app.json` blockers reported after W3A:

- `src/api/inspector.test.ts` had an incomplete `ScoreRef` test fixture.
- `src/components/predictions/viewer/fetchPartitionData.ts` assigned `number[] | number[][]` prediction arrays into scalar-only viewer vectors.

No full parity run in this batch.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Hegel | Inspector `ScoreRef` fixture audit | done | Read-only. Confirmed frontend `ScoreRef` intentionally requires `key` and `metric`; recommended updating only the test fixture. |
| Averroes | Prediction viewer array type audit | done | Read-only. Confirmed API shape is `number[] | number[][] | null` while viewer charts are scalar-only; recommended target-index vector extraction, not widening viewer state. |
| Parfit | W3D reviewer | done | Found an alignment bug in the first vector helper because invalid cells were filtered independently. Fixed by preserving row positions with `Number.NaN`; follow-up review found no blockers. |

## Decisions

- Keep `ScoreRef.key` and `ScoreRef.metric` required in frontend types.
- Keep `PartitionDataset.yTrue` / `yPred` as scalar `number[]`; do not widen the viewer chart contract to matrices.
- Convert aggregated prediction arrays at fetch time:
  - pass through scalar vectors;
  - extract `target_index` from matrices, defaulting to target `0`;
  - preserve row positions with `Number.NaN` for missing/non-numeric target cells so sample IDs and metadata remain aligned.

## Files Changed

`_worktrees/INT-studio`:

- `src/api/inspector.test.ts`
- `src/components/predictions/viewer/fetchPartitionData.ts`
- `src/components/predictions/viewer/__tests__/fetchPartitionData.test.ts`

## Gates

- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node_modules/.bin/tsc --noEmit --project tsconfig.app.json` - passed.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node_modules/.bin/vitest run src/api/inspector.test.ts src/components/predictions/viewer/__tests__/fetchPartitionData.test.ts` - 2 files, 7 tests passed.
- `PATH=/home/delete/.nvm/versions/node/v24.16.0/bin:$PATH node_modules/.bin/eslint src/api/inspector.test.ts src/components/predictions/viewer/fetchPartitionData.ts src/components/predictions/viewer/__tests__/fetchPartitionData.test.ts` - passed.
- `git diff --check` - passed.

## Risks

- Multi-target viewer charts still show one selected scalar target at a time; this batch does not add a target selector UI.
- If backend scalar vectors later allow `null` elements, `coercePredictionVector` should be extended deliberately to preserve scalar-vector positions as well.
