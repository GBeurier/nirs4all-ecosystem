# Wave 6F - multi-agent release repin and residual gaps

Generated: 2026-07-06T08:49:00Z

## Scope

This wave records the parallel review and integration state after the non-prod
release batch. The production `nirs4all` Python package and production
`nirs4all-studio` line remain intentionally outside the release switch.

## Parallel agents/reviews consumed

- `nirs4all-lite` worker: clarified `AGENTS.md` and `CLAUDE.md` so the checkout
  is explicitly legacy/compatibility-only and publish-disabled.
- `nirs4all-lite` integration follow-up: added a README legacy banner. Current
  pushed head is `1853186`.
- PyPI/release Claude audit: confirmed a single blocker class for the missing
  Python distributions: PyPI pending Trusted Publishers are absent; GitHub
  workflows and `pypi` environments are already OIDC-shaped.
- Core/lite Claude audit: confirmed canonical naming is aligned
  (`nirs4all-core` on Python, `nirs4all` on Rust/npm/R/MATLAB/WASM) and the
  legacy repo is fail-closed for publishing.
- Cross-language E2E Claude + Codex audits: confirmed the 10 scenario manifest
  is coherent and the new artifact freshness gate closes the stale-archive
  hole when `--max-age-seconds` is used.
- UI/web/org Codex audit: confirmed `web.nirs4all.org` is a static client-side
  WASM SPA and `nirs4all-ui` has brand assets plus a GitHub Pages component
  showcase. It also identified that shared UI reuse is partial, not complete:
  Web still carries many local primitives.
- Release/cockpit Claude audit: confirmed cockpit state is current, but the
  ecosystem meta-repo submodule pins lagged the published sibling heads.
- Providers/repository/tools/benchmarks/papers audit: clarified that
  `nirs4all-providers` is a Python convenience client over neutral contracts,
  not the multi-language source of truth; it found ambiguous bridge-extra docs.
- Cockpit target audit: confirmed the CRAN `nirs4allformats` target conflicted
  with the manual policy that says not to submit it to CRAN.

## Integrated changes

The ecosystem submodule pointers were advanced to the current validated sibling
heads for non-prod projects:

- `nirs4all-benchmarks` -> `a7fcd12a89f7`
- `nirs4all-cluster` -> `c0b428248d40`
- `nirs4all-cockpit` -> `3e1ac71b0e4c`
- `nirs4all-datasets` -> `c6275ad0e66c`
- `nirs4all-org` -> `25307a2a449e`
- `nirs4all-papers` -> `b6e521c3fb62`
- `nirs4all-providers` -> `8f15913ab8d9`
- `nirs4all-repository` -> `09ef4c47eec7`
- `nirs4all-ui` -> `456e048c0f4c`
- `nirs4all-web` -> `b64900be5fa5`

The excluded production-sensitive pins were not moved:

- `nirs4all` remains at `7edf60429bd3`
- `nirs4all-studio` remains at `198dff2d6f9f`

## Verification

Fast gates run after the repin:

- `python3 scripts/n4a_e2e_scenarios.py validate`
  - `OK: 10 cross-language E2E scenarios`
- `python3 scripts/n4a_e2e_scenarios.py coverage --json`
  - `scenario_count=10`
  - `ready_count=10`
  - `blocked_count=0`
  - `evidence_levels={"hybrid": 10}`
- `python3 -m pytest -q tests/test_e2e_scenarios.py`
  - `69 passed`
- `git diff --check`

Additional local targeted checks run during review:

- `nirs4all-lite`: `git diff --check` and `scripts/release_guard.py` for both
  `GBeurier/nirs4all-lite` (`allow_publish=false`) and
  `GBeurier/nirs4all-core` (`allow_publish=true`).
- `nirs4all-ui`: `npm test` (`60 passed`), `npm run typecheck`,
  `npm run build`.
- `nirs4all-web/studio-lite`: `npm run test:client-only`, 
  `npm run smoke:shared-ui-contract`, `npm run typecheck`, `npm run build`.
- `nirs4all-providers`: `.venv/bin/ruff check .`, `.venv/bin/mypy src`,
  `.venv/bin/python -m pytest -q`, local sibling release gate, and
  `.venv/bin/twine check dist/*` after rebuilding local `0.2.4` artifacts.
- `nirs4all-cockpit`: `n4a-cockpit validate-targets ops/targets.yaml`,
  `.venv/bin/python -m pytest -q tests/test_targets_topology.py`, and
  `.venv/bin/python -m pytest -q`.

## Current truths

- `nirs4all-core` is the canonical portable aggregate repository.
- Runtime/package publications named `nirs4all` for Rust/npm/R/MATLAB/WASM are
  the core aggregate surfaces, not the full Python modelling package.
- Python keeps the full `nirs4all` package as the reference oracle; the
  aggregate Python distribution is `nirs4all-core`.
- `web.nirs4all.org` is client-side-only for compute/runtime. Its default build
  lazy-loads same-origin static JS/WASM assets; the single-file build is the
  no-extra-asset variant.
- `nirs4all-web` consumes `nirs4all-ui` for shared score/runtime helpers and
  selected React components, but a full Studio/Web primitive extraction into
  `nirs4all-ui` remains incomplete.
- `nirs4all-providers` is a dependency-light Python read layer over datasets,
  repository, benchmarks, and papers. It does not own NIRS runtime, IO,
  parsing, ML, or write-back logic. Its Python package is one client of the
  provider contracts; R/WASM/Rust clients should port the neutral schemas and
  fetch/verify behavior, not depend on this Python package.
- `nirs4all-providers[all]` installs provider backings only. Bridge extras
  owned by those backings remain explicit, for example
  `nirs4all-datasets[nirs4all]` for `DatasetProvider.to_spectro_dataset()`.
- Cockpit now models `cran:nirs4allformats` as `excluded`, matching the manual
  policy that says not to submit that R surface to CRAN.

## Remaining blockers / decisions

1. Register PyPI pending Trusted Publishers for:
   - `nirs4all-core`
   - `nirs4all-providers`
   - `nirs4all-repository`
   - `nirs4all-tools`
   - `nirs4all-benchmarks`
2. Re-run the failed publish jobs after PyPI accepts those claims.
3. Decide whether `nirs4all-cockpit` should remain an internal dashboard only
   or gain its own PyPI workflow.
4. Keep the cross-language E2E gate honest: all 10 scenarios are currently
   `hybrid`, not fully strict. The largest non-strict holes remain
   repository forced-best-refit, papers export, and selected Web/reopen parity
   phases.
5. Plan the next UI extraction batch explicitly: move safe shared primitives
   from Web/Studio into `nirs4all-ui`, then update Web and Studio consumers
   behind targeted contract tests.
6. Finish the heavy parity/e2e artifact execution only after the current
   release topology is accepted and the PyPI first-publish blockers are removed.
