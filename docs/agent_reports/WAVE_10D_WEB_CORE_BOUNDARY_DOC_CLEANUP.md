# WAVE 10D - Web/core boundary doc cleanup

Date: 2026-07-09T07:50:02Z

## Scope

Clarify the active public wording around `nirs4all-web` and the V1 aggregate
target after the no-legacy-alias decision.

## Files changed

- `nirs4all-web/CLAUDE.md`
- `nirs4all-web/README.md`
- `nirs4all-ecosystem/README.md`
- `nirs4all-ecosystem/nirs4all-web` gitlink -> `e06994f`

## Tests / checks

- `rg -n "nirs4all-lite|NIRS4ALL Lite" README.md CLAUDE.md` in
  `nirs4all-web` -> no matches.
- `rg -n "nirs4all-lite|NIRS4ALL Lite" README.md` in `nirs4all-ecosystem`
  -> no matches.
- `git diff --check` in `nirs4all-web` -> pass.
- `git diff --check` in `nirs4all-ecosystem` -> pass.
- `python3.11 -m pytest -q tests/test_gitmodules_topology.py
  tests/test_cutover_state_gate.py` in `nirs4all-ecosystem` -> 7 passed.
- `python3.11 scripts/n4a_e2e_scenarios.py validate` in
  `nirs4all-ecosystem` -> OK, 11 scenarios.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  in `nirs4all-ecosystem` -> 11/11 ready, `full_strict_ready=true`.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_submodule_repin.py plan
  --json` after indexing the Web gitlink -> 20 submodules up to date, 0
  fast-forward remaining, 1 expected `nirs4all` manual review.

## Decisions

- Keep retired-format/session-key rejection tests unchanged: those are negative
  guards, not compatibility aliases.
- Remove active Web README/CLAUDE wording that explained the repo identity
  through the retired aggregate name.
- Keep historical agent reports and changelog entries factual.

## Risks

- Documentation-only change. No runtime parity or Web build rerun was needed for
  this bounded cleanup.
