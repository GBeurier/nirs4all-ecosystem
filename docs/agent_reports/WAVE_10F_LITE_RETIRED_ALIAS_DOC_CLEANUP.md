# WAVE 10F - Retired lite alias doc cleanup

Date: 2026-07-09T08:04:00Z

## Scope

Apply the no-legacy-alias policy to the old `nirs4all-lite` checkout so it no
longer promises a final public compatibility alias release.

## Files changed

- `nirs4all-lite/CLAUDE.md`
- `nirs4all-lite/README.md`
- `nirs4all-lite/docs/CORE_RENAME.md`
- `nirs4all-lite/docs/NAMING.md`
- `nirs4all-lite/docs/PUBLISHING.md`

## Tests / checks

- Codex explorer audit identified stale public-alias wording in the retired
  checkout docs.
- `rg -n "final .*alias|thin alias|must keep working|stays installable|Legacy
  compatibility|compatibility line|publish a final|alias wheel"` in the touched
  docs -> no positive alias promises remain; remaining matches are negative
  policy statements or historical rename references.
- `git diff --check` in `nirs4all-lite` -> pass.
- `python3.11 -m pytest -q tests/test_gitmodules_topology.py
  tests/test_cutover_state_gate.py` in `nirs4all-ecosystem` -> 7 passed.
- `python3.11 scripts/n4a_e2e_scenarios.py validate` in
  `nirs4all-ecosystem` -> OK, 11 scenarios.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
  in `nirs4all-ecosystem` -> 11/11 ready, `full_strict_ready=true`.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/n4a_submodule_repin.py plan
  --json` in `nirs4all-ecosystem` -> 20 submodules up to date, 0
  fast-forward remaining, 1 expected `nirs4all` manual review.

## Decisions

- Treat `nirs4all-lite` as audit/validation only.
- Keep existing historical PyPI artifacts non-yanked, but do not document or
  plan a new alias wheel for the RC target.
- Do not change implementation package paths in the retired checkout during
  this docs-only cleanup.

## Risks

- Documentation-only change outside the canonical aggregate repo. No release
  lock or product runtime behavior changed.
