# WAVE 10BD - Actions and web wording sweep

Date: 2026-07-09T18:59:31Z

Lane: workflow hygiene + public lite-to-web wording cleanup

## Summary

- Modernized a non-prod batch of GitHub Actions workflows outside the held
  Python `nirs4all` and `nirs4all-studio` production surfaces.
- Kept changes scoped to workflow versions and documentation/comment wording;
  no runtime, numerical, converter, prediction, pipeline, or binding behavior
  changed.
- Cleaned remaining public-ish `studio-lite` wording in the custom-host/web
  surface where `nirs4all-web` is the intended product name. Literal
  `studio-lite/` path references remain where they identify the current source
  directory.
- Confirmed the current E2E contract state remains 11 strict cross-language
  scenarios with 11 ready, 0 blocked, and no manifest-level strictness gaps.

## Repositories touched

Workflow hygiene:

- `nirs4all-web`
  - Commit `6963358` (`ci(actions): modernize web workflows`)
- `nirs4all-repository`
  - Commit `962d35f` (`ci(actions): modernize repository workflows`)
- `nirs4all-tools`
  - Commit `3ad7e83` (`ci(actions): modernize tools workflows`)
- `nirs4all-cluster`
  - Commit `4b06d7f` (`ci(actions): modernize cluster workflows`)
- `nirs4all-benchmarks`
  - Commit `43a5260` (`ci(actions): modernize benchmarks workflows`)

Public wording cleanup:

- `nirs4all-web`
  - Commit `822cea8` (`docs(web): align public app wording`)
- `nirs4all-benchmarks`
  - Commit `0af2916` (`docs(design): rename web producer capsule`)
- `nirs4all-methods`
  - Commit `fe2e050f` (`docs(js): reference nirs4all web catalog`)
- `nirs4all-papers`
  - Commit `201f123` (`docs(cli): generalize web wasm bundle wording`)

## Files modified

Workflow hygiene:

- `nirs4all-web/.github/workflows/deploy-pages.yml`
- `nirs4all-web/.github/workflows/version-guard.yml`
- `nirs4all-web/.github/workflows/web-ci.yml`
- `nirs4all-repository/.github/workflows/*.yml`
- `nirs4all-tools/.github/workflows/*.yml`
- `nirs4all-cluster/.github/workflows/*.yml`
- `nirs4all-benchmarks/.github/workflows/*.yml`

Public wording cleanup:

- `nirs4all-web/README.md`
- `nirs4all-web/.github/workflows/deploy-pages.yml`
- `nirs4all-web/.github/workflows/web-ci.yml`
- `nirs4all-web/studio-lite/examples/custom-app-host/README.md`
- `nirs4all-web/studio-lite/src/engine/wasm/methods/model.js`
- `nirs4all-web/studio-lite/src/engine/wasm/methods/model.d.ts`
- `nirs4all-benchmarks/DESIGN.md`
- `nirs4all-methods/bindings/js/src/model.ts`
- `nirs4all-papers/src/nirs4all_papers/cli.py`
- `nirs4all-papers/src/nirs4all_papers/site/__init__.py`

## Validation

Local:

- Workflow batch:
  - `git diff --check` across `nirs4all-web`, `nirs4all-repository`,
    `nirs4all-tools`, `nirs4all-cluster`, and `nirs4all-benchmarks` -> OK.
  - YAML parse check across the same workflows -> OK.
  - Search for old first-party action versions in the batch -> no matches for
    `checkout@v4`, `setup-node@v4`, `setup-python@v5`, `upload-artifact@v4`,
    `download-artifact@v4`, `upload-pages-artifact@v3`, `deploy-pages@v4`,
    `configure-pages@v5`, or Node 20 workflow pins.
- E2E contract:
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> 11 scenarios OK.
  - `python3 scripts/n4a_e2e_scenarios.py coverage --require-full-strict` ->
    11/11 ready, blocked 0, strictness gaps 0.
  - `python3 scripts/n4a_release_surface_matrix.py validate` -> OK.
  - `python3 scripts/n4a_release_lock.py validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
    -> OK.
- Wording cleanup:
  - `nirs4all-web/studio-lite`: `npm run test:client-only` -> 2 passed.
  - `nirs4all-web/studio-lite`: `npm run typecheck` -> OK.
  - `nirs4all-papers`: `python3 -m pytest -q` -> 50 passed, 2 skipped.
  - `nirs4all-benchmarks`: wording assertion -> OK.
  - `nirs4all-methods`: JS doc wording assertion -> OK.

GitHub:

- `nirs4all-web`:
  - `version-guard`, `web-ci`, and `Deploy nirs4all-web to GitHub Pages` ->
    success on `6963358` and `822cea8`.
- `nirs4all-repository`:
  - `CI`, `docs`, `CodeQL`, `Deploy catalogue site to GitHub Pages`,
    `version-guard`, and follow-up GitHub Actions update checks -> success on
    `962d35f`.
- `nirs4all-tools`:
  - `CI`, `version-guard`, and follow-up GitHub Actions update check -> success
    on `3ad7e83`.
- `nirs4all-cluster`:
  - `CI`, `version-guard`, and follow-up GitHub Actions update check -> success
    on `4b06d7f`.
- `nirs4all-benchmarks`:
  - `CI`, `pages`, `version-guard`, and follow-up GitHub Actions update check
    -> success on `43a5260`.
  - `CI` and `version-guard` -> success on `0af2916`.
- `nirs4all-methods`:
  - `version-guard`, `Coverage`, `version-sync`, `Sanitizers`, `docs`,
    `Cross-binding parity`, `ABI Surface`, `Parity gate`, and `CI` -> success
    on `fe2e050f`.
- `nirs4all-papers`:
  - `version-guard`, `CI`, `Content Check`, and `Site (GitHub Pages)` ->
    success on `201f123`.

## Parallel audit findings

- Cockpit/publication audit: public cockpit snapshot is coherent (`96 green`,
  `4 pending`, `1 stale`, `0 missing/broken`) and byte-identical to the public
  JSON. Remaining items are manual/external: Studio Windows RC smoke, CRAN
  submissions/resubmissions, Search Console credentials, and Studio Sentry
  triage before any production switch.
- E2E audit: current ecosystem state has 11 strict cross-language scenarios,
  71 verified runtime artifacts in the committed ledger, 11 ready, 0 blocked,
  and broad Python/R/WASM/Web coverage across datasets, IO, pipelines,
  repository, papers, predictions, workspace save, multimodal and multisource
  tags.
- Lite-to-core/custom-host audit: `nirs4all-core` is the canonical aggregate
  repo, `nirs4all-ui` is a reusable package with assets and GitHub Pages, and
  `.gitmodules` no longer tracks `nirs4all-lite`. Public wording gaps around
  `studio-lite` were reduced in this wave.

## Decisions

- Do not touch Python `nirs4all` production or `nirs4all-studio` production in
  this wave.
- Do not rename the `studio-lite/` directory/package in this wave; path
  references remain when they identify the current source tree.
- Do not run full Python parity here; the changes were workflows and
  documentation/comments. GitHub did run the `nirs4all-methods` parity/ABI gates
  because that repository's workflows trigger broadly on pushes.
- Do not edit `nirs4all-quality` in this wave; remaining references there are
  low-severity wording and quality work had recently been integrated by another
  agent.

## Remaining risks / blockers

- Studio Windows RC smoke remains a manual Windows-side gate.
- CRAN submissions/resubmissions remain manual/external for the R surfaces.
- Search Console credentials are still absent from cockpit collection.
- Studio Sentry unresolved issues remain a production-hold monitoring item.
- Broader workflow modernization debt may remain in repositories outside this
  batch, especially release workflows in core/data/runtime repos.
