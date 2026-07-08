# WAVE 10T - E2E Ledger Stable Proofs

Date: 2026-07-09

## Scope

Stabilize the committed runtime evidence ledger before triggering long
`execute=true` full-suite E2E runs.

## Files Modified

- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `docs/CROSS_LANGUAGE_E2E.md`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `docs/agent_reports/WAVE_10R_E2E_RUNTIME_EVIDENCE_LEDGER.md`
- `docs/agent_reports/WAVE_10T_E2E_LEDGER_STABLE_PROOFS.md`

## Decision

Do not hash complete runtime artifact files in the committed ledger. Several
artifacts legitimately contain absolute paths, timestamps, elapsed durations, or
timestamped native result directories. Full-file hashes would drift between CI
hosts even when the parity evidence remains valid.

The ledger now records:

- normalized artifact paths;
- `proof_kind` for each artifact;
- `proof_sha256` only for JSON artifacts with explicit scenario requirements;
- `requirement_count` so the proof cannot silently drop contract fields.

The proof hash is computed from the required JSON evidence fields and the
resolved comparison/tolerance fields, not from host-specific metadata.

## Risks / Follow-Up

- The ledger remains a summary of a verified full run. It is not a replacement
  for executing the full scenarios after large runtime batches.
- After this lands, trigger the manual full-suite E2E only when a long parity
  run is acceptable.
