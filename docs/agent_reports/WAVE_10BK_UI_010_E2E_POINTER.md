# Wave 10BK — nirs4all-ui 0.1.10 published package pointer

Date: 2026-07-09

## Scope

- Updated the custom-host E2E scenario to install the newly published `nirs4all-ui@0.1.10`.
- Regenerated the committed runtime evidence ledger metadata so contract tests track the new manifest hash.
- Did not re-run the full runtime E2E batch; that remains deferred until the next large parity batch.

## Files changed

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Tests run

- `python3 scripts/n4a_e2e_scenarios.py validate`
- `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `python3 -m pytest -q tests/test_e2e_scenarios.py` → 135 passed

## Decisions

- Keep the scenario on the current published UI package (`0.1.10`) so the next runtime dispatch validates the package actually shipped to npm.
- Keep the ledger as normalized existing-evidence metadata only; freshness is intentionally not claimed after this pointer update.

## Risks / follow-up

- The runtime artifacts behind `latest-runtime-evidence-ledger.n4a.json` predate the `0.1.10` pointer update.
- Run the full cross-language E2E workflow with `execute=true` after the next release batch, then refresh the ledger with a `--max-age-seconds` gate.
