# Wave 6U - Cluster Secret Alert Audit

Date: 2026-07-06

## Scope

- Repo: `nirs4all-cluster`
- Mode: read-only audit
- Trigger: GitGuardian reported a Generic CLI Option Secret on `GBeurier/nirs4all-cluster`, pushed
  on 2026-07-02 at 09:41:03 UTC.

## Result

No operational raw secret was found in the current working tree. The repository is clean locally.
The alert is most likely a false positive on historical CLI examples that used `--token` with a
shell variable or placeholder rather than an embedded token value.

## Suspect Areas

- Historical examples and help text using `--token` placeholders or shell variables.
- Historical `docs/operations.md` snippets using `N4CLUSTER_TOKEN=<placeholder>`.
- `.secrets.baseline` entries for high-entropy fixture/example strings; no raw value was copied into
  this report.

## Current Guards

- `scripts/secret_shape_guard.py` is present.
- CI runs secret detection and the shape guard.
- Release workflow uses OIDC/Trusted Publisher style configuration rather than a committed PyPI
  token.

## Decision

Mark the GitGuardian alert as false positive if the UI shows the same placeholder/variable shape.
No token revocation is required based on this local audit. Do not rewrite history unless reducing
scanner noise is worth the coordination cost.
