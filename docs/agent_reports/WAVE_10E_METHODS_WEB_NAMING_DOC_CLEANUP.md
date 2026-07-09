# WAVE 10E - Methods Web/WASM naming doc cleanup

Date: 2026-07-09T07:56:20Z

## Scope

Apply the no-legacy-alias naming policy to active `nirs4all-methods` Web/WASM
backlog docs.

## Files changed

- `nirs4all-methods/docs/STUDIO_LITE_WASM_GAPS.md`
- `nirs4all-methods/docs/dev/RELEASE_READINESS.md`
- `nirs4all-ecosystem/nirs4all-methods` gitlink -> `f99c78a6`

## Tests / checks

- Codex explorer audit found these two `nirs4all-methods` docs as active stale
  references; no code edits were made by the explorer.
- `rg -n "nirs4all-lite|NIRS4ALL Lite"
  docs/STUDIO_LITE_WASM_GAPS.md docs/dev/RELEASE_READINESS.md` in
  `nirs4all-methods` -> no matches.
- `git diff --check` in `nirs4all-methods` -> pass.
- `python3.11 -m pytest -q tests/test_gitmodules_topology.py
  tests/test_cutover_state_gate.py` in `nirs4all-ecosystem` -> 7 passed.
- `python3.11 scripts/n4a_e2e_scenarios.py validate` in
  `nirs4all-ecosystem` -> OK, 11 scenarios.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  in `nirs4all-ecosystem` -> 11/11 ready, `full_strict_ready=true`.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_submodule_repin.py plan
  --json` after indexing the Methods gitlink -> 20 submodules up to date, 0
  fast-forward remaining, 1 expected `nirs4all` manual review.

## Decisions

- Replace retired aggregate repo wording with `nirs4all-web/studio-lite` for
  the browser app and `nirs4all-core` for aggregate/runtime consumers.
- Keep the technical backlog unchanged; this is naming/topology cleanup only.

## Risks

- Documentation-only change. No native build or parity run was triggered for
  this bounded cleanup.
