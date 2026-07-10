# WAVE 9ZD — org sync, E2E portability, selected runtime smoke

Date: 2026-07-10

## Coordination

- Main Codex lane fixed public org-site/cockpit drift, regenerated E2E contract evidence metadata, and ran one selected runtime
  smoke.
- Pasteur the 3rd, read-only explorer: audited the current cross-language E2E suite. It confirmed 11 strict/ready scenarios,
  weekly scheduled cluster/core smoke, stale full-suite freshness beyond the smoke, and hardcoded local R/Node paths.
- Halley the 3rd, read-only explorer: audited public packaging/cockpit/org surfaces. It identified stale `nirs4all-org`
  wording for release bundles, `nirs4all-tools`, and `nirs4all-repository`.
- Noether the 4th, read-only explorer: audited current parity skip/xfail status. It confirmed the current parity-only gate is
  `799 passed` with no skips/xfails, and the old `11 xfailed` note belongs to an older full-suite ADR.

## Files/repos changed

- `nirs4all-org`: updated public content to `nirs4all-tools v0.0.5` published on PyPI, `nirs4all-repository v0.1.10`, removed
  leftover "release bundle" wording, removed an incorrect claim that `nirs4all-tools` GitHub Releases carry wheel/sdist
  assets, and bumped sitemap `lastmod`.
- `nirs4all-ecosystem`: advanced the `nirs4all-org` gitlink to `9ea2d94`.
- `nirs4all-cockpit`: removed release-lane wording from the public dashboard tooltips, bumped the static asset cache key to
  `20260710-current-only`, and kept the Manual blockers section at the bottom.
- `nirs4all-ecosystem`: advanced the `nirs4all-cockpit` gitlink to `37bc7a9`.
- `nirs4all-ecosystem`: replaced hardcoded R/Node developer-home paths in
  `docs/contracts/e2e/cross-language-scenarios.n4a.json` with `{r_bin_dir}`, `{node22_bin_dir}`, and `{node24_bin_dir}`.
- `nirs4all-ecosystem`: added runner support for `N4A_R_BIN_DIR`, `N4A_NODE22_BIN_DIR`, and `N4A_NODE24_BIN_DIR`.
- `nirs4all-ecosystem`: regenerated `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json` after the manifest hash changed.

## Validation

- `nirs4all-org`: HTML parser smoke for `index.html` and `open-source-nirs-tools.html`; XML parse for `sitemap.xml`;
  local copy check confirms `nirs4all-tools` no longer claims GitHub wheel/sdist assets; GitHub `version-guard` and Pages
  deployment passed for `9ea2d94`.
- `nirs4all-cockpit`: `pytest -q` passed (`142 passed`); GitHub `ci`, `version-guard`, and Pages deployment passed for
  `37bc7a9`; public `app.js`/`style.css` no longer contain `Release bundles`, `production held`, `bundle-chip`,
  `pkg-channel`, or `tt-reason`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`.
- `nirs4all-ecosystem`: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/test_e2e_scenarios.py
  tests/test_release_lock.py tests/test_release_surface_matrix.py tests/test_gitmodules_topology.py` passed (`160 passed`).
- Local selected runtime smoke: `python3 scripts/n4a_e2e_scenarios.py run e2e-cluster-dag-rights-client-core --execute` passed;
  `evidence --scenario e2e-cluster-dag-rights-client-core --max-age-seconds 14400` verified 4 fresh artifacts.
- GitHub selected runtime smoke: workflow run `29058382700` passed on `main`, executing and verifying
  `e2e-cluster-dag-rights-client-core` and uploading selected runtime evidence.

## Risks/decisions

- The full E2E runtime evidence set is structurally valid but not all artifacts are fresh within four hours; only the selected
  cluster/core smoke was refreshed in this batch.
- The selected manual workflow path still installs the full executed E2E dependency stack before the single selected scenario;
  this is correct but slower than the local smoke path.
- R-universe aggregate `nirs4all` remains externally stale at `0.3.8`; cockpit keeps that action visible.
