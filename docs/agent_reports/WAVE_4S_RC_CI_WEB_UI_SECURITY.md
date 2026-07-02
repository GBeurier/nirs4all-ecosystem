# Wave 4S: RC CI, Web/UI Install, Security Follow-up

Date: 2026-07-02

## Scope

This wave completed the normal `rc/**` CI trigger coverage across the selected
RC repositories, fixed the clean-runner `nirs4all-ui` dependency resolution for
Web and Studio, and recorded the GitGuardian follow-up for `nirs4all-cluster`.

No full Python parity run was launched in this wave.

## Commits

- `nirs4all-benchmarks`: `06d4146 fix(ci): cover rc branches`
- `nirs4all-cluster`: `9d6ab34 fix(ci): cover rc branches`
- `nirs4all-cockpit`: `f06f7b4 fix(ci): cover rc branches`
- `dag-ml`: `a8f6cb3 ci: cover rc branches in workflows`
- `dag-ml-data`: `95e56a7 ci: cover rc branches in workflows`
- `nirs4all-formats`: `32fc87f ci: cover rc branches in workflows`
- `nirs4all-io`: `0d20c80 ci: cover rc branches in workflows`
- `nirs4all-methods`: `d918c5e ci: cover rc branches in workflows`
- `nirs4all-core`: `0a516e2 ci: cover rc branches in workflows`
- `nirs4all-python`: `1fd3f7b ci: cover rc branches in workflows`
- `nirs4all-repository`: `ced219f fix(ci): cover rc branches`
- `nirs4all-papers`: `f1d84f4 fix(ci): cover rc branches`
- `nirs4all-org`: `61074ff fix(ci): cover rc branches`
- `nirs4all-web`: `9652058 fix(studio-lite): vendor nirs4all-ui for clean installs`
- `nirs4all-web`: `c2a6ab2 fix(web): sync ui vendor lock`
- `nirs4all-web`: `cdb43cc ci(web): cover rc version guard`
- `nirs4all-studio`: `4ffe081 fix(ci): vendor nirs4all-ui for clean installs`
- `nirs4all-studio`: `0d8b3cb fix(studio): make ui vendor install deterministic`

All listed repositories were pushed on their selected RC branch and tagged with
`n4a-v1-rc1-2026.07-refactor`.

## Validation

- Workflow YAML parsed successfully in touched repositories.
- `git diff --check` passed for touched repositories.
- Web, with Linux Node `v22.21.1` and a fresh `node_modules`:
  - `npm ci --ignore-scripts`
  - `npm run check:ui-shim`
  - `npm run typecheck`
  - `npm run test:client-only` -> `2 passed`
- Studio, with Linux Node `v22.21.1` and a fresh `node_modules`:
  - `npm ci --ignore-scripts`
  - `npm run check:ui-shim`
  - `npm run lint:tsc`
- Ecosystem:
  - `n4a_release_lock.py validate`
  - `n4a_release_surface_matrix.py validate`
  - `n4a_cutover_gates.py validate`
  - release JSON syntax checks

## Review Decisions

- `nirs4all-ui` is vendored as controlled package files for Web/Studio clean
  installs. `node_modules` and generated tarballs are not tracked.
- Studio uses `.npmrc` with `install-links=true` so npm treats the local
  `file:./vendor/nirs4all-ui` package consistently during `npm ci`.
- Web remains client-side-only. The validation retained the client-only contract
  test and introduced no backend dependency.
- Release/manual/pages/scheduled/long parity workflows were not widened. Long
  parity gates remain reserved for larger integrated batches.

## Risks

- Web `npm ci` reports existing npm audit findings in transitive dependencies
  (`3 moderate`, `1 high`, `1 critical`). This wave did not change the runtime
  dependency policy or run a breaking `npm audit fix --force`.
- R, MATLAB/Octave, Emscripten, and full Studio/Playwright gates were not
  rerun in this wave.
- GitGuardian closure still requires external rescan/support handling if the
  alert continues to reference cached history or hidden PR refs.
