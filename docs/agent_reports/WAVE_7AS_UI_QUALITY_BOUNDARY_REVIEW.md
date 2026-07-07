# Wave 7AS - nirs4all-ui / nirs4all-quality boundary review

Date: 2026-07-07

## Scope

- Read-only Claude Code review of `nirs4all-ui` and `nirs4all-quality`.
- Goal: identify which `nirs4all-ui` areas are currently consumed by the parallel `nirs4all-quality` work and which areas remain safe for ecosystem UI/showcase work.
- No files were edited by the reviewer.

## Findings

- `nirs4all-quality` consumes `nirs4all-ui` by source path, not by the published package:
  - `@lab` points at `nirs4all-ui/src/lab/index.ts`.
  - Tailwind scans `nirs4all-ui/src/lab/**/*.{ts,tsx}`.
  - app CSS imports `nirs4all-ui/assets/theme.css`.
  - the quality brand generator reads/writes `nirs4all-ui/assets/brand/{nirs4all,quali}`.
- Therefore these areas are reserved while the quality agent is active:
  - `nirs4all-ui/src/lab/**`
  - `nirs4all-ui/assets/theme.css`
  - `nirs4all-ui/assets/brand/nirs4all/**`
  - `nirs4all-ui/assets/brand/quali/**`
- Safe candidate areas for ecosystem/shared-UI work, subject to normal Studio/Web contract review:
  - `nirs4all-ui/site/**`
  - `nirs4all-ui/src/components/**`
  - `nirs4all-ui/src/score/**`
  - `nirs4all-ui/src/runtime/**`
  - `nirs4all-ui/src/dataset/**`
  - root package docs/metadata and the package-level brand kit not used by quality.

## Validation guidance

- Before committing UI work, confirm the diff does not touch reserved paths.
- Run:
  - `cd nirs4all-ui && npm run typecheck && npm test`
  - `cd nirs4all-quality/app && npm run typecheck`

## Risks

- Any change under `src/lab/**` can affect quality even if quality does not directly import that symbol, because the barrel and Tailwind source scan cover the whole directory.
- Token/name changes in `assets/theme.css` can break quality styling even if TypeScript passes.
- `assets/brand/{nirs4all,quali}` can be overwritten by quality's brand generator.
