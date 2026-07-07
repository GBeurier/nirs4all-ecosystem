# Wave 7W - E2E debt and cockpit manual actions

Date: 2026-07-07

## Scope

- Protected `nirs4all-ui` and `nirs4all-quality`: not modified; both remain owned by another agent.
- Production-held `nirs4all` Python and `nirs4all-studio`: not released or switched.
- This wave tightened ecosystem E2E reporting, artifact evidence validation, cockpit manual-action coverage, and public provider copy.

## Changes

- `nirs4all-ecosystem`
  - Added `debt_summary` to `scripts/n4a_e2e_scenarios.py coverage`.
  - Coverage now reports strictness gaps, V1 contract/gap phase totals, scenarios without strict parity checks, parity-check evidence levels, and per-scenario phase debt.
  - Evidence validation now checks typed non-JSON artifacts instead of accepting any non-empty file:
    - PNG: signature, IHDR dimensions, IDAT, IEND.
    - ZIP: valid, non-empty archive, no corrupt member.
    - Parquet: leading and trailing `PAR1` magic bytes.
  - Documented that green coverage means coherent executable contracts, not full strict parity.
- `nirs4all-cockpit`
  - Added manual CRAN actions and auto-checks for tracked RC R surfaces:
    - `nirs4allio`
    - `nirs4alldatasets`
    - aggregate `nirs4all` from `nirs4all-core`
  - Added a topology test so those tracked CRAN surfaces cannot remain non-green without a manual action.
- `nirs4all-org`
  - Corrected the public tools page so `nirs4all-providers` is described as datasets + repository only; benchmarks and papers keep their own APIs.

## Agent review inputs

- Codex/Hilbert and Laplace both confirmed PyPI Trusted Publisher blockers remain for the cascade release and that cockpit is honest but not fully green.
- Codex/Plato confirmed the cross-language core/app-host direction exists, while the broader missing contract is a portable controller/capability registry for cross-language UI/runtime composition.
- Codex/Arendt recommended stricter E2E evidence validation; this wave implemented the safe typed-artifact validation and debt summary. Artifact-specific semantic predicates are deferred until producer artifacts can be updated without breaking existing archives.
- Claude Code fable was launched read-only but hit `maxTurns` before a final report; no Claude changes were accepted.

## Validation

- `nirs4all-ecosystem`
  - `python3 -m pytest -q tests/test_e2e_scenarios.py tests/test_release_lock.py` -> 103 passed.
  - `python3 scripts/n4a_e2e_scenarios.py coverage` -> 11/11 ready; debt summary visible.
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> OK.
  - `python3 -m py_compile scripts/n4a_e2e_scenarios.py tests/test_e2e_scenarios.py`.
  - `git diff --check`.
- `nirs4all-cockpit`
  - `PYTHONDONTWRITEBYTECODE=1 n4a-cockpit validate-targets ops/targets.yaml` -> OK, 21 packages, 100 targets.
  - `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q` -> 113 passed.
  - `RUFF_CACHE_DIR=/tmp/n4a-cockpit-ruff-cache ruff check .` -> passed.
  - `git diff --check`.
- `nirs4all-org`
  - `rg` check confirms provider copy now says datasets/repository only.
  - `git diff --check`.

## Remaining blockers

- PyPI Trusted Publishers still need manual setup for several non-prod-held packages before those registry targets can turn green.
- Full parity was not rerun in this wave; per instruction, it remains reserved for larger batches/final selected heads.
- E2E suite remains intentionally hybrid: current coverage reports `strictness_gaps=12`, `v1_contract_phases=13`, `v1_gap_phases=31`, and `e2e-multimodal-python-r-wasm-roundtrip` has no strict parity check yet.
- Live cockpit collection was attempted but exceeded the local wait window and was interrupted before any `data/current.json` write. The current public snapshot was therefore not changed in this wave.
