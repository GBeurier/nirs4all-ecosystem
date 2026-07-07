# Wave 7J - cockpit and org topology copy

Date: 2026-07-06

## Scope

Aligned `nirs4all-cockpit` and `nirs4all-org` copy with the V1 RC topology:
`nirs4all-core` as canonical aggregate, `nirs4all-lite` as a retired historical
name rather than a release alias, `nirs4all-ui` as reusable components/assets
package, and
`nirs4all-providers` as read-side provider clients.

## Files modified

- `nirs4all-cockpit/README.md`
- `nirs4all-cockpit/ROADMAP.md`
- `nirs4all-cockpit/ops/targets.yaml`
- `nirs4all-cockpit/data/current.json`
- `nirs4all-cockpit/tests/test_targets_topology.py`
- `nirs4all-org/README.md`
- `nirs4all-org/index.html`
- `nirs4all-org/open-source-nirs-tools.html`

## Decisions

- `nirs4all-providers` is described as read-side/client/provider metadata, not a
  runtime core or write-back layer.
- `nirs4all-ui` is described as reusable UI components, status helpers, score
  helpers, view-model helpers, and brand assets.
- `nirs4all-core` public fallback copy was updated to `v0.2.7 RC`.
- Production `nirs4all` Python and `nirs4all-studio` were not changed.

## Validation

- `./.venv/bin/python -m cockpit.cli validate-targets ops/targets.yaml`
- `./.venv/bin/pytest -q tests/test_targets_topology.py` -> 13 passed.
- `./.venv/bin/ruff check .` -> OK.
- Agent-side full cockpit run: `./.venv/bin/pytest -q` -> 107 passed.

## Risks

- `nirs4all-org` is static HTML and has no local automated test suite.
- The cockpit live network collection was not regenerated; `data/current.json`
  received only targeted copy updates.
