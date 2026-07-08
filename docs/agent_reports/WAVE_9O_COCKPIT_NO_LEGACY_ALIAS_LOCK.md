# Wave 9O — Cockpit No-Legacy-Alias Lock

## Scope

- Apply the user decision that no public `nirs4all-lite` compatibility alias has to
  be kept.
- Keep the production-held Python `nirs4all` line intact while making clear that
  V1 RC release tracking is carried by `nirs4all-core`.
- Preserve the cockpit rule that manual blockers render at the bottom of the
  dashboard.

## Integrated changes

- `nirs4all-cockpit` was advanced to commit `42614d1`, then repinned to
  `7ecf345` after refreshing the Web head metadata and the cockpit roadmap core
  version note.
- The cockpit inventory wording for the held Python `nirs4all` GitHub release
  target now says the production release line is kept intact for existing users,
  not kept as a compatibility alias.
- `data/current.json` was refreshed with the same public wording.
- A topology test now asserts that no live release target named
  `nirs4all-lite` exists anywhere in `ops/targets.yaml`.
- The ecosystem submodule pointer for `nirs4all-cockpit` was repinned to the new
  cockpit head.

## Review

- Codex local review found no active Web/runtime acceptance of
  `nirs4all-lite` persisted formats or session keys. Current Web tests reject
  the retired `.n4a` format and retired backend id.
- Newton the 2nd reviewed the remaining E2E `wasm_web_reuse` contract gaps and
  recommended not promoting any of them to strict without additional true
  Web/WASM numeric evidence. The best next candidate is
  `e2e-pipeline-generation-performance-compare.wasm_web_reuse`, but only after
  the Web smoke compares the selected candidate predictions against Python.

## Tests

- `cd nirs4all-cockpit && python3.11 -m cockpit.cli validate-targets ops/targets.yaml`
- `cd nirs4all-cockpit && python3.11 -m pytest -q tests/test_targets_topology.py`
- `cd nirs4all-cockpit && python3.11 scripts/smoke_dashboard_dom.py`
- `cd nirs4all-ecosystem && python3.11 -m pytest -q tests/test_gitmodules_topology.py tests/test_cutover_state_gate.py tests/test_release_lock.py`

## Risks / decisions

- No runtime compatibility alias was added or preserved.
- Historical docs and rejection tests may still mention `nirs4all-lite`; those
  are acceptable when they describe retired history or assert rejection.
- The remaining four Web reuse phases stay as contract debt until strict numeric
  browser/WASM evidence exists.
