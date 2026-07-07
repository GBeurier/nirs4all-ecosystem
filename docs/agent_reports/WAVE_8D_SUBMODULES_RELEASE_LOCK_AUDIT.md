# Wave 8D - Submodule Pointers and Release Lock Audit

Date: 2026-07-07

## Scope

- Repository: `nirs4all-ecosystem`
- Files changed:
  - submodule pointer `dag-ml`
  - submodule pointer `dag-ml-data`
  - submodule pointer `nirs4all-cockpit`
  - submodule pointer `nirs4all-core`
  - submodule pointer `nirs4all-formats`
  - submodule pointer `nirs4all-io`
  - submodule pointer `nirs4all-org`
  - submodule pointer `nirs4all-providers`
  - submodule pointer `nirs4all-tools`
  - submodule pointer `nirs4all-ui`
  - `docs/agent_reports/WAVE_8D_SUBMODULES_RELEASE_LOCK_AUDIT.md`

## Decision

Updated ecosystem gitlinks for non-prod release/cockpit/site repos that had advanced on canonical sibling `main` checkouts.

The two progressive-production repositories remain outside this submodule refresh:

- `nirs4all`
- `nirs4all-studio`

## Release Lock Validation

The aggregation lock is valid when checked through the selected-member checkout specified by the release-lock tool.

Commands run:

- `rm -rf /tmp/n4a-lock-selected && python3.11 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-lock-selected`
- `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-lock-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json` -> OK
- `python3.11 scripts/n4a_release_lock.py audit-fetchability --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --fail-on-unfetchable` -> 7/7 commits fetchable

Validation against `/home/delete/nirs4all` still reports the lock as stale or inconsistent. This is expected because the live sibling workspace contains post-lock documentation/site/cockpit heads. The tool itself recommends validating against a selected-member checkout unless the lock is intentionally regenerated.

## Remaining External Gaps

- PyPI Trusted Publisher still needs external configuration for affected packages before rerunning failed publish jobs.
- Some R/CRAN/R-universe surfaces remain pending or stale in cockpit status and should stay visible rather than be hidden.
- `nirs4all-methods/bindings/python_nirs4all_methods/pyproject.toml` is still locally generated at `1.0.5` while canonical binding sources are `1.0.6`; workflows regenerate it, but a local reproducibility cleanup remains useful.
