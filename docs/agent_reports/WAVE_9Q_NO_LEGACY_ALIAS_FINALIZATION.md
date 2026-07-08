# Wave 9Q - No Legacy Alias Finalization

Date: 2026-07-08

## Scope

Apply the final naming decision that no public `nirs4all-lite` compatibility
alias is kept for V1. `nirs4all-core` is the canonical aggregate repository and
release surface; the full Python `nirs4all` package remains the production-held
oracle until its explicit cutover.

## Changes

- Updated active roadmap/prompt/debt docs so lanes target `nirs4all-core`, not
  the retired `nirs4all-lite` workstream.
- Marked pre-cutover critical-review statements about `nirs4all-core` being a
  temporary clone as historical/superseded.
- Repinned ecosystem submodules to already-published heads for:
  `nirs4all-core`, `nirs4all-web`, `nirs4all-studio`, and `nirs4all-cockpit`.
- Kept rejection tests that mention `nirs4all-lite` as intentional guards
  against old bundle/session/package/workflow names.

## Reviews

- Codex explorer `Arendt the 2nd` audited active repositories read-only.
  Finding: no active release action, packaging target, cockpit target,
  workflow, or executable surface still publishes or maintains `nirs4all-lite`.
- Codex explorer `Hilbert the 2nd` audited non-package legacy aliases. Finding:
  do not remove technical aliases that preserve Python-oracle parity, Studio/Web
  import compatibility, migration fixtures, SDK compatibility, or methods ABI.

## Tests

- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py`
- `python3.11 scripts/n4a_e2e_scenarios.py validate`

## Risks

- Historical agent reports still mention `nirs4all-lite` because they are
  provenance records. They should not be treated as current topology.
- Public package/release aliases are retired, but technical compatibility
  aliases such as `float_log`, score-column mappings, old prediction fields,
  `submit_run()`, `venv`, Studio `legacyClassPaths`, and methods ABI/catalog
  aliases remain load-bearing until separate parity/ABI migrations replace
  them.
