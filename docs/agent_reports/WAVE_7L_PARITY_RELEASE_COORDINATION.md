# Wave 7L - Python parity, release blockers, and UI-safe coordination

Date: 2026-07-06

## Scope

- Integrated the latest Python parity batch on `GBeurier/nirs4all` without releasing the Python production package.
- Reconciled the ecosystem E2E scenario count/status after the semantic-hardening pass.
- Refreshed the cockpit PyPI blocker text for the current `nirs4all-core` release attempt.
- Audited Web/Studio/UI relationships without editing `nirs4all-ui`, which has concurrent work for `nirs4all-quality`.
- Rechecked the `nirs4all-cluster` GitGuardian signal against the current tree and reachable history.

## Integrated heads

- `nirs4all` branch `refactor/L17-pyref`
  - `95e81280202488a0b7f9504a0b1baffde65a38f4` - `fix(parity): close dagml conformance gaps`
  - `471398be` - `docs(parity): pin dagml conformance ledger`
- `nirs4all-cockpit` main
  - `49da6da` - `docs(targets): refresh core PyPI publisher blocker`
- `nirs4all-ecosystem` main
  - `3876ca8` - `test(e2e): harden cross-language scenario contracts`

## Validation

- `nirs4all`
  - Full parity: `PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3.11 -m pytest -q tests/integration/parity -p no:cacheprovider`
  - Result: `799 passed, 0 skipped, 0 xfailed, 1858 warnings in 2043.75s`
  - Focused ledger: `tests/integration/parity/test_compatibility_ledger.py` -> `2 passed`
- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> `OK: 11 cross-language E2E scenarios`
  - `python3 -m pytest -q tests/test_e2e_scenarios.py -p no:cacheprovider` -> `86 passed`
  - `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> `11 ready`, `0 blocked`
- `nirs4all-cockpit`
  - `python3 -m pytest -q tests/test_targets_topology.py -p no:cacheprovider` -> `13 passed`
  - `python3 -m cockpit.cli validate-targets ops/targets.yaml` -> `OK: 21 packages, 100 targets`
- `nirs4all-web/studio-lite`
  - `npm run test:client-only` -> `2 passed`
  - `npm run smoke:shared-ui-contract` -> `3 passed`
  - `npm run smoke:custom-app-host` -> `1 passed`
  - `npm run typecheck` -> pass
  - `npm run test` -> `144 passed`
  - `npm run validate:catalog` -> `64 symbols referenced`, `702 exported upstream`, catalog/studio registry sync
  - `npm run build` -> pass with existing Vite warnings for browser-externalized `node:module` and large chunks
  - `npm run build:single` -> pass with the same browser-externalization warning
- `nirs4all-cluster`
  - `python3 scripts/secret_shape_guard.py` -> pass

## Decisions

- Python `nirs4all` remains held on the refactor branch. It is parity-green but not tagged/promoted to production in this batch.
- `nirs4all-studio` remains held for production. The local Windows RC builder is prepared; native Windows execution is still a manual validation step.
- `nirs4all-ui` was not modified. The current main checkout is dirty due to concurrent quality/UI work and must not be overwritten by this batch.
- `web.nirs4all.org` is still client-side-only by static contract tests and Pages deployment shape, but Web and Studio are not yet fully converged onto `nirs4all-ui`.
- Studio package/runtime tests that consume `file:../nirs4all-ui` were not re-run in this batch because the sibling UI checkout is intentionally dirty from concurrent `nirs4all-quality` work.
- `nirs4all-core` is the canonical aggregate. Non-Python surfaces publish as `nirs4all`; the Python aggregate uses `nirs4all-core` because the full Python `nirs4all` package owns the bare name.

## Release state

- Confirmed live:
  - `nirs4all-core` GitHub release `v0.2.7`
  - npm `nirs4all@0.2.7`
  - crates.io `nirs4all = 0.2.7`
  - `nirs4all-providers` GitHub release `v0.2.5`
- Blocked by external PyPI Trusted Publisher configuration:
  - PyPI `nirs4all-core`: latest run `release-python` on tag `v0.2.7` fails with `invalid-publisher` for `repo:GBeurier/nirs4all-core:environment:pypi`.
  - PyPI `nirs4all-providers`: latest release run on tag `v0.2.5` fails with `invalid-publisher` for `repo:GBeurier/nirs4all-providers:environment:pypi`.

## Security note

The current `nirs4all-cluster` tree is clean under its custom secret-shape guard and has no current literal token finding from the audit. Reachable historical commits still contain token-shaped examples such as `s3cr3t` / `example-token`; this matches a documentation/example pattern, not a high-entropy production credential, but can keep GitGuardian alerts alive until the alert is marked false-positive/resolved or history is purged.

## Risks

- The Python parity suite is green with no skips/xfails, but warnings remain and should not be confused with zero-warning release quality.
- The cross-language E2E suite is ready and semantically hardened, but its evidence level is still hybrid; only 10 of 11 scenarios are parity-tagged and the multimodal proxy is contract-level evidence, not strict numeric parity.
- Web/Studio custom-app-host convergence still needs more real component extraction into `nirs4all-ui`; current shared UI coverage is partial.
- PyPI publication cannot be completed by rerunning GitHub workflows alone until the PyPI Trusted Publisher entries exist.
