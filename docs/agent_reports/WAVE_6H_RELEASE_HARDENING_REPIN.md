# Wave 6H - release hardening repin

Generated: 2026-07-06T09:55:00Z

## Scope

This wave integrated the latest reviewed release-hardening heads for non-prod
surfaces and updated the ecosystem coordination board. It did not switch
`nirs4all` Python production or `nirs4all-studio` production, and it did not run
full parity.

## Integrated heads

- `nirs4all-benchmarks` `1b5f3f3` - public benchmark upload/release guard, pages
  path filter, repository extra.
- `nirs4all-cluster` `94b1466` - secret-shape remediation guidance and local
  pre-commit secret gates.
- `nirs4all-cockpit` `47bcc41` - core channel marked RC; providers PyPI blocker
  wording refreshed to `v0.2.4`.
- `nirs4all-core` `b0f4f37` - version-sync guard covers Rust, Python surfaces,
  npm lock roots and release topology.
- `nirs4all-org` `349c74c` - Studio wording no longer implies a production
  cutover.
- `nirs4all-papers` `6f2f870` - CI permissions, Pages path filter, runtime
  import/dependency guard, provider write token aligned to `local-output`.
- `nirs4all-providers` `2f84add` - version/tag sync guard wired into CI/release
  gate.
- `nirs4all-repository` `bd41e96` - pickle artifact scans wired through
  scan/validate/build/publish, including `.n4a` pickle members.
- `nirs4all-tools` `389ffc8` - publish workflow refuses tag/version mismatches.
- `nirs4all-ui` `784f343` - GitHub Pages root favicon published from the brand
  kit.

## Ecosystem changes

- Repinned the ten submodule gitlinks above.
- Added `v1_refactor_phase_scenario_ids` to `scripts/n4a_e2e_scenarios.py`
  coverage output so the board exposes the exact scenarios behind each
  `strict` / `contract` / `gap` count.
- Strengthened `tests/test_e2e_scenarios.py` to lock current E2E phase counts and
  known semantic gaps for repository refit, papers export, WASM/Web reuse,
  multisource, dataset-provider, formats/bindings, and cluster lanes.

## Validation run

- `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 10 scenarios.
- `python3 scripts/n4a_e2e_scenarios.py coverage --json` -> ready `10`,
  blocked `0`, evidence `{"hybrid": 10}`.
- `python3 scripts/n4a_e2e_scenarios.py evidence --json --max-age-seconds 604800`
  -> verified `10`, failed `0`, artifacts `43`.
- `python3 -m pytest -q tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_e2e_scenarios.py`
  -> `86 passed`.
- `python3 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-selected-lock validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  -> OK after `checkout-members` from the existing lock.
- `python3 scripts/n4a_release_surface_matrix.py validate` -> OK.

## Release-lock note

The live `_worktrees/RC-v1-dmd` checkout is dirty (`docs/index.md`) and has moved
past the existing clean `dag-ml-data` lock member. The lock was therefore **not**
regenerated from live `_worktrees`; doing so would record a dirty member. The
existing lock validates against an isolated selected-root produced by
`checkout-members`, which is the safe validation path for the current disk state.

## Remaining blockers

- PyPI Trusted Publisher/project claims remain external blockers for
  `nirs4all-core`, `nirs4all-providers`, `nirs4all-repository`,
  `nirs4all-tools`, and `nirs4all-benchmarks`.
- E2E scenarios are still intentionally `hybrid`. Current strict phase counts:
  `python_parity=10`, `papers_export=1`, `repository_forced_best_refit=0`,
  `wasm_web_reuse=3`.
- Full parity, strict repository best-refit execution, strict papers/Web
  handoff, and live provider/catalog dataset roundtrips remain future gates.
