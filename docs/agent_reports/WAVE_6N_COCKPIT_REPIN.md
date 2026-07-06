# Wave 6N - Cockpit refresh and ecosystem repin

Date: 2026-07-06

## Scope

- Stabilize `nirs4all-cockpit` after a flaky public refresh.
- Refresh the cockpit snapshot without losing public GitHub source, workflow,
  repository, or actions facts when GitHub API calls fail or time out.
- Repin `nirs4all-ecosystem` to the new `nirs4all-cockpit`, `nirs4all-core`,
  `nirs4all-ui`, and `nirs4all-org` heads.

## Commits

- `nirs4all-cockpit`:
  `ba8c1ed fix(collect): preserve public GitHub facts on flaky refresh`
- `nirs4all-ecosystem`:
  `3a0afa7 chore(release): repin cockpit core ui and org`
- Upstream heads included by the repin:
  - `nirs4all-cockpit` `ba8c1ed`
  - `nirs4all-core` `635b929`
  - `nirs4all-ui` `61f1f23`
  - `nirs4all-org` `198b911`

## Tests run

`nirs4all-cockpit`:

- `.venv/bin/python -m pytest -q` -> `107 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `.venv/bin/n4a-cockpit validate-targets ops/targets.yaml` -> passed,
  `21 packages`, `100 targets`
- Snapshot audit: no loss of prior `source.latest_prod_tag`, `source.commit`,
  `repo_stats.stars`, `repo_stats.default_branch`, `actions_stats.total_runs`,
  or workflow conclusions.

`nirs4all-ecosystem`:

- `python3 scripts/n4a_submodule_repin.py plan --json` -> protected
  `aggregation-lock.n4a.lock.json` clean
- `python3 -m pytest tests/test_submodule_repin_plan.py tests/test_gitmodules_topology.py tests/test_release_lock.py tests/test_e2e_scenarios.py -q`
  -> `92 passed`

## Decisions

- The cockpit now carries forward public GitHub facts when a refresh loses them
  transiently.
- If a package manifest changed and GitHub is unavailable, the cockpit may fill
  source facts from a matching local sibling git tag. It does not invent tags:
  no local tag means the source fact remains unresolved.
- Full parity was not launched in this wave; this was a release/topology/cockpit
  batch.

## Risks

- The current sandbox lost DNS/API access to GitHub after the pushes. Local git
  pushes completed before the outage, but post-push GitHub Actions checks for
  the final cockpit and ecosystem commits could not be re-read from `gh` in this
  environment.
- The repin plan reports the four new submodule heads as `ahead_of_remote`
  because its local remote refs were not fetchable under the network outage.
  This is a verification limitation, not a protected-lock modification.
- `nirs4all-core` and `nirs4all-ui` are one commit ahead of their `v0.2.5` /
  `v0.1.4` release tags because the new commits are documentation/test hardening
  after the release cut.
