# Wave 5X - UI package contract smokes

Date: 2026-07-04

## Scope

- `nirs4all-ui`: package-owned packed-consumer smoke for React 18 and React 19.
- `nirs4all-studio`: CI smoke proving Studio can consume the installed `nirs4all-ui` package exports, not only sibling source aliases.
- `nirs4all-ecosystem`: submodule pointer coordination only.

## Integrated heads

- `nirs4all-ui`: `c0ae3e9` (`test(package): smoke react consumer compatibility`)
- `nirs4all-studio`: `198dff2` (`test(ui): smoke installed nirs4all-ui package`)

## Review decisions

- `nirs4all-ui` owns React 18/19 compatibility because its peer range is `react >=18 <20`.
- Studio still uses source aliases for normal local/CI app builds, but now has a separate `smoke:nirs4all-ui-package` gate that removes those aliases and imports the installed package/subpath exports.
- Studio CI packs `nirs4all-ui` from the checked-out library, installs that tarball into Studio, and runs the package smoke before the normal frontend checks.
- No Studio release/tag was created; this is a source/CI hardening commit only.

## Tests run

- `nirs4all-ui`: `npm run ci` with Node 24.16.0 passed.
  - Includes `typecheck`, `vitest` (12 files / 59 tests), `build`, `npm pack --dry-run`, and `smoke:react-consumers`.
  - `smoke:react-consumers` passed for React 18 and React 19 packed consumers.
- `nirs4all-studio`: `npm run smoke:nirs4all-ui-package` passed.
- `nirs4all-studio`: `npm run lint:tsc` passed.
- `nirs4all-studio`: `npm run test:frontend` passed (516 files / 3695 passed / 1 skipped).
- `nirs4all-studio`: `npm run build` passed.
- `nirs4all-studio`: `npm run build:electron` passed.
- `nirs4all-studio`: `npm run lint:eslint` passed.

## Risks / follow-up

- The UI packed-consumer smoke needs npm registry access to install temporary React/TypeScript consumer dependencies.
- Studio GitHub CI and Playwright checks for `198dff2` were still running when this report was written.
- No full parity suite was run in this wave; deferred to the next large integration batch.
