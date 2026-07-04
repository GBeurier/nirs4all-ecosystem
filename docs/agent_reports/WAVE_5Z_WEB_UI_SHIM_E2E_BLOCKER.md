# Wave 5Z - Web UI shim E2E blocker

Date: 2026-07-04

## Scope

- `nirs4all-web`: refresh vendored `nirs4all-ui` metadata after `nirs4all-ui` added the React 18/19 packed-consumer smoke.
- `nirs4all-ecosystem`: submodule pointer coordination.

## Reason

`python3 scripts/n4a_e2e_scenarios.py --artifacts-dir .n4a-e2e-artifacts/wave5y run-ready --execute`
started the 10-scenario E2E batch and passed:

- `e2e-r-dataset-io-pipeline-save`
- `e2e-python-reopen-paper-repository-refit.python-reopen-rerun`
- `e2e-python-reopen-paper-repository-refit.papers-export-repository-refit`

It then failed at the first Web step because `npm run check:ui-shim` detected vendored `nirs4all-ui` drift in `nirs4all-web/studio-lite`.

## Integrated head

- `nirs4all-web`: `591e312` (`chore(ui): refresh vendored shared ui metadata`)

## Tests run

- `nirs4all-web/studio-lite`: `npm run check:ui-shim` passed.
- `nirs4all-web/studio-lite`: `npm run smoke:shared-ui-contract` passed.
- `nirs4all-web/studio-lite`: `npm run build` passed.

## Follow-up

- Rerun the E2E batch after this pointer lands in ecosystem.
