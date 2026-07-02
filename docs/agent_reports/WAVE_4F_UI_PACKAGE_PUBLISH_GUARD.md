# Wave 4F - nirs4all-ui package publish guard

Date: 2026-07-02  
Coordinator: Codex

## Scope

Small follow-up after Wave 4E. No full Python parity rerun.

## Published code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-ui` | `rc/v1-full-refactor` | `4667ed2` / `n4a-v1-rc1-2026.07-refactor` | `package.json` |

## Change

- Added npm `repository` metadata for `GBeurier/nirs4all-ui`.
- Added `prepack` so `dist/` is rebuilt before `npm pack`.
- Added `prepublishOnly` so typecheck and Vitest must pass before publication.

No public TypeScript or React exports changed.

## Tests and gates

Run in `_worktrees/RC-v1-ui` with Node `/home/delete/.nvm/versions/node/v24.16.0/bin`:

- `npm run typecheck` -> clean.
- `npm test` -> `8 passed`, `50 tests`.
- `npm run build` -> clean.
- `npm run prepublishOnly` -> typecheck + `50 tests` passed.
- `npm pack --dry-run` -> passed; tarball limited to `README.md`, `package.json`, and `dist`.

Worker audit also checked:

- Package import smoke for `nirs4all-ui`, `nirs4all-ui/score`,
  `nirs4all-ui/runtime`, and `nirs4all-ui/components`.
- Studio/Web RC imports remain aligned with the package exports.
- `npm view nirs4all-ui name version --json` returned `E404`, so the package
  name was not visible on the current npm registry at audit time.

## Risks and decisions

- This makes the package more publishable, but it does not decide npm
  publication timing or registry credentials.
- `nirs4all-ui` remains outside the aggregation lock and is tracked as a public
  surface in the release surface matrix.
