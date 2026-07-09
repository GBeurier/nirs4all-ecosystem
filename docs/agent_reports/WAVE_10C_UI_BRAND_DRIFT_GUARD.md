# Wave 10C - UI brand drift guard

## Scope

- Repinned `nirs4all-ui` from `cc0b5db` to `6b5f52f`.
- Integrated the brand asset drift guard that checks generated SVG assets and
  mirrored `src/brand` definitions without touching quality-specific UI
  components.

## Files Modified

- gitlink: `nirs4all-ui`
- `docs/agent_reports/WAVE_10C_UI_BRAND_DRIFT_GUARD.md`

## Tests And Gates

- `nirs4all-ui`: `npm run brand:check`
- `nirs4all-ui`: `npm test -- src/brand/index.test.ts`
- `nirs4all-ui`: `npm run typecheck`
- `nirs4all-ui`: `npm run ci`
- `nirs4all-ui@6b5f52f`: GitHub `version-guard`, `CI`, and `GitHub Pages`
  completed successfully.

## Decisions

- Kept this as a non-release package maintenance guard. It changes CI/test
  coverage and the asset generator check path, not the published runtime API.
- Did not modify `nirs4all-quality` or any quality-specific components.

## Risks / Follow-Up

- If a future brand generator change intentionally updates assets, run
  `npm run brand:generate` in `nirs4all-ui` and keep `npm run brand:check`
  green before publishing.
