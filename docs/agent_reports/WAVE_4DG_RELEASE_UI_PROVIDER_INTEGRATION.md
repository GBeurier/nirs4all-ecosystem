# Wave 4DG — Release/UI/Provider integration

Date: 2026-07-04

## Integrated heads

- `nirs4all-core@43e1768` — release workflows/docs now target the canonical `nirs4all-core` repository and guard the PyPI Trusted Publisher tuple.
- `nirs4all-lite@6a50785` — legacy repository release workflows now resolve a central publish guard and can only build/dry-run, not publish canonical artifacts.
- `nirs4all-ui@6f9cec9` — shared React component package exports runtime status, diagnostics, and metric badges; Pages showcase now targets `ui.nirs4all.org`.
- `nirs4all-org@0da1103` — public site links the UI component showcase through `https://ui.nirs4all.org/`.
- `nirs4all-providers@383865c` — governance, security, citation, and full dual-license texts are present and tested.
- `nirs4all-papers@315118f` — CI installs the repository handoff provider before running the strict paper/repository handoff test.

## Tests and checks

- `nirs4all-core`: GitHub CI and `version-guard` passed for `43e1768`.
- `nirs4all-lite`: local `PYTHONPATH=bindings/python/src python3 -m unittest discover -s bindings/python/tests` passed (`56 tests, 1 skipped`); release guard verified `allow_publish=false` for `GBeurier/nirs4all-lite` and `allow_publish=true` only for `GBeurier/nirs4all-core`.
- `nirs4all-ui`: `npm run ci`, `npm run site:build`, and Chrome DevTools mobile overflow check passed (`scrollWidth == clientWidth == 390`); GitHub CI and Pages passed for `6f9cec9`.
- `nirs4all-org`: GitHub Pages and `version-guard` passed for `0da1103`.
- `nirs4all-providers`: `python3.11 scripts/ci_gate.py`, `python3.11 -m build`, `python3.11 -m twine check dist/*`, and `PYTHONPATH=src python3.11 -m pytest -q tests/test_repository_health.py` passed.
- `nirs4all-papers`: GitHub CI, content check, and `version-guard` passed for `315118f`; GitHub Pages deployment failed after artifact creation with a platform-side “try again later” message and was rerun.
- `nirs4all-ecosystem`: `python3 scripts/n4a_e2e_scenarios.py validate` and `python3 -m pytest -q tests/test_e2e_scenarios.py` passed (`32 passed`).

## Risks and decisions

- The PyPI project/Trusted Publisher for `nirs4all-core` still requires external PyPI configuration; the local guard only prevents wrong-repo publication.
- `nirs4all-lite` remains a legacy repository until the GitHub rename/cutover is complete, but its release workflows are now protected from publishing canonical artifacts.
- `ui.nirs4all.org` requires DNS/GitHub Pages domain configuration outside the repository, but the repo carries `CNAME`, canonical URLs, robots, sitemap, and manifest.
- `nirs4all-papers` Pages failure is not a build/test failure; it occurred in `actions/deploy-pages` after the deployment was created.
