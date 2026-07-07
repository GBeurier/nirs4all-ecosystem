# Wave 7AT - nirs4all-cluster GitGuardian review

Date: 2026-07-07

## Scope

- Read-only Claude Code review of `nirs4all-cluster` after GitGuardian reported a Generic CLI Option Secret on `GBeurier/nirs4all-cluster`, pushed 2026-07-02 09:41:03 UTC.
- No secret values were printed or copied into this report.
- No files were edited by the reviewer.

## Findings

- The reported shape is consistent with token-like CLI examples in cluster docs/help:
  - `--token <redacted>`
  - `--principal NAME:<redacted-token>:ROLES`
  - `N4CLUSTER_TOKEN=<redacted>`
- Current repository trees are clean: the repo has `scripts/secret_shape_guard.py`, detect-secrets baseline enforcement, pre-commit wiring, and CI secret-scan guardrails.
- The residual issue is git history: the token-shaped examples were introduced before the cleanup and remain reachable through public history/tags even though current trees no longer contain them.
- Likely historical intro/remediation areas:
  - Docs and CLI help around quickstart, operations, CLI reference, REST API, server app, and tests.
  - Cleanup and guardrail commits already replaced literals with metavars/placeholders and added shape guards.

## Recommended remediation

- Treat any token value that was ever used in a real deployment as compromised.
- Rotate cluster shared secrets/principal tokens and restart affected server/worker deployments if the historical literals were ever real.
- Resolve the GitGuardian incident as revoked/rotated, or as false-positive/example only if that is verified.
- Keep CI secret-scan and `secret_shape_guard.py` required.

## History-clean decision

- Current trees and releases are clean, so a history rewrite is a policy decision, not a tree-fix requirement.
- If strict clean-history compliance is required, use a fresh mirror clone and `git filter-repo --replace-text` or BFG, then force-push affected branches/tags and coordinate all downstream clones.
- Rewriting history would disturb release provenance and existing SHA pins; rotation is the primary security control.

## Suggested validation

- `cd nirs4all-cluster && python3 scripts/secret_shape_guard.py`
- `cd nirs4all-cluster && git ls-files -z | xargs -0 uvx --from detect-secrets detect-secrets-hook --baseline .secrets.baseline`
- Optional independent scans after any rewrite: `gitleaks detect --source . --redact -v` and `trufflehog git file://. --only-verified`.

## Risks

- Public clones and old source artifacts can still contain the historical diffs unless history is rewritten.
- If a historical literal was real, closing the alert without rotation would leave the deployment exposed.
