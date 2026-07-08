# Wave 9L - Custom Host Strict Published Package Gate

## Scope

- Closed the `e2e-core-ui-custom-app-host` strictness gap by adding a downstream Vite/React host build from the published `nirs4all@0.3.3` and `nirs4all-ui@0.1.7` npm packages.
- Promoted the custom-host scenario from `hybrid` to `strict`; suite debt is now `strictness_gaps=10`.
- Left the concurrent `nirs4all-ui` quality work untouched. Shim verification was executed against a clean `/tmp/n4a-clean-ui-origin` checkout to avoid overwriting local UI edits.

## Agents

- Codex main: implemented web smoke artifact output, E2E manifest/validator/test integration, and executed targeted gates.
- Codex explorer `019f3f9a-d37d-71e0-ae71-fe6b49d66958`: read-only audit of custom-host scenario constraints.
- Claude Opus `abc0af72-982d-4f8b-a3ca-2c980f2ce8ab`: read-only legacy alias audit; found no shipped `nirs4all-lite` alias in committed trees.

## Files Changed

- `nirs4all-web/studio-lite/scripts/smoke-published-custom-host.mjs`
- `nirs4all-ecosystem/docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `nirs4all-ecosystem/scripts/n4a_e2e_scenarios.py`
- `nirs4all-ecosystem/tests/test_e2e_scenarios.py`
- `nirs4all-ecosystem/docs/CROSS_LANGUAGE_E2E.md`

## Tests

- `nirs4all-web/studio-lite`: `npm run smoke:published-custom-host`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py coverage`
- `nirs4all-ecosystem`: `python3.11 -m pytest -q tests/test_e2e_scenarios.py` -> `127 passed`
- `nirs4all-ecosystem`: `NIRS4ALL_UI_SHIM_ROOT=/tmp/n4a-clean-ui-origin python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-custom-host-published run e2e-core-ui-custom-app-host --execute`
- `nirs4all-ecosystem`: `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-e2e-custom-host-published evidence --scenario e2e-core-ui-custom-app-host --json` -> `verified_count=1`, `failed_count=0`, `artifact_count=8`

## Decisions

- The published custom-host smoke now writes `published-custom-host.json` when `ARTIFACTS_DIR` is set.
- The new artifact validates package install, public imports only, controller count, `javascript_wasm` predict surface, portable run/predict entrypoints, and a non-empty Vite dist build.
- No full parity suite was launched in this tranche.

## Risks

- Local execution without `NIRS4ALL_UI_SHIM_ROOT` can fail while `nirs4all-ui` contains concurrent dirty work. This is intentional: the committed web vendor shim is still verified against a clean UI checkout.
- The Claude read-only audit surfaced `pls4all` naming residues outside the lite/core alias lane; those were not changed in this wave.
