# Wave 6I - parallel acceleration board

Generated: 2026-07-06T10:25:00Z  
Updated: 2026-07-06T12:23:00+02:00

## Scope

This wave increases parallel review and implementation capacity for the V1
refactor release push. It does not publish packages, move production
`nirs4all` Python, move production `nirs4all-studio`, or run full parity.

The coordinator remains responsible for integration, review, repins, and final
publish decisions. Agents must not touch `nirs4all-drafts`, `nirs4all-lab`, or
root token files.

## Codex agents

Read-only agents inherited from the previous coordination slice:

- `019f36d5-10c6-77e0-9ce4-f61fe15e1bc2` - release/versioning audit across
  non-prod repos.
- `019f36d5-313b-70f0-ab35-706fe1660272` - stale `nirs4all-lite` reference
  audit after the core rename.
- `019f36d5-4df7-7310-9328-ebb1026bc675` - e2e strict-gap audit for repository,
  papers, and WASM/Web phases.

Implementation workers launched with disjoint ownership:

- `019f36d8-103c-7e50-a1d0-342f3e6db852` - `nirs4all-core` only; prepare
  version/package consistency for the current release-candidate head.
- `019f36d8-1210-7761-8c2c-7368e94bb367` - `nirs4all-providers` only; prepare
  version/package consistency for the current release-candidate head.
- `019f36d8-13e0-7d33-a9ba-519e0f2b878b` - `nirs4all-ui` only; verify or
  complete component-page/package readiness, including branding/static assets.

The Codex agent thread limit was reached after these workers were started.
Additional review capacity was therefore moved to Claude Code sessions.

Second acceleration batch:

- `019f36e8-f58a-7f22-aac0-417a7cf527b2` - `nirs4all-org` only; branding and
  site metadata audit for core/UI/providers.
- `019f36e8-f7ca-7fa3-9351-50fd09e0def2` - `nirs4all-cockpit` only; Pages URL
  and topology fixes for the RC roster.
- `019f36e8-fa15-7973-ac17-cbe374910b22` - `nirs4all-ecosystem` contract/tests
  only; semantic guards for cross-language e2e scenarios.
- `019f36e8-fc41-7f22-aa12-e9c9a10480a1` - `nirs4all-studio` only; Windows
  installer RC workflow audit and docs, without production release.
- `019f36e8-fe6a-7ee0-ada2-f6e0f6f89f0e` - read-only release/publish readiness
  audit across non-production repos.

## Active Claude Code sessions

All Claude Code calls were launched with explicit allowed tools to avoid
permission stalls. The sessions are read-only by instruction.

- `eb0356b6-155f-4f34-990c-f1bb5787d700` - Opus/max release publication review
  for non-prod repos, excluding `nirs4all` Python and `nirs4all-studio`.
- `0e58bede-0a45-4083-86ac-1bea80671f28` - Opus/max `nirs4all-org` and
  `nirs4all-cockpit` consistency review.
- `d364005c-b721-446f-b33a-8ec76e3ead5d` - Opus/max cross-language e2e strict
  upgrade review.
- `bf30902a-7d0f-4ad5-9450-bfb92ec967a6` - Fable/max non-prod release,
  cockpit, docs, site, and action gap review.
- `7a9001c3-38dc-446e-b96b-c764a13d0873` - Opus/max parity/e2e coverage and
  skip/xfail risk review.

## Integration rules

- Do not tag, push, or publish from an agent workspace.
- Do not integrate a worker patch before coordinator review and targeted tests.
- Prefer patch-version bumps for distributable runtime/package changes; treat
  docs-only and workflow-only heads separately.
- Keep the release-lock validation path isolated until dirty worktrees are
  audited; do not regenerate the lock from dirty `_worktrees`.
- Keep full parity deferred until a larger batch is integrated.

## Immediate decisions expected

1. Which current heads need real version bumps before publication rather than
   tag-only documentation releases.
2. Whether `nirs4all-core`, `nirs4all-providers`, and `nirs4all-ui` worker
   patches are safe to integrate and repin.
3. Which e2e gaps can be moved from `hybrid` to stricter evidence without
   running the full parity suite yet.
4. Which public pages/cockpit records still overstate production readiness or
   understate the core/UI/providers split.

## Integrated outputs

- Published GitHub releases/tags for `nirs4all-core v0.2.5`,
  `nirs4all-providers v0.2.5`, `nirs4all-ui v0.1.4`,
  `nirs4all-benchmarks v0.1.4`, `nirs4all-repository v0.1.6`,
  `nirs4all-papers v0.2.3`, and `nirs4all-methods v1.0.3`.
- Pushed `nirs4all-web` runtime compatibility for `nirs4all-core/n4a` bundles
  while preserving the legacy `nirs4all-lite/n4a` parser path.
- Repinned the ecosystem `nirs4all-papers` submodule to the published
  `v0.2.3` forced-best-refit evidence commit.
- Hardened ecosystem e2e semantic coverage checks to keep declared languages,
  tags, strict parity checks, and non-gap V1 phases artifact-backed.
- Hardened cockpit Pages URLs and roster coverage for providers/UI/current RC
  pages.

## Validation for this report

- `git diff --check`
- `python3.11 -m pytest tests/test_e2e_scenarios.py -q` in
  `nirs4all-ecosystem` - 73 passed.
- `.venv/bin/python -m pytest -q` in `nirs4all-cockpit` - 104 passed.
- `.venv/bin/python -m ruff check .` in `nirs4all-cockpit` - passed.
- `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml` - 21 packages,
  100 targets.

## Still pending

- Remote Actions from the new tags are still running or queued for several
  package registries.
- PyPI Trusted Publisher setup remains an external blocker where the registry
  project/publisher is not configured.
- Full parity remains deferred until after this batch of published heads and
  dashboard repins settles.
