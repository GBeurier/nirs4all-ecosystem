# WAVE 10R - E2E Runtime Evidence Ledger

Date: 2026-07-09

## Scope

Make the cross-language E2E runtime evidence durable without committing the
large generated artifact tree.

The runtime artifacts stay local/CI-only under `.n4a-e2e-artifacts/`, but the
repository now tracks a normalized evidence ledger:

- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`

## Files Modified

- `scripts/n4a_e2e_scenarios.py`
- `tests/test_e2e_scenarios.py`
- `.github/workflows/cross-language-e2e.yml`
- `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `docs/agent_reports/WAVE_10R_E2E_RUNTIME_EVIDENCE_LEDGER.md`

## Decision

Add `python3 scripts/n4a_e2e_scenarios.py evidence-ledger` as the canonical
command for writing a portable runtime evidence snapshot.

The ledger records:

- the canonical E2E manifest schema and source path;
- the canonical E2E manifest SHA-256;
- full-strict coverage counters;
- required language and tag coverage;
- V1 refactor phase status counts;
- verified scenario count, artifact count, and failure count;
- per-scenario normalized artifact inventory, verified artifact SHA-256 values,
  and strict parity metadata.

It intentionally does not record absolute paths, timestamps, or full artifact
payloads, so it can be reviewed and regenerated without noisy churn.

`--check` compares a regenerated ledger with the tracked ledger and exits
non-zero on drift; it is intended for full executed E2E batches, not for a fresh
checkout with no `.n4a-e2e-artifacts/` tree.

The Cross-language E2E GitHub workflow now runs this check only for the full
manual `execute=true` path after artifact verification.

## Tests And Gates

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --out /tmp/n4a-latest-runtime-evidence-ledger.n4a.json`
- `python3.11 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_e2e_scenarios.py -k 'runtime_evidence_ledger or evidence_ledger_fails'` -> `2 passed`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_gitmodules_topology.py tests/test_e2e_scenarios.py` -> `133 passed`
- `python3.11 scripts/n4a_release_surface_matrix.py validate`
- `git diff --check`

## Current Evidence

- `11/11` scenarios ready.
- Full strict gate: pass.
- Runtime evidence: `11/11` scenarios verified.
- Runtime artifact inventory: `70` expected artifacts.
- Runtime evidence failures: `0`.

## Risks / Follow-Up

- The ledger is a durable summary of the last verified runtime evidence, not a
replacement for executing the full scenarios after large runtime batches.
- Full artifact payloads remain in CI artifacts or local `.n4a-e2e-artifacts/`
because committing screenshots, CSVs, parquet files, archives, and workspaces
would create unnecessary repository churn.
