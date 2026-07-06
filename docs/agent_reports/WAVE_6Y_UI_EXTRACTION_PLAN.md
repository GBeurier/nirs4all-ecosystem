# Wave 6Y - UI Extraction Plan

Date: 2026-07-06

## Scope

- Repos audited: `nirs4all-ui`, `nirs4all-studio`, `nirs4all-web`
- Mode: read-only planning

## Finding

`nirs4all-ui` is not yet a shared Studio/Web application base. It currently provides shared
score/runtime helpers and a few runtime/metric badges. The first useful extraction wave should be
small presentational contracts, not a full design-system migration.

## Recommended First Batch

1. Score task metrics and compact metric chips
   - Destination: `nirs4all-ui/src/score/taskMetrics.ts`
   - Consumers: Web score formatting, Studio score row/columns helpers
   - Risk: low

2. Dataset preview summary contract
   - Destination: `nirs4all-ui/src/dataset/previewSummary.ts`
   - Consumers: Studio dataset preview/detail helpers, Web dataset summary
   - Risk: medium because Studio and Web adapters have different source shapes

3. Operator catalog / palette row contract
   - Destination: `nirs4all-ui/src/pipeline/operatorCatalog.ts`
   - Consumers: Studio palette data, Web node palette/model picker
   - Risk: medium because taxonomy names differ between hosts

4. Optional follow-up: runtime progress display contract
   - Destination: `nirs4all-ui/src/runtime/progressDisplay.ts`
   - Lower priority than the three above.

## Integration Order

Start with score metrics because it is low risk and proves the full cycle:

1. Add helper/tests in `nirs4all-ui`.
2. Run `npm run typecheck`, `npm test`, `npm run build`, `npm run site:build`.
3. Adapt Studio with targeted tests and `npm run smoke:nirs4all-ui-package`.
4. Sync Web's vendored `nirs4all-ui`, adapt Web tests, and run Web typecheck/test/build.

Do not claim Studio/Web UI parity until dataset, pipeline, result, prediction, and workbench
contracts are actually shared.
