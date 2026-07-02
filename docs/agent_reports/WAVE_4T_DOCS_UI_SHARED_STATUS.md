# Wave 4T: Docs Drift and Shared Runtime UI

Date: 2026-07-02

## Scope

This wave integrated two low-risk, non-numerical follow-ups:

- documentation drift cleanup for methods and datasets language/binding claims;
- a larger shared `nirs4all-ui` runtime badge view-model consumed by Studio and
  Web.

A targeted parity probe was attempted in `nirs4all-python`, but it produced only
temporary artifacts and no reviewed code change. Those artifacts were removed.
No full Python parity run was launched in this wave.

## Commits

- `nirs4all-methods`: `6f6a3fa docs(bindings): clarify active methods surfaces`
- `nirs4all-datasets`: `93e9f39 docs(datasets): clarify native acquisition boundary`
- `nirs4all-ui`: `69501bd feat(runtime): share engine badge status rendering`
- `nirs4all-studio`: `f1eba56 refactor(runtime): consume shared engine badge status`
- `nirs4all-web`: `6924da5 chore(web): sync shared ui engine badge`

All touched repositories were pushed on `rc/v1-full-refactor` and retagged with
`n4a-v1-rc1-2026.07-refactor`.

## Validation

- `nirs4all-methods`: `git diff --check`; grep audit for active-binding
  overclaims.
- `nirs4all-datasets`: `git diff --check`; version/source audit against
  `Cargo.toml`, `pyproject.toml`, R DESCRIPTION, and `N4DS_ABI_VERSION`.
- `nirs4all-ui` with Linux Node `v22.21.1`:
  - `npm ci --ignore-scripts`
  - `npm run typecheck`
  - `npm test` -> `52 passed`
  - `npm run build`
  - `npm pack --dry-run`
- `nirs4all-web` with fresh Linux `node_modules`:
  - `npm ci --ignore-scripts`
  - `npm run check:ui-shim`
  - `npm run typecheck`
  - `npm run test:client-only` -> `2 passed`
- `nirs4all-studio` with fresh Linux `node_modules`:
  - `npm ci --ignore-scripts`
  - `npm run check:ui-shim`
  - `npm run lint:tsc`
- Ecosystem pre-report gate:
  - `n4a_release_lock.py audit-fetchability` -> `7/7 member commits checked out`

## Decisions

- Methods docs now present Python, R, MATLAB/Octave, and JS/WASM as the current
  target bindings. Julia, JNI/Android, Go, Rust, .NET, Ruby, Lua, and Nim are
  documented as archived/on-hold PoCs under `bindings/_archive/`.
- Datasets docs now distinguish the Rust acquisition core/C ABI/CLI/bindings
  from the optional Python package and optional `nirs4all` / `nirs4all-io`
  bridges.
- Studio delegates title formatting and fallback/default badge rendering to the
  shared `nirs4all-ui` component. Web already imports the shared component; its
  vendored copy was synchronized.

## Risks

- No runtime parity debt was burned down in this wave. The strict dag-ml
  workspace/session/predict/explain/retrain blockers still need a focused
  implementation batch before a production flip.
- R, MATLAB/Octave, Emscripten, Playwright, and full Studio backend suites were
  not rerun in this wave.
- Web still reports existing npm audit findings during `npm ci`; this wave did
  not change dependency policy or run a breaking `npm audit fix --force`.
